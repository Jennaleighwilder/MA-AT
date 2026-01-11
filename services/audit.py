from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
import json, zipfile, uuid
from .utils import sha256_file, sha256_json, stable_inputs_hash, now_iso, ensure_dir, sha256_bytes
from .db import connect

def create_audit_packet(case_id: str, template_version: str, ruleset_sha: str, input_artifact_paths: List[str], report_path: str) -> str:
    """
    Generates a zip audit packet with:
      - ruleset sha
      - inputs sha (combined)
      - outputs sha
      - manifest.json
      - hashes.json
      - report copy
    Stores a DB entry in audit_packets.
    """
    audit_id = str(uuid.uuid4())
    out_dir = Path(__file__).resolve().parent.parent / "data" / case_id / "audit"
    ensure_dir(str(out_dir))
    packet_path = out_dir / f"audit_{audit_id}.zip"

    input_hashes = [sha256_file(p) for p in input_artifact_paths]
    inputs_sha = stable_inputs_hash(input_hashes)
    outputs_sha = sha256_file(report_path)

    manifest = {
        "audit_id": audit_id,
        "case_id": case_id,
        "template_version": template_version,
        "ruleset_sha256": ruleset_sha,
        "inputs_sha256": inputs_sha,
        "outputs_sha256": outputs_sha,
        "created_at": now_iso(),
        "inputs": [{"path": p, "sha256": sha256_file(p)} for p in input_artifact_paths],
        "report": {"path": report_path, "sha256": outputs_sha},
    }

    with zipfile.ZipFile(packet_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        z.write(report_path, arcname="report.md")
        for p in input_artifact_paths:
            z.write(p, arcname=f"inputs/{Path(p).name}")

    conn = connect()
    conn.execute(
        "INSERT INTO audit_packets(audit_id,case_id,ruleset_sha256,inputs_sha256,outputs_sha256,template_version,packet_path,created_at) VALUES(?,?,?,?,?,?,?,?)",
        (audit_id, case_id, ruleset_sha, inputs_sha, outputs_sha, template_version, str(packet_path), now_iso())
    )
    conn.commit()
    conn.close()
    return str(packet_path)
