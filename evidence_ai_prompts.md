# AI Prompts & Reasoning Log

## Tool used: Claude (claude.ai)

---

## Prompt 1 — Initial data ingestion and structure analysis
**Goal:** Parse the CSV and term sheets, identify transaction types and fee structures.

> "I have a 50-row transaction CSV and 3 term sheets for a fee reconciliation exercise. 
> Parse the data, identify all transaction types present (inbound_deposit, on_ramp, off_ramp, 
> off_ramp_swift, refund, fee_disbursement, reserve_deposit), and tell me what fee logic 
> applies to each type per client."

**Claude output:** Identified 7 transaction types, mapped each to the relevant term sheet clause. 
Flagged that on_ramp/off_ramp fees are monthly-volume tiered (not per-txn), requiring 
monthly volume aggregation before computing expected fees.

---

## Prompt 2 — Monthly volume aggregation and tier determination
**Goal:** Compute monthly VA, on-ramp, and off-ramp volumes per client to determine which 
pricing tier applies.

> "Aggregate volume per client per month for: inbound_deposit (VA volume), on_ramp, off_ramp, 
> off_ramp_swift. Only count completed transactions. Exclude refunds from VA volume. 
> Determine which pricing tier applies for each."

**Claude output:**
- Client A April: VA $5.1M (Tier I), On-ramp $2M (Tier I)
- Client A May: VA $15.85M → TIER BLEND (crosses $15M threshold mid-month)
- Client B: intro Tier II applies to all April+May regardless of volume
- Client C: all volumes in Tier I

Key insight surfaced: Client A May VA volume crosses the $15M→$30M tier boundary, 
requiring a blended calculation for the bank account fee, not a flat rate.

---

## Prompt 3 — Bank account fee tier-blend calculation
**Goal:** Calculate the correct tier-blended bank account fee for Client A May.

> "Client A May VA volume is $15.85M. Tier I is 0.08% for $0-15M, Tier II is 0.07% for 
> $15M-30M. Calculate the blended fee."

**Claude reasoning:**
- Tier I: $15,000,000 × 0.08% = $12,000
- Tier II: $850,000 × 0.07% = $595
- Total: $12,595
- vs recorded $16,520 for the full window → delta $155 when added to April fee

---

## Prompt 4 — Gap identification and ranking
**Goal:** Surface non-obvious gaps beyond simple null checks.

> "Given all the deltas found, what are the 'silent breakages' — gaps that wouldn't show 
> up as an obvious error in the DB but represent real revenue risk?"

**Claude output — key silent gaps identified:**
1. Missing fee_disbursement rows for B and C (invisible — no row = no error flag in DB)
2. wire_international undercharge (looks like a valid fee, just wrong amount)
3. Client A tier-blend error (recorded fee exists, just slightly wrong)
4. Client A 2bp subsidiary discount clause — never applied, term sheet clause that has 
   no DB representation at all
5. Client C wire pricing — charged with no contractual basis

---

## Prompt 5 — Questions to ask @Nicolle and @Diego
**Goal:** Identify what can't be resolved from data alone and needs human clarification.

> "What questions should I escalate to the PD and the engineer that I cannot answer 
> from the data and term sheets alone?"

**Claude output:** 6 questions covering: wire pricing for Client C, monthly min definition, 
subsidiary discount, failed txn policy, NULL fee pattern, and rail enum normalization.

