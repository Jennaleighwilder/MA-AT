# MAAT API (v1.0)

Authentication: send header `X-API-Key: <key>`.

## Endpoints
- `POST /cases` → create case
- `GET /cases/{case_id}` → fetch case
- `POST /cases/{case_id}/rulesets` → upload ruleset YAML (as string)
- `GET /cases/{case_id}/rulesets/active` → get active ruleset
- `POST /cases/{case_id}/artifacts?artifact_type=...` → upload artifact file
- `POST /cases/{case_id}/report` → generate report + audit packet
- `GET /cases/{case_id}/report/latest` → download latest report
- `GET /cases/{case_id}/audit/latest` → download latest audit packet

## Artifact types
- transcript (txt)
- venue (json)
- sjq (csv)
- voir_dire (jsonl)
- public_records (csv)
- public_social (json)

MAAT enforces:
- no-contact (hard-coded)
- platform permissioning (ruleset)
- vocabulary firewall (report output)
