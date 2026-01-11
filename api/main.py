from __future__ import annotations
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from services.db import init_db_if_needed
from services.case import create_case, get_case
from services.ruleset_store import add_ruleset_yaml, latest_ruleset
from services.ingest import ingest_artifact
from services.orchestrate import generate_report_and_audit

API_KEYS = set(k.strip() for k in os.environ.get("MAAT_API_KEYS", "demo-key").split(",") if k.strip())

def api_key_guard(x_api_key: str = Header(default="")):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")
    return x_api_key

app = FastAPI(title="MAAT API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    init_db_if_needed()

class CaseCreate(BaseModel):
    name: str
    jurisdiction: str
    judge: Optional[str] = None

class RulesetCreate(BaseModel):
    name: str
    rules_yaml: str

@app.post("/cases", dependencies=[Depends(api_key_guard)])
def api_create_case(payload: CaseCreate):
    return create_case(payload.name, payload.jurisdiction, payload.judge)

@app.get("/cases/{case_id}", dependencies=[Depends(api_key_guard)])
def api_get_case(case_id: str):
    c = get_case(case_id)
    if not c:
        raise HTTPException(404, "case_not_found")
    return c

@app.post("/cases/{case_id}/rulesets", dependencies=[Depends(api_key_guard)])
def api_add_ruleset(case_id: str, payload: RulesetCreate):
    return add_ruleset_yaml(case_id, payload.name, payload.rules_yaml)

@app.get("/cases/{case_id}/rulesets/active", dependencies=[Depends(api_key_guard)])
def api_get_active_ruleset(case_id: str):
    rs = latest_ruleset(case_id)
    if not rs:
        raise HTTPException(404, "ruleset_not_found")
    return {"name": rs.name, "version": rs.version, "sha256": rs.sha256(), "rules": rs.rules}

@app.post("/cases/{case_id}/artifacts", dependencies=[Depends(api_key_guard)])
async def api_upload_artifact(case_id: str, artifact_type: str, f: UploadFile = File(...)):
    if artifact_type not in {"transcript","venue","sjq","voir_dire","public_records","public_social"}:
        raise HTTPException(400, "unsupported_artifact_type")
    path = ingest_artifact(case_id, artifact_type, await f.read(), filename=f.filename)
    return {"stored_path": path}

@app.post("/cases/{case_id}/report", dependencies=[Depends(api_key_guard)])
def api_generate_report(case_id: str):
    try:
        return generate_report_and_audit(case_id)
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/cases/{case_id}/report/latest", dependencies=[Depends(api_key_guard)])
def api_get_latest_report(case_id: str):
    report_path = os.path.join("data", case_id, "report", "latest_report.md")
    if not os.path.exists(report_path):
        raise HTTPException(404, "report_not_found")
    return FileResponse(report_path, media_type="text/markdown", filename=f"MAAT_Report_{case_id}.md")

@app.get("/cases/{case_id}/audit/latest", dependencies=[Depends(api_key_guard)])
def api_get_latest_audit(case_id: str):
    audit_path = os.path.join("data", case_id, "audit", "latest_audit.zip")
    if not os.path.exists(audit_path):
        raise HTTPException(404, "audit_not_found")
    return FileResponse(audit_path, media_type="application/zip", filename=f"MAAT_Audit_{case_id}.zip")
