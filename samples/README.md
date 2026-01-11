# Samples
These are synthetic / placeholder sample inputs so you can run MAAT end-to-end without live data access.

Run:
- `python -m services.cli initdb`
- `python -m services.cli newcase --name "Demo Matter" --jurisdiction "NC" --judge "Doe"`
- `python -m services.cli addruleset <case_id> --name default --ruleset_path config/rulesets/default.yml`
- `python -m services.cli report <case_id> --transcript samples/transcript.txt --venue samples/venue.json --sjq samples/sjq.csv --voir_dire samples/voir_dire.jsonl --public_records samples/public_records.csv --public_social samples/public_social.json`
