from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any, List

from .case import get_case
from .ruleset_store import latest_ruleset
from .rules_engine import JurisdictionRulesEngine, OutputLanguageFirewall
from .ingest import list_artifacts
from .report import render_markdown
from .audit import create_audit_packet

from .analyzers.transcript import process_forensics
from .analyzers.venue import venue_sensitivity_matrix
from .analyzers.voir_dire import load_sjq, load_voir_dire_jsonl, response_distribution, disclosure_consistency_flags
from .analyzers.osint import summarize_public_social
from .analyzers.truth_engine_adapter import truth_engine_safe_summary

TEMPLATE_VERSION = "1.0"

def _latest_artifact_path(case_id: str, artifact_type: str) -> str | None:
    rows = [r for r in list_artifacts(case_id) if r[1] == artifact_type]
    if not rows:
        return None
    # rows ordered by created_at, take last
    return rows[-1][2]

def generate_report_and_audit(case_id: str) -> Dict[str, Any]:
    case = get_case(case_id)
    if not case:
        raise ValueError("case_not_found")

    rs = latest_ruleset(case_id)
    if not rs:
        raise ValueError("ruleset_not_found")

    jre = JurisdictionRulesEngine(rs)
    fw = OutputLanguageFirewall()

    sections: Dict[str, Any] = {}

    # Transcript forensics
    transcript_path = _latest_artifact_path(case_id, "transcript")
    if transcript_path:
        pf = process_forensics(transcript_path)
        # Truth Engine (internal consistency only, court-safe)
        try:
            txt = open(transcript_path, 'r', encoding='utf-8', errors='replace').read()
            sections['statement_consistency_summary'] = truth_engine_safe_summary(txt)
        except Exception as _e:
            sections['statement_consistency_summary'] = {'error': 'truth_engine_failed'}
        sections["process_timeline"] = f"Observed phase estimate: **{pf['phase_estimate']}**."
        sections["authority_event_log"] = f"Recorded authority cue count: {pf['counts']['authority_cues']}."
        sections["unresolved_evidence_ledger"] = pf["unresolved_evidence_items"]
        sections["pre_retcon_snapshot"] = {"phase_estimate": pf["phase_estimate"], "counts": pf["counts"]}
        notes: List[str] = []
        if pf["counts"]["authority_cues"] > 5 and pf["counts"]["evidence_refs"] < 3:
            notes.append("Observed authority cue density coinciding with reduced evidence references.")
        if pf["counts"]["abstraction_markers"] > pf["counts"]["evidence_refs"]:
            notes.append("Observed abstraction markers exceeding evidence references in the provided transcript.")
        sections["process_integrity_notes"] = notes

    # Venue
    venue_path = _latest_artifact_path(case_id, "venue")
    if venue_path:
        sections["venue_sensitivity_matrix"] = venue_sensitivity_matrix(venue_path)

    # SJQ + voir dire
    sjq_path = _latest_artifact_path(case_id, "sjq")
    voir_path = _latest_artifact_path(case_id, "voir_dire")
    if sjq_path and voir_path:
        sjq = load_sjq(sjq_path)
        voir = load_voir_dire_jsonl(voir_path)
        sections["response_distribution_map"] = response_distribution(sjq, voir)
        sections["disclosure_consistency_flags"] = disclosure_consistency_flags(sjq, voir)

    # Public social
    social_path = _latest_artifact_path(case_id, "public_social")
    if social_path:
        sections["public_social_summary"] = summarize_public_social(social_path)

    md = render_markdown(case, rs, sections)

    # Firewall validate
    issues = fw.validate(md)
    if issues:
        raise ValueError(f"vocabulary_firewall_violation:{issues}")

    # Persist report
    report_dir = Path(__file__).resolve().parent.parent / "data" / case_id / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = str(report_dir / "latest_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    # Audit packet: include all artifact paths that exist
    artifact_paths = []
    for at in ["transcript","venue","sjq","voir_dire","public_records","public_social"]:
        p = _latest_artifact_path(case_id, at)
        if p:
            artifact_paths.append(p)

    audit_zip = create_audit_packet(case_id, TEMPLATE_VERSION, rs.sha256(), artifact_paths, report_path)

    return {
        "case_id": case_id,
        "report_path": report_path,
        "audit_zip": audit_zip,
        "ruleset_sha256": rs.sha256(),
        "artifact_count": len(artifact_paths),
        "platform_policy_example": {k: jre.platform_allowed(k) for k in (rs.rules.get("platforms", {}) or {}).keys()}
    }
