from __future__ import annotations
import argparse, os, json, csv
from pathlib import Path
import yaml

from .db import init_db
from .case import create_case, get_case
from .ruleset_store import add_ruleset, latest_ruleset
from .ingest import ingest_artifact, list_artifacts
from .rules_engine import JurisdictionRulesEngine, OutputLanguageFirewall
from .analyzers.osint import summarize_public_social
from .analyzers.venue import venue_sensitivity_matrix
from .analyzers.voir_dire import load_sjq, load_voir_dire_jsonl, response_distribution, disclosure_consistency_flags
from .analyzers.transcript import process_forensics
from .report import render_markdown
from .audit import create_audit_packet
from .utils import now_iso, ensure_dir, sha256_file

ROOT = Path(__file__).resolve().parent.parent

def cmd_initdb(_):
    schema = str(ROOT / "schema" / "maat.sql")
    init_db(schema)
    print("DB initialized at", os.environ.get("MAAT_DB", str(ROOT / "maat.sqlite")))

def cmd_newcase(args):
    c = create_case(args.name, args.jurisdiction, args.judge)
    print(json.dumps(c.__dict__, indent=2))

def cmd_addruleset(args):
    rs = add_ruleset(args.case_id, args.name, args.ruleset_path)
    print("Added ruleset", rs.name, "sha256", rs.sha256())

def cmd_ingest(args):
    aid = ingest_artifact(args.case_id, args.type, args.path)
    print("Ingested artifact", aid)

def cmd_list(args):
    for row in list_artifacts(args.case_id):
        print(row)

def cmd_report(args):
    case = get_case(args.case_id)
    rs = latest_ruleset(args.case_id)
    jre = JurisdictionRulesEngine(rs)

    # Load artifacts from provided paths (explicit, no auto-discovery)
    sections = {}

    # Transcript forensics
    if args.transcript:
        pf = process_forensics(args.transcript)
        sections["process_timeline"] = f"Observed phase estimate: **{pf['phase_estimate']}**."
        sections["authority_event_log"] = f"Recorded authority cue count: {pf['counts']['authority_cues']}."
        sections["unresolved_evidence_ledger"] = pf["unresolved_evidence_items"]
        sections["pre_retcon_snapshot"] = {"phase_estimate": pf["phase_estimate"], "counts": pf["counts"]}
        sections["process_integrity_notes"] = []
        if pf["counts"]["authority_cues"] > 5 and pf["counts"]["evidence_refs"] < 3:
            sections["process_integrity_notes"].append("Observed elevated authority cue density coinciding with reduced evidence references.")
        if pf["counts"]["abstraction_markers"] > pf["counts"]["evidence_refs"]:
            sections["process_integrity_notes"].append("Observed abstraction markers exceeding evidence references in the provided transcript segment.")

    # Venue
    if args.venue:
        sections["venue_sensitivity_matrix"] = venue_sensitivity_matrix(args.venue)

    # Voir dire / SJQ
    sjq_rows = load_sjq(args.sjq) if args.sjq else []
    vd_events = load_voir_dire_jsonl(args.voir_dire) if args.voir_dire else []
    if vd_events:
        sections["response_distribution_map"] = response_distribution(vd_events)
    else:
        sections["response_distribution_map"] = {}

    # Public records optional CSV as rows: juror_label,field,value
    pr_rows = []
    if args.public_records:
        with open(args.public_records, "r", encoding="utf-8", newline="") as f:
            pr_rows = [r for r in csv.DictReader(f)]

    if sjq_rows:
        sections["disclosure_consistency_flags"] = disclosure_consistency_flags(sjq_rows, pr_rows)
    else:
        sections["disclosure_consistency_flags"] = []

    # Public social summary (optional)
    if args.public_social:
        sections["public_social_summary"] = summarize_public_social(args.public_social)

    # Render report
    template_version = "1.0"
    report_md = render_markdown(case.__dict__, sections)

    # Firewall validate
    forbidden = rs.rules.get("outputs", {}).get("forbidden_terms")
    fw = OutputLanguageFirewall(forbidden)
    issues = fw.validate(report_md)
    if issues:
        raise SystemExit(f"Firewall violation: {issues}")

    out_dir = ROOT / "data" / args.case_id / "report"
    ensure_dir(str(out_dir))
    out_path = out_dir / f"report_{now_iso().replace(':','-')}.md"
    out_path.write_text(report_md, encoding="utf-8")
    print("Report written:", str(out_path))

    # Audit packet
    input_paths = [p for p in [args.transcript, args.venue, args.sjq, args.voir_dire, args.public_records, args.public_social] if p]
    packet = create_audit_packet(args.case_id, template_version, rs.sha256(), input_paths, str(out_path))
    print("Audit packet:", packet)

def build_parser():
    p = argparse.ArgumentParser(prog="maat")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("initdb")

    nc = sub.add_parser("newcase")
    nc.add_argument("--name", required=True)
    nc.add_argument("--jurisdiction", required=True)
    nc.add_argument("--judge", default=None)

    ar = sub.add_parser("addruleset")
    ar.add_argument("case_id")
    ar.add_argument("--name", required=True)
    ar.add_argument("--ruleset_path", required=True)

    ing = sub.add_parser("ingest")
    ing.add_argument("case_id")
    ing.add_argument("--type", required=True, choices=["public_social","public_records","sjq","voir_dire","venue","transcript"])
    ing.add_argument("--path", required=True)

    ls = sub.add_parser("list")
    ls.add_argument("case_id")

    rp = sub.add_parser("report")
    rp.add_argument("case_id")
    rp.add_argument("--transcript")
    rp.add_argument("--venue")
    rp.add_argument("--sjq")
    rp.add_argument("--voir_dire")
    rp.add_argument("--public_records")
    rp.add_argument("--public_social")

    return p

def main():
    p = build_parser()
    args = p.parse_args()
    if args.cmd == "initdb":
        cmd_initdb(args)
    elif args.cmd == "newcase":
        cmd_newcase(args)
    elif args.cmd == "addruleset":
        cmd_addruleset(args)
    elif args.cmd == "ingest":
        cmd_ingest(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "report":
        cmd_report(args)

if __name__ == "__main__":
    main()
