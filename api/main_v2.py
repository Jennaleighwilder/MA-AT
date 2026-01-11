"""
MAAT API v2 - Multi-Tenant RBAC-Protected Endpoints
====================================================

All endpoints require authentication via:
  - X-API-Key header (for API clients)
  - Authorization: Bearer <session_token> (for web UI)

All data is org-scoped. Users can only access their organization's cases.
"""
from __future__ import annotations
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import json

from services.db import init_db_if_needed
from services.rbac import (
    init_rbac_schema, validate_api_key, validate_session,
    create_org, get_org, create_user, authenticate_user, list_org_users,
    create_api_key, create_session, destroy_session,
    link_case_to_org, user_can_access_case, list_org_cases, get_case_org,
    log_action, get_audit_log,
    User, Organization, PERMISSIONS
)
from services.case import create_case as _create_case, get_case
from services.ruleset_store import add_ruleset_yaml, latest_ruleset
from services.ingest import ingest_artifact
from services.orchestrate import generate_report_and_audit

app = FastAPI(title="MAAT API", version="2.0", description="Multi-Tenant Jury Analysis Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    init_db_if_needed()
    init_rbac_schema()


# =============================================================================
# Serve Web UI
# =============================================================================

UI_DIR = Path(__file__).parent.parent / "ui"

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the main console UI."""
    console_path = UI_DIR / "console.html"
    if console_path.exists():
        return HTMLResponse(content=console_path.read_text(), status_code=200)
    return HTMLResponse(content="<h1>MAAT API</h1><p>UI not found. API is running.</p>", status_code=200)


# =============================================================================
# Authentication Dependency
# =============================================================================

async def get_current_user(
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None)
) -> User:
    """
    Authenticate via API key or session token.
    Returns the authenticated User or raises 401.
    """
    # Try API key first
    if x_api_key:
        result = validate_api_key(x_api_key)
        if result:
            org_id, key_id, user_id = result
            if user_id:
                from services.rbac import get_user
                user = get_user(user_id)
                if user:
                    return user
            # Org-wide key: return synthetic admin user
            return User(id="api_key", org_id=org_id, email="api@key", role="admin")
    
    # Try session token
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        user = validate_session(token)
        if user:
            return user
    
    raise HTTPException(status_code=401, detail="Invalid or missing authentication")


def require_permission(permission: str):
    """Dependency that checks for a specific permission."""
    async def checker(user: User = Depends(get_current_user)):
        if not user.can(permission):
            raise HTTPException(status_code=403, detail=f"Permission denied: {permission}")
        return user
    return checker


# =============================================================================
# Auth Endpoints
# =============================================================================

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user_id: str
    org_id: str
    role: str
    email: str

@app.post("/auth/login", response_model=LoginResponse)
async def login(payload: LoginRequest, request: Request):
    """Authenticate and get a session token."""
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_session(
        user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    log_action(user.org_id, "login", user.id, ip_address=request.client.host if request.client else None)
    
    return LoginResponse(
        token=token,
        user_id=user.id,
        org_id=user.org_id,
        role=user.role,
        email=user.email
    )

@app.post("/auth/logout")
async def logout(authorization: str = Header()):
    """Logout and destroy session."""
    if authorization.startswith("Bearer "):
        destroy_session(authorization[7:])
    return {"status": "logged_out"}

@app.get("/auth/me")
async def get_me(user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return {
        "id": user.id,
        "org_id": user.org_id,
        "email": user.email,
        "role": user.role,
        "name": user.name,
        "permissions": list(PERMISSIONS.get(user.role, set()))
    }


# =============================================================================
# Organization Endpoints
# =============================================================================

class OrgCreate(BaseModel):
    name: str
    admin_email: str
    admin_password: str
    subscription_tier: str = "professional"

@app.post("/orgs")
async def api_create_org(payload: OrgCreate):
    """Create a new organization with an admin user. (Bootstrap endpoint)"""
    org = create_org(payload.name, payload.subscription_tier)
    admin = create_user(org.id, payload.admin_email, payload.admin_password, "admin", name="Admin")
    key_id, raw_key = create_api_key(org.id, admin.id, name="Initial API Key")
    
    return {
        "org_id": org.id,
        "org_name": org.name,
        "admin_user_id": admin.id,
        "admin_email": admin.email,
        "api_key": raw_key,  # Only shown once!
        "api_key_id": key_id
    }

@app.get("/orgs/current")
async def get_current_org(user: User = Depends(get_current_user)):
    """Get current user's organization."""
    org = get_org(user.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {
        "id": org.id,
        "name": org.name,
        "subscription_tier": org.subscription_tier
    }


# =============================================================================
# User Management Endpoints
# =============================================================================

class UserCreate(BaseModel):
    email: str
    password: str
    role: str
    name: Optional[str] = None

@app.post("/users", dependencies=[Depends(require_permission("users.create"))])
async def api_create_user(payload: UserCreate, user: User = Depends(get_current_user)):
    """Create a new user in the organization."""
    if payload.role not in PERMISSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid role: {payload.role}")
    
    new_user = create_user(user.org_id, payload.email, payload.password, payload.role, payload.name)
    log_action(user.org_id, "user_created", user.id, "user", new_user.id)
    
    return {
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
        "name": new_user.name
    }

@app.get("/users", dependencies=[Depends(require_permission("users.read"))])
async def api_list_users(user: User = Depends(get_current_user)):
    """List all users in the organization."""
    users = list_org_users(user.org_id)
    return [{"id": u.id, "email": u.email, "role": u.role, "name": u.name} for u in users]


# =============================================================================
# API Key Management
# =============================================================================

class ApiKeyCreate(BaseModel):
    name: Optional[str] = None
    expires_days: int = 365

@app.post("/api-keys", dependencies=[Depends(require_permission("org.manage"))])
async def api_create_api_key(payload: ApiKeyCreate, user: User = Depends(get_current_user)):
    """Create a new API key for the organization."""
    key_id, raw_key = create_api_key(user.org_id, user.id, payload.name, payload.expires_days)
    log_action(user.org_id, "api_key_created", user.id, "api_key", key_id)
    
    return {
        "key_id": key_id,
        "api_key": raw_key,  # Only shown once!
        "name": payload.name,
        "expires_days": payload.expires_days,
        "warning": "Store this key securely - it cannot be retrieved again"
    }


# =============================================================================
# Case Endpoints (Org-Scoped)
# =============================================================================

class CaseCreate(BaseModel):
    name: str
    jurisdiction: str
    judge: Optional[str] = None

@app.post("/cases", dependencies=[Depends(require_permission("cases.create"))])
async def api_create_case(payload: CaseCreate, user: User = Depends(get_current_user)):
    """Create a new case in the organization."""
    case_data = _create_case(payload.name, payload.jurisdiction, payload.judge)
    case_id = case_data["case_id"]
    
    # Link case to org
    link_case_to_org(case_id, user.org_id, user.id)
    log_action(user.org_id, "case_created", user.id, "case", case_id)
    
    return case_data

@app.get("/cases", dependencies=[Depends(require_permission("cases.read"))])
async def api_list_cases(user: User = Depends(get_current_user)):
    """List all cases in the organization."""
    case_ids = list_org_cases(user.org_id)
    cases = []
    for cid in case_ids:
        c = get_case(cid)
        if c:
            cases.append(c)
    return cases

@app.get("/cases/{case_id}", dependencies=[Depends(require_permission("cases.read"))])
async def api_get_case(case_id: str, user: User = Depends(get_current_user)):
    """Get a specific case."""
    if not user_can_access_case(user, case_id):
        raise HTTPException(status_code=403, detail="Access denied to this case")
    
    c = get_case(case_id)
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return c


# =============================================================================
# Ruleset Endpoints
# =============================================================================

class RulesetCreate(BaseModel):
    name: str
    rules_yaml: str

@app.post("/cases/{case_id}/rulesets", dependencies=[Depends(require_permission("rulesets.create"))])
async def api_add_ruleset(case_id: str, payload: RulesetCreate, user: User = Depends(get_current_user)):
    """Add a ruleset to a case."""
    if not user_can_access_case(user, case_id):
        raise HTTPException(status_code=403, detail="Access denied to this case")
    
    result = add_ruleset_yaml(case_id, payload.name, payload.rules_yaml)
    log_action(user.org_id, "ruleset_added", user.id, "case", case_id, json.dumps({"name": payload.name}))
    return result

@app.get("/cases/{case_id}/rulesets/active", dependencies=[Depends(require_permission("rulesets.read"))])
async def api_get_active_ruleset(case_id: str, user: User = Depends(get_current_user)):
    """Get the active ruleset for a case."""
    if not user_can_access_case(user, case_id):
        raise HTTPException(status_code=403, detail="Access denied to this case")
    
    rs = latest_ruleset(case_id)
    if not rs:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return {"name": rs.name, "version": rs.version, "sha256": rs.sha256(), "rules": rs.rules}


# =============================================================================
# Artifact Endpoints
# =============================================================================

ARTIFACT_TYPES = {"transcript", "venue", "sjq", "voir_dire", "public_records", "public_social"}

@app.post("/cases/{case_id}/artifacts", dependencies=[Depends(require_permission("artifacts.upload"))])
async def api_upload_artifact(
    case_id: str,
    artifact_type: str,
    f: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    """Upload an artifact to a case."""
    if not user_can_access_case(user, case_id):
        raise HTTPException(status_code=403, detail="Access denied to this case")
    
    if artifact_type not in ARTIFACT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid artifact type. Must be one of: {ARTIFACT_TYPES}")
    
    path = ingest_artifact(case_id, artifact_type, await f.read(), filename=f.filename)
    log_action(user.org_id, "artifact_uploaded", user.id, "case", case_id, 
               json.dumps({"type": artifact_type, "filename": f.filename}))
    
    return {"stored_path": path, "artifact_type": artifact_type}


# =============================================================================
# Report Endpoints
# =============================================================================

@app.post("/cases/{case_id}/report", dependencies=[Depends(require_permission("reports.generate"))])
async def api_generate_report(case_id: str, user: User = Depends(get_current_user)):
    """Generate a report and audit packet for a case."""
    if not user_can_access_case(user, case_id):
        raise HTTPException(status_code=403, detail="Access denied to this case")
    
    try:
        result = generate_report_and_audit(case_id)
        log_action(user.org_id, "report_generated", user.id, "case", case_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/cases/{case_id}/report/latest", dependencies=[Depends(require_permission("reports.read"))])
async def api_get_latest_report(case_id: str, user: User = Depends(get_current_user)):
    """Download the latest report for a case."""
    if not user_can_access_case(user, case_id):
        raise HTTPException(status_code=403, detail="Access denied to this case")
    
    report_path = os.path.join("data", case_id, "report", "latest_report.md")
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(report_path, media_type="text/markdown", filename=f"MAAT_Report_{case_id}.md")

@app.get("/cases/{case_id}/audit/latest", dependencies=[Depends(require_permission("reports.read"))])
async def api_get_latest_audit(case_id: str, user: User = Depends(get_current_user)):
    """Download the latest audit packet for a case."""
    if not user_can_access_case(user, case_id):
        raise HTTPException(status_code=403, detail="Access denied to this case")
    
    audit_path = os.path.join("data", case_id, "audit", "latest_audit.zip")
    if not os.path.exists(audit_path):
        raise HTTPException(status_code=404, detail="Audit packet not found")
    return FileResponse(audit_path, media_type="application/zip", filename=f"MAAT_Audit_{case_id}.zip")


# =============================================================================
# Audit Log Endpoints
# =============================================================================

@app.get("/audit", dependencies=[Depends(require_permission("audit.read"))])
async def api_get_audit_log(
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user)
):
    """Get the audit log for the organization."""
    logs = get_audit_log(user.org_id, limit, offset)
    return {"logs": logs, "limit": limit, "offset": offset}


# =============================================================================
# Health Check
# =============================================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0", "features": ["rbac", "multi-tenant", "audit-log"]}
