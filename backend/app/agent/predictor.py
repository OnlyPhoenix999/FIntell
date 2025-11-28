from datetime import datetime
from typing import List, Dict, Any
import statistics

# ------------------------------------------------------------
# HELPER: Group transactions by month
# ------------------------------------------------------------

def _group_by_month(txns: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Returns:
    {
        "2025-01": 12234,
        "2025-02": 15678,
        ...
    }
    """
    monthly = {}

    for t in txns:
        if t["type"] != "DEBIT":
            continue

        dt = t["date"]
        key = f"{dt.year}-{dt.month:02d}"

        monthly[key] = monthly.get(key, 0) + t["amount"]

    return monthly


# ------------------------------------------------------------
# SIMPLE TREND PREDICTION
# ------------------------------------------------------------

def _predict_next_value(values: List[float]) -> float:
    """
    Basic trend extrapolation:
    - If 1 value: return it
    - If 2 values: linear projection
    - If 3+ values: weighted moving trend + slope
    """
    if not values:
        return 0.0
    
    if len(values) == 1:
        return values[0]

    if len(values) == 2:
        # Simple linear extrapolation
        diff = values[1] - values[0]
        return values[-1] + diff

    # For 3+, compute slope as average difference
    diffs = [values[i] - values[i-1] for i in range(1, len(values))]
    slope = statistics.mean(diffs)

    # Weighted moving average for stability
    wma = (values[-1] * 0.6) + (values[-2] * 0.3) + (values[-3] * 0.1)

    return wma + slope


# ------------------------------------------------------------
# CATEGORY-LEVEL TREND PREDICTION
# ------------------------------------------------------------

def _predict_category(txns: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Predict spend per category for next month.
    """
    categories = {}

    # Group by category per month
    monthly_cat = {}

    for t in txns:
        if t["type"] != "DEBIT":
            continue

        dt = t["date"]
        key = f"{dt.year}-{dt.month:02d}"

        cat = t["category"]
        monthly_cat.setdefault(cat, {})
        monthly_cat[cat][key] = monthly_cat[cat].get(key, 0) + t["amount"]

    # Predict per category
    for cat, monthly_data in monthly_cat.items():
        values = [monthly_data[m] for m in sorted(monthly_data)]
        predicted = _predict_next_value(values)
        categories[cat] = round(predicted, 2)

    return categories


# ------------------------------------------------------------
# PUBLIC API: PREDICT FUTURE SPENDING
# ------------------------------------------------------------

def predict_future(txns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predicts:
    - next month's total spending
    - category-level predictions
    - average monthly spending (historical)
    - trend (rising / falling)
    """
    # Group by month
    monthly = _group_by_month(txns)

    if not monthly:
        return {
            "predicted_total_next_month": 0,
            "average_monthly_spend": 0,
            "trend": "flat",
            "category_predictions": {}
        }

    # Sort chronologically
    months = sorted(monthly.keys())
    values = [monthly[m] for m in months]

    avg_spend = statistics.mean(values)
    prediction = _predict_next_value(values)

    # Trend detection
    if len(values) >= 2:
        if values[-1] > values[-2] * 1.1:
            trend = "rising"
        elif values[-1] < values[-2] * 0.9:
            trend = "falling"
        else:
            trend = "flat"
    else:
        trend = "flat"

    cat_predictions = _predict_category(txns)

    return {
        "predicted_total_next_month": round(prediction, 2),
        "average_monthly_spend": round(avg_spend, 2),
        "trend": trend,
        "category_predictions": cat_predictions
    }
