from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
import json

def render_markdown(case_meta: Dict[str, Any], sections: Dict[str, Any]) -> str:
    lines=[]
    lines.append(f"# MAAT Report — {case_meta.get('name','')}")
    lines.append("")
    lines.append(f"- Case ID: `{case_meta.get('case_id','')}`")
    lines.append(f"- Jurisdiction: {case_meta.get('jurisdiction','')}")
    if case_meta.get("judge"):
        lines.append(f"- Judge: {case_meta.get('judge')}")
    lines.append("")
    lines.append("## 1) Process Timeline")
    lines.append(sections.get("process_timeline","(none)"))
    lines.append("")
    lines.append("## 2) Authority Event Log")
    lines.append(sections.get("authority_event_log","(none)"))
    lines.append("")
    lines.append("## 3) Unresolved Evidence Ledger")
    uel = sections.get("unresolved_evidence_ledger", [])
    if uel:
        for it in uel:
            lines.append(f"- {it}")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("## 4) Pre-Retcon Snapshot")
    prs = sections.get("pre_retcon_snapshot", {})
    lines.append("```json")
    lines.append(json.dumps(prs, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## 5) Process Integrity Notes")
    pin = sections.get("process_integrity_notes", [])
    if pin:
        for it in pin:
            lines.append(f"- {it}")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("## 6) Venue Sensitivity Matrix")
    v = sections.get("venue_sensitivity_matrix", {})
    lines.append("```json")
    lines.append(json.dumps(v, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## 7) Response Distribution Map")
    rdm = sections.get("response_distribution_map", {})
    lines.append("```json")
    lines.append(json.dumps(rdm, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## 8) Disclosure Consistency Flags")
    dcf = sections.get("disclosure_consistency_flags", [])
    if dcf:
        lines.append("```json")
        lines.append(json.dumps(dcf, ensure_ascii=False, indent=2))
        lines.append("```")
    else:
        lines.append("(none)")
    lines.append("")

    # Statement consistency (Truth Engine adapter)
    scs = sections.get("statement_consistency_summary")
    if scs:
        lines.append("\n## Statement Consistency Summary")
        if isinstance(scs, dict) and scs.get("error"):
            lines.append("- Status: unavailable (analysis error).")
        else:
            lines.append(f"- Coherence score: **{scs.get('coherence_score')}**")
            lines.append(f"- Truth gradient: **{scs.get('truth_gradient')}**")
            lines.append(f"- Contradiction count (heuristic): **{scs.get('contradiction_count')}**")
            if scs.get("consistency_flags"):
                lines.append("\n**Flags (sample):**")
                for f in scs.get("consistency_flags", [])[:10]:
                    lines.append(f"- {f}")
            if scs.get("evidence_gaps"):
                lines.append("\n**Evidence gaps (sample):**")
                for g in scs.get("evidence_gaps", [])[:10]:
                    lines.append(f"- {g}")
            if scs.get("recommended_followups"):
                lines.append("\n**Recommended followups (sample):**")
                for r in scs.get("recommended_followups", [])[:10]:
                    lines.append(f"- {r}")

    return "\n".join(lines)
