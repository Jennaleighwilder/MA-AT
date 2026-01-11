MA'AT - Jury Analysis Platform
Truth weighs the heart.
The first court-defensible jury analysis platform. Process forensics, not psychology. Document conditions, not predict verdicts.

Quick Start
bashdocker compose up --build

Console UI: http://localhost:8000
API Docs: http://localhost:8000/docs

First-Time Setup
bash# Create organization + admin user
curl -X POST http://localhost:8000/orgs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Law Firm",
    "admin_email": "admin@yourfirm.com",
    "admin_password": "securepassword",
    "subscription_tier": "professional"
  }'
```

Save the `api_key` from the response - it's only shown once.

---

## What MA'AT Does

| Feature | Description |
|---------|-------------|
| **Statement Consistency** | Analyzes transcripts for internal coherence, contradictions, evidence gaps |
| **Audit Packets** | SHA-256 hash-verified, timestamped, immutable documentation |
| **Language Firewall** | Blocks diagnostic/predictive language before it reaches reports |
| **RBAC** | Multi-tenant org isolation with admin/attorney/analyst/viewer roles |
| **Judge Overrides** | Standing orders compile into enforcement rules |

## What MA'AT Does NOT Do

- ❌ Contact jurors (hard-coded prohibition)
- ❌ Predict verdicts
- ❌ Psychological profiling
- ❌ Archetype labeling
- ❌ "Read" jurors

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orgs` | Create organization |
| POST | `/auth/login` | Get session token |
| GET | `/auth/me` | Current user info |
| POST | `/cases` | Create case |
| GET | `/cases` | List org cases |
| POST | `/cases/{id}/artifacts` | Upload artifact |
| POST | `/cases/{id}/report` | Generate report + audit |
| GET | `/cases/{id}/report/latest` | Download report |
| GET | `/cases/{id}/audit/latest` | Download audit packet |
| GET | `/audit` | View audit log |

---

## Project Structure
```
├── api/
│   ├── main_v2.py          # RBAC-protected API
│   └── requirements.txt
├── services/
│   ├── rbac.py             # Role-based access control
│   ├── orchestrate.py      # Report generation pipeline
│   ├── rules_engine.py     # Language firewall
│   └── analyzers/
│       └── truth_engine_adapter.py  # Court-safe output
├── schema/
│   ├── maat.sql            # Core schema
│   └── rbac.sql            # Multi-tenant schema
├── ui/
│   ├── landing.html        # Marketing page
│   └── console.html        # Admin console
├── vendor/
│   └── truth_engine/       # Statement analysis engine
├── Dockerfile
└── docker-compose.yml

Roles & Permissions
RoleCreate CasesUploadGenerate ReportsManage Usersadmin✓✓✓✓attorney✓✓✓✗analyst✗✓✓✗viewer✗✗✗✗

Contact
The Forgotten Code Research Institute

Email: TheForgottenCode@gmail.com
Phone: 423-388-8304


License
© 2026 Jennifer Leigh West / The Forgotten Code Research Institute
Mirror Protocol™ - U.S. Copyright Registration No. 1-14949237971
