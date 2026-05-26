# kira-pm-exercise-1

**Fee Reconciliation & Gap Hunt — 30-Day Sample**

## Links
- 📊 Google Sheet: *(paste your sheet URL here before submitting)*
- 🗂 This repo: `evidence/ai/` contains prompts and Claude session transcripts

---

## Headline Revenue Numbers (30-day window: Apr 25 – May 22, 2026)

| Client | Expected Revenue | Recorded in DB | Delta |
|--------|-----------------|----------------|-------|
| Client A | $33,949.50 | $33,794.50 | -$155.00 |
| Client B | $8,077.50 | $2,077.50 | -$6,000.00 *(fee_disbursement missing)* |
| Client C | $2,558.75 | $1,662.75 | -$896.00 *(fee_disbursement missing)* |
| **TOTAL** | **$44,585.75** | **~$35,677** | **-$8,909** |

> ⚠️ ~$8,909 is currently unrecorded or undercharged across the 3 clients in this window.

---

## Top 5 Gaps (ranked by revenue impact)

### 1 · SCHEMA GAP — Missing fee_disbursement rows for Client B and Client C
**Revenue impact: $6,896**
No bank account fee roll-up transactions exist in the DB for Client B ($6,000 expected at intro Tier II 0.05%) or Client C ($896 expected at 0.16% combined rate). These are the single largest source of unrecorded revenue. Fix: add automated monthly fee_disbursement trigger per client at billing cycle close.

### 2 · PRICING GAP — wire_international charged $15 instead of $30 (txn_00010, Client A)
**Revenue impact: $15 direct, systemic risk per additional txn**
txn_00010 (wire_international to Brazil) recorded $15.00 — term sheet specifies $30.00 for all international wires. A second wire_international (txn_00014) failed so no fee applied, but the fee engine clearly has a routing bug conflating domestic and international wire rates. Fix: audit all wire_international txns historically; patch fee engine to enforce correct rail mapping.

### 3 · DATA GAP — NULL recorded_fee on completed fednow deposit (txn_00012, Client A)
**Revenue impact: $0.60 direct, unknown systemic exposure**
txn_00012 is completed with a $250K fednow deposit but recorded_fee is NULL. A null fee on a completed txn means it was never billed. Risk: if this is a pattern (not just a one-off), total exposure could be material. Fix: backfill $0.60; add NOT NULL constraint with validation rule: `status=completed AND ttype=inbound_deposit → recorded_fee MUST NOT be null`.

### 4 · SCHEMA GAP — Non-normalized rail value "wire" (txn_00008, Client A)
**Revenue impact: $15/txn if misrouted as domestic when international**
The rail enum accepts "wire" as a value, which is ambiguous. System appears to default it to wire_domestic ($15), but if any international wire enters as "wire" it gets undercharged by $15. Fix: enforce enum constraint: `wire_domestic | wire_international | ach_standard | ach_same_day | fednow`. Reject or flag any other value at ingestion.

### 5 · PRICING GAP — Client C term sheet has no wire pricing, but wire_domestic txn exists (txn_00044)
**Revenue impact: unknown / potential overbilling**
Client C's Exhibit C lists only FedNow, ACH same-day, and ACH standard pass-throughs. txn_00044 is a $250K wire_domestic charged at $15 — but there is no contractual basis for this in the term sheet. This is either an overbilling risk or a term sheet gap. Escalating to @Nicolle.

---

## Key Decisions & Assumptions Documented

1. **txn_00008 rail="wire"** → treated as wire_domestic ($15). Flagged as schema gap.
2. **Client B intro period** → Tier II pricing applied to all months through June 2026 (3-month window from 2026-04-10).
3. **Monthly minimum check** → performed per calendar month, not per 30-day window. Client A exceeds $13,995/month on variable fees; Client B exceeds $4,995 → minimums not applicable in this window.
4. **Reserve (txn_00040)** → correctly recorded at $0, excluded from revenue per instructions.
5. **Failed transactions** → $0 fee treated as correct; flagged as ambiguity since term sheet is silent.
6. **Client A bank account fee tier-blend** → May volume of $15.85M crosses $15M Tier I/II boundary. Correct calculation: $15M × 0.08% + $0.85M × 0.07% = $12,595 (not flat-rate on full volume).
7. **Client A 2bp entity discount** → not applied; flagged for clarification with @Nicolle.

---

## Questions Sent to @Nicolle and @Diego

**To @Nicolle (PD):**
1. Client C term sheet has no wire_domestic or wire_international pricing, but txn_00044 is a completed wire_domestic. Was wire pricing intentionally excluded? Should $15 be billed or waived?
2. What fees count toward the monthly minimum floor — only variable % fees (BA fee + ramps), or also pass-throughs?
3. Does Client A have any subsidiary entities in the system that should receive the 2bp discount on bank variable fees?

**To @Diego (Eng):**
1. Is $0 fee on failed transactions a hard system rule, or does it depend on how far the txn progressed?
2. Is txn_00012's NULL fee a one-off data entry issue or could there be other completed txns with null fees in the full dataset?
3. What is the intended enum for the `rail` field? "wire" (txn_00008) is not wire_domestic or wire_international — is this a known ingestion bug?

---

## Repo Structure

```
kira-pm-exercise-1/
├── README.md
├── evidence/
│   ├── ai/
│   │   ├── prompts.md         ← all prompts used with Claude
│   │   └── session_log.md     ← Claude reasoning transcripts
│   └── work/
│       └── reconcile.py       ← reconciliation script
```
