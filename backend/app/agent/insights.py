from typing import List, Dict, Any
from datetime import datetime, timedelta

# ------------------------------------------------------------
# SUMMARY GENERATION
# ------------------------------------------------------------

def generate_summary(txns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    High-level 30-day financial summary.
    """
    if not txns:
        return {
            "total_spent_30d": 0,
            "total_received_30d": 0,
            "largest_category": None,
            "largest_merchant": None,
            "daily_avg_spend": 0,
        }

    # 30-day filter
    now = datetime.utcnow()
    days_30_txns = [
        t for t in txns
        if (now - t["date"]).days <= 30
    ]

    total_spent = sum(t["amount"] for t in days_30_txns if t["type"] == "DEBIT")
    total_received = sum(t["amount"] for t in days_30_txns if t["type"] == "CREDIT")

    by_category = {}
    by_merchant = {}

    for t in days_30_txns:
        if t["type"] != "DEBIT":
            continue

        by_category[t["category"]] = by_category.get(t["category"], 0) + t["amount"]
        by_merchant[t["merchant"]] = by_merchant.get(t["merchant"], 0) + t["amount"]

    largest_category = max(by_category, key=by_category.get) if by_category else None
    largest_merchant = max(by_merchant, key=by_merchant.get) if by_merchant else None

    return {
        "total_spent_30d": round(total_spent, 2),
        "total_received_30d": round(total_received, 2),
        "largest_category": largest_category,
        "largest_merchant": largest_merchant,
        "daily_avg_spend": round(total_spent / 30, 2),
    }


# ------------------------------------------------------------
# PATTERN DETECTION (simple but effective)
# ------------------------------------------------------------

def detect_patterns(txns: List[Dict[str, Any]]) -> List[str]:
    patterns = []

    if not txns:
        return patterns

    # Weekend pattern
    weekend = sum(t["amount"] for t in txns if t["type"] == "DEBIT" and t["date"].weekday() >= 5)
    weekday = sum(t["amount"] for t in txns if t["type"] == "DEBIT" and t["date"].weekday() < 5)

    if weekend > weekday:
        patterns.append("You tend to spend more on weekends.")
    else:
        patterns.append("You spend more during weekdays.")

    # Evening spending
    evening = sum(t["amount"] for t in txns if t["type"] == "DEBIT" and t["date"].hour >= 18)
    if evening > sum(t["amount"] for t in txns) * 0.35:
        patterns.append("Your evening spending is higher than usual.")

    # Food habits
    food_total = sum(t["amount"] for t in txns if t["category"] == "Food")
    if food_total > 2000:
        patterns.append("Your food expenses are consistently high.")

    return patterns


# ------------------------------------------------------------
# ALERTS (Based on thresholds + anomalies)
# ------------------------------------------------------------

def generate_alerts(txns: List[Dict[str, Any]], anomalies: List[Dict[str, Any]]) -> List[str]:
    alerts = []

    # High Category Spending Alerts
    food_spend = sum(t["amount"] for t in txns if t["category"] == "Food")
    if food_spend > 3000:
        alerts.append("Food spending is significantly higher than usual.")

    transport_spend = sum(t["amount"] for t in txns if t["category"] == "Transport")
    if transport_spend > 2000:
        alerts.append("Transport costs seem unusually high.")

    # Add anomaly alerts
    for a in anomalies:
        alerts.append(f"Unusual spending detected: {a['merchant']} - ₹{a['amount']}")

    return alerts


# ------------------------------------------------------------
# RECOMMENDATIONS
# ------------------------------------------------------------

def generate_recommendations(summary, subs):
    recs = []

    # Largest category spending advice
    if summary.get("largest_category") == "Food":
        recs.append("Consider reducing food delivery orders to improve savings.")
    elif summary.get("largest_category") == "Shopping":
        recs.append("Shopping is your biggest expense this month — you may want to set a budget.")

    # Subscription load
    if subs:
        total_subs = sum(s["amount"] for s in subs)
        if total_subs > 1000:
            recs.append(f"Your monthly subscriptions cost ₹{total_subs}. Consider removing unused services.")

    return recs


# ------------------------------------------------------------
# FINAL INSIGHTS PACKAGE
# ------------------------------------------------------------

def generate_insights(
    txns: List[Dict[str, Any]],
    subs: List[Dict[str, Any]],
    anomalies: List[Dict[str, Any]],
    prediction: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Combines all intelligence into a single insights JSON.
    """
    summary = generate_summary(txns)
    patterns = detect_patterns(txns)
    alerts = generate_alerts(txns, anomalies)
    recommendations = generate_recommendations(summary, subs)

    return {
        "summary": summary,
        "patterns": patterns,
        "alerts": alerts,
        "subscriptions": subs,
        "anomalies": anomalies,
        "prediction": prediction,
        "recommendations": recommendations,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
