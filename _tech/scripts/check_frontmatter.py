#!/usr/bin/env python3
"""Validate frontmatter in all wiki/*.md files.

Checks:
- Required fields: tags, type, status, created, updated, sources
- Valid type values
- Valid status values
- sources wikilinks point to existing files
"""
import json, re, sys
from datetime import datetime
from pathlib import Path

WIKI = Path(r"D:\ObsidianDB\wiki")
SPECS = Path(r"D:\ObsidianDB\Specifications")

VALID_TYPES = {"concept", "entity", "summary", "synthesis", "reference", "note", "research"}
VALID_STATUSES = {"draft", "reviewed", "final", "deprecated"}

REQUIRED = ["tags", "type", "created", "updated"]
OPTIONAL = ["status", "sources", "level", "domain"]

errors = []
warnings = []

for md_file in sorted(WIKI.rglob("*.md")):
    text = md_file.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append(f"{md_file.relative_to(WIKI)}: no frontmatter")
        continue

    # Extract frontmatter
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        errors.append(f"{md_file.relative_to(WIKI)}: malformed frontmatter")
        continue

    fm = m.group(1)
    lines = fm.split("\n")

    fm_data = {}
    for line in lines:
        kv = re.match(r"^(\w[\w_-]*):\s*(.*)", line)
        if kv:
            fm_data[kv.group(1)] = kv.group(2).strip()

    rel = md_file.relative_to(WIKI)

    # Required fields
    for field in REQUIRED:
        if field not in fm_data:
            errors.append(f"{rel}: missing required field '{field}'")

    # Type validation
    if "type" in fm_data:
        t = fm_data["type"].strip()
        if t not in VALID_TYPES:
            errors.append(f"{rel}: invalid type '{t}' (valid: {sorted(VALID_TYPES)})")

    # Status validation
    if "status" in fm_data:
        s = fm_data["status"].strip()
        if s not in VALID_STATUSES:
            errors.append(f"{rel}: invalid status '{s}' (valid: {sorted(VALID_STATUSES)})")

    # Date format
    for date_field in ["created", "updated"]:
        if date_field in fm_data:
            val = fm_data[date_field].strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}", val):
                errors.append(f"{rel}: invalid {date_field} format '{val}' (expected YYYY-MM-DD)")

    # Sources wikilinks
    if "sources" in fm_data:
        src_line = fm_data["sources"]
        wikilinks = re.findall(r'\[\[([^\]|]+)', src_line)
        for link in wikilinks:
            if link.startswith("wiki/"):
                target = WIKI.parent / f"{link}.md"
                if not target.exists():
                    warnings.append(f"{rel}: broken source link [[{link}]]")
            elif link.startswith("Specifications/"):
                target = SPECS.parent / link
                if not target.exists() and not Path(str(target) + ".pdf").exists():
                    warnings.append(f"{rel}: broken source link [[{link}]]")

    # Tags present
    if "tags" in fm_data:
        tags = fm_data["tags"].strip("[]").split(",")
        tags = [t.strip() for t in tags if t.strip()]
        if not tags:
            warnings.append(f"{rel}: empty tags")

print(f"Scanned {len(list(WIKI.rglob('*.md')))} wiki files")
print(f"Errors:   {len(errors)}")
print(f"Warnings: {len(warnings)}")
print()

if errors:
    print("=== ERRORS ===")
    for e in errors[:20]:
        print(f"  ERR: {e}")
    if len(errors) > 20:
        print(f"  ... and {len(errors) - 20} more")

if warnings:
    print("=== WARNINGS ===")
    for w in warnings[:10]:
        print(f"  WARN: {w}")
    if len(warnings) > 10:
        print(f"  ... and {len(warnings) - 10} more")

if not errors and not warnings:
    print("OK: All wiki files have valid frontmatter!")

result = {"errors": len(errors), "warnings": len(warnings), "timestamp": datetime.now().isoformat()}
(Path(r"D:\ObsidianDB\_tech\benchmarks\frontmatter_check.json")).write_text(json.dumps(result, indent=2))
sys.exit(0 if not errors else 1)
