import json
import os
import sqlite3
from typing import Any, List, Optional

DB_PATH = os.getenv("BOT_DB_PATH", "bot.db")

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
    return conn

def get_raw(key: str) -> Optional[str]:
    conn = _conn()
    try:
        cur = conn.execute("SELECT v FROM kv WHERE k=?", (key,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()

def set_raw(key: str, value: str) -> None:
    conn = _conn()
    try:
        conn.execute(
            "INSERT INTO kv(k,v) VALUES(?,?) "
            "ON CONFLICT(k) DO UPDATE SET v=excluded.v",
            (key, value),
        )
        conn.commit()
    finally:
        conn.close()

def get_str(key: str, default: str) -> str:
    v = get_raw(key)
    return default if v is None else str(v)

def set_str(key: str, value: str) -> None:
    set_raw(key, str(value))

def get_int(key: str, default: int) -> int:
    v = get_raw(key)
    try:
        return default if v is None else int(v)
    except Exception:
        return default

def set_int(key: str, value: int) -> None:
    set_raw(key, str(int(value)))

def get_bool(key: str, default: bool) -> bool:
    v = get_raw(key)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")

def set_bool(key: str, value: bool) -> None:
    set_raw(key, "true" if value else "false")

def get_json(key: str, default: Any) -> Any:
    v = get_raw(key)
    if v is None:
        return default
    try:
        return json.loads(v)
    except Exception:
        return default

def set_json(key: str, value: Any) -> None:
    set_raw(key, json.dumps(value, ensure_ascii=False))

def get_list(key: str, default: Optional[List[str]] = None) -> List[str]:
    if default is None:
        default = []
    v = get_json(key, default)
    return v if isinstance(v, list) else default

def set_list(key: str, value: List[str]) -> None:
    set_json(key, value)
