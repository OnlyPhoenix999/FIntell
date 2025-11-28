from datetime import datetime, timedelta
from typing import List, Dict, Any
import statistics

# ------------------------------------------------------------
# HELPER: Check if two amounts are "similar"
# ------------------------------------------------------------

def _amount_similar(a: float, b: float, tolerance: float = 0.20) -> bool:
    """
    Returns True if amounts are within ±20%, enough for subscription jitter.
    Example: Netflix ₹649 → sometimes shows as ₹648.99, etc.
    """
    if a == 0 or b == 0:
        return False
    return abs(a - b) / max(a, b) <= tolerance


# ------------------------------------------------------------
# HELPER: Determine billing cycle
# ------------------------------------------------------------

def _detect_cycle(dates: List[datetime]) -> str:
    """
    Analyze gaps between payments. Returns Monthly/Quarterly/Yearly/Unknown.
    """
    if len(dates) < 2:
        return "Unknown"

    gaps = []
    for i in range(1, len(dates)):
        diff = (dates[i] - dates[i-1]).days
        gaps.append(diff)

    avg_gap = statistics.mean(gaps)

    if 26 <= avg_gap <= 34:
        return "Monthly"
    if 85 <= avg_gap <= 95:
        return "Quarterly"
    if 350 <= avg_gap <= 380:
        return "Yearly"

    return "Unknown"


# ------------------------------------------------------------
# MAIN LOGIC: DETECT SUBSCRIPTION GROUPS
# ------------------------------------------------------------

def detect_subscriptions(txns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect recurring transactions by grouping merchants with repeated,
    similar amounts spaced consistently over time.
    """
    subscriptions = []

    # STEP 1 — group by merchant
    merchant_groups = {}
    for t in txns:
        if t["type"] != "DEBIT":
            continue

        m = t["merchant"].upper().strip()
        if not m:
            continue

        merchant_groups.setdefault(m, []).append(t)

    # STEP 2 — analyze each merchant
    for merchant, group in merchant_groups.items():
        if len(group) < 2:
            continue  # Not enough occurrences to be a subscription

        # Sort by date
        group = sorted(group, key=lambda x: x["date"])

        # Extract amounts and dates
        amounts = [t["amount"] for t in group]
        dates = [t["date"] for t in group]

        # STEP 3 — check amount similarity
        similar_amounts = all(_amount_similar(amounts[i], amounts[i-1]) for i in range(1, len(amounts)))
        if not similar_amounts:
            continue

        # STEP 4 — detect cycle type
        cycle = _detect_cycle(dates)
        if cycle == "Unknown":
            continue

        last_payment = dates[-1]

        # STEP 5 — predict next payment date
        if cycle == "Monthly":
            next_date = last_payment + timedelta(days=30)
        elif cycle == "Quarterly":
            next_date = last_payment + timedelta(days=90)
        elif cycle == "Yearly":
            next_date = last_payment + timedelta(days=365)
        else:
            next_date = None

        subscriptions.append({
            "merchant": merchant,
            "amount": round(statistics.mean(amounts), 2),
            "cycle": cycle,
            "last_payment": last_payment.isoformat(),
            "next_payment": next_date.isoformat() if next_date else None,
            "confidence": 0.9  # starter confidence for now
        })

    return subscriptions
