# Security & Governance (v1.0)

## Principles
- Least privilege via RBAC (not implemented in this demo beyond API keys)
- Immutable audit packets for every report run
- Separation of duties: ruleset creation vs case analysis

## Data handling
- Case artifacts are stored under `data/<case_id>/...`
- Audit packet zips contain: ruleset hash, input hashes, outputs hash, template version.

## Compliance guardrails (enforced)
- No-contact: MAAT does not implement any function that messages, connects, follows, or requests access.
- Passive-only: OSINT ingestion is treated as importing already-collected public artifacts; MAAT itself does not scrape in this demo.
- Vocabulary firewall blocks diagnostic/predictive language in outputs.
