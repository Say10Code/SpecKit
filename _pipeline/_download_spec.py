"""Download 3GPP specs from FTP into !INCOMING/.

Mirrors the output structure so Librarian needs zero changes.
"""

import shutil
from pathlib import Path

import httpx

from .config import CHECKOUT_DIR, HTTP_TIMEOUT, HTTP_USER_AGENT
from ._resolve_spec import (
    resolve,
    resolve_release,
    _dotted,
    _series_dir,
    _specfile_to_docx,
    _normalize_number,
    SpecRelease,
)


def download_spec(
    spec_number: str,
    target_release: str | None = None,
    *,
    checkout_dir: Path | None = None,
) -> Path | None:
    """Download a 3GPP spec .docx file into the checkout directory.

    Returns the path to the downloaded .docx file, or None on failure.
    """
    checkout = checkout_dir or CHECKOUT_DIR
    dotted = _dotted(spec_number)
    compact = _normalize_number(spec_number)
    series = _series_dir(dotted)

    # Resolve metadata
    print(f"  Resolving {dotted} (release={target_release or 'latest'})...")
    rel = resolve_release(spec_number, target_release)
    if not rel:
        print(f"  [FAIL] Could not resolve spec {dotted}")
        return None

    print(f"  Found: {dotted} v{rel.version} ({rel.release_label}) — {rel.docx_filename}")

    # Build checkout path
    #
    # Creates: !INCOMING/Specs/archive/<series>/<number>/<file>.docx
    # e.g.:  !INCOMING/Specs/archive/31_series/31.102/31102-j40.docx
    dest_dir = checkout / "Specs" / "archive" / series / dotted
    dest_dir.mkdir(parents=True, exist_ok=True)

    docx_path = dest_dir / rel.docx_filename

    # Check if already downloaded
    if docx_path.exists():
        print(f"  Already downloaded: {docx_path.name}")
        return docx_path

    # Download from 3GPP FTP
    if not rel.ftp_url:
        # Try to construct URL manually
        rel.ftp_url = (
            f"https://www.3gpp.org/ftp/Specs/archive/{series}/{dotted}/{rel.docx_filename}"
        )

    print(f"  Downloading: {rel.ftp_url} ...")
    try:
        # 3GPP FTP requires browser-like headers to avoid 403
        BROWSER_HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        client = httpx.Client(headers=BROWSER_HEADERS, timeout=HTTP_TIMEOUT,
                              follow_redirects=True)
        with client.stream("GET", rel.ftp_url) as response:
            response.raise_for_status()

            with open(docx_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)

        size_kb = docx_path.stat().st_size // 1024
        print(f"  Downloaded: {docx_path.name} ({size_kb} KB)")
        return docx_path

    except httpx.HTTPStatusError as e:
        print(f"  [FAIL] HTTP {e.response.status_code} for {rel.ftp_url}")
        return None
    except Exception as e:
        print(f"  [FAIL] {e}")
        return None
