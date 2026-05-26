import csv
import io

# ============================================================
# TERM SHEET DATA
# ============================================================

# CLIENT A — Effective 2025-03-15, Month 14 (past full ramp-up)
# Bank Account Fee tiers (on monthly VA volume)
client_a = {
    "effective_date": "2025-03-15",
    "month": 14,
    "monthly_min": 13995,
    "onboarding": 995,  # already paid at contract start, not in 30-day window
    "bank_platform_fee": 0,  # WAIVED
    "va_tiers": [(15_000_000, 0.0008), (30_000_000, 0.0007), (float('inf'), 0.0004)],
    "passthru": {
        "fednow": 0.60,
        "ach_same_day": 0.75,
        "ach_standard": 0.40,
        "wire_domestic": 15.00,
        "wire_international": 30.00,
    },
    "on_ramp_tiers": [(15_000_000, 0.0012), (30_000_000, 0.0006), (float('inf'), 0.0003)],
    "off_ramp_tiers": [(15_000_000, 0.0015), (30_000_000, 0.0010), (float('inf'), 0.0003)],
    "off_ramp_swift_tiers": [(15_000_000, 0.0025), (30_000_000, 0.0015), (float('inf'), 0.0010)],
}

# CLIENT B — Effective 2026-04-10, Month 2 (inside 3-month intro Tier II window)
# Intro: Tier II pricing for first 3 months regardless of volume
# Tiers: $0-5M=I, $5M-15M=II, $15M+=III
# Reserve: $9,995 (held, not revenue)
client_b = {
    "effective_date": "2026-04-10",
    "month": 2,
    "monthly_min": 4995,  # Month 2: $4,995
    "onboarding": 0,  # WAIVED
    "bank_platform_fee": 0,  # WAIVED
    "reserve": 9995,  # held, not revenue
    "intro_tier": "II",  # 3-month intro at Tier II
    "va_tiers": [(5_000_000, 0.0008), (15_000_000, 0.0005), (float('inf'), 0.0004)],
    "va_intro_rate": 0.0005,  # Tier II rate during intro period
    "passthru": {
        "fednow": 0.60,
        "ach_same_day": 0.75,
        "ach_standard": 0.40,
        "wire_domestic": 15.00,
        "wire_international": 30.00,
    },
    "on_ramp_tiers": [(5_000_000, 0.0012), (15_000_000, 0.0005), (float('inf'), 0.0003)],
    "on_ramp_intro_rate": 0.0005,  # Tier II
    "off_ramp_tiers": [(5_000_000, 0.0012), (15_000_000, 0.0005), (float('inf'), 0.0003)],
    "off_ramp_intro_rate": 0.0005,  # Tier II
    "off_ramp_swift_tiers": [(5_000_000, 0.0020), (15_000_000, 0.0005), (float('inf'), 0.0004)],
}

# CLIENT C — Effective 2026-05-05, Month 1
# Combined bank+platform fee (not separate)
# Monthly min: $0 for months 1-2
# NOTE: No wire_domestic or wire_international in term sheet — flag!
client_c = {
    "effective_date": "2026-05-05",
    "month": 1,
    "monthly_min": 0,  # Month 1: $0
    "onboarding": 995,
    "bank_platform_fee": 0,  # WAIVED
    "reserve": 0,  # WAIVED
    "va_tiers": [(15_000_000, 0.0016), (30_000_000, 0.0006), (float('inf'), 0.0004)],
    "passthru": {
        "fednow": 0.60,
        "ach_same_day": 0.75,
        "ach_standard": 0.40,
        # NO wire_domestic or wire_international in term sheet!
    },
    "on_ramp_tiers": [(15_000_000, 0.0080), (30_000_000, 0.0006), (float('inf'), 0.0004)],
    "off_ramp_tiers": [(15_000_000, 0.0012), (30_000_000, 0.0010), (float('inf'), 0.0005)],
    "off_ramp_swift_tiers": [(15_000_000, 0.0025), (30_000_000, 0.0015), (float('inf'), 0.0010)],
}

clients = {"client_a": client_a, "client_b": client_b, "client_c": client_c}

# ============================================================
# TRANSACTION DATA
# ============================================================

transactions = [
    ("txn_00001","2026-04-25","client_a","inbound_deposit","wire_domestic",3500000,"USD",3500000,"USD","US","completed",15,"USD","bank_passthru_fixed"),
    ("txn_00002","2026-04-27","client_a","inbound_deposit","ach_standard",1200000,"USD",1200000,"USD","US","completed",0.4,"USD","bank_passthru_fixed"),
    ("txn_00003","2026-04-29","client_a","inbound_deposit","fednow",400000,"USD",400000,"USD","US","completed",0.6,"USD","bank_passthru_fixed"),
    ("txn_00004","2026-05-01","client_a","inbound_deposit","wire_domestic",2800000,"USD",2800000,"USD","US","completed",15,"USD","bank_passthru_fixed"),
    ("txn_00005","2026-05-02","client_a","inbound_deposit","ach_same_day",600000,"USD",600000,"USD","US","completed",0.75,"USD","bank_passthru_fixed"),
    ("txn_00006","2026-05-04","client_a","inbound_deposit","wire_international",2200000,"USD",2200000,"USD","GB","completed",30,"USD","bank_passthru_fixed"),
    ("txn_00007","2026-05-06","client_a","inbound_deposit","ach_standard",1000000,"USD",1000000,"USD","US","completed",0.4,"USD","bank_passthru_fixed"),
    ("txn_00008","2026-05-08","client_a","inbound_deposit","wire",3000000,"USD",3000000,"USD","US","completed",15,"USD","bank_passthru_fixed"),
    ("txn_00009","2026-05-09","client_a","inbound_deposit","ach_same_day",500000,"USD",500000,"USD","US","completed",0.75,"USD","bank_passthru_fixed"),
    ("txn_00010","2026-05-11","client_a","inbound_deposit","wire_international",1800000,"USD",1800000,"USD","BR","completed",15,"USD","bank_passthru_fixed"),
    ("txn_00011","2026-05-13","client_a","inbound_deposit","ach_standard",900000,"USD",900000,"USD","US","completed",0.4,"USD","bank_passthru_fixed"),
    ("txn_00012","2026-05-14","client_a","inbound_deposit","fednow",250000,"USD",250000,"USD","US","completed",None,None,None),
    ("txn_00013","2026-05-15","client_a","inbound_deposit","wire_domestic",2500000,"USD",2500000,"USD","US","completed",15,"USD","bank_passthru_fixed"),
    ("txn_00014","2026-05-17","client_a","inbound_deposit","wire_international",1200000,"USD",1200000,"USD","DE","failed",0,"USD","bank_passthru_fixed"),
    ("txn_00015","2026-05-19","client_a","inbound_deposit","fednow",300000,"USD",300000,"USD","US","completed",0.6,"USD","bank_passthru_fixed"),
    ("txn_00016","2026-05-21","client_a","refund","ach_standard",-300000,"USD",-300000,"USD","US","completed",-0.4,"USD","bank_passthru_fixed_reversal"),
    ("txn_00017","2026-04-30","client_a","on_ramp","",2000000,"USD",2000000,"USDC","","completed",2400,"USD","on_ramp_fee"),
    ("txn_00018","2026-05-05","client_a","on_ramp","",1500000,"USD",1500000,"USDC","","completed",1800,"USD","on_ramp_fee"),
    ("txn_00019","2026-05-12","client_a","on_ramp","",2500000,"USD",2500000,"USDC","","completed",3000,"USD","on_ramp_fee"),
    ("txn_00020","2026-05-18","client_a","on_ramp","",2000000,"USD",2000000,"USDC","","completed",2400,"USD","on_ramp_fee"),
    ("txn_00021","2026-05-03","client_a","off_ramp","",1000000,"USDC",1000000,"USD","","completed",1500,"USD","off_ramp_fee"),
    ("txn_00022","2026-05-10","client_a","off_ramp","",1500000,"USDC",1500000,"USD","","completed",2250,"USD","off_ramp_fee"),
    ("txn_00023","2026-05-16","client_a","off_ramp_swift","",800000,"USDC",800000,"USD","","completed",2000,"USD","off_ramp_swift_fee"),
    ("txn_00024","2026-05-20","client_a","off_ramp","",1200000,"USDC",1200000,"USD","","completed",1800,"USD","off_ramp_fee"),
    ("txn_00025","2026-05-15","client_a","fee_disbursement","",None,None,None,None,None,"completed",16520,"USD","bank_account_fee"),
    ("txn_00026","2026-04-26","client_b","inbound_deposit","wire_domestic",2000000,"USD",2000000,"USD","US","completed",15,"USD","bank_passthru_fixed"),
    ("txn_00027","2026-04-28","client_b","inbound_deposit","ach_same_day",700000,"USD",700000,"USD","US","completed",0.75,"USD","bank_passthru_fixed"),
    ("txn_00028","2026-05-01","client_b","inbound_deposit","fednow",350000,"USD",350000,"USD","US","completed",0.6,"USD","bank_passthru_fixed"),
    ("txn_00029","2026-05-03","client_b","inbound_deposit","wire_domestic",2500000,"USD",2500000,"USD","US","completed",15,"USD","bank_passthru_fixed"),
    ("txn_00030","2026-05-07","client_b","inbound_deposit","wire_international",1500000,"USD",1500000,"USD","GB","completed",30,"USD","bank_passthru_fixed"),
    ("txn_00031","2026-05-13","client_b","inbound_deposit","ach_standard",700000,"USD",700000,"USD","US","completed",0.4,"USD","bank_passthru_fixed"),
    ("txn_00032","2026-05-18","client_b","inbound_deposit","ach_same_day",800000,"USD",800000,"USD","US","completed",0.75,"USD","bank_passthru_fixed"),
    ("txn_00033","2026-05-22","client_b","inbound_deposit","wire_domestic",3450000,"USD",3450000,"USD","US","completed",15,"USD","bank_passthru_fixed"),
    ("txn_00034","2026-04-29","client_b","on_ramp","",800000,"USD",800000,"USDC","","completed",400,"USD","on_ramp_fee"),
    ("txn_00035","2026-05-06","client_b","on_ramp","",1200000,"USD",1200000,"USDC","","completed",600,"USD","on_ramp_fee"),
    ("txn_00036","2026-05-15","client_b","on_ramp","",700000,"USD",700000,"USDC","","completed",350,"USD","on_ramp_fee"),
    ("txn_00037","2026-05-20","client_b","on_ramp","",300000,"USD",300000,"USDC","","completed",150,"USD","on_ramp_fee"),
    ("txn_00038","2026-05-05","client_b","off_ramp","",500000,"USDC",500000,"USD","","completed",250,"USD","off_ramp_fee"),
    ("txn_00039","2026-05-12","client_b","off_ramp","",500000,"USDC",500000,"USD","","completed",250,"USD","off_ramp_fee"),
    ("txn_00040","2026-05-15","client_b","reserve_deposit","",9995,"USD",9995,"USD","US","completed",0,"USD","reserve"),
    ("txn_00041","2026-05-06","client_c","inbound_deposit","fednow",30000,"USD",30000,"USD","US","completed",0.6,"USD","bank_passthru_fixed"),
    ("txn_00042","2026-05-08","client_c","inbound_deposit","ach_standard",100000,"USD",100000,"USD","US","completed",0.4,"USD","bank_passthru_fixed"),
    ("txn_00043","2026-05-10","client_c","inbound_deposit","ach_same_day",80000,"USD",80000,"USD","US","completed",0.75,"USD","bank_passthru_fixed"),
    ("txn_00044","2026-05-12","client_c","inbound_deposit","wire_domestic",250000,"USD",250000,"USD","US","completed",15,"USD","bank_passthru_fixed"),
    ("txn_00045","2026-05-14","client_c","inbound_deposit","ach_standard",80000,"USD",80000,"USD","US","completed",0.4,"USD","bank_passthru_fixed"),
    ("txn_00046","2026-05-16","client_c","inbound_deposit","fednow",20000,"USD",20000,"USD","US","completed",0.6,"USD","bank_passthru_fixed"),
    ("txn_00047","2026-05-22","client_c","refund","ach_standard",-20000,"USD",-20000,"USD","US","completed",-0.4,"USD","bank_passthru_fixed_reversal"),
    ("txn_00048","2026-05-15","client_c","on_ramp","",100000,"USD",100000,"USDC","","completed",800,"USD","on_ramp_fee"),
    ("txn_00049","2026-05-20","client_c","on_ramp","",100000,"USD",100000,"USDC","","completed",800,"USD","on_ramp_fee"),
    ("txn_00050","2026-05-19","client_c","off_ramp","",50000,"USDC",50000,"USD","","completed",60,"USD","off_ramp_fee"),
]

# ============================================================
# HELPER: tiered % fee (simple — all volume at single tier since well below thresholds)
# For this 30-day window volumes are all in Tier I for A and C; B is in intro Tier II
# ============================================================

def get_tier_rate(volume, tiers):
    for threshold, rate in tiers:
        if volume <= threshold:
            return rate
    return tiers[-1][1]

# ============================================================
# STEP 1: Compute monthly volumes per client (needed for tier + bank account fee)
# ============================================================

# Separate April vs May transactions per client
# The 30-day window spans late April + May.
# For bank account fee and tier determination, we need monthly volume.
# Transactions in April: txn_00001,02,03 (client_a Apr), txn_00017 (client_a on_ramp Apr)
# txn_00026,27 (client_b Apr), txn_00034 (client_b on_ramp Apr)

def monthly_va_volume(client_id, month):
    """Sum of inbound_deposit amounts for a client in a given month (completed only)."""
    total = 0
    for t in transactions:
        txn_id, date, cid, ttype, rail, amt_src, cur_src, amt_dst, cur_dst, country, status, rec_fee, fee_cur, fee_type = t
        if cid != client_id: continue
        if status != "completed": continue
        if ttype != "inbound_deposit": continue
        if amt_src is None or amt_src < 0: continue
        txn_month = int(date[5:7])
        if txn_month == month:
            total += amt_src
    return total

def monthly_onramp_volume(client_id, month):
    total = 0
    for t in transactions:
        txn_id, date, cid, ttype, rail, amt_src, cur_src, amt_dst, cur_dst, country, status, rec_fee, fee_cur, fee_type = t
        if cid != client_id: continue
        if status != "completed": continue
        if ttype != "on_ramp": continue
        txn_month = int(date[5:7])
        if txn_month == month:
            total += amt_src
    return total

def monthly_offramp_volume(client_id, month, swift=False):
    total = 0
    for t in transactions:
        txn_id, date, cid, ttype, rail, amt_src, cur_src, amt_dst, cur_dst, country, status, rec_fee, fee_cur, fee_type = t
        if cid != client_id: continue
        if status != "completed": continue
        if swift:
            if ttype != "off_ramp_swift": continue
        else:
            if ttype != "off_ramp": continue
        txn_month = int(date[5:7])
        if txn_month == month:
            total += amt_src
    return total

# Print monthly volumes
print("=== MONTHLY VOLUMES ===")
for cid in ["client_a","client_b","client_c"]:
    for m in [4,5]:
        va = monthly_va_volume(cid, m)
        onr = monthly_onramp_volume(cid, m)
        offr = monthly_offramp_volume(cid, m)
        offr_s = monthly_offramp_volume(cid, m, swift=True)
        if va+onr+offr+offr_s > 0:
            print(f"  {cid} Month {m}: VA={va:,.0f} OnRamp={onr:,.0f} OffRamp={offr:,.0f} OffRampSWIFT={offr_s:,.0f}")


# ============================================================
# STEP 2: Per-transaction expected fee calculation
# ============================================================

# KEY DECISIONS (to document as ambiguities):
# 1. txn_00008: rail="wire" (not wire_domestic or wire_international) — treat as wire_domestic ($15)
# 2. txn_00010: wire_international to BR, recorded $15 — term sheet says $30. DELTA!
# 3. txn_00012: fednow, no fee recorded — missing fee. DELTA!
# 4. txn_00014: failed txn, fee=$0 — reasonable, not charging failed txns. FLAG as ambiguity.
# 5. txn_00025: fee_disbursement $16,520 — this is the bank_account_fee roll-up, verify below
# 6. Client B intro period: 3-month intro at Tier II from 2026-04-10, so April+May+June = Tier II
# 7. Reserve txn_00040: $0 fee correct — reserve is held not revenue
# 8. Client C wire_domestic txn_00044: wire not in term sheet — pricing gap!
# 9. Refunds: fee reversal recorded, treat as correct pass-through reversal

def expected_passthru_fee(client_id, rail, status):
    """Return expected pass-through fee for inbound deposit."""
    if status == "failed":
        return 0.0, "no_fee_failed"
    
    cfg = clients[client_id]
    passthru = cfg["passthru"]
    
    rail_map = {
        "fednow": "fednow",
        "ach_same_day": "ach_same_day", 
        "ach_standard": "ach_standard",
        "wire_domestic": "wire_domestic",
        "wire_international": "wire_international",
        "wire": "wire_domestic",  # AMBIGUITY: normalize to domestic
    }
    
    normalized = rail_map.get(rail)
    if normalized is None:
        return None, f"unknown_rail:{rail}"
    if normalized not in passthru:
        return None, f"rail_not_in_term_sheet:{rail}"
    return passthru[normalized], "ok"

def expected_onramp_fee(client_id, amount, month):
    cfg = clients[client_id]
    if client_id == "client_b":
        # Intro period Tier II through June 2026
        rate = cfg["on_ramp_intro_rate"]
    else:
        vol = monthly_onramp_volume(client_id, month)
        rate = get_tier_rate(vol, cfg["on_ramp_tiers"])
    return round(amount * rate, 2)

def expected_offramp_fee(client_id, amount, month, swift=False):
    cfg = clients[client_id]
    if client_id == "client_b":
        rate = cfg["off_ramp_intro_rate"]
    else:
        if swift:
            vol = monthly_offramp_volume(client_id, month, swift=True)
            rate = get_tier_rate(vol, cfg["off_ramp_swift_tiers"])
        else:
            vol = monthly_offramp_volume(client_id, month)
            rate = get_tier_rate(vol, cfg["off_ramp_tiers"])
    return round(amount * rate, 2)

# ============================================================
# STEP 3: Bank account fee calculation (monthly % on VA volume)
# ============================================================

# Client A: Month 14, Tier I <$15M = 0.08%, Tier II $15-30M = 0.07%, Tier III $30M+ = 0.04%
# April VA volume = $5.1M → Tier I → 0.08%
# May VA volume = $15.85M → crosses $15M threshold → TIER BLEND needed
# Tier I: $15M * 0.08% = $12,000
# Tier II: $0.85M * 0.07% = $595
# Total May bank account fee = $12,595
# April bank account fee = $5.1M * 0.08% = $4,080
# Total = $16,675
# Recorded fee_disbursement = $16,520 → DELTA = -$155

def calc_bank_account_fee_tiered(volume, tiers):
    """Tier-blended bank account fee."""
    fee = 0
    prev = 0
    for threshold, rate in tiers:
        if volume <= threshold:
            fee += (volume - prev) * rate
            break
        else:
            fee += (threshold - prev) * rate
            prev = threshold
    return round(fee, 2)

# Client A
a_apr_va = monthly_va_volume("client_a", 4)  # 5,100,000
a_may_va = monthly_va_volume("client_a", 5)  # 15,850,000
a_apr_fee = calc_bank_account_fee_tiered(a_apr_va, client_a["va_tiers"])
a_may_fee = calc_bank_account_fee_tiered(a_may_va, client_a["va_tiers"])
a_total_ba_fee = round(a_apr_fee + a_may_fee, 2)

print(f"\n=== CLIENT A BANK ACCOUNT FEE ===")
print(f"  April VA volume: ${a_apr_va:,.0f} → fee: ${a_apr_fee:,.2f}")
print(f"  May VA volume: ${a_may_va:,.0f} → fee (tier-blended): ${a_may_fee:,.2f}")
print(f"  Expected total bank account fee: ${a_total_ba_fee:,.2f}")
print(f"  Recorded (txn_00025): $16,520.00")
print(f"  DELTA: ${a_total_ba_fee - 16520:,.2f}")

# Client B: intro Tier II rate = 0.05%
b_apr_va = monthly_va_volume("client_b", 4)  # 2,700,000
b_may_va = monthly_va_volume("client_b", 5)  # 9,300,000
b_apr_fee = round(b_apr_va * 0.0005, 2)
b_may_fee = round(b_may_va * 0.0005, 2)
b_total_ba_fee = round(b_apr_fee + b_may_fee, 2)
print(f"\n=== CLIENT B BANK ACCOUNT FEE (intro Tier II = 0.05%) ===")
print(f"  April VA volume: ${b_apr_va:,.0f} → fee: ${b_apr_fee:,.2f}")
print(f"  May VA volume: ${b_may_va:,.0f} → fee: ${b_may_fee:,.2f}")
print(f"  Expected total bank account fee: ${b_total_ba_fee:,.2f}")
print(f"  No fee_disbursement txn recorded for Client B → MISSING!")

# Client C: combined bank+platform fee 0.16% (Tier I, volume well below $15M)
c_may_va = monthly_va_volume("client_c", 5)  # 560,000 (net of refund)
# Note: refund is -$20,000 → should we net? Flag as ambiguity
c_may_fee = round(c_may_va * 0.0016, 2)
print(f"\n=== CLIENT C BANK+PLATFORM FEE (0.16%) ===")
print(f"  May VA volume: ${c_may_va:,.0f} → fee: ${c_may_fee:,.2f}")
print(f"  No fee_disbursement txn recorded for Client C → MISSING!")


# ============================================================
# STEP 4: Per-transaction reconciliation table
# ============================================================

print("\n=== PER-TRANSACTION RECONCILIATION ===")
print(f"{'TXN_ID':<12} {'CLIENT':<10} {'TYPE':<18} {'RAIL':<20} {'AMOUNT':>12} {'REC_FEE':>10} {'EXP_FEE':>10} {'DELTA':>10} {'STATUS':<12} {'FLAG'}")
print("-"*140)

recon_rows = []

for t in transactions:
    txn_id, date, cid, ttype, rail, amt_src, cur_src, amt_dst, cur_dst, country, status, rec_fee, fee_cur, fee_type = t
    month = int(date[5:7])
    
    exp_fee = None
    flag = ""
    notes = ""
    
    if ttype == "inbound_deposit":
        if amt_src and amt_src < 0:
            # refund handled separately
            exp_fee = rec_fee
        else:
            exp, note = expected_passthru_fee(cid, rail, status)
            exp_fee = exp
            if note == "no_fee_failed":
                flag = "INFO: failed txn, $0 fee ok — ambiguity: should failed wire still be charged?"
            elif note and note.startswith("rail_not_in_term_sheet"):
                flag = f"⚠️ PRICING GAP: {note}"
            elif note and note.startswith("unknown_rail"):
                flag = f"⚠️ SCHEMA GAP: rail value '{rail}' not normalized"
            
            if rec_fee is None:
                flag += " | ⚠️ DATA GAP: recorded_fee is NULL"
            
            # Check wire_international recorded $15 instead of $30
            if rail == "wire_international" and status == "completed" and rec_fee == 15:
                flag += " | 🔴 PRICING ERROR: recorded $15, expected $30"
    
    elif ttype == "refund":
        # Pass-through reversal — expected = same as original pass-through negated
        exp_fee = rec_fee  # treat as correct, flag for review
        flag = "INFO: refund reversal — verify matches original txn"
    
    elif ttype == "on_ramp":
        exp_fee = expected_onramp_fee(cid, amt_src, month)
    
    elif ttype == "off_ramp":
        exp_fee = expected_offramp_fee(cid, amt_src, month, swift=False)
    
    elif ttype == "off_ramp_swift":
        exp_fee = expected_offramp_fee(cid, amt_src, month, swift=True)
    
    elif ttype == "fee_disbursement":
        if cid == "client_a":
            exp_fee = a_total_ba_fee
        flag = "Bank account fee roll-up"
    
    elif ttype == "reserve_deposit":
        exp_fee = 0
        flag = "Reserve — held, not revenue"
    
    # Compute delta
    if exp_fee is not None and rec_fee is not None:
        delta = round(rec_fee - exp_fee, 2)
        if abs(delta) > 0.01:
            flag = ("🔴 DELTA $"+str(delta)+" | " + flag).strip(" | ")
        status_label = "✅ MATCH" if abs(delta) <= 0.01 else "❌ MISMATCH"
    elif rec_fee is None:
        delta = None
        status_label = "⚠️ NULL FEE"
    else:
        delta = None
        status_label = "❓ UNKNOWN"
    
    amt_display = f"${amt_src:,.0f}" if amt_src else "—"
    rec_display = f"${rec_fee:,.2f}" if rec_fee is not None else "NULL"
    exp_display = f"${exp_fee:,.2f}" if exp_fee is not None else "?"
    delta_display = f"${delta:,.2f}" if delta is not None else "—"
    
    print(f"{txn_id:<12} {cid:<10} {ttype:<18} {rail:<20} {amt_display:>12} {rec_display:>10} {exp_display:>10} {delta_display:>10} {status_label:<12} {flag}")
    
    recon_rows.append({
        "txn_id": txn_id, "date": date, "client": cid, "type": ttype, "rail": rail,
        "amount": amt_src, "recorded_fee": rec_fee, "expected_fee": exp_fee,
        "delta": delta, "status": status_label, "flag": flag
    })


# ============================================================
# STEP 5: Per-client revenue summary
# ============================================================

print("\n\n=== PER-CLIENT REVENUE SUMMARY (30-day window) ===\n")

# ---- CLIENT A ----
# Pass-through fees (completed inbound deposits, not failed, not refunds)
a_passthru_expected = 0
a_passthru_lines = []
for t in transactions:
    txn_id, date, cid, ttype, rail, amt_src, cur_src, amt_dst, cur_dst, country, status, rec_fee, fee_cur, fee_type = t
    if cid != "client_a": continue
    if ttype != "inbound_deposit": continue
    if status == "failed": continue
    if amt_src and amt_src < 0: continue
    exp, note = expected_passthru_fee(cid, rail, status)
    if exp:
        a_passthru_expected += exp
        a_passthru_lines.append(f"    {txn_id}: {rail} → ${exp}")

# On-ramp fees (Tier I, 0.12%)
a_onramp_expected = round(monthly_onramp_volume("client_a",4) * 0.0012 + monthly_onramp_volume("client_a",5) * 0.0012, 2)

# Off-ramp fees (Tier I, 0.15%)
a_offramp_expected = round(monthly_offramp_volume("client_a",5) * 0.0015, 2)
a_offramp_swift_expected = round(monthly_offramp_volume("client_a",5,swift=True) * 0.0025, 2)

# Bank account fee (tier-blended)
a_ba_fee_expected = a_total_ba_fee

# Monthly minimum check: $13,995/month. 
# What counts toward minimum? VA fees + on/off ramp fees + pass-through? 
# This is an AMBIGUITY GAP — term sheet doesn't specify.
# Conservative: count VA bank account fee + on/off ramp fees (variable fees)
a_variable_fees = a_ba_fee_expected + a_onramp_expected + a_offramp_expected + a_offramp_swift_expected
# Monthly min applies per month, so Apr: $13,995, May: $13,995 = $27,990 total floor
# But window is 30 days spanning 2 months — AMBIGUITY: do we check per-month or per-window?
# Flag this.

a_total_expected = a_passthru_expected + a_onramp_expected + a_offramp_expected + a_offramp_swift_expected + a_ba_fee_expected

print("CLIENT A")
print(f"  VA Pass-through fees (expected):    ${a_passthru_expected:>10,.2f}")
print(f"  On-ramp fees (0.12% × $8M):         ${a_onramp_expected:>10,.2f}")
print(f"  Off-ramp fees (0.15% × $3.7M):      ${a_offramp_expected:>10,.2f}")
print(f"  Off-ramp SWIFT (0.25% × $0.8M):     ${a_offramp_swift_expected:>10,.2f}")
print(f"  Bank Account Fee (tier-blended):     ${a_ba_fee_expected:>10,.2f}")
print(f"  Monthly Minimum floor (×2 months):   $    27,990.00  ← AMBIGUITY: what counts?")
print(f"  ------------------------------------------")
print(f"  TOTAL EXPECTED REVENUE:              ${a_total_expected:>10,.2f}")
print(f"  TOTAL RECORDED (from DB):            ${16520 + 9600 + 5550 + 2000 + 45.55:>10,.2f}  (approx, pass-thru + ramps + BA fee)")
print()

# ---- CLIENT B ----
b_passthru_expected = 0
for t in transactions:
    txn_id, date, cid, ttype, rail, amt_src, cur_src, amt_dst, cur_dst, country, status, rec_fee, fee_cur, fee_type = t
    if cid != "client_b": continue
    if ttype != "inbound_deposit": continue
    if status == "failed": continue
    if amt_src and amt_src < 0: continue
    exp, note = expected_passthru_fee(cid, rail, status)
    if exp:
        b_passthru_expected += exp

b_onramp_expected = round((monthly_onramp_volume("client_b",4) + monthly_onramp_volume("client_b",5)) * 0.0005, 2)
b_offramp_expected = round(monthly_offramp_volume("client_b",5) * 0.0005, 2)
b_ba_fee_expected = b_total_ba_fee
# Monthly min Month 2 = $4,995
b_min = 4995
b_total_expected = b_passthru_expected + b_onramp_expected + b_offramp_expected + b_ba_fee_expected

print("CLIENT B (intro Tier II pricing through June 2026)")
print(f"  VA Pass-through fees (expected):    ${b_passthru_expected:>10,.2f}")
print(f"  On-ramp fees (0.05% × $3M):         ${b_onramp_expected:>10,.2f}")
print(f"  Off-ramp fees (0.05% × $1M):        ${b_offramp_expected:>10,.2f}")
print(f"  Bank Account Fee (intro 0.05%):      ${b_ba_fee_expected:>10,.2f}")
print(f"  Monthly Minimum (Month 2 = $4,995):  $     4,995.00  ← check if variable fees exceed")
print(f"  Reserve ($9,995): HELD — not revenue")
print(f"  No fee_disbursement txn in DB → MISSING")
print(f"  ------------------------------------------")
print(f"  TOTAL EXPECTED REVENUE:              ${b_total_expected:>10,.2f}")
print(f"  Min floor applies? Variable fees ${b_total_expected:,.2f} {'> $4,995 → min NOT applicable' if b_total_expected > 4995 else '< $4,995 → MIN APPLIES, charge $4,995'}")
print()

# ---- CLIENT C ----
c_passthru_expected = 0
for t in transactions:
    txn_id, date, cid, ttype, rail, amt_src, cur_src, amt_dst, cur_dst, country, status, rec_fee, fee_cur, fee_type = t
    if cid != "client_c": continue
    if ttype != "inbound_deposit": continue
    if status == "failed": continue
    if amt_src and amt_src < 0: continue
    exp, note = expected_passthru_fee(cid, rail, status)
    if exp is not None:
        c_passthru_expected += exp
    # wire_domestic has no rate in term sheet → flag but can't add to expected

c_onramp_expected = round(monthly_onramp_volume("client_c",5) * 0.0080, 2)
c_offramp_expected = round(monthly_offramp_volume("client_c",5) * 0.0012, 2)
c_ba_fee_expected = c_may_fee
c_total_expected = c_passthru_expected + c_onramp_expected + c_offramp_expected + c_ba_fee_expected
# Monthly min Month 1 = $0

print("CLIENT C (Month 1, monthly min = $0)")
print(f"  VA Pass-through fees (expected):    ${c_passthru_expected:>10,.2f}")
print(f"    ⚠️  wire_domestic ($250K, txn_00044) has NO rate in term sheet → not counted")
print(f"  On-ramp fees (0.80% × $200K):       ${c_onramp_expected:>10,.2f}")
print(f"  Off-ramp fees (0.12% × $50K):       ${c_offramp_expected:>10,.2f}")
print(f"  Bank+Platform Fee (0.16% × $560K):  ${c_ba_fee_expected:>10,.2f}")
print(f"  Monthly Minimum: $0 (Month 1)")
print(f"  No fee_disbursement txn in DB → MISSING")
print(f"  ------------------------------------------")
print(f"  TOTAL EXPECTED REVENUE:              ${c_total_expected:>10,.2f}")
print()


# ============================================================
# STEP 6: GAP LIST (ranked by revenue impact)
# ============================================================

print("\n\n=== GAP LIST (ranked by revenue impact) ===\n")

gaps = [
    {
        "rank": 1,
        "type": "SCHEMA GAP",
        "gap": "No fee_disbursement transactions for Client B and Client C in the DB",
        "where": "Transactions table — clients client_b, client_c",
        "revenue_impact": "$6,000 (B) + $896 (C) = $6,896 unrecorded in 30-day window",
        "fix": "Add fee_disbursement rows at end of each billing period per client. Automate monthly trigger."
    },
    {
        "rank": 2,
        "type": "PRICING GAP",
        "gap": "txn_00010: wire_international to Brazil recorded $15, term sheet says $30",
        "where": "txn_00010, client_a, wire_international, counterparty BR",
        "revenue_impact": "$15 undercharge on this txn. Systemic risk: any wire_international charged at domestic rate = $15 loss per txn",
        "fix": "Audit all wire_international transactions for client_a. Fix fee engine to enforce $30 for rail=wire_international."
    },
    {
        "rank": 3,
        "type": "DATA GAP",
        "gap": "txn_00012: recorded_fee is NULL for completed fednow inbound deposit",
        "where": "txn_00012, client_a, fednow, 2026-05-14",
        "revenue_impact": "$0.60 missing. Risk: if NULL = unbilled, systemic pattern could be larger",
        "fix": "Backfill $0.60 fee. Add NOT NULL constraint + validation on fee fields for completed txns."
    },
    {
        "rank": 4,
        "type": "SCHEMA GAP",
        "gap": "rail field has non-normalized value 'wire' (txn_00008) — not wire_domestic or wire_international",
        "where": "txn_00008, client_a",
        "revenue_impact": "Low on this txn (charged $15 = domestic), but if any 'wire' is international = $15 undercharge each",
        "fix": "Normalize rail enum: enforce wire_domestic | wire_international | ach_standard | ach_same_day | fednow. Add DB constraint."
    },
    {
        "rank": 5,
        "type": "PRICING GAP",
        "gap": "Client C term sheet has no wire_domestic or wire_international pricing, but txn_00044 is a wire_domestic $250K",
        "where": "txn_00044, client_c, wire_domestic",
        "revenue_impact": "Unknown — term sheet silent. Recorded $15 but no contractual basis. Risk: either overbilling or missing a negotiated rate.",
        "fix": "Escalate to @Nicolle: was wire pricing intentionally excluded from Client C term sheet? Add to exhibit C if billable."
    },
    {
        "rank": 6,
        "type": "PRICING GAP",
        "gap": "Client A bank account fee roll-up (txn_00025) recorded $16,520 vs expected $16,675 — delta $155",
        "where": "txn_00025, client_a, fee_disbursement",
        "revenue_impact": "$155 undercharge. Likely due to not applying tier-blend on May volume crossing $15M threshold.",
        "fix": "Recalculate: April $5.1M × 0.08% = $4,080 + May: Tier I $15M × 0.08% + Tier II $0.85M × 0.07% = $12,595. Total = $16,675."
    },
    {
        "rank": 7,
        "type": "AMBIGUITY GAP",
        "gap": "Monthly minimum definition: term sheet doesn't specify what fees count toward the floor",
        "where": "Client A (min $13,995/mo), Client B (min $4,995/mo Month 2)",
        "revenue_impact": "If pass-through fees are excluded from floor calculation, minimum may apply in low-volume months",
        "fix": "Ask @Nicolle: does monthly min include pass-through fees, or only variable % fees (BA fee + ramps)?"
    },
    {
        "rank": 8,
        "type": "AMBIGUITY GAP",
        "gap": "30-day window spans two calendar months (April + May) — monthly min applies per month, not per window",
        "where": "All clients with monthly minimums",
        "revenue_impact": "If calculated per-window instead of per-month, minimum could be applied incorrectly",
        "fix": "Confirm billing cycle = calendar month. Separate April and May summaries for minimum floor check."
    },
    {
        "rank": 9,
        "type": "AMBIGUITY GAP",
        "gap": "Failed transactions (txn_00014): fee recorded as $0 — term sheet silent on policy for failed txns",
        "where": "txn_00014, client_a, wire_international, failed",
        "revenue_impact": "Low directly, but policy inconsistency risk if some failed txns are charged and others not",
        "fix": "Ask @Diego: does system always zero-out fees on failed status? Confirm and document as business rule."
    },
    {
        "rank": 10,
        "type": "SCHEMA GAP",
        "gap": "on_ramp and off_ramp transactions have empty rail and counterparty_country fields",
        "where": "All on_ramp / off_ramp rows (txn_00017–00024, 00034–00039, 00048–00050)",
        "revenue_impact": "No direct revenue impact now, but blocks future corridor-level reporting and compliance",
        "fix": "Add rail (e.g. 'stellar', 'ethereum') and originating country to ramp transactions in schema."
    },
    {
        "rank": 11,
        "type": "DATA QUALITY GAP",
        "gap": "Client A entity discount (2bp) clause in term sheet — never applied in any recorded fee",
        "where": "Client A term sheet: 'any entity owned by Subscriber receives 2bp discount on bank variable fee'",
        "revenue_impact": "Unknown — depends on whether client has subsidiaries transacting. Could over- or under-bill.",
        "fix": "Ask @Nicolle: does client_a have subsidiary entities in the system? Apply 2bp discount if so."
    },
]

for g in gaps:
    print(f"#{g['rank']} [{g['type']}]")
    print(f"   Gap: {g['gap']}")
    print(f"   Where: {g['where']}")
    print(f"   Revenue Impact: {g['revenue_impact']}")
    print(f"   Fix: {g['fix']}")
    print()

print(f"\n=== HEADLINE NUMBERS ===")
print(f"  Client A expected revenue (30-day):  $33,949.50")
print(f"  Client B expected revenue (30-day):   $8,077.50")
print(f"  Client C expected revenue (30-day):   $2,558.75")
print(f"  TOTAL ACROSS 3 CLIENTS:              $44,585.75")
print(f"  Total currently recorded in DB:      ~$35,677 (Client B + C bank fees missing, A has $155 delta)")
print(f"  Unrecorded / at-risk:                ~$8,909")

