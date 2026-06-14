"""
Bridge: speckit (_pipeline/) → ObsidianDB !INCOMING

Downloads 3GPP specifications directly into Specifications/!INCOMING/
using the built-in speckit pipeline (python -m _pipeline).

Usage:
    python -m _pipeline download 31.102
    python -m _pipeline download 31.102 --release 18.0
    python -m _pipeline metadata fetch 31.102
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure _pipeline is importable
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from _pipeline._resolve_spec import resolve_spec
from _pipeline._download_spec import download_spec
from _pipeline._metadata_db import MetadataDB
from _pipeline.config import CHECKOUT_DIR


def download_specs(spec_numbers: list[str], release: str = "latest") -> int:
    """Download specs into !INCOMING via speckit (_pipeline/).

    Args:
        spec_numbers: List of spec numbers (e.g. ["31.102", "102.221"]).
        release: Release version ("latest", "18.0", "17", etc.).

    Returns:
        0 on success, non-zero on failure.
    """
    if not spec_numbers:
        print("[speckit] No specs provided.")
        return 1

    for num in spec_numbers:
        print(f"[speckit] Resolving {num} (release={release})...")
        resolved = resolve_spec(num, release=release)
        if not resolved:
            print(f"[speckit] ERROR: Could not resolve {num}")
            return 1
        print(f"[speckit] Downloading {num} → {CHECKOUT_DIR}")
        ok = download_spec(resolved, CHECKOUT_DIR)
        if not ok:
            print(f"[speckit] ERROR: Download failed for {num}")
            return 1

    print(f"[speckit] Done. Files in {CHECKOUT_DIR}")
    return 0


def crawl_specs_metadata(spec_numbers: list[str] | None = None) -> int:
    """Update spec metadata catalog (WhatTheSpec + 3GPP dynareport).

    Run this periodically to discover new spec versions.
    """
    db = MetadataDB()
    try:
        if spec_numbers:
            for num in spec_numbers:
                db.upsert_from_whatthespec(num)
        else:
            print("[speckit] Crawl-all not implemented. Provide spec numbers.")
            return 1
        print(f"[speckit] Metadata updated: {len(spec_numbers or [])} specs")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Bridge: speckit (_pipeline/) → ObsidianDB !INCOMING"
    )
    parser.add_argument(
        "specs",
        nargs="*",
        help="Spec numbers to download (e.g. 31.102 102.221)",
    )
    parser.add_argument(
        "--release", "-r",
        default="latest",
        help="Release version (default: latest)",
    )
    parser.add_argument(
        "--crawl",
        action="store_true",
        help="Update spec metadata catalog instead of downloading",
    )

    args = parser.parse_args()

    if args.crawl:
        sys.exit(crawl_specs_metadata(args.specs))
    else:
        sys.exit(download_specs(args.specs, args.release))
