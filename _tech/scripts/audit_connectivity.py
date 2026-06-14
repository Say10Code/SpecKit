#!/usr/bin/env python3
"""Deep connectivity audit for ObsidianDB wiki/ knowledge graph.

Usage:
  python audit_connectivity.py              # Full audit
  python audit_connectivity.py --json       # JSON output
  python audit_connectivity.py --fix        # Suggest specific wikilinks to add

Output: _tech/reports/connectivity-audit-YYYY-MM-DD.md (or .json)
"""

import json, re, sys
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

WIKI = Path(r"D:\ObsidianDB\wiki")
OUTPUT = Path(r"D:\ObsidianDB\_tech\reports")


def parse_wikilinks(text: str) -> list[str]:
    """Extract [[wiki/...]] targets from markdown text. Strips wiki/ prefix."""
    # Match [[wiki/path]] or [[wiki/path|display]] or [[wiki/path\|display]]
    links = re.findall(r'\[\[(wiki/[^\]|\\]+)', text)
    result = []
    for l in links:
        clean = l.strip()
        if clean.startswith('wiki/'):
            clean = clean[5:]  # strip wiki/ prefix
        result.append(clean)
    return result


def build_graph():
    """Build directed graph: node_id -> {outgoing links}, <- {incoming links}."""
    pages = {}          # slug -> {path, frontmatter_type, out_links, in_links}
    index_pages = set() # pages that are index.md files

    for md_file in sorted(WIKI.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        rel = str(md_file.relative_to(WIKI)).replace("\\", "/")
        slug = rel.replace(".md", "")

        # Extract type from frontmatter
        fm_type = None
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                import yaml
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                    fm_type = fm.get("type")
                except Exception:
                    pass

        # Extract outgoing wikilinks
        out_links = parse_wikilinks(text)
        # Normalise: remove anchor fragments, deduplicate
        seen = set()
        unique_out = []
        for l in out_links:
            l_clean = l.split("#")[0]
            if l_clean not in seen and l_clean != slug:
                seen.add(l_clean)
                unique_out.append(l_clean)

        is_index = md_file.name == "index.md"
        if is_index:
            index_pages.add(slug)

        pages[slug] = {
            "path": rel,
            "type": fm_type,
            "out": unique_out,
            "in_count": 0,
            "in_from": set(),
            "is_index": is_index,
        }

    # Also parse non-wiki links (Specifications, notes, etc.)
    def parse_external_links(text: str) -> list[str]:
        """Extract [[...]] targets that are NOT wiki/ links."""
        return re.findall(r'\[\[(?!wiki/)([^\]|#]+)', text)

    # Compute inbound links
    broken_links = []
    for slug, data in pages.items():
        for target in data["out"]:
            if target in pages:
                pages[target]["in_count"] += 1
                pages[target]["in_from"].add(slug)
            else:
                # Check if it might be an external wikilink (Specifications, notes, Roadmap)
                if not target.startswith("Specifications/") and not target.startswith("notes/") and target != "Roadmap":
                    broken_links.append((slug, target))

    # Convert in_from sets to lists for JSON
    for data in pages.values():
        data["in_from"] = sorted(data["in_from"])

    return pages, broken_links, index_pages


def find_orphans(pages, index_pages):
    """Pages with 0 inbound links (excluding index pages)."""
    return [s for s, d in pages.items() if d["in_count"] == 0 and not d["is_index"] and s not in index_pages]


def find_weak(pages, index_pages, threshold=3):
    """Pages with <threshold inbound OR outbound links."""
    weak_in = []
    weak_out = []
    for slug, data in pages.items():
        if data["is_index"] or slug in index_pages:
            continue
        if data["in_count"] < threshold:
            weak_in.append((slug, data["in_count"], len(data["out"])))
        if len(data["out"]) < threshold:
            weak_out.append((slug, data["in_count"], len(data["out"])))
    return weak_in, weak_out


def find_isolated_clusters(pages, index_pages):
    """Find groups of pages that only link to each other (no external wiki links)."""
    # Build undirected graph
    graph = defaultdict(set)
    for slug, data in pages.items():
        if data["is_index"]:
            continue
        for target in data["out"]:
            if target in pages and not pages[target]["is_index"]:
                graph[slug].add(target)
                graph[target].add(slug)

    # Find connected components via BFS
    visited = set()
    clusters = []

    for slug in sorted(pages.keys()):
        if slug in visited or pages[slug]["is_index"]:
            continue
        if slug not in graph:
            # Single page with no links at all
            continue

        # BFS
        component = set()
        queue = [slug]
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            component.add(node)
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    queue.append(neighbor)

        if len(component) >= 2:
            # Check if this component has external links
            has_external = False
            for node in component:
                for target in pages[node]["out"]:
                    if target in pages and target not in component and not pages[target]["is_index"]:
                        has_external = True
                        break
                for source in pages[node]["in_from"]:
                    if source not in component and not (source in index_pages or pages.get(source, {}).get("is_index")):
                        has_external = True
                        break

            if not has_external and len(component) >= 2:
                clusters.append(sorted(component))

    return clusters


def find_bridges(pages, index_pages):
    """Find bridge pages that connect different clusters/sections of the graph."""
    # Betweenness approximation: pages that link between different wiki/ subdirs
    bridges = []
    for slug, data in pages.items():
        if data["is_index"]:
            continue
        # Count distinct target directories
        target_dirs = set()
        source_dirs = set()
        for target in data["out"]:
            parts = target.split("/")
            if len(parts) >= 2:
                target_dirs.add(parts[0])
        for source in data["in_from"]:
            parts = source.split("/")
            if len(parts) >= 2:
                source_dirs.add(parts[0])

        # Bridge = links to OR from 3+ different wiki/ subdirectories
        if len(target_dirs) >= 3 or len(source_dirs) >= 3:
            bridges.append((slug, sorted(target_dirs), sorted(source_dirs),
                          data["in_count"], len(data["out"])))

    bridges.sort(key=lambda x: -len(x[1]) - len(x[2]))
    return bridges


def find_cross_reference_gaps(pages):
    """Find pages that reference the same spec/entity but don't link to each other."""
    # Group pages by shared outbound links
    shared_targets = defaultdict(set)
    for slug, data in pages.items():
        if data["is_index"]:
            continue
        for target in data["out"]:
            if target.startswith("wiki/summaries/") or target.startswith("wiki/concepts/"):
                shared_targets[target].add(slug)

    gaps = []
    for target, sources in shared_targets.items():
        if len(sources) >= 3:
            # Check which pairs don't link to each other
            sources_list = sorted(sources)
            for i, s1 in enumerate(sources_list):
                for s2 in sources_list[i+1:]:
                    if s2 not in pages[s1]["out"] and s1 not in pages[s2]["out"]:
                        # Both reference same source but don't link to each other
                        if pages[s1]["type"] == pages[s2]["type"] or True:
                            gaps.append((s1, s2, target))

    # Deduplicate and take top
    seen_pairs = set()
    unique_gaps = []
    for s1, s2, target in gaps:
        pair = tuple(sorted([s1, s2]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_gaps.append((s1, s2, target))
            if len(unique_gaps) >= 30:
                break

    return unique_gaps


def compute_link_density(pages, index_pages):
    """Compute link density metrics."""
    content_pages = [d for s, d in pages.items() if not d["is_index"] and s not in index_pages]

    if not content_pages:
        return {}

    in_degrees = [d["in_count"] for d in content_pages]
    out_degrees = [len(d["out"]) for d in content_pages]

    return {
        "total_pages": len(pages),
        "content_pages": len(content_pages),
        "index_pages": len(index_pages),
        "total_links": sum(len(d["out"]) for d in pages.values()),
        "avg_inbound": sum(in_degrees) / len(in_degrees),
        "avg_outbound": sum(out_degrees) / len(out_degrees),
        "median_inbound": sorted(in_degrees)[len(in_degrees)//2],
        "median_outbound": sorted(out_degrees)[len(out_degrees)//2],
        "max_inbound": max(in_degrees),
        "max_outbound": max(out_degrees),
        "inbound_distribution": dict(Counter(in_degrees).most_common(10)),
        "outbound_distribution": dict(Counter(out_degrees).most_common(10)),
    }


def build_type_connectivity_matrix(pages):
    """Build connectivity matrix by page type."""
    types = defaultdict(lambda: {"count": 0, "total_in": 0, "total_out": 0, "cross_type_links": Counter()})

    for slug, data in pages.items():
        if data["is_index"] or not data["type"]:
            continue
        t = data["type"]
        types[t]["count"] += 1
        types[t]["total_in"] += data["in_count"]
        types[t]["total_out"] += len(data["out"])

        for target in data["out"]:
            if target in pages and pages[target].get("type") and pages[target]["type"] != t:
                types[t]["cross_type_links"][pages[target]["type"]] += 1

    return dict(types)


def generate_report(pages, broken_links, index_pages):
    """Generate connectivity audit report."""
    orphans = find_orphans(pages, index_pages)
    weak_in, weak_out = find_weak(pages, index_pages)
    clusters = find_isolated_clusters(pages, index_pages)
    bridges = find_bridges(pages, index_pages)
    gaps = find_cross_reference_gaps(pages)
    density = compute_link_density(pages, index_pages)
    type_matrix = build_type_connectivity_matrix(pages)

    lines = []
    lines.append(f"# Connectivity Audit — ObsidianDB wiki/")
    lines.append(f"")
    lines.append(f"> **Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"> **Метод**: Полный граф-анализ wikilinks")
    lines.append(f"> **Страниц**: {density['total_pages']} ({density['content_pages']} контентных + {density['index_pages']} индексов)")
    lines.append(f"> **Связей**: {density['total_links']}")
    lines.append(f"")

    # Dashboard
    lines.append(f"## Dashboard")
    lines.append(f"")
    lines.append(f"| Метрика | Значение | Статус |")
    lines.append(f"|---|---|---|")
    lines.append(f"| Битых ссылок | {len(broken_links)} | {'✅' if len(broken_links)==0 else '❌'} |")
    lines.append(f"| Сирот (0 inbound) | {len(orphans)} | {'✅' if len(orphans)==0 else '❌'} |")
    lines.append(f"| Слабых (<3 in) | {len(weak_in)} | {'⚠️' if len(weak_in)>5 else '✅'} |")
    lines.append(f"| Слабых (<3 out) | {len(weak_out)} | {'⚠️' if len(weak_out)>5 else '✅'} |")
    lines.append(f"| Изолированных кластеров | {len(clusters)} | {'⚠️' if clusters else '✅'} |")
    lines.append(f"| Мостовых страниц | {len(bridges)} | {'ℹ️' if bridges else '—'} |")
    lines.append(f"| Cross-ref пробелов | {len(gaps)} | {'⚠️' if gaps else '✅'} |")
    lines.append(f"| Средняя связность | {density['avg_inbound']:.1f} in / {density['avg_outbound']:.1f} out | — |")
    lines.append(f"")

    # Summary verdict
    issues = len(broken_links) + len(orphans) + (1 if len(weak_in) > 10 else 0) + (1 if clusters else 0)
    if issues == 0 and len(weak_in) <= 5:
        lines.append(f"> **Вердикт**: ✅ HEALTHY — нет критических проблем связности.")
    elif issues <= 5:
        lines.append(f"> **Вердикт**: ⚠️ NEEDS ATTENTION — {issues} проблем требуют исправления.")
    else:
        lines.append(f"> **Вердикт**: ❌ DEGRADED — {issues} проблем, требуется Linker.")
    lines.append(f"")

    # Broken links
    if broken_links:
        lines.append(f"## ❌ Битые ссылки ({len(broken_links)})")
        lines.append(f"")
        for src, target in broken_links[:15]:
            lines.append(f"- `{src}` → `[[{target}]]` — **страница не существует**")
        if len(broken_links) > 15:
            lines.append(f"- ... и ещё {len(broken_links) - 15}")
        lines.append(f"")

    # Orphans
    if orphans:
        lines.append(f"## ❌ Сиротские страницы ({len(orphans)})")
        lines.append(f"")
        lines.append(f"Страницы с 0 входящих wikilinks:")
        lines.append(f"")
        for o in orphans[:15]:
            t = pages[o]["type"] or "?"
            lines.append(f"- `{o}` (type={t}) — ни одна страница не ссылается")
        if len(orphans) > 15:
            lines.append(f"- ... и ещё {len(orphans) - 15}")
        lines.append(f"")

    # Weak pages
    if weak_in:
        lines.append(f"## ⚠️ Слабые страницы — <3 входящих ({len(weak_in)})")
        lines.append(f"")
        lines.append(f"| Страница | In | Out | Тип |")
        lines.append(f"|---|---|---|---|")
        for slug, inc, outg in sorted(weak_in, key=lambda x: x[1])[:20]:
            t = pages[slug]["type"] or "?"
            lines.append(f"| `{slug}` | {inc} | {outg} | {t} |")
        lines.append(f"")

    if weak_out:
        lines.append(f"## ⚠️ Слабые страницы — <3 исходящих ({len(weak_out)})")
        lines.append(f"")
        lines.append(f"| Страница | In | Out | Тип |")
        lines.append(f"|---|---|---|---|")
        for slug, inc, outg in sorted(weak_out, key=lambda x: x[2])[:10]:
            t = pages[slug]["type"] or "?"
            lines.append(f"| `{slug}` | {inc} | {outg} | {t} |")
        lines.append(f"")

    # Isolated clusters
    if clusters:
        lines.append(f"## ⚠️ Изолированные кластеры ({len(clusters)})")
        lines.append(f"")
        lines.append(f"Группы страниц, связанных только между собой (нет внешних ссылок):")
        lines.append(f"")
        for i, cluster in enumerate(clusters[:5]):
            types_in = Counter(pages[s]["type"] for s in cluster if pages[s]["type"])
            lines.append(f"### Кластер {i+1}: {len(cluster)} страниц ({', '.join(f'{t}({c})' for t,c in types_in.most_common(3))})")
            for s in cluster:
                lines.append(f"- `{s}`")
            # Suggest bridge
            lines.append(f"  → **Рекомендация**: добавить хотя бы 1 внешнюю ссылку из кластера на `wiki/concepts/...` или `wiki/summaries/...`")
            lines.append(f"")

    # Bridge pages
    if bridges:
        lines.append(f"## 🔗 Мостовые страницы ({len(bridges)})")
        lines.append(f"")
        lines.append(f"Страницы, соединяющие разные разделы wiki/:")
        lines.append(f"")
        lines.append(f"| Страница | Связывает разделы | In | Out |")
        lines.append(f"|---|---|---|---|")
        for slug, t_dirs, s_dirs, inc, outg in bridges[:15]:
            dirs = sorted(set(t_dirs) | set(s_dirs))
            lines.append(f"| `{slug}` | {', '.join(dirs[:5])} | {inc} | {outg} |")
        lines.append(f"")

    # Cross-reference gaps
    if gaps:
        lines.append(f"## 🔍 Cross-reference пробелы ({len(gaps)})")
        lines.append(f"")
        lines.append(f"Пары страниц, ссылающихся на один источник, но не друг на друга:")
        lines.append(f"")
        for s1, s2, shared in gaps[:10]:
            lines.append(f"- `{s1}` ↔ `{s2}` — обе ссылаются на `{shared}`, но не связаны между собой")
        lines.append(f"")

    # Type connectivity matrix
    lines.append(f"## 📊 Матрица связности по типам")
    lines.append(f"")
    lines.append(f"| Тип | Страниц | Avg In | Avg Out | Cross-type links |")
    lines.append(f"|---|---|---|---|---|")
    for t in ["concept", "entity", "summary", "synthesis", "reference", "research", "note"]:
        if t in type_matrix:
            d = type_matrix[t]
            cross = sum(d["cross_type_links"].values())
            lines.append(f"| **{t}** | {d['count']} | {d['total_in']/d['count']:.1f} | {d['total_out']/d['count']:.1f} | {cross} |")
    lines.append(f"")

    # Link density distribution
    lines.append(f"## 📈 Распределение связности")
    lines.append(f"")
    lines.append(f"### Inbound links")
    lines.append(f"")
    lines.append(f"| Степень | Страниц |")
    lines.append(f"|---|---|")
    for deg, count in sorted(density.get("inbound_distribution", {}).items())[:10]:
        bar = "█" * min(count, 30)
        lines.append(f"| {deg} in | {count} {bar} |")
    lines.append(f"")

    lines.append(f"### Outbound links")
    lines.append(f"")
    lines.append(f"| Степень | Страниц |")
    lines.append(f"|---|---|")
    for deg, count in sorted(density.get("outbound_distribution", {}).items())[:10]:
        bar = "█" * min(count, 30)
        lines.append(f"| {deg} out | {count} {bar} |")
    lines.append(f"")

    # Recommendations
    lines.append(f"## 🔧 Приоритеты исправлений")
    lines.append(f"")
    if broken_links:
        lines.append(f"1. **Срочно**: исправить {len(broken_links)} битых ссылок")
    if orphans:
        lines.append(f"2. **Срочно**: добавить входящие ссылки на {len(orphans)} сиротских страниц")
    if weak_in:
        lines.append(f"3. **Важно**: усилить {len(weak_in)} страниц с <3 входящими ссылками")
    if clusters:
        lines.append(f"4. **Планово**: создать мосты для {len(clusters)} изолированных кластеров")
    if gaps:
        lines.append(f"5. **Оптимизация**: связать {len(gaps)} тематически близких страниц")
    if not any([broken_links, orphans, weak_in, clusters]):
        lines.append(f"Граф знаний в хорошем состоянии. Рекомендуется повторный аудит через 7 дней.")
    lines.append(f"")

    report = "\n".join(lines)
    return report, {
        "broken_links": len(broken_links),
        "orphans": len(orphans),
        "weak_in": len(weak_in),
        "weak_out": len(weak_out),
        "clusters": len(clusters),
        "bridges": len(bridges),
        "gaps": len(gaps),
        "density": density,
        "broken_links_list": [(s, t) for s, t in broken_links],
        "orphans_list": orphans,
        "clusters_list": [[str(s) for s in c] for c in clusters],
    }


def main():
    pages, broken_links, index_pages = build_graph()
    report, metrics = generate_report(pages, broken_links, index_pages)

    if "--json" in sys.argv:
        print(json.dumps(metrics, indent=2, ensure_ascii=False))
        return

    # Save report
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = OUTPUT / f"connectivity-audit-{date_str}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Report: {out_path}")

    # Print summary
    print(f"Pages: {metrics['density']['total_pages']} ({metrics['density']['content_pages']} content)")
    print(f"Links: {metrics['density']['total_links']}")
    print(f"Broken links: {metrics['broken_links']}")
    print(f"Orphans: {metrics['orphans']}")
    print(f"Weak (<3 in): {metrics['weak_in']}")
    print(f"Weak (<3 out): {metrics['weak_out']}")
    print(f"Isolated clusters: {metrics['clusters']}")
    print(f"Bridges: {metrics['bridges']}")
    print(f"Cross-ref gaps: {metrics['gaps']}")
    print(f"Avg connectivity: {metrics['density']['avg_inbound']:.1f} in / {metrics['density']['avg_outbound']:.1f} out")

    # Suggest fixes
    if metrics["broken_links"] > 0:
        print(f"\n[!] {metrics['broken_links']} broken links need fixing")
    if metrics["orphans"] > 0:
        print(f"[!] {metrics['orphans']} orphan pages need incoming links")
    if metrics["clusters"] > 0:
        print(f"[!] {metrics['clusters']} isolated clusters need bridges")
    if all([metrics["broken_links"] == 0, metrics["orphans"] == 0, metrics["clusters"] == 0]):
        print("\n[OK] Wiki knowledge graph is HEALTHY")


if __name__ == "__main__":
    main()
