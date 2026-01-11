-- MAAT RBAC Schema - Multi-Tenant Organization Isolation
-- Roles: admin, attorney, analyst, viewer

-- Organizations (tenants)
CREATE TABLE IF NOT EXISTS organizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    subscription_tier TEXT DEFAULT 'professional',  -- 'liberation', 'professional', 'enterprise'
    active INTEGER DEFAULT 1
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'attorney', 'analyst', 'viewer')),
    name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    active INTEGER DEFAULT 1
);

-- API Keys (per-user or per-org)
CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    user_id TEXT REFERENCES users(id),  -- NULL = org-wide key
    key_hash TEXT NOT NULL UNIQUE,
    name TEXT,
    permissions TEXT DEFAULT '{}',  -- JSON permissions override
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    last_used DATETIME,
    active INTEGER DEFAULT 1
);

-- Sessions (for web UI)
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id),
    token_hash TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    ip_address TEXT,
    user_agent TEXT
);

-- Audit log (who did what)
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    user_id TEXT REFERENCES users(id),
    action TEXT NOT NULL,
    resource_type TEXT,  -- 'case', 'ruleset', 'report', etc.
    resource_id TEXT,
    details TEXT,  -- JSON
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Link cases to organizations
CREATE TABLE IF NOT EXISTS case_org_map (
    case_id TEXT NOT NULL,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    created_by TEXT REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (case_id, org_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_org ON users(org_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_api_keys_org ON api_keys(org_id);
CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_log(org_id);
CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_case_org ON case_org_map(org_id);
