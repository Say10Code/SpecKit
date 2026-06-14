"""Resolve spec metadata: number → versions, filenames, FTP URLs.

Sources (tried in order):
  1. WhatTheSpec API — public REST, no auth
  2. 3GPP Dynareport — legacy portal, follows redirect
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import httpx

from .config import HTTP_TIMEOUT, HTTP_USER_AGENT, SPEC_SOURCES

WHATSPEC_URL = "https://whatthespec.net/3gpp/spec.php?q={compact}&api=1"
DYNAREPORT_URL = "https://www.3gpp.org/dynareport/{compact}.htm"
FTP_BASE = "https://www.3gpp.org/ftp/Specs/archive"


@dataclass
class SpecRelease:
    version: str          # "19.4.0"
    release_label: str    # "Rel-19"
    specfile: str         # "31102-j40.zip"
    docx_filename: str    # "31102-j40.docx"
    ftp_url: str          # full URL to .docx on 3GPP FTP


@dataclass
class SpecMetadata:
    spec_number: str      # "31.102"
    title: str
    type: str             # "TS" / "TR"
    wg: str               # "C6"
    releases: list[SpecRelease] = field(default_factory=list)


def _normalize_number(spec_number: str) -> str:
    """Accept dotted (31.102) or undotted (31102). Return compact form (31102)."""
    number = spec_number.strip()
    if "." in number:
        return number.replace(".", "")
    return number


def _dotted(number: str) -> str:
    """Convert compact (31102) to dotted (31.102)."""
    if "." in number:
        return number
    # TS numbers: 31102 → 31.102, 351206 → 35.206
    # Pattern: first 2-3 digits = series, rest = sub-number
    if len(number) <= 5:
        return f"{number[:2]}.{number[2:]}"
    else:
        # e.g. 15101004 → 15.101.004? Actually 151.010.04 → 151.010-04
        # For ObsidianDB scope we handle: 31xxx, 33xxx, 35xxx, 102xxx, 151xxx
        if number.startswith("1"):
            return f"{number[:3]}.{number[3:5]}.{number[5:]}" if len(number) >= 5 else f"{number[:3]}.{number[3:]}"
        return f"{number[:2]}.{number[2:]}"


def _series_dir(spec_number: str) -> str:
    """Convert spec number to 3GPP FTP series directory. E.g. 31.102 → 31_series."""
    dotted = _dotted(spec_number)
    series = dotted.split(".")[0]
    return f"{series}_series"


def _specfile_to_docx(specfile: str) -> str:
    """Convert .zip filename to .docx. E.g. 31102-j40.zip → 31102-j40.docx."""
    return specfile.replace(".zip", ".docx")


def resolve_whatthespec(spec_number: str) -> SpecMetadata | None:
    """Query WhatTheSpec API for spec metadata."""
    compact = _normalize_number(spec_number)
    url = WHATSPEC_URL.format(compact=compact)

    try:
        r = httpx.get(url, timeout=HTTP_TIMEOUT, headers={"User-Agent": HTTP_USER_AGENT})
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        print(f"  [WARN] WhatTheSpec API: {exc}")
        return None

    if not isinstance(data, list) or not data:
        print(f"  [WARN] WhatTheSpec API: unexpected response format")
        return None

    entry = data[0]
    dotted = _dotted(spec_number)
    title = entry.get("title", "")
    spec_type = entry.get("type", "TS")
    wg = entry.get("WG", "")
    versions: list[str] = entry.get("vers", [])
    specfiles: list[str] = entry.get("specfile", [])
    releases: list[str] = entry.get("release", [])

    # Build release objects
    result_releases = []
    series = _series_dir(dotted)
    for i, version in enumerate(versions):
        zipfile = specfiles[i] if i < len(specfiles) else ""
        docx_file = _specfile_to_docx(zipfile)
        ftp_url = f"{FTP_BASE}/{series}/{dotted}/{docx_file}" if zipfile else ""

        rel_label = releases[i] if i < len(releases) else ""

        result_releases.append(SpecRelease(
            version=version,
            release_label=rel_label,
            specfile=zipfile,
            docx_filename=docx_file,
            ftp_url=ftp_url,
        ))

    return SpecMetadata(
        spec_number=dotted,
        title=title,
        type=spec_type,
        wg=wg,
        releases=result_releases,
    )


def resolve_dynareport(spec_number: str) -> SpecMetadata | None:
    """Query 3GPP Dynareport (legacy portal) for spec metadata.
    Falls back if WhatTheSpec is unavailable."""
    compact = _normalize_number(spec_number)
    url = DYNAREPORT_URL.format(compact=compact)

    try:
        r = httpx.get(url, timeout=HTTP_TIMEOUT,
                       headers={"User-Agent": HTTP_USER_AGENT},
                       follow_redirects=True)
        r.raise_for_status()
    except Exception as exc:
        print(f"  [WARN] 3GPP Dynareport: {exc}")
        return None

    # Dynareport returns JSON after redirect
    try:
        data = r.json()
    except Exception:
        return None

    dotted = _dotted(spec_number)
    title = data.get("title", "")
    spec_type = data.get("type", "TS")
    wg = data.get("wg", "")

    return SpecMetadata(
        spec_number=dotted,
        title=title,
        type=spec_type,
        wg=wg,
        releases=[],
    )


def resolve(spec_number: str, *, source: str | None = None) -> SpecMetadata | None:
    """Resolve spec metadata from available sources."""
    sources = [source] if source else SPEC_SOURCES

    for src in sources:
        if src == "whatthespec":
            meta = resolve_whatthespec(spec_number)
            if meta and meta.releases:
                return meta
        elif src == "threegpp":
            meta = resolve_dynareport(spec_number)
            if meta:
                return meta

    return None


def resolve_release(spec_number: str, target_release: str | None = None) -> SpecRelease | None:
    """Resolve a specific release version. If target_release is None, return latest."""
    meta = resolve(spec_number)
    if not meta or not meta.releases:
        return None

    if target_release is None:
        return meta.releases[0]  # latest is first

    # Normalize target: "16", "16.0", "Rel-16", "v16.0.0" → major version "16"
    target = target_release.strip().lower()
    target = target.replace("rel-", "").replace("rel", "").replace("v", "").replace("-", "")

    # Target is "16.0" → try exact match first, then prefix match
    # Target is "16" → prefix match

    for rel in meta.releases:
        if rel.version == target or rel.version.startswith(target):
            return rel

    # As fallback, try major version only: "16.0" → "16"
    if "." in target:
        major = target.split(".")[0]
        # Already tried "16.0", now try just "16" if it wasn't already
        if target != major:
            for rel in meta.releases:
                if rel.version.startswith(major + "."):
                    return rel

    return None
