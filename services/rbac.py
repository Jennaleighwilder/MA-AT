"""
MAAT RBAC Service - Role-Based Access Control + Multi-Tenant Isolation
======================================================================

Roles:
    admin    - Full org access, user management, billing
    attorney - Create/manage cases, generate reports, view all org cases
    analyst  - Upload artifacts, run analyses, view assigned cases
    viewer   - Read-only access to assigned cases

All operations are org-scoped. Users cannot see other orgs' data.
"""
from __future__ import annotations
import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from functools import wraps

DB_PATH = os.environ.get("MAAT_DB_PATH", "data/maat.db")

# Role permission matrix
PERMISSIONS = {
    "admin": {
        "users.create", "users.read", "users.update", "users.delete",
        "cases.create", "cases.read", "cases.update", "cases.delete",
        "rulesets.create", "rulesets.read", "rulesets.update",
        "artifacts.upload", "artifacts.read",
        "reports.generate", "reports.read",
        "audit.read",
        "org.manage", "org.billing",
    },
    "attorney": {
        "cases.create", "cases.read", "cases.update",
        "rulesets.create", "rulesets.read", "rulesets.update",
        "artifacts.upload", "artifacts.read",
        "reports.generate", "reports.read",
        "audit.read",
    },
    "analyst": {
        "cases.read",
        "rulesets.read",
        "artifacts.upload", "artifacts.read",
        "reports.generate", "reports.read",
    },
    "viewer": {
        "cases.read",
        "rulesets.read",
        "artifacts.read",
        "reports.read",
    },
}


@dataclass
class User:
    id: str
    org_id: str
    email: str
    role: str
    name: Optional[str] = None
    active: bool = True

    def has_permission(self, permission: str) -> bool:
        return permission in PERMISSIONS.get(self.role, set())

    def can(self, permission: str) -> bool:
        return self.has_permission(permission)


@dataclass
class Organization:
    id: str
    name: str
    subscription_tier: str = "professional"
    active: bool = True


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hash password with salt. Returns (hash, salt)."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash (format: salt:hash)."""
    try:
        salt, hash_val = stored_hash.split(":", 1)
        computed, _ = _hash_password(password, salt)
        return secrets.compare_digest(computed, hash_val)
    except:
        return False


def _hash_token(token: str) -> str:
    """Hash API key or session token."""
    return hashlib.sha256(token.encode()).hexdigest()


def init_rbac_schema():
    """Initialize RBAC tables."""
    conn = _get_conn()
    schema_path = os.path.join(os.path.dirname(__file__), "..", "schema", "rbac.sql")
    if os.path.exists(schema_path):
        with open(schema_path) as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()


# =============================================================================
# Organization Management
# =============================================================================

def create_org(name: str, subscription_tier: str = "professional") -> Organization:
    """Create a new organization."""
    org_id = secrets.token_urlsafe(12)
    conn = _get_conn()
    conn.execute(
        "INSERT INTO organizations (id, name, subscription_tier) VALUES (?, ?, ?)",
        (org_id, name, subscription_tier)
    )
    conn.commit()
    conn.close()
    return Organization(id=org_id, name=name, subscription_tier=subscription_tier)


def get_org(org_id: str) -> Optional[Organization]:
    """Get organization by ID."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM organizations WHERE id = ? AND active = 1", (org_id,)).fetchone()
    conn.close()
    if row:
        return Organization(
            id=row["id"],
            name=row["name"],
            subscription_tier=row["subscription_tier"],
            active=bool(row["active"])
        )
    return None


# =============================================================================
# User Management
# =============================================================================

def create_user(org_id: str, email: str, password: str, role: str, name: Optional[str] = None) -> User:
    """Create a new user in an organization."""
    if role not in PERMISSIONS:
        raise ValueError(f"Invalid role: {role}")
    
    user_id = secrets.token_urlsafe(12)
    hash_val, salt = _hash_password(password)
    password_hash = f"{salt}:{hash_val}"
    
    conn = _get_conn()
    conn.execute(
        "INSERT INTO users (id, org_id, email, password_hash, role, name) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, org_id, email, password_hash, role, name)
    )
    conn.commit()
    conn.close()
    
    return User(id=user_id, org_id=org_id, email=email, role=role, name=name)


def get_user(user_id: str) -> Optional[User]:
    """Get user by ID."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ? AND active = 1", (user_id,)).fetchone()
    conn.close()
    if row:
        return User(
            id=row["id"],
            org_id=row["org_id"],
            email=row["email"],
            role=row["role"],
            name=row["name"],
            active=bool(row["active"])
        )
    return None


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ? AND active = 1", (email,)).fetchone()
    conn.close()
    if row:
        return User(
            id=row["id"],
            org_id=row["org_id"],
            email=row["email"],
            role=row["role"],
            name=row["name"],
            active=bool(row["active"])
        )
    return None


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user by email/password. Returns User if valid, None otherwise."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ? AND active = 1", (email,)).fetchone()
    if not row:
        conn.close()
        return None
    
    if _verify_password(password, row["password_hash"]):
        # Update last login
        conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.utcnow(), row["id"]))
        conn.commit()
        conn.close()
        return User(
            id=row["id"],
            org_id=row["org_id"],
            email=row["email"],
            role=row["role"],
            name=row["name"],
            active=True
        )
    
    conn.close()
    return None


def list_org_users(org_id: str) -> List[User]:
    """List all users in an organization."""
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM users WHERE org_id = ? AND active = 1", (org_id,)).fetchall()
    conn.close()
    return [
        User(id=r["id"], org_id=r["org_id"], email=r["email"], role=r["role"], name=r["name"])
        for r in rows
    ]


def update_user_role(user_id: str, new_role: str, by_user: User) -> bool:
    """Update user's role. Requires admin permission."""
    if not by_user.can("users.update"):
        return False
    if new_role not in PERMISSIONS:
        return False
    
    conn = _get_conn()
    conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()
    return True


def deactivate_user(user_id: str, by_user: User) -> bool:
    """Deactivate a user. Requires admin permission."""
    if not by_user.can("users.delete"):
        return False
    
    conn = _get_conn()
    conn.execute("UPDATE users SET active = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True


# =============================================================================
# API Key Management
# =============================================================================

def create_api_key(org_id: str, user_id: Optional[str] = None, name: Optional[str] = None, 
                   expires_days: int = 365) -> Tuple[str, str]:
    """
    Create an API key. Returns (key_id, raw_key).
    The raw_key is only shown once - store it securely.
    """
    key_id = secrets.token_urlsafe(8)
    raw_key = f"maat_{secrets.token_urlsafe(32)}"
    key_hash = _hash_token(raw_key)
    expires_at = datetime.utcnow() + timedelta(days=expires_days)
    
    conn = _get_conn()
    conn.execute(
        "INSERT INTO api_keys (id, org_id, user_id, key_hash, name, expires_at) VALUES (?, ?, ?, ?, ?, ?)",
        (key_id, org_id, user_id, key_hash, name, expires_at)
    )
    conn.commit()
    conn.close()
    
    return key_id, raw_key


def validate_api_key(raw_key: str) -> Optional[Tuple[str, str, Optional[str]]]:
    """
    Validate an API key. Returns (org_id, key_id, user_id) if valid, None otherwise.
    """
    key_hash = _hash_token(raw_key)
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM api_keys WHERE key_hash = ? AND active = 1 AND (expires_at IS NULL OR expires_at > ?)",
        (key_hash, datetime.utcnow())
    ).fetchone()
    
    if row:
        # Update last used
        conn.execute("UPDATE api_keys SET last_used = ? WHERE id = ?", (datetime.utcnow(), row["id"]))
        conn.commit()
        conn.close()
        return row["org_id"], row["id"], row["user_id"]
    
    conn.close()
    return None


def revoke_api_key(key_id: str, by_user: User) -> bool:
    """Revoke an API key."""
    if not by_user.can("org.manage"):
        return False
    
    conn = _get_conn()
    conn.execute("UPDATE api_keys SET active = 0 WHERE id = ?", (key_id,))
    conn.commit()
    conn.close()
    return True


# =============================================================================
# Session Management (for web UI)
# =============================================================================

def create_session(user_id: str, ip_address: Optional[str] = None, 
                   user_agent: Optional[str] = None, expires_hours: int = 24) -> str:
    """Create a session token for web UI. Returns the raw token."""
    session_id = secrets.token_urlsafe(8)
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)
    expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
    
    conn = _get_conn()
    conn.execute(
        "INSERT INTO sessions (id, user_id, token_hash, expires_at, ip_address, user_agent) VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, user_id, token_hash, expires_at, ip_address, user_agent)
    )
    conn.commit()
    conn.close()
    
    return raw_token


def validate_session(raw_token: str) -> Optional[User]:
    """Validate a session token. Returns User if valid, None otherwise."""
    token_hash = _hash_token(raw_token)
    conn = _get_conn()
    row = conn.execute(
        """SELECT s.*, u.* FROM sessions s 
           JOIN users u ON s.user_id = u.id 
           WHERE s.token_hash = ? AND s.expires_at > ? AND u.active = 1""",
        (token_hash, datetime.utcnow())
    ).fetchone()
    conn.close()
    
    if row:
        return User(
            id=row["user_id"],
            org_id=row["org_id"],
            email=row["email"],
            role=row["role"],
            name=row["name"]
        )
    return None


def destroy_session(raw_token: str):
    """Destroy a session (logout)."""
    token_hash = _hash_token(raw_token)
    conn = _get_conn()
    conn.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
    conn.commit()
    conn.close()


# =============================================================================
# Case Access Control
# =============================================================================

def link_case_to_org(case_id: str, org_id: str, created_by: Optional[str] = None):
    """Link a case to an organization."""
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO case_org_map (case_id, org_id, created_by) VALUES (?, ?, ?)",
        (case_id, org_id, created_by)
    )
    conn.commit()
    conn.close()


def get_case_org(case_id: str) -> Optional[str]:
    """Get the org_id that owns a case."""
    conn = _get_conn()
    row = conn.execute("SELECT org_id FROM case_org_map WHERE case_id = ?", (case_id,)).fetchone()
    conn.close()
    return row["org_id"] if row else None


def user_can_access_case(user: User, case_id: str) -> bool:
    """Check if user can access a specific case."""
    case_org = get_case_org(case_id)
    return case_org == user.org_id


def list_org_cases(org_id: str) -> List[str]:
    """List all case IDs belonging to an organization."""
    conn = _get_conn()
    rows = conn.execute("SELECT case_id FROM case_org_map WHERE org_id = ?", (org_id,)).fetchall()
    conn.close()
    return [r["case_id"] for r in rows]


# =============================================================================
# Audit Logging
# =============================================================================

def log_action(org_id: str, action: str, user_id: Optional[str] = None,
               resource_type: Optional[str] = None, resource_id: Optional[str] = None,
               details: Optional[str] = None, ip_address: Optional[str] = None):
    """Log an action to the audit trail."""
    conn = _get_conn()
    conn.execute(
        """INSERT INTO audit_log (org_id, user_id, action, resource_type, resource_id, details, ip_address)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (org_id, user_id, action, resource_type, resource_id, details, ip_address)
    )
    conn.commit()
    conn.close()


def get_audit_log(org_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
    """Get audit log for an organization."""
    conn = _get_conn()
    rows = conn.execute(
        """SELECT * FROM audit_log WHERE org_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?""",
        (org_id, limit, offset)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =============================================================================
# Permission Decorator for API endpoints
# =============================================================================

def require_permission(permission: str):
    """Decorator to require a specific permission."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, user: User = None, **kwargs):
            if user is None:
                raise PermissionError("Authentication required")
            if not user.can(permission):
                raise PermissionError(f"Permission denied: {permission}")
            return func(*args, user=user, **kwargs)
        return wrapper
    return decorator
