"""Lightweight SQLite metadata cache — no ORM, just sqlite3."""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from .config import CACHE_DIR

SCHEMA = """
CREATE TABLE IF NOT EXISTS specs (
    spec_id     TEXT PRIMARY KEY,   -- "31.102"
    title       TEXT,
    type        TEXT,               -- "TS" / "TR"
    wg          TEXT                -- "C6"
);

CREATE TABLE IF NOT EXISTS spec_releases (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_id         TEXT NOT NULL,
    version         TEXT NOT NULL,   -- "19.4.0"
    release_label   TEXT,            -- "Rel-19"
    specfile        TEXT,            -- "31102-j40.zip"
    docx_filename   TEXT,            -- "31102-j40.docx"
    ftp_url         TEXT,            -- full URL
    fetched_at      TEXT,            -- ISO timestamp
    UNIQUE(spec_id, version)
);
"""


def _db_path() -> Path:
    """Get path to metadata SQLite database."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / "metadata.db"


def _connect() -> sqlite3.Connection:
    """Open a connection to the metadata database."""
    db = sqlite3.connect(str(_db_path()))
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    db.commit()
    return db


def store_spec(spec_id: str, title: str, type_: str, wg: str):
    """Insert or update a spec record."""
    db = _connect()
    db.execute(
        "INSERT OR REPLACE INTO specs (spec_id, title, type, wg) VALUES (?, ?, ?, ?)",
        (spec_id, title, type_, wg)
    )
    db.commit()
    db.close()


def store_release(spec_id: str, version: str, release_label: str,
                  specfile: str, docx_filename: str, ftp_url: str):
    """Insert or update a release record."""
    db = _connect()
    db.execute(
        "INSERT OR REPLACE INTO spec_releases (spec_id, version, release_label, specfile, docx_filename, ftp_url, fetched_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (spec_id, version, release_label, specfile, docx_filename, ftp_url,
         datetime.now(timezone.utc).isoformat())
    )
    db.commit()
    db.close()


def get_releases(spec_id: str) -> list[dict]:
    """Get all cached releases for a spec."""
    db = _connect()
    rows = db.execute(
        "SELECT version, release_label, specfile, docx_filename, ftp_url, fetched_at "
        "FROM spec_releases WHERE spec_id = ? ORDER BY version DESC",
        (spec_id,)
    ).fetchall()
    db.close()
    return [dict(r) for r in rows]


def get_latest_release(spec_id: str) -> dict | None:
    """Get the latest cached release (highest version)."""
    releases = get_releases(spec_id)
    return releases[0] if releases else None


def get_spec(spec_id: str) -> dict | None:
    """Get cached spec metadata."""
    db = _connect()
    row = db.execute("SELECT * FROM specs WHERE spec_id = ?", (spec_id,)).fetchone()
    db.close()
    return dict(row) if row else None
