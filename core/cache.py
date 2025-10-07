import sqlite3
import json
import os
from pathlib import Path
from typing import Optional

DB = Path(os.getenv("LOLO_HOME", Path.home() / ".lolo")) / "cache.db"
DB.parent.mkdir(parents=True, exist_ok=True)


def _hash(s: str) -> str:
    import hashlib as _h

    return _h.sha256(s.encode("utf-8")).hexdigest()


def get(key: str) -> Optional[dict]:
    h = _hash(key)
    with sqlite3.connect(DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)")
        cur = conn.execute("SELECT v FROM kv WHERE k=?", (h,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None


def set_(key: str, value: dict) -> None:
    h = _hash(key)
    val = json.dumps(value, ensure_ascii=False)
    with sqlite3.connect(DB) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)")
        conn.execute("REPLACE INTO kv (k, v) VALUES (?, ?)", (h, val))
        conn.commit()
