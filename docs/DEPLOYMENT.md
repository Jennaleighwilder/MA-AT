# Deployment (v1.0)

## Local (Docker)
1. `docker compose up --build`
2. API at `http://localhost:8000`
3. Use header `X-API-Key: demo-key`

## Production notes
- Replace API key auth with OIDC/SAML SSO (Okta/AzureAD).
- Use Postgres for multi-tenant scale; keep audit log immutable (WORM storage).
- Add object storage (S3/GCS) for artifacts + audit packets.
- Configure per-case ruleset ingestion and judge standing order upload.

MAAT is designed to be procurement-friendly: audit packets are first-class outputs.
