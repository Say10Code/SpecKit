"""speckit CLI — unified interface for spec download & extraction.

Usage:
  python -m _pipeline metadata fetch 31.102
  python -m _pipeline download 31.102 [--release 18.0]
  python -m _pipeline extract docx <file> [--tables]
  python -m _pipeline extract docling <file>
  python -m _pipeline extract text <file>
  python -m _pipeline status
"""

from __future__ import annotations

import sys
from pathlib import Path

from ._resolve_spec import resolve, resolve_release, _dotted
from ._metadata_db import store_spec, store_release, get_releases, get_spec
from ._download_spec import download_spec


def cmd_metadata_fetch(spec_numbers: list[str]):
    """Fetch and cache metadata for specs."""
    for num in spec_numbers:
        meta = resolve(num)
        if not meta:
            print(f"  [FAIL] {num}: no metadata found")
            continue

        store_spec(meta.spec_number, meta.title, meta.type, meta.wg)
        print(f"  {meta.spec_number}: {meta.title} ({meta.type}, {meta.wg})")

        for rel in meta.releases:
            store_release(
                meta.spec_number, rel.version, rel.release_label,
                rel.specfile, rel.docx_filename, rel.ftp_url
            )
        print(f"    {len(meta.releases)} releases cached (latest: {meta.releases[0].version})")


def cmd_download(spec_numbers: list[str], release: str | None = None):
    """Download specs into !INCOMING/."""
    ok = 0
    fail = 0
    for num in spec_numbers:
        path = download_spec(num, target_release=release)
        if path:
            ok += 1
        else:
            fail += 1

    print(f"\nDownloaded: {ok}, Failed: {fail}")


def cmd_extract(mode: str, path: str = "", tables: bool = False, all_: bool = False):
    """Extract text from a spec file, or all files with --all."""
    if all_:
        from pathlib import Path as P
        from .config import ROOT
        specs_dir = ROOT / "Specifications"
        extracted_dir = ROOT / "specs-extracted"

        if mode == "docling":
            pdfs = [p for p in sorted(specs_dir.rglob("*.pdf"))
                    if "!INCOMING" not in str(p) and "!double" not in str(p)
                    and not list(extracted_dir.rglob(f"*{p.stem}*.md"))]
            print(f"Found {len(pdfs)} PDFs without MD")
            ok = fail = 0
            for i, pdf in enumerate(pdfs):
                topic = pdf.relative_to(specs_dir).parts[0]
                out_dir = extracted_dir / topic
                out_dir.mkdir(parents=True, exist_ok=True)
                try:
                    from .extract_docling import extract
                    md_path, json_path = extract(pdf, output_dir=out_dir)
                    ok += 1
                except Exception as e:
                    print(f"  FAIL {pdf.name}: {e}")
                    fail += 1
            print(f"\nDone. OK: {ok}, FAIL: {fail}")
        elif mode == "docx":
            docs = list(specs_dir.rglob("*.docx"))
            print(f"Found {len(docs)} .docx files")
            ok = 0
            for docx in sorted(docs):
                try:
                    from .extract_docx import extract
                    txt_path, md_path = extract(docx)
                    print(f"  {docx.name}: TXT {txt_path.stat().st_size//1024}KB, MD {md_path.stat().st_size//1024}KB")
                    ok += 1
                except Exception as e:
                    print(f"  FAIL {docx.name}: {e}")
            print(f"\nDone. OK: {ok}")
        else:
            print(f"--all is only supported for 'docling' and 'docx' modes")
        return

    file_path = Path(path)
    if not file_path.exists():
        print(f"File not found: {path}")
        return

    if mode == "docx":
        from .extract_docx import extract
        txt_path, md_path = extract(file_path)
        print(f"  {file_path.name}: TXT {txt_path.stat().st_size//1024}KB, MD {md_path.stat().st_size//1024}KB")
    elif mode == "docling":
        from .extract_docling import extract
        md_path, json_path = extract(file_path)
        print(f"  {file_path.name}: MD {md_path.stat().st_size//1024}KB, JSON {json_path.stat().st_size//1024}KB")
    elif mode == "text":
        from .extract_pypdf2 import extract
        txt_path = extract(file_path)
        print(f"  {file_path.name}: TXT {txt_path.stat().st_size//1024}KB")
    else:
        print(f"Unknown extract mode: {mode} (valid: docx, docling, text)")


def cmd_status():
    """Show pipeline status: cached specs, extracted files."""
    from .config import CACHE_DIR, CHECKOUT_DIR
    specs_extracted = Path("specs-extracted")

    print("=== speckit status ===")
    print(f"  Cache dir:  {CACHE_DIR}")
    print(f"  Checkout:   {CHECKOUT_DIR}")

    # Count specs in DB
    db_path = CACHE_DIR / "metadata.db"
    if db_path.exists():
        from ._metadata_db import _connect
        db = _connect()
        specs_count = db.execute("SELECT COUNT(*) FROM specs").fetchone()[0]
        releases_count = db.execute("SELECT COUNT(*) FROM spec_releases").fetchone()[0]
        db.close()
        print(f"  Specs cached:  {specs_count} with {releases_count} releases")
    else:
        print(f"  Specs cached:  0 (no metadata.db)")

    # Count extracted files
    if specs_extracted.exists():
        txt = len(list(specs_extracted.rglob("*.txt")))
        md = len(list(specs_extracted.rglob("*.md")))
        print(f"  Extracted: {txt} TXT + {md} MD")
    else:
        print(f"  Extracted: 0")

    # Check !INCOMING
    incoming = CHECKOUT_DIR
    if incoming.exists():
        incoming_files = len(list(incoming.rglob("*")))
        print(f"  !INCOMING:  {incoming_files} files")


def main():
    args = sys.argv[1:]

    if not args:
        print("speckit — ObsidianDB specification pipeline")
        print()
        print("Commands:")
        print("  metadata fetch <spec...>    Fetch & cache metadata")
        print("  download <spec...>          Download spec .docx into !INCOMING/")
        print("  extract docx <file>         Extract .docx -> TXT + MD tables")
        print("  extract docling <file>      Extract .pdf -> Docling MD+JSON")
        print("  extract text <file>         Extract .pdf -> flat TXT (PyPDF2)")
        print("  registry update             Enrich .spec-registry.md from WhatTheSpec API")
        print("  registry suggest <topic>    Find relevant specs by topic")
        print("  status                      Show pipeline status")
        print()
        print("Examples:")
        print("  python -m _pipeline metadata fetch 31.102")
        print("  python -m _pipeline download 31.102 --release 18.0")
        print("  python -m _pipeline extract docx 31102-j40.docx --tables")
        return

    cmd = args[0]

    if cmd == "metadata" and len(args) >= 3 and args[1] == "fetch":
        cmd_metadata_fetch(args[2:])
    elif cmd == "download":
        # Parse --release flag
        release = None
        specs = []
        i = 1
        while i < len(args):
            if args[i] == "--release" and i + 1 < len(args):
                release = args[i + 1]
                i += 2
            else:
                specs.append(args[i])
                i += 1
        if specs:
            cmd_download(specs, release=release)
        else:
            print("Usage: python -m _pipeline download <spec> [--release 18.0]")
    elif cmd == "extract" and len(args) >= 2:
        mode = args[1]
        path = args[2] if len(args) >= 3 and not args[2].startswith("--") else ""
        tables = "--tables" in args
        all_ = "--all" in args
        cmd_extract(mode, path, tables=tables, all_=all_)
    elif cmd == "registry" and len(args) >= 2:
        sub = args[1]
        if sub == "update":
            from .registry import enrich_registry
            apply_flag = "--apply" in args
            print("[registry] Fetching spec titles from WhatTheSpec API...")
            if apply_flag:
                print("[registry] --apply: will write changes to .spec-registry.md")
            changes = enrich_registry(dry_run=not apply_flag)
            new = sum(1 for c in changes if c["status"] == "new")
            updated = sum(1 for c in changes if c["status"] == "updated")
            nf = sum(1 for c in changes if c["status"] == "not_found")
            errs = sum(1 for c in changes if c["status"] == "error")
            for c in changes:
                if c["status"] in ("new", "updated"):
                    print(f"  [{c['status']}] {c['spec']:12s} {c['title'][:70]}")
                elif c["status"] == "not_found":
                    print(f"  [skip]   {c['spec']:12s} (not found on WhatTheSpec)")
                elif c["status"] == "error":
                    print(f"  [ERROR]  {c['spec']:12s} {c['title'][:50]}")
            print(f"\nSummary: {new} new, {updated} updated, {nf} skipped, {errs} errors")
            if not apply_flag:
                print("Run 'python -m _pipeline registry update --apply' to write changes.")
        elif sub == "suggest" and len(args) >= 3:
            from .registry import suggest_specs, print_suggestions
            topic = " ".join(args[2:])
            results = suggest_specs(topic)
            print_suggestions(results)
        else:
            print("Usage: python -m _pipeline registry update|suggest")
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Unknown command: {cmd}")
        print("Run without arguments for help.")


if __name__ == "__main__":
    main()
