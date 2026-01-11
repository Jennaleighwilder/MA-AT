# MAAT™ — Full War-Horse Build (v1.0)

## 1. Product assertion
MAAT prevents **jury surprises** by consolidating legally permissible juror-awareness inputs and converting them into
**court-safe, auditable decision-environment intelligence**.

MAAT does **not**:
- evaluate jurors psychologically
- label traits/archetypes
- predict verdicts
- recommend persuasion strategy
- contact jurors/prospective jurors

MAAT **does**:
- document observable statements/events
- consolidate public + court-approved inputs
- detect process integrity risks (authority events, evidence reference decay, unresolved evidence)
- generate defensible outputs + audit packets

---

## 2. System modules

### A) Jurisdiction Rules Engine (JRE)
**Purpose:** Turn ethics rules + judge standing orders into a machine-enforced permission set.

Inputs:
- jurisdiction (state/federal)
- judge standing order text (optional upload)
- platform list (LinkedIn, Facebook, X, etc.)
- firm policy overrides

Outputs:
- allowed actions matrix (passive_view, login_required_view, notification_risk, third_party_vendor_allowed)
- enforced blocks (e.g., block LinkedIn viewing if judge order prohibits any view that can notify)

Hard blocks:
- sending access requests (friend/follow/connect)
- messaging jurors/prospective jurors
- any action that constitutes ex parte communication

### B) OSINT Intake (Passive, Public Only)
B1: Public social media monitor (passive)
- Ingests public posts/bios/affiliations.
- No interaction.
- Optional 'no-notify safe mode' for platforms/jurisdictions.

B2: Public records / subscription data connector
- Litigation history (where relevant), licensing, property, etc.
- Used for *experience exposure* and *disclosure consistency*, not character judgments.

### C) Venue Intelligence
- Mock trials / focus groups / surveys / local media salience
Outputs:
- Venue Sensitivity Matrix
- Narrative Volatility Zones
- Theme Friction Map (by venue)

### D) SJQ + Voir Dire Suite
- SJQ builder (court-approved questionnaires)
- Voir dire logger (question → answer mapping, contradiction ledger)

Outputs:
- Response Distribution Map
- Disclosure Consistency Flags (for nondisclosure issues only)
- Strike-Justification Notes (facts only; no demographic inference)

### E) Deliberation Process Forensics
Kernel tracks:
- deliberation phase shifts
- authority event log
- evidence reference decay
- dissent compression signals (as process, not psychology)
- convergence timing
- unresolved evidence ledger
- pre-retcon snapshot at convergence
- hard-halt integrity state (prevents cherry-picking)

Outputs (standard MAAT report):
1) Process Timeline
2) Authority Event Log
3) Unresolved Evidence Ledger
4) Pre-Retcon Snapshot
5) Process Integrity Notes
6) Venue Sensitivity Matrix
7) Response Distribution Map
8) Disclosure Consistency Flags

---

## 3. Output language firewall (court survivability)
MAAT uses a restricted vocabulary.

Allowed verbs:
- observed, recorded, stated, disclosed, referenced, shifted, coincided, remained unresolved

Forbidden verbs/claims:
- caused, manipulated, intended, biased (as personal claim), diagnosed, predicted (re: individuals)

If an output violates the firewall, generation fails and produces an Integrity Halt.

---

## 4. Audit packet (defense-ready)
For every run, MAAT produces an audit packet containing:
- ruleset hash + version
- data source ledger (what was accessed, when)
- no-contact attestations (system-enforced)
- input hashes (transcripts, SJQ, logs)
- output hash + template version

---

## 5. Enterprise UX (what buyers see)
- Case Workspace → (Venue) → Jury Pool → SJQ/Voir Dire → Report
- No juror “scores.” Only distributions, ledgers, and documented signals.

---

## 6. Security + procurement
- Role-based access control (RBAC)
- Encryption at rest for internal case materials
- Immutable audit log
- Export control: only report artifacts + audit packet

---

## 7. What makes MAAT expensive
- It replaces scattered jury consultants + ad hoc OSINT with a governed system.
- It produces court-safe documentation and reduces sanction risk.
