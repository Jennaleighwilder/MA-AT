from __future__ import annotations
import json, uuid
from typing import Optional
import yaml

from .db import connect
from .utils import now_iso
from .rules_engine import Ruleset

def add_ruleset(case_id: str, name: str, rules_path: str) -> Ruleset:
    """Add ruleset from a YAML file path (CLI use)."""
    rules = yaml.safe_load(open(rules_path, "r", encoding="utf-8"))
    return add_ruleset_yaml(case_id, name, yaml.safe_dump(rules, sort_keys=False))

def add_ruleset_yaml(case_id: str, name: str, rules_yaml: str) -> Ruleset:
    """Add ruleset from YAML text (API/UI use)."""
    rules = yaml.safe_load(rules_yaml)
    version = str(rules.get("version","1.0"))
    rs = Ruleset(name=name, version=version, rules=rules)
    rs_sha = rs.sha256()
    rid = str(uuid.uuid4())
    conn = connect()
    conn.execute(
        "INSERT INTO rulesets(ruleset_id,case_id,name,version,rules_json,sha256,created_at) VALUES(?,?,?,?,?,?,?)",
        (rid, case_id, name, version, json.dumps(rules, ensure_ascii=False, sort_keys=True), rs_sha, now_iso())
    )
    conn.commit()
    conn.close()
    return rs

def latest_ruleset(case_id: str) -> Optional[Ruleset]:
    conn = connect()
    row = conn.execute(
        "SELECT name,version,rules_json FROM rulesets WHERE case_id=? ORDER BY created_at DESC LIMIT 1",
        (case_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    name, version, rules_json = row
    return Ruleset(name=name, version=version, rules=json.loads(rules_json))
