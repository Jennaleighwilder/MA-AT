from __future__ import annotations
import os, sqlite3
from pathlib import Path

DB_PATH = os.environ.get("MAAT_DB", str(Path(__file__).resolve().parent.parent / "maat.sqlite"))

def db_path() -> str:
    return DB_PATH

def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

def init_db(schema_path: str | None = None) -> None:
    """
    Initialize DB using schema/maat.sql.
    """
    if schema_path is None:
        schema_path = str(Path(__file__).resolve().parent.parent / "schema" / "maat.sql")
    conn = connect()
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def init_db_if_needed() -> None:
    """
    Create schema if the DB file is empty/uninitialized.
    """
    # If DB doesn't exist, init.
    if not os.path.exists(DB_PATH):
        init_db()
        return
    # If tables missing, init.
    conn = connect()
    try:
        row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cases'").fetchone()
        if not row:
            init_db()
    finally:
        conn.close()
