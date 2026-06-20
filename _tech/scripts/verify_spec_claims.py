#!/usr/bin/env python3
"""
Universal Deep Spec Verification Engine.
Извлекает утверждения из статьи и сверяет с эталонными текстами спецификаций.
Доменно-независим: никаких FID/RAT-Type в коде — только структурные паттерны.
Использует grep для быстрого поиска в больших файлах.
"""

import re, sys, json, argparse, subprocess
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict


# ── Data ─────────────────────────────────────────────────────────

@dataclass
class Claim:
    claim_type: str  # hex_value, section_ref, code_block, table_row, key_value, numeric, encoding, structural, prose
    text: str
    line: int
    spec_ref: str = ""
    expected_value: str = ""
    context: str = ""

@dataclass
class Finding:
    claim: Claim
    verdict: str  # VERIFIED | NOT_FOUND | NEEDS_SPEC | AMBIGUOUS
    evidence: str = ""
    suggestion: str = ""

# ── Spec Discovery ───────────────────────────────────────────────

def discover_specs(dirs: list[Path]) -> dict[str, Path]:
    """Найти файлы спецификаций: {spec_name: path-to-txt-or-md}."""
    specs: dict[str, Path] = {}
    for base in dirs:
        if not base.exists():
            continue
        for f in base.rglob("*"):
            if not f.is_file() or f.suffix.lower() not in ('.txt', '.md'):
                continue
            name = _spec_name(f)
            if name:
                # Prefer larger file (more complete extraction)
                existing = specs.get(name)
                if not existing or f.stat().st_size > existing.stat().st_size:
                    specs[name] = f
    return specs

def _spec_name(path: Path) -> str:
    stem = path.stem
    # 38331-j20 → TS 38.331
    m = re.match(r'(\d{2})(\d{3})', stem.replace('-', '').replace('_', ''))
    if m:
        return f"TS {int(m.group(1))}.{int(m.group(2)):03d}"
    # ts_131102v171000p → TS 131.102
    m = re.match(r'ts[_-](\d{2})(\d{3})', stem, re.IGNORECASE)
    if m:
        return f"TS {int(m.group(1))}.{int(m.group(2)):03d}"
    return ""

# ── Grep utility ─────────────────────────────────────────────────

def grep_file(path: Path, pattern: str) -> tuple[str, int]:
    """Grep for pattern in file. Returns (matching_line, line_number)."""
    try:
        r = subprocess.run(
            ['grep', '-n', '-m', '1', '-F', pattern, str(path)],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0 and ':' in r.stdout:
            parts = r.stdout.strip().split(':', 1)
            return (parts[1][:300], int(parts[0]))
    except Exception:
        pass
    return ("", 0)

def grep_any_spec(specs: dict[str, Path], pattern: str) -> tuple[str, str, int]:
    """Search all specs for pattern. Returns (spec_name, line, line_number)."""
    for name, path in specs.items():
        line, num = grep_file(path, pattern)
        if line:
            return (name, line, num)
    return ("", "", 0)

# ── Claim Extraction ─────────────────────────────────────────────

def extract_claims(text: str) -> list[Claim]:
    """Extract all verifiable claims from article text (domain-agnostic)."""
    lines = text.split('\n')
    claims = []

    # 1. Hex values: 0x6F07, '6F07'H, 9000h
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'\b(0x[0-9A-Fa-f]{2,})\b', line):
            claims.append(Claim('hex_value', line.strip()[:200], i,
                               expected_value=m.group(1).upper(),
                               spec_ref=_infer_spec(lines, i, line),
                               context=_ctx(lines, i)))

    # 2. Section refs: TS 38.331 §6.3.3, ^[TS 24.008 §10.5.1.6]
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'(?:TS|TR)\s+[\d.]+\s+[§]\s*([\d]+(?:\.[\d]+)*[A-Za-z]?)', line):
            claims.append(Claim('section_ref', m.group(0), i,
                               expected_value=m.group(1),
                               spec_ref=_infer_spec(lines, i, line),
                               context=_ctx(lines, i)))

    # 3. Provenance: ^[TS 38.331 §6.2.1]
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'\^\[(?:TS|TR)\s+[\d.]+\s+[§]\s*([\d.]+[A-Za-z]?)\]', line):
            claims.append(Claim('section_ref', m.group(0), i,
                               expected_value=m.group(1),
                               spec_ref=_infer_spec(lines, i, line),
                               context=_ctx(lines, i)))

    # 4. Code blocks: ```asn1 ... ```
    in_block = False
    block_lines, block_start = [], 0
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```') and not in_block:
            in_block, block_lines, block_start = True, [], i
        elif in_block and line.strip() == '```':
            in_block = False
            content = '\n'.join(block_lines)
            m = re.search(r'(\w[\w-]*)\s*::=\s*(?:SEQUENCE|CHOICE|ENUMERATED)', content)
            if m:
                claims.append(Claim('code_block', content[:500], block_start,
                                   expected_value=m.group(1),
                                   spec_ref=_infer_spec(lines, block_start, '\n'.join(block_lines[:3])),
                                   context=_ctx(lines, block_start)))
        elif in_block:
            block_lines.append(line)

    # 5. Key=Value pairs
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'\b([A-Z][A-Za-z0-9_-]{2,40})\s*[:=]\s*([\w\d.,()/+\-]{1,60})', line):
            key, val = m.group(1), m.group(2)
            if not re.match(r'^[A-Z][a-z]+$', key):  # skip simple English words
                claims.append(Claim('key_value', m.group(0), i,
                                   expected_value=f"{key}={val}",
                                   spec_ref=_infer_spec(lines, i, line),
                                   context=_ctx(lines, i)))

    # 6. Numeric claims: "9 bytes", "size = 28"
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'(\d+)\s*(bytes?|octets?|байт|бит|records?|записей)\b', line, re.I):
            claims.append(Claim('numeric', m.group(0), i,
                               expected_value=m.group(0),
                               spec_ref=_infer_spec(lines, i, line),
                               context=_ctx(lines, i)))

    # 7. Encoding claims
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'\b(PER|DER|CSN\.1|BER-TLV|TLV|ASN\.1)\b', line):
            ctx = line[max(0,m.start()-50):m.end()+50]
            if re.search(r'кодирован|encoding|encoded|формат|formatted', ctx, re.I):
                claims.append(Claim('encoding', line.strip()[:200], i,
                                   expected_value=m.group(1).upper(),
                                   spec_ref=_infer_spec(lines, i, line),
                                   context=_ctx(lines, i)))

    # 8. Prose candidates (for AI review)
    for i, line in enumerate(lines, 1):
        clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', line)
        clean = re.sub(r'[*_`>#\[\]|]', '', clean).strip()
        if len(clean) > 50 and re.search(r'\b(TS|TR|ETSI)\s+[\d.]+', clean):
            claims.append(Claim('prose', clean[:300], i,
                               spec_ref=_infer_spec(lines, i, line),
                               context=_ctx(lines, i, 3)))

    # 9. Table rows — key cells
    in_table, header, rows = False, [], []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if '|' in s and not s.startswith('```'):
            if not in_table:
                in_table = True
                header, rows = [], []
            if '---' in s:
                if rows:
                    header = rows[-1]
                    rows = []
                continue
            if s.startswith('|') and s.endswith('|'):
                rows.append((i, s))
        elif in_table:
            in_table = False
            for ri, row in rows[1:]:  # skip header
                cells = [c.strip() for c in row[1].split('|') if c.strip()]
                for ci, cell in enumerate(cells):
                    if re.match(r'^(0x[0-9A-Fa-f]{2,}|[0-9A-Fa-f]{4}H?|\d+\s*(bytes?|octets?))$', cell):
                        hdr = header[1] if header else f"col{ci}"
                        claims.append(Claim('table_row', f"{hdr}: {cell}", ri,
                                           expected_value=cell,
                                           spec_ref=_infer_spec(lines, ri, lines[ri-1] if ri <= len(lines) else ""),
                                           context=_ctx(lines, ri, 2)))

    return claims

def _infer_spec(lines: list[str], idx: int, claim_text: str = "") -> str:
    """Find nearest spec reference."""
    # 0. Check claim's own text first (most accurate)
    for m in re.finditer(r'(?:TS|TR)\s+([\d]{2}\.[\d]{3})', claim_text):
        return f"TS {m.group(1)}"
    for m in re.finditer(r'\b(24\.008|24\.301|24\.501|44\.018|44\.060)\b', claim_text):
        return f"TS {m.group(1)}"
    # 1. Search vicinity
    for j in range(max(0,idx-40), min(len(lines),idx+40)):
        m = re.search(r'(?:TS|TR)\s+(\d{2}\.\d{3})', lines[j])
        if m:
            return f"TS {m.group(1)}"
        m = re.search(r'\b(24\.008|24\.301|24\.501|44\.018|44\.060)\b', lines[j])
        if m:
            return f"TS {m.group(1)}"
    # 2. Default: most common spec in article
    spec_counts = defaultdict(int)
    for j in range(len(lines)):
        for m in re.finditer(r'(?:TS|TR)\s+(\d{2}\.\d{3})', lines[j]):
            spec_counts[f"TS {m.group(1)}"] += 1
    if spec_counts:
        return max(spec_counts, key=spec_counts.get)
    return ""

def _ctx(lines: list[str], idx: int, r: int = 2) -> str:
    s, e = max(0,idx-r-1), min(len(lines),idx+r)
    return '\n'.join(lines[s:e])

# ── Verification ─────────────────────────────────────────────────

def verify_claims(claims: list[Claim], specs: dict[str, Path]) -> list[Finding]:
    """Verify each claim against specs using grep."""
    findings = []
    for c in claims:
        f = _verify_one(c, specs)
        findings.append(f)
    return findings

def _verify_one(c: Claim, specs: dict[str, Path]) -> Finding:
    spec_name = c.spec_ref
    spec_path = specs.get(spec_name) if spec_name else None

    if not spec_path and c.expected_value:
        # Try to find spec containing the value
        sn, _, _ = grep_any_spec(specs, c.expected_value)
        if sn:
            spec_name = sn
            spec_path = specs[sn]

    if not spec_path:
        return Finding(c, 'NEEDS_SPEC', '',
                      suggestion=f'Specificatsiya {spec_name or "?"} ne naydena. /spec-download?')

    val = c.expected_value
    if not val:
        return Finding(c, 'AMBIGUOUS', '',
                      suggestion='Net znacheniya dlya poiska')

    # Direct grep check
    try:
        r = subprocess.run(
            ['grep', '-n', '-m', '1', '-F', val, str(spec_path)],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0 and ':' in r.stdout:
            parts = r.stdout.strip().split(':', 1)
            line_text = parts[1][:300] if len(parts) > 1 else ""
            line_num = int(parts[0])
            return Finding(c, 'VERIFIED', f"{spec_name}:{line_num}: {line_text[:120]}")
    except Exception as e:
        pass

    # Try alternate formats for hex values
    if c.claim_type == 'hex_value':
        clean = val.upper().replace('0X', '').replace('0x', '')
        if len(clean) == 4:
            try:
                r = subprocess.run(
                    ['grep', '-n', '-m', '1', '-F', f"0x{clean}", str(spec_path)],
                    capture_output=True, text=True, timeout=5
                )
                if r.returncode == 0 and ':' in r.stdout:
                    parts = r.stdout.strip().split(':', 1)
                    return Finding(c, 'VERIFIED', f"{spec_name}:{parts[0]} (as 0x{clean})")
            except Exception:
                pass

    return Finding(c, 'NOT_FOUND', '',
                  suggestion=f"'{val}' ne naydeno v {spec_name}")

# ── Report ───────────────────────────────────────────────────────

def format_report(findings: list[Finding], article: Path) -> str:
    by_v = defaultdict(list)
    for f in findings:
        by_v[f.verdict].append(f)

    lines = [
        f"# Deep Spec Verify: `{article.name}`",
        f"**Claims**: {len(findings)} | **VERIFIED**: {len(by_v['VERIFIED'])} | "
        f"**NOT_FOUND**: {len(by_v['NOT_FOUND'])} | "
        f"**NEEDS_SPEC**: {len(by_v['NEEDS_SPEC'])} | "
        f"**AMBIGUOUS**: {len(by_v['AMBIGUOUS'])}",
        "", "---", ""
    ]

    for verdict, label in [('NOT_FOUND', 'Not Found'), ('NEEDS_SPEC', 'Needs Spec'), ('AMBIGUOUS', 'AI Review')]:
        fs = by_v.get(verdict, [])
        if not fs:
            continue
        lines.append(f"## {label} ({len(fs)})")
        lines.append("")
        for f in fs[:50]:
            lines.append(f"- **L{f.claim.line}** `{f.claim.claim_type}`: `{f.claim.text[:150]}`")
            if f.suggestion:
                lines.append(f"  → {f.suggestion}")
        lines.append("")

    verified = by_v.get('VERIFIED', [])
    if verified:
        lines.append(f"## Verified ({len(verified)})")
        lines.append("")
        lines.append("| Line | Type | Claim | Evidence |")
        lines.append("|---|---|---|---|")
        for f in verified[:80]:
            lines.append(f"| {f.claim.line} | `{f.claim.claim_type}` | `{f.claim.text[:80]}` | `{f.evidence[:80]}` |")

    return '\n'.join(lines)

# ── CLI ──────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='Universal Deep Spec Verification')
    p.add_argument('article', type=Path)
    p.add_argument('--specs', type=Path, nargs='+')
    p.add_argument('--json', action='store_true')
    p.add_argument('--fix', action='store_true')
    args = p.parse_args()

    article = args.article.resolve()
    if not article.exists():
        print(f"ERROR: {article} not found", file=sys.stderr)
        sys.exit(1)

    # Spec dirs
    root = Path(__file__).resolve().parent.parent.parent
    spec_dirs = [root / 'specs-extracted', root / 'Specifications' / '!INCOMING']
    if args.specs:
        spec_dirs = args.specs

    specs = discover_specs(spec_dirs)
    print(f"Specs: {len(specs)} files", file=sys.stderr)

    # Extract
    text = article.read_text(encoding='utf-8', errors='replace')
    claims = extract_claims(text)
    print(f"Claims: {len(claims)}", file=sys.stderr)

    # Verify
    findings = verify_claims(claims, specs)

    # Report
    if args.json:
        print(json.dumps([{
            'line': f.claim.line, 'type': f.claim.claim_type,
            'text': f.claim.text[:200], 'verdict': f.verdict,
            'evidence': f.evidence[:200], 'suggestion': f.suggestion
        } for f in findings], indent=2, ensure_ascii=False))
    else:
        report = format_report(findings, article)
        rp = article.with_suffix('.verify.md')
        rp.write_text(report, encoding='utf-8')
        vc = defaultdict(int)
        for f in findings:
            vc[f.verdict] += 1
        print(f"VERIFIED={vc['VERIFIED']} NOT_FOUND={vc['NOT_FOUND']} "
              f"NEEDS_SPEC={vc['NEEDS_SPEC']} AMBIGUOUS={vc['AMBIGUOUS']}")
        print(f"Report: {rp}")

    sys.exit(0)

if __name__ == '__main__':
    main()
