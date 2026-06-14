"""speckit configuration — one file, 5 constants. No cascade, no env vars, no pydantic."""

from pathlib import Path

# Project root (where pyproject.toml lives)
ROOT = Path(__file__).resolve().parent.parent

# Cache directory (metadata DB + HTTP cache)
CACHE_DIR = ROOT / ".speckit"  # migrated from .3gpp-crawler (2026-06-14)

# Where downloaded specs land (Librarian expects this structure)
CHECKOUT_DIR = ROOT / "Specifications" / "!INCOMING"

# Spec metadata sources (tried in order)
SPEC_SOURCES = ["whatthespec", "threegpp"]

# HTTP settings
HTTP_TIMEOUT = 120
HTTP_USER_AGENT = "obsidiandb-speckit/0.1"

# Docling device: "auto" = CUDA if available else CPU
DEVICE = "auto"
