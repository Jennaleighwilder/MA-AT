from __future__ import annotations
import json, uuid
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .db import connect
from .utils import now_iso

@dataclass
class Case:
    case_id: str
    name: str
    jurisdiction: str
    judge: Optional[str]
    created_at: str

def create_case(name: str, jurisdiction: str, judge: Optional[str]=None) -> Case:
    cid = str(uuid.uuid4())
    created = now_iso()
    conn = connect()
    conn.execute(
        "INSERT INTO cases(case_id,name,jurisdiction,judge,created_at) VALUES(?,?,?,?,?)",
        (cid, name, jurisdiction, judge, created)
    )
    conn.commit()
    conn.close()
    return Case(case_id=cid, name=name, jurisdiction=jurisdiction, judge=judge, created_at=created)

def get_case(case_id: str) -> Case:
    conn = connect()
    row = conn.execute("SELECT case_id,name,jurisdiction,judge,created_at FROM cases WHERE case_id=?", (case_id,)).fetchone()
    conn.close()
    if not row:
        raise KeyError(f"case_id not found: {case_id}")
    return Case(*row)
