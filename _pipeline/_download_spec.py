"""Download 3GPP specs from FTP into !INCOMING/.

Mirrors the output structure so Librarian needs zero changes.

Strategy (tried in order):
  1. DOCX direct download (preferred — smaller, already unpacked)
  2. ZIP download (fallback — 3GPP FTP often blocks DOCX but allows ZIP)
     ZIP is unpacked and the .docx inside is placed in the checkout directory.
"""

import shutil
import zipfile
import io
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


def _try_download_url(
    url: str, dest_path: Path, http_timeout: int
) -> bool:
    """Download a file from url into dest_path. Returns True on success."""
    BROWSER_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    try:
        client = httpx.Client(headers=BROWSER_HEADERS, timeout=http_timeout,
                              follow_redirects=True)
        with client.stream("GET", url) as response:
            response.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception:
        return False


def _download_via_zip_fallback(
    dotted: str,
    series: str,
    rel: SpecRelease,
    dest_dir: Path,
    http_timeout: int,
) -> Path | None:
    """Download .zip from 3GPP FTP, extract .docx from inside.

    3GPP FTP often returns HTTP 403 for .docx but HTTP 200 for .zip
    with the same base filename (e.g. 38306-j20.zip —> 38306-j20.docx inside).
    """
    zip_filename = rel.specfile  # e.g. 38306-j20.zip
    if not zip_filename or not zip_filename.endswith(".zip"):
        return None

    zip_url = (
        f"https://www.3gpp.org/ftp/Specs/archive/{series}/{dotted}/{zip_filename}"
    )
    print(f"  DOCX blocked (HTTP 403). Trying ZIP fallback: {zip_url} ...")

    zip_tmp = dest_dir / zip_filename
    if not _try_download_url(zip_url, zip_tmp, http_timeout):
        print(f"  [FAIL] ZIP download also failed: {zip_url}")
        if zip_tmp.exists():
            zip_tmp.unlink()
        return None

    print(f"  ZIP downloaded: {zip_filename} ({zip_tmp.stat().st_size // 1024} KB)")

    # Extract .docx from ZIP
    try:
        with zipfile.ZipFile(zip_tmp) as zf:
            docx_names = [f for f in zf.namelist() if f.endswith(".docx")]
            if not docx_names:
                print(f"  [FAIL] ZIP contains no .docx: {zf.namelist()}")
                zip_tmp.unlink()
                return None
            docx_inner = docx_names[0]
            docx_data = zf.read(docx_inner)
    except zipfile.BadZipFile as e:
        print(f"  [FAIL] Corrupt ZIP: {e}")
        zip_tmp.unlink()
        return None

    docx_path = dest_dir / rel.docx_filename
    docx_path.write_bytes(docx_data)
    size_kb = docx_path.stat().st_size // 1024
    print(f"  Extracted DOCX from ZIP: {rel.docx_filename} ({size_kb} KB)")

    # Clean up: keep .docx, remove .zip
    zip_tmp.unlink()
    return docx_path


def download_spec(
    spec_number: str,
    target_release: str | None = None,
    *,
    checkout_dir: Path | None = None,
) -> Path | None:
    """Download a 3GPP spec .docx file into the checkout directory.

    Returns the path to the downloaded .docx file, or None on failure.
    Tries DOCX first, falls back to ZIP extraction if DOCX returns 403.
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
    dest_dir = checkout / "Specs" / "archive" / series / dotted
    dest_dir.mkdir(parents=True, exist_ok=True)

    docx_path = dest_dir / rel.docx_filename

    # Check if already downloaded
    if docx_path.exists():
        print(f"  Already downloaded: {docx_path.name}")
        return docx_path

    # --- Step 1: Try DOCX direct download ---
    if not rel.ftp_url:
        rel.ftp_url = (
            f"https://www.3gpp.org/ftp/Specs/archive/{series}/{dotted}/{rel.docx_filename}"
        )

    print(f"  Downloading: {rel.ftp_url} ...")
    success = _try_download_url(rel.ftp_url, docx_path, HTTP_TIMEOUT)

    if success:
        size_kb = docx_path.stat().st_size // 1024
        print(f"  Downloaded: {docx_path.name} ({size_kb} KB)")
        return docx_path

    # --- Step 2: DOCX failed — try ZIP fallback ---
    if docx_path.exists():
        docx_path.unlink()  # Remove partial/empty file

    result = _download_via_zip_fallback(dotted, series, rel, dest_dir, HTTP_TIMEOUT)
    if result:
        return result

    print(f"  [FAIL] Both DOCX and ZIP download failed for {dotted}")
    return None
