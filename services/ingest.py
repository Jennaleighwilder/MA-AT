from __future__ import annotations
import uuid, os, shutil
from pathlib import Path
from typing import Literal
from .db import connect
from .utils import now_iso, sha256_file, ensure_dir

ArtifactType = Literal["public_social","public_records","sjq","voir_dire","venue","transcript","report","audit"]

def case_dir(case_id: str) -> str:
    return str(Path(__file__).resolve().parent.parent / "data" / case_id)

def ingest_artifact(case_id: str, artifact_type: ArtifactType, src_path: str) -> str:
    aid = str(uuid.uuid4())
    dst_dir = Path(case_dir(case_id)) / artifact_type
    ensure_dir(str(dst_dir))
    src = Path(src_path)
    dst = dst_dir / f"{aid}{src.suffix if src.suffix else ''}"
    shutil.copy2(src, dst)
    sha = sha256_file(str(dst))
    conn = connect()
    conn.execute(
        "INSERT INTO artifacts(artifact_id,case_id,artifact_type,path,sha256,created_at) VALUES(?,?,?,?,?,?)",
        (aid, case_id, artifact_type, str(dst), sha, now_iso())
    )
    conn.commit()
    conn.close()
    return aid

def list_artifacts(case_id: str):
    conn = connect()
    rows = conn.execute(
        "SELECT artifact_id,artifact_type,path,sha256,created_at FROM artifacts WHERE case_id=? ORDER BY created_at",
        (case_id,)
    ).fetchall()
    conn.close()
    return rows
