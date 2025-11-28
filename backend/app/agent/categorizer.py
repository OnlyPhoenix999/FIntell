from typing import Dict, Any

# ------------------------------------------------------------
# CATEGORY KEYWORDS (India-focused)
# ------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Food": [
        "ZOMATO", "SWIGGY", "KFC", "MCDONALD", "DOMINOS",
        "PIZZA", "BURGER", "EATFIT", "FAASOS", "BEHROOZ",
        "BIRYANI", "RESTAURANT"
    ],
    "Groceries": [
        "BIG BASKET", "BLINKIT", "ZEpto", "SPENCER", "MORE",
        "DMART", "FRESH", "NATURES BASKET", "GROCER"
    ],
    "Transport": [
        "UBER", "OLA", "AUTORICKSHAW", "METRO", "TRAIN",
        "IRCTC", "RED BUS", "FUEL", "PETROL", "DIESEL"
    ],
    "Shopping": [
        "AMAZON", "FLIPKART", "MYNTRA", "AJIO", "NYKAA",
        "TATA CLIQ", "SHOPPING"
    ],
    "Bills": [
        "ELECTRICITY", "WATER BILL", "GAS BILL", "BESCOM",
        "RECHARGE", "POSTPAID", "PREPAID", "DTH", "BILLDESK"
    ],
    "Subscriptions": [
        "NETFLIX", "PRIME", "AMAZON PRIME", "SPOTIFY",
        "APPLE MUSIC", "YOUTUBE", "HOTSTAR", "SONY LIV",
        "ZEE5", "GAANA", "WYNK"
    ],
    "Entertainment": [
        "BOOKMYSHOW", "MOVIE", "THEATRE", "CINEMA",
        "PVR", "INOX"
    ],
    "Travel": [
        "MAKEMYTRIP", "GOIBIBO", "AGODA", "AIR INDIA",
        "INDIGO", "VISTARA", "YATRA", "TRAVEL"
    ],
    "Health": [
        "PHARMA", "APOLLO", "1MG", "PHARMACY", "DIAGNOSTIC",
        "HOSPITAL", "CLINIC", "MEDICINE"
    ],
    "Education": [
        "COURSERA", "UDACITY", "UDEMY", "BYJUS", "UNACADEMY",
        "VEDANTU", "EDUCATION", "SCHOOL", "COLLEGE"
    ],
    "Investments": [
        "GROWW", "ZERODHA", "UPSTOX", "MUTUAL FUND",
        "SIP", "COIN", "STOCK", "EQUITY"
    ],
    "Rent": [
        "RENT", "NO BROKER", "NOBROKER", "HOUSING", "PROP"
    ],
    "Salary": [
        "SALARY", "PAYROLL", "CREDIT SALARY", "HR", "PAYOUT"
    ],
    "Refunds": [
        "REFUND", "REVERSAL", "REVERSED"
    ]
}

DEFAULT_CATEGORY = "Others"


# ------------------------------------------------------------
# CLEAN STRING HELPER
# ------------------------------------------------------------

def _clean(s: str) -> str:
    return (s or "").upper()


# ------------------------------------------------------------
# MAIN CATEGORY DETECTION
# ------------------------------------------------------------

def categorize_transaction(txn: Dict[str, Any]) -> str:
    """
    Categorizes a single transaction based on merchant and narration.
    Returns a category string.
    """
    merchant = _clean(txn.get("merchant", ""))
    narration = _clean(txn.get("narration", ""))

    # Merge both fields into a searchable blob
    blob = f"{merchant} {narration}"

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in blob:
                return category

    # Special rules
    if txn["type"] == "CREDIT":
        # Salary inference
        if "SALARY" in blob or "PAYROLL" in blob:
            return "Salary"
        # Refund detection
        if "REFUND" in blob or "REVERSAL" in blob:
            return "Refunds"

    return DEFAULT_CATEGORY


# ------------------------------------------------------------
# BATCH CATEGORIZATION
# ------------------------------------------------------------

def categorize_batch(txns: list) -> list:
    """
    Categorizes a list of transactions in place.
    Returns the same list with updated category labels.
    """
    for t in txns:
        t["category"] = categorize_transaction(t)
    return txns
