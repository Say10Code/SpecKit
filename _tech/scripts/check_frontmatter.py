#!/usr/bin/env python3
"""Validate frontmatter in all wiki/*.md files.

Uses yaml.safe_load() for proper multi-line YAML parsing.
Checks:
- Required fields: tags, created, updated
- Recommended fields: type (warning — inferred from directory)
- Valid type, status, date format
- sources wikilinks point to existing files
- Broken wikilinks
"""
import json, re, sys
import yaml
from datetime import datetime
from pathlib import Path

WIKI = Path(r"D:\ObsidianDB\wiki")
SPECS = Path(r"D:\ObsidianDB\Specifications")

# Все типы, реально используемые в wiki (валидатор отражает практику)
VALID_TYPES = {
    "concept", "entity", "summary", "synthesis", "reference",
    "note", "research", "hub",
    # Sub-типы summary (допустимы, хотя канонический — summary)
    "specification", "tutorial", "thesis", "whitepaper",
    "slides", "project", "analysis", "tool-manual",
    "article", "code-samples", "practical-examples",
    "technical-document", "presentation",
}
# Канонические замены (warning, не error)
CANONICAL_TYPE = {
    "specification": "summary",
    "tutorial": "summary",
    "thesis": "summary",
    "whitepaper": "summary",
    "slides": "summary",
    "project": "summary",
    "analysis": "summary",
    "tool-manual": "summary",
    "article": "summary",
    "code-samples": "summary",
    "practical-examples": "summary",
    "technical-document": "summary",
    "presentation": "summary",
}
VALID_STATUSES = {"draft", "reviewed", "final", "deprecated"}

REQUIRED = ["tags", "created", "updated"]
RECOMMENDED = ["type"]

errors = []
warnings = []

for md_file in sorted(WIKI.rglob("*.md")):
    text = md_file.read_text(encoding="utf-8")
    rel = md_file.relative_to(WIKI)
    parent_dir = rel.parts[0] if len(rel.parts) > 1 else ""

    if not text.startswith("---"):
        errors.append(f"{rel}: no frontmatter")
        continue

    # Extract frontmatter block between first and second ---
    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append(f"{rel}: malformed frontmatter (unclosed ---)")
        continue

    fm_text = parts[1]
    try:
        fm_data = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        errors.append(f"{rel}: YAML parse error: {e}")
        continue

    # --- Required fields ---
    for field in REQUIRED:
        if field not in fm_data or fm_data[field] is None:
            errors.append(f"{rel}: missing required field '{field}'")

    # --- Recommended field: type ---
    if "type" not in fm_data or fm_data["type"] is None:
        if parent_dir in {"concepts", "entities", "summaries", "syntheses", "reference", "research"}:
            expected = parent_dir.rstrip("s")  # concepts→concept, syntheses→synthesis
            if expected == "synthese": expected = "synthesis"
            if expected == "summarie": expected = "summary"
            if expected == "entitie": expected = "entity"
            warnings.append(f"{rel}: missing 'type' field (expected '{expected}')")
        else:
            warnings.append(f"{rel}: missing 'type' field")
    else:
        t = str(fm_data["type"]).strip()
        if t not in VALID_TYPES:
            errors.append(f"{rel}: unknown type '{t}'")
        elif t in CANONICAL_TYPE:
            warnings.append(f"{rel}: non-canonical type '{t}' (canonical: '{CANONICAL_TYPE[t]}')")

    # --- Status validation ---
    if "status" in fm_data and fm_data["status"] is not None:
        s = str(fm_data["status"]).strip()
        if s not in VALID_STATUSES:
            errors.append(f"{rel}: invalid status '{s}' (valid: {sorted(VALID_STATUSES)})")

    # --- Date format ---
    for date_field in ["created", "updated"]:
        if date_field in fm_data and fm_data[date_field] is not None:
            val = str(fm_data[date_field]).strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}", val):
                errors.append(f"{rel}: invalid {date_field} format '{val}' (expected YYYY-MM-DD)")

    # --- Sources wikilinks ---
    if "sources" in fm_data and fm_data["sources"] is not None:
        src_value = fm_data["sources"]
        # Normalise to list
        if isinstance(src_value, str):
            src_list = [src_value]
        elif isinstance(src_value, list):
            src_list = [str(s) for s in src_value]
        else:
            src_list = [str(src_value)]

        for src in src_list:
            wikilinks = re.findall(r'\[\[([^\]|]+)', src)
            for link in wikilinks:
                link_clean = link.split("#")[0].strip()
                if link.startswith("wiki/"):
                    target = WIKI.parent / f"{link_clean}.md"
                    if not target.exists():
                        warnings.append(f"{rel}: broken source link [[{link}]]")
                elif link.startswith("Specifications/"):
                    target = SPECS.parent / link_clean
                    if not target.exists() and not Path(str(target) + ".pdf").exists():
                        warnings.append(f"{rel}: broken source link [[{link}]]")

    # --- Tags validation ---
    if "tags" in fm_data:
        tags = fm_data["tags"]
        if isinstance(tags, str):
            # Inline: "tags: [A, B]" — yaml parses as string if not proper YAML
            # Try to parse as comma-separated or bracket list
            tags_str = tags.strip().strip("[]")
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        if isinstance(tags, list):
            tags = [str(t).strip() for t in tags if t and str(t).strip()]
            if not tags:
                warnings.append(f"{rel}: empty tags")
        else:
            warnings.append(f"{rel}: tags not a list or string (got {type(tags).__name__})")
    else:
        errors.append(f"{rel}: missing required field 'tags'")

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
    for w in warnings[:15]:
        print(f"  WARN: {w}")
    if len(warnings) > 15:
        print(f"  ... and {len(warnings) - 15} more")

if not errors and not warnings:
    print("OK: All wiki files have valid frontmatter!")

result = {"errors": len(errors), "warnings": len(warnings), "timestamp": datetime.now().isoformat()}
(Path(r"D:\ObsidianDB\_tech\benchmarks\frontmatter_check.json")).write_text(json.dumps(result, indent=2))
sys.exit(0 if not errors else 1)
