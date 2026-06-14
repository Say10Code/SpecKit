#!/usr/bin/env python3
"""
backup_data.py — создаёт бэкап Data-слоя ObsidianDB.

Бэкапит: wiki/, Specifications/, specs-extracted/, notes/, Clippings/
Пропускает: !INCOMING/Specs/ (временные артефакты speckit), .gitkeep

Формат: ZIP-архив с метаданными, имя = obsidiandb-data-YYYY-MM-DD-HHMMSS.zip

Usage:
    python backup_data.py                          # бэкап в _backups/
    python backup_data.py --output-dir D:/backups  # свой каталог
    python backup_data.py --no-specs               # без Specifications/ (экономия 181 MB)
    python backup_data.py --compress-level 0       # без сжатия (быстрее, больше)
    python backup_data.py --json                   # вывод в JSON для автоматизации
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
import os
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent.parent  # D:\ObsidianDB

DATA_DIRS = {
    "wiki": ROOT / "wiki",
    "specifications": ROOT / "Specifications",
    "specs_extracted": ROOT / "specs-extracted",
    "notes": ROOT / "notes",
    "clippings": ROOT / "Clippings",
}

DEFAULT_OUTPUT = ROOT / "_backups"

# Sub-paths inside Specifications/ to skip (temporary artifacts)
SKIP_PATTERNS = {
    "Specifications/!INCOMING/Specs",   # speckit download temp
}

# Files to skip everywhere
SKIP_FILES = {".gitkeep", "Thumbs.db", ".DS_Store"}


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def collect_files(root: Path, base: Path, skip: set[str]) -> list[tuple[Path, str]]:
    """Walk `root`, return (absolute_path, archive_name) pairs."""
    result = []
    for dirpath, _, filenames in os.walk(root):
        for fname in sorted(filenames):
            if fname in SKIP_FILES:
                continue
            abs_path = Path(dirpath) / fname
            rel = abs_path.relative_to(base).as_posix()

            # Skip temporary artifacts
            if any(rel.startswith(p) for p in skip):
                continue

            result.append((abs_path, rel))
    return result


def build_manifest(files: dict[str, list[tuple[Path, str]]]) -> dict:
    """Build summary manifest for the backup."""
    manifest = {
        "backup_date": datetime.now(timezone.utc).isoformat(),
        "project_root": str(ROOT),
        "directories": {},
        "total_files": 0,
        "total_bytes": 0,
    }
    for dir_name, file_list in files.items():
        count = len(file_list)
        size = sum(f[0].stat().st_size for f in file_list)
        manifest["directories"][dir_name] = {
            "path": str(DATA_DIRS[dir_name]),
            "files": count,
            "bytes": size,
            "size_human": _human_size(size),
        }
        manifest["total_files"] += count
        manifest["total_bytes"] += size
    manifest["total_human"] = _human_size(manifest["total_bytes"])
    return manifest


def create_backup(
    dirs: list[str],
    output_dir: Path,
    compress: int,
    skip: set[str],
) -> Path:
    """Create a ZIP backup of the given directories."""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    archive_name = f"obsidiandb-data-{timestamp}.zip"
    archive_path = output_dir / archive_name

    # Collect all files first
    all_files: dict[str, list[tuple[Path, str]]] = {}
    total = 0
    for key in dirs:
        if key in DATA_DIRS:
            root = DATA_DIRS[key]
            if not root.exists():
                print(f"[backup] WARNING: {root} not found, skipping.", file=sys.stderr)
                continue
            files = collect_files(root, ROOT, skip)
            all_files[key] = files
            total += len(files)

    if total == 0:
        print("[backup] ERROR: No files to backup.", file=sys.stderr)
        sys.exit(1)

    manifest = build_manifest(all_files)

    # Write ZIP
    written = 0
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=compress) as zf:
        # Manifest first
        zf.writestr("MANIFEST.json", json.dumps(manifest, indent=2, ensure_ascii=False))

        for dir_name, file_list in all_files.items():
            for abs_path, arc_name in file_list:
                zf.write(abs_path, arcname=arc_name)
                written += 1
                if written % 100 == 0:
                    print(f"\r[backup] ... {written}/{total}", end="", flush=True)

    print(f"\r[backup] {written} files -> {archive_path.name}")
    return archive_path, manifest


def _human_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Backup ObsidianDB Data layer")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT),
                        help=f"Output directory (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--compress-level", type=int, default=6, choices=range(0, 10),
                        help="ZIP compression level: 0=store, 9=max (default: 6)")
    parser.add_argument("--no-wiki", action="store_true", help="Skip wiki/")
    parser.add_argument("--no-specs", action="store_true", help="Skip Specifications/")
    parser.add_argument("--no-extracted", action="store_true", help="Skip specs-extracted/")
    parser.add_argument("--no-notes", action="store_true", help="Skip notes/")
    parser.add_argument("--no-clippings", action="store_true", help="Skip Clippings/")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    # Build directory list
    dirs = []
    if not args.no_wiki: dirs.append("wiki")
    if not args.no_specs: dirs.append("specifications")
    if not args.no_extracted: dirs.append("specs_extracted")
    if not args.no_notes: dirs.append("notes")
    if not args.no_clippings: dirs.append("clippings")

    if not dirs:
        print("[backup] ERROR: All directories excluded.", file=sys.stderr)
        sys.exit(1)

    print(f"[backup] ObsidianDB Data backup")
    print(f"[backup] Directories: {', '.join(dirs)}")
    print(f"[backup] Root: {ROOT}")

    skip = set(SKIP_PATTERNS)
    archive_path, manifest = create_backup(dirs, Path(args.output_dir), args.compress_level, skip)

    if args.json:
        print(json.dumps({
            "archive": str(archive_path),
            "size_bytes": archive_path.stat().st_size,
            "size_human": _human_size(archive_path.stat().st_size),
            **manifest,
        }, indent=2, ensure_ascii=False))
    else:
        print(f"\n[backup] Archive: {archive_path}")
        print(f"[backup]         {_human_size(archive_path.stat().st_size)}")
        print(f"[backup] Contents:")
        for dir_name, info in manifest["directories"].items():
            print(f"  {dir_name:20s} {info['files']:4d} files  {info['size_human']:>10s}")
        print(f"  {'TOTAL':20s} {manifest['total_files']:4d} files  {manifest['total_human']:>10s}")


if __name__ == "__main__":
    main()
