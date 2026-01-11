from __future__ import annotations
import hashlib, json, os
from pathlib import Path
from typing import Any, Dict, Iterable

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_json(obj: Any) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return sha256_bytes(blob)

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def now_iso() -> str:
    import datetime
    return datetime.datetime.now().isoformat(timespec="seconds")

def stable_inputs_hash(hashes: Iterable[str]) -> str:
    # Combine hashes deterministically
    joined = "\n".join(sorted(hashes)).encode("utf-8")
    return sha256_bytes(joined)
