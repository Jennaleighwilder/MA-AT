-- MAAT SQLite Schema (v1.0 full build)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cases (
  case_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  jurisdiction TEXT NOT NULL,
  judge TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rulesets (
  ruleset_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  rules_json TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  artifact_type TEXT NOT NULL, -- public_social, public_records, sjq, voir_dire, venue, transcript, report, audit
  path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jurors (
  juror_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS juror_items (
  item_id TEXT PRIMARY KEY,
  juror_id TEXT NOT NULL REFERENCES jurors(juror_id) ON DELETE CASCADE,
  source_type TEXT NOT NULL, -- sjq, voir_dire, public_social, public_records
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
  report_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  template_version TEXT NOT NULL,
  report_path TEXT NOT NULL,
  report_sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_packets (
  audit_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
  ruleset_sha256 TEXT NOT NULL,
  inputs_sha256 TEXT NOT NULL,
  outputs_sha256 TEXT NOT NULL,
  template_version TEXT NOT NULL,
  packet_path TEXT NOT NULL,
  created_at TEXT NOT NULL
);
