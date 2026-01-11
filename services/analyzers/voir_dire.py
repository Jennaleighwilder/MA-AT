from __future__ import annotations
from typing import Dict, Any, List
import json, csv

def load_sjq(csv_path: str) -> List[Dict[str, str]]:
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(r) for r in reader]

def load_voir_dire_jsonl(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: 
                continue
            rows.append(json.loads(line))
    return rows

def response_distribution(voir_dire_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Events contain: {juror_label, question_id, question_text, answer_text, timestamp}
    Output: distribution by question_id and juror label.
    """
    by_q = {}
    for e in voir_dire_events:
        qid = e.get("question_id","Q?")
        by_q.setdefault(qid, {"question_text": e.get("question_text",""), "answers":[]})
        by_q[qid]["answers"].append({
            "juror": e.get("juror_label",""),
            "answer": (e.get("answer_text") or "").strip()[:300],
            "timestamp": e.get("timestamp","")
        })
    return {"questions": by_q}

def disclosure_consistency_flags(sjq_rows: List[Dict[str,str]], public_records_rows: List[Dict[str,str]] | None=None) -> List[Dict[str,Any]]:
    """
    Very conservative: flags only direct contradictions on declared litigation history yes/no
    where public record data exists in provided input.
    public_records_rows: list with keys: juror_label, field, value
    """
    flags=[]
    if not public_records_rows:
        return flags
    # Build a map: juror -> has_litigation_history (True if any row field == litigation_history and value truthy)
    pr = {}
    for r in public_records_rows:
        if r.get("field") == "litigation_history":
            pr[r.get("juror_label","")] = (r.get("value","").strip().lower() not in ("", "no", "none", "0"))
    for s in sjq_rows:
        jl = s.get("juror_label","")
        declared = (s.get("litigation_history_declared","").strip().lower() not in ("", "no", "none", "0"))
        if jl in pr and pr[jl] != declared:
            flags.append({
                "juror": jl,
                "field": "litigation_history",
                "declared": s.get("litigation_history_declared",""),
                "public_record": "indicates history" if pr[jl] else "indicates none",
                "note": "Flag for counsel review (nondisclosure consistency)."
            })
    return flags
