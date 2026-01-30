# storage.py
import json
from typing import Any, Optional, List

from replit import db

def get_str(key: str, default: str) -> str:
    return str(db.get(key, default))

def set_str(key: str, value: str) -> None:
    db[key] = str(value)

def get_int(key: str, default: int) -> int:
    v = db.get(key, default)
    try:
        return int(v)
    except Exception:
        return default

def set_int(key: str, value: int) -> None:
    db[key] = int(value)

def get_bool(key: str, default: bool) -> bool:
    v = db.get(key, default)
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.lower() in ("1", "true", "yes", "on")
    return bool(v)

def set_bool(key: str, value: bool) -> None:
    db[key] = bool(value)

def get_json(key: str, default: Any) -> Any:
    raw = db.get(key, None)
    if raw is None:
        return default
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return default

def set_json(key: str, value: Any) -> None:
    db[key] = json.dumps(value, ensure_ascii=False)

def get_list(key: str, default: Optional[List[str]] = None) -> List[str]:
    if default is None:
        default = []
    v = get_json(key, default)
    if isinstance(v, list):
        return v
    return default

def set_list(key: str, value: List[str]) -> None:
    set_json(key, value)
