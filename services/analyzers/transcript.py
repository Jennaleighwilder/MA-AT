from __future__ import annotations
from typing import Dict, Any, List, Tuple
import re

def _count_phrases(text: str, phrases: List[str]) -> int:
    lower = text.lower()
    return sum(lower.count(p) for p in phrases)

def process_forensics(transcript_path: str) -> Dict[str, Any]:
    """
    Lightweight v1: detects
    - authority cues: occurrences of 'instruction', 'judge said', 'the law says', 'must'
    - evidence reference: occurrences of 'exhibit', 'testimony', 'timeline', 'record', 'document'
    - abstraction: occurrences of 'i feel', 'seems', 'kind of', 'just', 'probably'
    Produces process timeline summary + unresolved evidence placeholders if marked by [UNRESOLVED: ...]
    """
    text = open(transcript_path, "r", encoding="utf-8").read()
    authority = _count_phrases(text, ["judge said", "instruction", "the law says", "must ", "required"])
    evidence = _count_phrases(text, ["exhibit", "testimony", "timeline", "record", "document", "evidence"])
    abstraction = _count_phrases(text, ["i feel", "seems", "kind of", "just ", "probably", "maybe"])

    unresolved = re.findall(r"\[UNRESOLVED:(.*?)\]", text, flags=re.IGNORECASE|re.DOTALL)
    unresolved = [u.strip()[:220] for u in unresolved]

    # crude phase heuristics
    phase = "Evidence Assembly"
    if abstraction > evidence:
        phase = "Narrative Seeding"
    if authority > 2 and evidence < 3:
        phase = "Soft Alignment"
    if authority > 5 and abstraction > evidence:
        phase = "Convergence / Closure"

    return {
        "counts": {"authority_cues": authority, "evidence_refs": evidence, "abstraction_markers": abstraction},
        "phase_estimate": phase,
        "unresolved_evidence_items": unresolved
    }
