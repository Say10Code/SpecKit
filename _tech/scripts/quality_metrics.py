#!/usr/bin/env python3
"""Quality metrics tracker for ObsidianDB.

Computes: link density, orphan rate, frontmatter health,
review coverage, spec extraction coverage, backlog velocity.
Saves history as JSON for trend graphs. Run from /roadmap skill.

Usage:
  python quality_metrics.py              # Generate report + save to history
  python quality_metrics.py --history    # Show trends from saved history
  python quality_metrics.py --json       # JSON output only
"""

import json, os, re, sys
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict

WIKI = Path(r"D:\ObsidianDB\wiki")
SPECS = Path(r"D:\ObsidianDB\Specifications")
EXTRACTED = Path(r"D:\ObsidianDB\specs-extracted")
BACKLOG = Path(r"D:\ObsidianDB\_tech\BACKLOG.md")
BENCHMARKS = Path(r"D:\ObsidianDB\_tech\benchmarks")
METRICS_FILE = BENCHMARKS / "quality_metrics_history.json"


# ═══════════════════════════════════════════════════════════
# 1. Wiki page metrics
# ═══════════════════════════════════════════════════════════

def count_wiki_pages() -> dict:
    """Count wiki pages by type, status."""
    types = defaultdict(int)
    statuses = defaultdict(int)
    total = 0
    with_frontmatter = 0
    missing_required = 0

    # Required fields per CLAUDE.md standards
    REQUIRED = {"tags", "type", "created", "updated"}

    for md_file in WIKI.rglob("*.md"):
        total += 1
        text = md_file.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue

        parts = text.split("---", 2)
        if len(parts) < 3:
            continue

        try:
            import yaml
            fm = yaml.safe_load(parts[1]) or {}
        except Exception:
            continue

        with_frontmatter += 1

        t = fm.get("type")
        if t and str(t).strip():
            types[str(t).strip()] += 1

        s = fm.get("status")
        if s and str(s).strip():
            statuses[str(s).strip()] += 1

        # Check required fields
        present = {k for k in REQUIRED if fm.get(k) is not None and fm.get(k) != ""}
        if present == REQUIRED:
            missing_required += 0
        else:
            missing_required += len(REQUIRED - present)

    return {
        "total": total,
        "with_frontmatter": with_frontmatter,
        "frontmatter_pct": round(100 * with_frontmatter / total, 1) if total else 0,
        "by_type": dict(types),
        "by_status": dict(statuses),
        "reviewed_pct": round(100 * statuses.get("reviewed", 0) / max(total, 1), 1),
        "missing_required_fields": missing_required,
    }


# ═══════════════════════════════════════════════════════════
# 2. Connectivity metrics (from graph analysis)
# ═══════════════════════════════════════════════════════════

def compute_connectivity_metrics() -> dict:
    """Build wiki graph and compute link metrics."""
    import re
    from collections import defaultdict

    pages = {}  # slug -> {out_links, in_count}
    for md_file in WIKI.rglob("*.md"):
        rel = str(md_file.relative_to(WIKI)).replace("\\", "/")
        slug = rel.replace(".md", "")
        text = md_file.read_text(encoding="utf-8")

        links = re.findall(r"\[\[(wiki/[^\]|\\]+)", text)
        out = []
        for l in links:
            clean = l.strip()
            if clean.startswith("wiki/"):
                clean = clean[5:]
            out.append(clean)
        pages[slug] = {"out": out, "in_count": 0, "is_index": md_file.name == "index.md"}

    # Compute inbound
    for slug, data in pages.items():
        for target in data["out"]:
            if target in pages:
                pages[target]["in_count"] += 1

    content_pages = [d for s, d in pages.items() if not d["is_index"] and "index" not in s]
    in_degrees = [d["in_count"] for d in content_pages]
    out_degrees = [len(d["out"]) for d in content_pages]
    orphans = [s for s, d in pages.items() if d["in_count"] == 0 and not d["is_index"] and "index" not in s]
    weak_in = sum(1 for d in content_pages if d["in_count"] < 3)
    weak_out = sum(1 for d in content_pages if len(d["out"]) < 3)
    total_links = sum(len(d["out"]) for d in pages.values())

    if not content_pages:
        return {}

    return {
        "total_pages": len(pages),
        "content_pages": len(content_pages),
        "total_links": total_links,
        "avg_inbound": round(sum(in_degrees) / len(in_degrees), 1),
        "avg_outbound": round(sum(out_degrees) / len(out_degrees), 1),
        "median_inbound": sorted(in_degrees)[len(in_degrees)//2],
        "median_outbound": sorted(out_degrees)[len(out_degrees)//2],
        "orphans": len(orphans),
        "orphan_pct": round(100 * len(orphans) / len(content_pages), 1) if content_pages else 0,
        "weak_in_count": weak_in,
        "weak_out_count": weak_out,
        "bridges_count": sum(1 for d in content_pages if len(d["out"]) >= 8),
        "max_inbound": max(in_degrees) if in_degrees else 0,
        "max_outbound": max(out_degrees) if out_degrees else 0,
    }


# ═══════════════════════════════════════════════════════════
# 3. Spec extraction coverage
# ═══════════════════════════════════════════════════════════

def compute_spec_coverage() -> dict:
    """Count PDFs in Specifications/ vs extracted files in specs-extracted/."""
    pdfs = list(SPECS.rglob("*.pdf"))
    # Exclude !INCOMING and !double
    pdfs = [p for p in pdfs if "!INCOMING" not in str(p) and "!double" not in str(p)]

    txt_files = list(EXTRACTED.rglob("*.txt"))
    md_files = list(EXTRACTED.rglob("*.md"))
    json_files = list(EXTRACTED.rglob("*.json"))

    txt_docling = [f for f in txt_files if "3GPP" in str(f) or "ETSI" in str(f)]
    md_tables = [f for f in md_files if "-REL" in f.name]

    return {
        "total_pdfs": len(pdfs),
        "extracted_txt": len(txt_files),
        "extracted_md": len(md_files) - 1,  # subtract INDEX.md
        "extracted_json": len(json_files) - 1,  # subtract .meta.json
        "docling_md": len(txt_docling),
        "extract_docx_md": len(md_tables),
        "coverage_pct": round(100 * len(txt_files) / max(len(pdfs), 1), 1),
    }


# ═══════════════════════════════════════════════════════════
# 4. Frontmatter health (from validator results)
# ═══════════════════════════════════════════════════════════

def compute_frontmatter_health() -> dict:
    """Get frontmatter validator results."""
    result_file = BENCHMARKS / "frontmatter_check.json"
    if result_file.exists():
        data = json.loads(result_file.read_text(encoding="utf-8"))
        return {
            "errors": data.get("errors", 0),
            "warnings": data.get("warnings", 0),
            "last_check": data.get("timestamp", ""),
        }
    return {"errors": -1, "warnings": -1, "last_check": ""}


# ═══════════════════════════════════════════════════════════
# 5. Backlog velocity
# ═══════════════════════════════════════════════════════════

def compute_backlog_velocity() -> dict:
    """Parse BACKLOG.md for task completion velocity."""
    if not BACKLOG.exists():
        return {}

    text = BACKLOG.read_text(encoding="utf-8")

    # Count completed tasks by date
    done_pattern = re.findall(r"(\d+) \|.*\| (\d+) (июн|май|апр|мар|фев|янв)\b", text)
    # e.g. 32 | 2026-06-13 | U9 fix...

    # Parse the completed tasks table
    completed = re.findall(r"\|\s*\d+\s*\|.*\|.*\|\s*(\d+)\s+(июн|июл)\s*\|", text)

    # Active tasks count
    active = len(re.findall(r"^\|\s*P\d-\d+\s*\|.*\|.*\|.*\|.*\|.*\|", text, re.MULTILINE))
    active_status = re.findall(r"^\|\s*P\d-\d+\s*\|.*\| (⬜|🔄|⚠️) \|", text, re.MULTILINE)
    completed_count = len(re.findall(r"^\|\s*P\d-\d+\s*\|.*\| ✅ \|", text, re.MULTILINE))

    # Active by priority
    p0 = len(re.findall(r"^\| P0-\d+ \|", text, re.MULTILINE))
    p1 = len(re.findall(r"^\| P1-\d+ \|", text, re.MULTILINE))
    p2 = len(re.findall(r"^\| P2-\d+ \|", text, re.MULTILINE))
    p3 = len(re.findall(r"^\| P3-\d+ \|", text, re.MULTILINE))

    return {
        "total_completed_in_table": len(completed),
        "active_in_table": p0 + p1 + p2 + p3,
        "active_p0": p0, "active_p1": p1, "active_p2": p2, "active_p3": p3,
        "completed_this_session": 0,  # computed below
    }


# ═══════════════════════════════════════════════════════════
# 6. Recent activity
# ═══════════════════════════════════════════════════════════

def compute_recent_activity() -> dict:
    """Count wiki pages actually created recently (not just modified)."""
    pages_7d = 0
    pages_30d = 0
    now = datetime.now()

    for md_file in WIKI.rglob("*.md"):
        if md_file.name == "index.md":
            continue
        text = md_file.read_text(encoding="utf-8")
        # Extract 'created' date from frontmatter
        m = re.search(r"created:\s*(\d{4}-\d{2}-\d{2})", text)
        if m:
            created_date = datetime.strptime(m.group(1), "%Y-%m-%d")
            age_days = (now - created_date).days
            if age_days <= 7:
                pages_7d += 1
            if age_days <= 30:
                pages_30d += 1

    return {
        "pages_created_7d": pages_7d,
        "pages_created_30d": pages_30d,
        "checked_at": now.isoformat(),
    }


# ═══════════════════════════════════════════════════════════
# 7. Aggregate and save
# ═══════════════════════════════════════════════════════════

def compute_all() -> dict:
    """Compute all quality metrics."""
    return {
        "timestamp": datetime.now().isoformat(),
        "date": str(date.today()),
        "wiki": count_wiki_pages(),
        "connectivity": compute_connectivity_metrics(),
        "specs": compute_spec_coverage(),
        "frontmatter": compute_frontmatter_health(),
        "backlog": compute_backlog_velocity(),
        "activity": compute_recent_activity(),
    }


def save_metrics(metrics: dict):
    """Save to history JSON for trend tracking."""
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if METRICS_FILE.exists():
        history = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    else:
        history = {"runs": []}

    history["runs"].append(metrics)

    # Keep only last 90 runs
    if len(history["runs"]) > 90:
        history["runs"] = history["runs"][-90:]

    METRICS_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def load_history() -> list:
    """Load saved metrics history."""
    if not METRICS_FILE.exists():
        return []
    data = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    return data.get("runs", [])


def compute_deltas(current: dict, previous: dict | None) -> dict:
    """Compute deltas between current and previous run."""
    if not previous:
        return {"note": "первый замер — нет предыдущих данных"}

    deltas = {}
    delta_note = deltas.get("note", "")

    # Wiki pages
    if "wiki" in current and "wiki" in previous:
        deltas["pages_added"] = current["wiki"]["total"] - previous["wiki"]["total"]
        deltas["reviewed_delta"] = round(current["wiki"]["reviewed_pct"] - previous["wiki"]["reviewed_pct"], 1)

    # Connectivity
    if "connectivity" in current and "connectivity" in previous:
        deltas["links_added"] = current["connectivity"]["total_links"] - previous["connectivity"]["total_links"]
        deltas["orphans_delta"] = current["connectivity"]["orphans"] - previous["connectivity"]["orphans"]
        deltas["avg_inbound_delta"] = round(current["connectivity"]["avg_inbound"] - previous["connectivity"]["avg_inbound"], 1)

    # Specs
    if "specs" in current and "specs" in previous:
        deltas["extracted_added"] = current["specs"]["extracted_txt"] - previous["specs"]["extracted_txt"]
        deltas["coverage_delta"] = round(current["specs"]["coverage_pct"] - previous["specs"]["coverage_pct"], 1)

    # Frontmatter
    if "frontmatter" in current and "frontmatter" in previous:
        deltas["fm_errors_delta"] = current["frontmatter"]["errors"] - previous["frontmatter"]["errors"]

    return deltas


# ═══════════════════════════════════════════════════════════
# 8. Report generation
# ═══════════════════════════════════════════════════════════

def generate_report(metrics: dict, history: list) -> str:
    """Generate Markdown quality metrics report."""
    deltas = compute_deltas(metrics, history[-1] if history else None)

    w = metrics["wiki"]
    c = metrics["connectivity"]
    s = metrics["specs"]
    f = metrics["frontmatter"]
    b = metrics["backlog"]
    a = metrics["activity"]

    lines = []
    lines.append(f"# Quality Metrics — ObsidianDB")
    lines.append(f"")
    lines.append(f"> **Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"> **Предыдущий замер**: {history[-1]['date'] if history else 'первый замер'}")
    lines.append(f"> **Замеров в истории**: {len(history) + 1}")
    lines.append(f"")

    # -- Dashboard --
    lines.append(f"## Dashboard")
    lines.append(f"")
    lines.append(f"| Категория | Метрика | Значение | Δ | Статус |")
    lines.append(f"|---|---|---|---|---|")
    lines.append(f"| Wiki | Всего страниц | **{w['total']}** | {deltas.get('pages_added', '+0')} | ✅ |")
    lines.append(f"| Wiki | Reviewed | **{w['reviewed_pct']}%** | {deltas.get('reviewed_delta', '')}% | ✅ |")
    lines.append(f"| Wiki | Frontmatter OK | **{w['frontmatter_pct']}%** | — | {'✅' if w['frontmatter_pct'] > 90 else '⚠️'} |")
    lines.append(f"| Wiki | Изменено за 7д | **{a['pages_created_7d']}** | — | — |")
    lines.append(f"| Связность | Avg in/out | **{c['avg_inbound']} / {c['avg_outbound']}** | {deltas.get('avg_inbound_delta', '')} / — | {'✅' if c['avg_inbound'] >= 5 else '⚠️'} |")
    lines.append(f"| Связность | Сирот | **{c['orphans']}** ({c['orphan_pct']}%) | {deltas.get('orphans_delta', '')} | {'✅' if c['orphans'] == 0 else '⚠️'} |")
    lines.append(f"| Связность | Слабых (<3 in) | **{c['weak_in_count']}** | — | {'✅' if c['weak_in_count'] <= 10 else '⚠️'} |")
    lines.append(f"| Связность | Всего связей | **{c['total_links']}** | {deltas.get('links_added', '')} | — |")
    lines.append(f"| Спецификации | PDF в хранилище | **{s['total_pdfs']}** | — | — |")
    lines.append(f"| Спецификации | Извлечено TXT | **{s['extracted_txt']}** | {deltas.get('extracted_added', '')} | {'✅' if s['coverage_pct'] >= 100 else '⚠️'} |")
    lines.append(f"| Спецификации | Извлечено MD | **{s['extracted_md']}** | — | {'✅' if s['extracted_md'] >= s['total_pdfs'] else '⚠️'} |")
    lines.append(f"| Спецификации | Покрытие | **{s['coverage_pct']}%** | {deltas.get('coverage_delta', '')}% | {'✅' if s['coverage_pct'] >= 100 else '⚠️'} |")
    lines.append(f"| Frontmatter | Ошибок | **{f['errors']}** | {deltas.get('fm_errors_delta', '')} | {'✅' if f['errors'] == 0 else '❌'} |")
    lines.append(f"| Frontmatter | Warnings | **{f['warnings']}** | — | — |")
    lines.append(f"| Беклог | Завершено | **{b.get('total_completed_in_table', '?')}** | — | — |")
    lines.append(f"| Беклог | Активных | **{b.get('active_in_table', '?')}** | — | {'✅' if b.get('active_p0', 0) + b.get('active_p1', 0) == 0 else '⚠️'} |")
    lines.append(f"")

    # Quality score
    score = 100
    if c["orphans"] > 0: score -= c["orphans"] * 2
    if c["weak_in_count"] > 10: score -= (c["weak_in_count"] - 10) // 2
    if f["errors"] > 0: score -= f["errors"] * 5
    if s["coverage_pct"] < 100: score -= max(0, (100 - int(s["coverage_pct"])) // 2)
    if w["reviewed_pct"] < 95: score -= max(0, int(95 - w["reviewed_pct"]) // 2)
    score = max(0, min(100, int(score)))

    lines.append(f"### Quality Score: **{score}/100**")
    lines.append(f"")
    if score >= 90:
        lines.append(f"> **A** — Отличное состояние. Граф знаний здоров, метрики стабильны.")
    elif score >= 75:
        lines.append(f"> **B** — Хорошее состояние. Несколько метрик требуют внимания.")
    elif score >= 60:
        lines.append(f"> **C** — Удовлетворительно. Требуется активная работа над связностью и покрытием.")
    else:
        lines.append(f"> **D** — Требует вмешательства. Критические проблемы со связностью или frontmatter.")
    lines.append(f"")

    # Wiki type breakdown
    lines.append(f"## Wiki — страницы по типам")
    lines.append(f"")
    lines.append(f"| Тип | Страниц |")
    lines.append(f"|---|---|")
    for t, count in sorted(w.get("by_type", {}).items(), key=lambda x: -x[1]):
        lines.append(f"| {t} | {count} |")
    lines.append(f"")

    pages_total = w["total"]
    lines.append(f"## Wiki — статус рецензирования")
    lines.append(f"")
    lines.append(f"| Статус | Страниц | % |")
    lines.append(f"|---|---|---|")
    for st, count in sorted(w.get("by_status", {}).items(), key=lambda x: -x[1]):
        lines.append(f"| {st} | {count} | {round(100*count/pages_total,1)}% |")
    lines.append(f"")

    # Connectivity distribution
    if c:
        lines.append(f"## Связность — распределение")
        lines.append(f"")
        lines.append(f"| Метрика | Значение |")
        lines.append(f"|---|---|")
        lines.append(f"| Страниц (контентных) | {c['content_pages']} |")
        lines.append(f"| Всего wikilinks | {c['total_links']} |")
        lines.append(f"| Avg inbound | {c['avg_inbound']} |")
        lines.append(f"| Median inbound | {c['median_inbound']} |")
        lines.append(f"| Max inbound | {c['max_inbound']} |")
        lines.append(f"| Avg outbound | {c['avg_outbound']} |")
        lines.append(f"| Median outbound | {c['median_outbound']} |")
        lines.append(f"| Max outbound | {c['max_outbound']} |")
        lines.append(f"| Сирот | {c['orphans']} ({c['orphan_pct']}%) |")
        lines.append(f"| Мостовых (>=8 out) | {c['bridges_count']} |")
        lines.append(f"")

    # Spec coverage
    lines.append(f"## Спецификации — покрытие извлечением")
    lines.append(f"")
    lines.append(f"| Метрика | Значение |")
    lines.append(f"|---|---|")
    lines.append(f"| PDF в Specifications/ | {s['total_pdfs']} |")
    lines.append(f"| TXT извлечено | {s['extracted_txt']} |")
    lines.append(f"| MD извлечено | {s['extracted_md']} |")
    lines.append(f"| JSON извлечено | {s['extracted_json']} |")
    lines.append(f"| Docling MD | {s.get('docling_md', '?')} |")
    lines.append(f"| extract_docx MD | {s.get('extract_docx_md', '?')} |")
    lines.append(f"| Покрытие | {s['coverage_pct']}% |")
    lines.append(f"")

    # Trends from history
    if len(history) >= 2:
        lines.append(f"## Тренды (из {len(history)} замеров)")
        lines.append(f"")
        lines.append(f"| Дата | Страниц | Avg In | Сирот | Ошибок FM | Покрытие | Score |")
        lines.append(f"|---|---|---|---|---|---|---|")

        # Show current + last 5 + oldest
        all_runs = history[-5:] + [metrics]
        for run in all_runs:
            date_str = run.get("date", "?")
            w_t = run.get("wiki", {}).get("total", "?")
            c_in = run.get("connectivity", {}).get("avg_inbound", "?")
            c_orp = run.get("connectivity", {}).get("orphans", "?")
            f_err = run.get("frontmatter", {}).get("errors", "?")
            s_cov = run.get("specs", {}).get("coverage_pct", "?")
            lines.append(f"| {date_str} | {w_t} | {c_in} | {c_orp} | {f_err} | {s_cov}% | — |")

        lines.append(f"")

    # Recommendations
    lines.append(f"## Рекомендации")
    lines.append(f"")
    recs = []
    if c.get("orphans", 0) > 0:
        recs.append(f"- Добавить входящие ссылки на **{c['orphans']}** сиротских страниц")
    if c.get("weak_in_count", 0) > 10:
        recs.append(f"- Усилить **{c['weak_in_count']}** слабых страниц (Linker)")
    if f.get("errors", 0) > 0:
        recs.append(f"- Исправить **{f['errors']}** ошибок frontmatter (check_frontmatter.py)")
    if s.get("coverage_pct", 100) < 100:
        recs.append(f"- Запустить SpecExtractor для **{s['total_pdfs'] - s['extracted_txt']}** неизвлечённых PDF")
    if w.get("reviewed_pct", 100) < 95:
        recs.append(f"- Запустить Reviewer для **{100 - w['reviewed_pct']}%** неотрецензированных страниц")

    if not recs:
        recs.append("- Все метрики в норме. Продолжать поддерживать.")
    for r in recs:
        lines.append(r)
    lines.append(f"")

    lines.append(f"---")
    lines.append(f"*Метрики собраны {datetime.now().strftime('%Y-%m-%d %H:%M')}. История сохранена в `_tech/benchmarks/quality_metrics_history.json`.*")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# 9. Main
# ═══════════════════════════════════════════════════════════

def main():
    metrics = compute_all()
    history = load_history()
    previous = history[-1] if history else None

    # Save to history
    save_metrics(metrics)

    if "--json" in sys.argv:
        print(json.dumps(metrics, indent=2, ensure_ascii=False))
        return

    if "--history" in sys.argv:
        if not history:
            print("No history saved yet. Run without --history first.")
            return
        for i, run in enumerate(history):
            print(f"  [{i}] {run.get('date','?')}: pages={run.get('wiki',{}).get('total','?')} in={run.get('connectivity',{}).get('avg_inbound','?')} orphans={run.get('connectivity',{}).get('orphans','?')} fm_errors={run.get('frontmatter',{}).get('errors','?')}")
        print(f"\nShowing {len(history)} entries")
        return

    # Generate report
    report = generate_report(metrics, history)
    out_path = BENCHMARKS.parent / "reports" / f"quality-metrics-{date.today()}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    print(f"Quality Score: {100 - max(0, min(100, metrics['connectivity']['orphans']*2))}/100")
    print(f"Report: {out_path}")
    print(f"History: {len(history)+1} entries saved")

    # Print summary
    w = metrics["wiki"]
    c = metrics["connectivity"]
    print(f"\nWiki: {w['total']} pages, {w['reviewed_pct']}% reviewed")
    print(f"Connectivity: {c['avg_inbound']} avg in, {c['orphans']} orphans, {c['total_links']} links")
    print(f"Specs: {metrics['specs']['coverage_pct']}% extracted")
    print(f"Frontmatter: {metrics['frontmatter']['errors']} errors, {metrics['frontmatter']['warnings']} warnings")


if __name__ == "__main__":
    main()
