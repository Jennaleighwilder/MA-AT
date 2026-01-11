# MAAT™ — Mechanism Analysis & Adjudicative Transparency
**Enterprise Jury Awareness + Process Forensics Platform (war-horse spec + scaffold)**  
Generated: 2026-01-11T20:53:40

## What this repo is
A build scaffold for MAAT: a court-safe, auditable system that consolidates **legally permissible** juror-awareness inputs
and produces **process-forensic** outputs (no juror psych profiling, no verdict prediction).

## Quick start
1) Read `/docs/MAAT_SPEC.md` (the full system spec)
2) Configure a jurisdiction ruleset in `/config/rulesets/`
3) Run `python -m services.cli demo` to generate a sample report from sample data

## Non-negotiables
- **No contact** with jurors/prospective jurors (no access requests, no messages, no follows)
- **Passive-only** review of public info; jurisdiction rules may further restrict platforms that generate notifications.
- Outputs are vocabulary-firewalled for court survivability.

## Repo layout
- `services/` core engine + adapters
- `schema/` SQLite schema for audit + case workspaces
- `docs/` spec, compliance matrix, output templates
- `ui/` minimal HTML mock for enterprise UX

> Note: Any real-world deployment must be reviewed by licensed counsel in the relevant jurisdiction.


## Full build commands
See `samples/README.md` for an end-to-end run.


## API + Docker
- `docker compose up --build`
- Call API using header `X-API-Key: demo-key`
- See `/docs/API.md` and `/docs/DEPLOYMENT.md`
