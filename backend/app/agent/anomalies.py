from typing import List, Dict, Any
from statistics import mean, stdev

# ------------------------------------------------------------
# HELPER: Safe standard deviation
# ------------------------------------------------------------

def _std(values: List[float]) -> float:
    """Standard deviation with safe fallback."""
    if len(values) < 2:
        return 0
    return stdev(values)


# ------------------------------------------------------------
# HELPER: Detect category-level spending baseline
# ------------------------------------------------------------

def _compute_baselines(txns: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Builds a baseline for each category:
    {
        "Food": { "avg": X, "std": Y },
        "Shopping": { "avg": X, "std": Y },
        ...
    }
    """
    buckets = {}

    for t in txns:
        if t["type"] != "DEBIT":
            continue

        cat = t["category"]
        buckets.setdefault(cat, []).append(t["amount"])

    baselines = {}
    for cat, amounts in buckets.items():
        baselines[cat] = {
            "avg": mean(amounts),
            "std": _std(amounts)
        }

    return baselines


# ------------------------------------------------------------
# MAIN ANOMALY DETECTION
# ------------------------------------------------------------

def detect_anomalies(txns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detects transactions whose amount is unusually high
    compared to the user's typical category baseline.

    Returns a list of anomalies:
    {
        "amount": float,
        "category": str,
        "merchant": str,
        "narration": str,
        "reason": str
    }
    """
    anomalies = []

    if not txns:
        return anomalies

    # Step 1 — compute baselines
    baselines = _compute_baselines(txns)

    for t in txns:
        if t["type"] != "DEBIT":
            continue

        cat = t["category"]
        amount = t["amount"]

        if cat not in baselines:
            continue

        avg = baselines[cat]["avg"]
        std = baselines[cat]["std"]

        # If std = 0, skip (means user spends identical amounts)
        if std == 0:
            continue

        # Step 2 — anomaly rule: beyond 2.5 standard deviations
        if amount > avg + 2.5 * std:
            anomalies.append({
                "amount": amount,
                "category": cat,
                "merchant": t["merchant"],
                "narration": t["narration"],
                "date": t["date"].isoformat(),
                "reason": f"Unusually high compared to your typical {cat} spending."
            })

    return anomalies
