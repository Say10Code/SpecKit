#!/usr/bin/env python3
"""
sync_data.py — синхронизирует Data-слой между проектами ObsidianDB.

Читает бэкап (ZIP от backup_data.py) и мёрджит его Data в текущий проект.

Режимы:
    --dry-run (по умолчанию)  Показать что изменится, без действий
    --apply                   Применить изменения

Стратегии конфликтов:
    --skip     (по умолчанию) Пропустить существующие файлы
    --overwrite               Заменить существующие новыми из бэкапа
    --backup                  Переименовать существующий в .bak, записать новый

Usage:
    python sync_data.py D:/backups/obsidiandb-data-2026-06-14.zip
    python sync_data.py backup.zip --dry-run
    python sync_data.py backup.zip --apply
    python sync_data.py backup.zip --apply --strategy overwrite
    python sync_data.py backup.zip --apply --only wiki,notes
    python sync_data.py backup.zip --apply --output-dir D:/OtherProject
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
import shutil
import os
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent.parent  # D:\ObsidianDB

# Directories that sync_data operates on (same as backup_data)
SYNC_DIRS = ["wiki", "Specifications", "specs-extracted", "notes", "Clippings"]

# Files to always skip
SKIP_FILES = {".gitkeep", "Thumbs.db", ".DS_Store"}


# ---------------------------------------------------------------------------
# Plan: read backup, compare, plan actions
# ---------------------------------------------------------------------------

def read_backup_manifest(zf: zipfile.ZipFile) -> dict | None:
    """Read MANIFEST.json from the backup, return its content."""
    try:
        return json.loads(zf.read("MANIFEST.json"))
    except KeyError:
        return None


def file_hash(path: Path) -> str:
    """Quick hash for size+modified_time — fast conflict detection."""
    stat = path.stat()
    return f"{stat.st_size}_{int(stat.st_mtime)}"


def plan_sync(
    backup_path: Path,
    target_root: Path,
    only_dirs: list[str] | None,
    strategy: str,
) -> list[dict]:
    """Compare backup contents against target project, return action plan."""
    plan = []

    with zipfile.ZipFile(backup_path, "r") as zf:
        manifest = read_backup_manifest(zf)
        if manifest:
            print(f"[sync] Backup from: {manifest.get('backup_date', 'unknown')}")
            print(f"[sync]              {manifest.get('total_files', '?')} files, "
                  f"{manifest.get('total_human', '?')}")
            print()

        for info in zf.infolist():
            # Skip directories and manifest
            if info.is_dir() or info.filename == "MANIFEST.json":
                continue

            # Skip files matching SKIP_FILES
            if Path(info.filename).name in SKIP_FILES:
                continue

            # Determine which sync dir this belongs to
            parts = info.filename.replace("\\", "/").split("/")
            top_dir = parts[0] if parts else ""

            # Map backup names to target names
            dir_map = {
                "wiki": "wiki",
                "specifications": "Specifications",
                "specs_extracted": "specs-extracted",
                "notes": "notes",
                "clippings": "Clippings",
            }

            target_top = dir_map.get(top_dir)
            if target_top is None:
                continue  # unknown directory

            if only_dirs and target_top not in only_dirs:
                continue

            # Target path in THIS project
            target_path = target_root / info.filename.replace("\\", "/")

            action = {
                "archive_path": info.filename,
                "target_path": str(target_path),
                "archive_size": info.file_size,
                "action": None,  # add, skip, overwrite, backup_then_overwrite
                "reason": "",
            }

            if target_path.exists():
                existing_size = target_path.stat().st_size
                if existing_size == info.file_size:
                    # Same size — assume identical (fast path)
                    action["action"] = "skip"
                    action["reason"] = f"same size ({existing_size} bytes)"
                else:
                    # Different size — conflict
                    if strategy == "skip":
                        action["action"] = "skip"
                        action["reason"] = (f"size differs: archive={info.file_size}, "
                                            f"existing={existing_size}")
                    elif strategy == "overwrite":
                        action["action"] = "overwrite"
                        action["reason"] = (f"size differs: archive={info.file_size}, "
                                            f"existing={existing_size}")
                    elif strategy == "backup":
                        action["action"] = "backup_then_overwrite"
                        action["reason"] = (f"size differs: archive={info.file_size}, "
                                            f"existing={existing_size}")
            else:
                action["action"] = "add"
                action["reason"] = "new file"

            plan.append(action)

    return plan


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

def apply_plan(backup_path: Path, plan: list[dict], dry_run: bool) -> dict:
    """Execute the sync plan."""
    stats = {"add": 0, "skip": 0, "overwrite": 0, "backup_then_overwrite": 0, "errors": 0}
    actions_taken = [a for a in plan if a["action"] not in ("skip",)]

    if dry_run:
        return stats

    if not actions_taken:
        return stats

    with zipfile.ZipFile(backup_path, "r") as zf:
        for action in actions_taken:
            target = Path(action["target_path"])
            act = action["action"]

            try:
                if act == "add" or act == "overwrite":
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(action["archive_path"]) as src:
                        with open(target, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                    stats[act] += 1
                    if stats[act] % 50 == 0:
                        print(f"\r[sync] ... {sum(stats.values())}/{len(actions_taken)}",
                              end="", flush=True)

                elif act == "backup_then_overwrite":
                    bak = target.with_suffix(target.suffix + ".bak")
                    target.rename(bak)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(action["archive_path"]) as src:
                        with open(target, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                    stats[act] += 1

            except Exception as e:
                print(f"\n[sync] ERROR on {action['archive_path']}: {e}", file=sys.stderr)
                stats["errors"] += 1

    if not dry_run and stats["add"] + stats["overwrite"] + stats["backup_then_overwrite"] > 0:
        print()

    return stats


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def print_plan(plan: list[dict]):
    """Show sync plan in readable form."""
    by_action: dict[str, list[dict]] = {}
    for a in plan:
        by_action.setdefault(a["action"], []).append(a)

    total = len(plan)

    # Summary table
    labels = {
        "add": "NEW — будут добавлены",
        "overwrite": "OVERWRITE — будут заменены",
        "backup_then_overwrite": "BACKUP+OVERWRITE — старый → .bak, новый записан",
        "skip": "SKIP — пропущены",
    }

    print(f"\n{'='*60}")
    print(f"SYNC PLAN: {total} files total")
    print(f"{'='*60}")

    for act in ["add", "overwrite", "backup_then_overwrite", "skip"]:
        items = by_action.get(act, [])
        if items:
            label = labels.get(act, act)
            size = sum(a["archive_size"] for a in items)
            print(f"\n  {label}: {len(items)} files ({_human_size(size)})")
            # Show first 5 examples
            for a in items[:5]:
                print(f"    {a['archive_path']}")
            if len(items) > 5:
                print(f"    ... и ещё {len(items) - 5}")


def print_result(stats: dict):
    """Show sync result."""
    print(f"\n{'='*60}")
    print(f"SYNC RESULT")
    print(f"{'='*60}")
    print(f"  Added:            {stats['add']}")
    print(f"  Overwritten:      {stats['overwrite']}")
    print(f"  Backed-up+New:    {stats['backup_then_overwrite']}")
    print(f"  Skipped:          {stats['skip']}")
    if stats["errors"]:
        print(f"  Errors:           {stats['errors']}")
    total = sum(v for k, v in stats.items() if k != "skip")
    print(f"  Total changed:    {total}")


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------

def print_warnings(backup_path: Path, target_root: Path):
    """Print cross-project warnings."""

    # Check if this is a cross-project sync
    is_cross_project = target_root.resolve() != ROOT.resolve()
    if is_cross_project:
        print(f"[sync] ⚠️  CROSS-PROJECT sync: {backup_path} → {target_root}")
        print(f"[sync]    wikilinks внутри wiki/ содержат пути относительно исходного vault.")
        print(f"[sync]    После синхронизации запусти Linker для перелинковки.")

    # Warn about large syncs
    try:
        size = backup_path.stat().st_size
        if size > 500 * 1024 * 1024:  # > 500 MB
            print(f"[sync] ⚠️  Large backup: {_human_size(size)}. Sync может занять время.")
    except Exception:
        pass


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
    parser = argparse.ArgumentParser(
        description="Sync ObsidianDB Data from backup into project"
    )
    parser.add_argument("backup", help="Path to backup ZIP (from backup_data.py)")
    parser.add_argument(
        "--apply", action="store_true",
        help="Apply changes (default: dry-run — show what would change)"
    )
    parser.add_argument(
        "--strategy", choices=["skip", "overwrite", "backup"], default="skip",
        help="Conflict resolution: skip (default), overwrite, backup"
    )
    parser.add_argument(
        "--only", default=None,
        help="Comma-separated dirs to sync: wiki,Specifications,specs-extracted,notes,Clippings"
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Target project root (default: current project)"
    )

    args = parser.parse_args()

    backup_path = Path(args.backup)
    if not backup_path.exists():
        print(f"[sync] ERROR: Backup not found: {backup_path}", file=sys.stderr)
        sys.exit(1)

    target_root = Path(args.output_dir) if args.output_dir else ROOT
    only_dirs = [d.strip() for d in args.only.split(",")] if args.only else None

    print_warnings(backup_path, target_root)

    # Phase 1: Plan
    print(f"[sync] Analyzing: {backup_path.name}")
    plan = plan_sync(backup_path, target_root, only_dirs, args.strategy)
    print_plan(plan)

    changes = [a for a in plan if a["action"] != "skip"]
    if not changes:
        print("\n[sync] No changes needed — project is up to date.")
        return

    # Phase 2: Apply (or dry-run)
    if args.apply:
        print(f"\n[sync] Applying {len(changes)} changes (strategy: {args.strategy})...")
        stats = apply_plan(backup_path, plan, dry_run=False)
        print_result(stats)
    else:
        print(f"\n[sync] Dry run — {len(changes)} changes would be applied.")
        print(f"[sync] Run with --apply to execute.")


if __name__ == "__main__":
    main()
