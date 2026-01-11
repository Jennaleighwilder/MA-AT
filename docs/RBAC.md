# MAAT RBAC & Multi-Tenant Architecture

## Overview

MAAT uses Role-Based Access Control (RBAC) with multi-tenant organization isolation. Every piece of data is scoped to an organization, and users can only access data within their own organization.

## Roles

| Role | Description | Key Permissions |
|------|-------------|-----------------|
| **admin** | Full organization control | User management, billing, all case operations |
| **attorney** | Case management | Create/manage cases, generate reports, view all org cases |
| **analyst** | Analysis operations | Upload artifacts, run analyses, view assigned cases |
| **viewer** | Read-only access | View cases and reports, no modifications |

## Permission Matrix

| Permission | admin | attorney | analyst | viewer |
|------------|-------|----------|---------|--------|
| users.create | ✓ | | | |
| users.read | ✓ | | | |
| users.update | ✓ | | | |
| users.delete | ✓ | | | |
| cases.create | ✓ | ✓ | | |
| cases.read | ✓ | ✓ | ✓ | ✓ |
| cases.update | ✓ | ✓ | | |
| cases.delete | ✓ | | | |
| rulesets.create | ✓ | ✓ | | |
| rulesets.read | ✓ | ✓ | ✓ | ✓ |
| rulesets.update | ✓ | ✓ | | |
| artifacts.upload | ✓ | ✓ | ✓ | |
| artifacts.read | ✓ | ✓ | ✓ | ✓ |
| reports.generate | ✓ | ✓ | ✓ | |
| reports.read | ✓ | ✓ | ✓ | ✓ |
| audit.read | ✓ | ✓ | | |
| org.manage | ✓ | | | |
| org.billing | ✓ | | | |

## Authentication

### API Key Authentication

```bash
curl -X GET http://localhost:8000/cases \
  -H "X-API-Key: maat_your_api_key_here"
```

### Session Token Authentication (Web UI)

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'

# Response: {"token": "session_token_here", ...}

# Use token
curl -X GET http://localhost:8000/cases \
  -H "Authorization: Bearer session_token_here"
```

## Quick Start

### 1. Create an Organization

```bash
curl -X POST http://localhost:8000/orgs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Law Firm",
    "admin_email": "admin@demolaw.com",
    "admin_password": "securepassword123",
    "subscription_tier": "professional"
  }'
```

Response includes:
- `org_id`: Your organization ID
- `api_key`: Your initial API key (save this!)

### 2. Create Additional Users

```bash
curl -X POST http://localhost:8000/users \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@demolaw.com",
    "password": "analystpass",
    "role": "analyst",
    "name": "Jane Analyst"
  }'
```

### 3. Create a Case

```bash
curl -X POST http://localhost:8000/cases \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smith v. Jones",
    "jurisdiction": "NC",
    "judge": "Hon. Williams"
  }'
```

### 4. Upload Artifacts

```bash
curl -X POST "http://localhost:8000/cases/{case_id}/artifacts?artifact_type=transcript" \
  -H "X-API-Key: your_api_key" \
  -F "f=@transcript.txt"
```

### 5. Generate Report

```bash
curl -X POST http://localhost:8000/cases/{case_id}/report \
  -H "X-API-Key: your_api_key"
```

## Audit Logging

All actions are logged to an immutable audit trail:

```bash
curl -X GET "http://localhost:8000/audit?limit=50" \
  -H "X-API-Key: your_api_key"
```

Each log entry includes:
- Timestamp
- User ID
- Action performed
- Resource type and ID
- IP address

## Security Features

1. **Password Hashing**: PBKDF2-SHA256 with random salt
2. **API Key Hashing**: SHA-256 (keys cannot be retrieved)
3. **Session Expiry**: 24-hour default, configurable
4. **Organization Isolation**: Users cannot access other orgs' data
5. **Audit Trail**: Immutable log of all actions

## API Key Management

### Create New API Key

```bash
curl -X POST http://localhost:8000/api-keys \
  -H "X-API-Key: your_admin_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Key",
    "expires_days": 365
  }'
```

**Important**: The raw API key is only shown once. Store it securely.

## Subscription Tiers

| Tier | Features |
|------|----------|
| liberation | Free tier, limited cases |
| professional | Full features, standard support |
| enterprise | Custom limits, SSO, dedicated support |
