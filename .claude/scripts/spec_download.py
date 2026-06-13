"""
Bridge: 3gpp-crawler → ObsidianDB !INCOMING

Downloads 3GPP specifications directly into Specifications/!INCOMING/
using the globally installed spec-crawler CLI tool.

Usage from agent (Bash):
    # Download single spec (latest release)
    uvx spec-crawler checkout 31.102 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"

    # Download specific release
    uvx spec-crawler checkout 31.102 --release 18.0 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"

    # Download multiple specs
    uvx spec-crawler checkout 31.102 102.221 102.223 --checkout-dir "D:\ObsidianDB\Specifications\!INCOMING"

No authentication required — all spec downloads use public 3GPP FTP and WhatTheSpec.

Cache lives in: D:\ObsidianDB\.3gpp-crawler\
(TDC_CACHE_DIR env var set by CLAUDE.md or .env)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Paths
OBSIDIAN_DB = Path(r"D:\ObsidianDB")
INCOMING = OBSIDIAN_DB / "Specifications" / "!INCOMING"
CACHE_DIR = OBSIDIAN_DB / ".3gpp-crawler"

# Ensure cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def download_specs(spec_numbers: list[str], release: str = "latest") -> int:
    """Download specs into !INCOMING via spec-crawler.

    Args:
        spec_numbers: List of spec numbers (e.g. ["31.102", "102.221"]).
        release: Release version ("latest", "18.0", "17", etc.).

    Returns:
        Exit code from spec-crawler.
    """
    if not spec_numbers:
        print("[spec_download] No specs provided.")
        return 1

    cmd = [
        "spec-crawler", "checkout",
        *spec_numbers,
        "--release", release,
        "--checkout-dir", str(INCOMING),
    ]

    env = {
        **__import__("os").environ,
        "TDC_CACHE_DIR": str(CACHE_DIR),
    }

    print(f"[spec_download] Running: {' '.join(cmd)}")
    print(f"[spec_download] Output → {INCOMING}")

    result = subprocess.run(cmd, env=env)
    return result.returncode


def crawl_specs_metadata() -> int:
    """Update spec metadata catalog (WhatTheSpec + 3GPP dynareport).

    Run this periodically to discover new spec versions.
    No authentication required.
    """
    cmd = ["spec-crawler", "crawl"]
    env = {
        **__import__("os").environ,
        "TDC_CACHE_DIR": str(CACHE_DIR),
    }

    print(f"[spec_download] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)
    return result.returncode


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Bridge: 3gpp-crawler → ObsidianDB !INCOMING"
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
        sys.exit(crawl_specs_metadata())
    else:
        sys.exit(download_specs(args.specs, args.release))
