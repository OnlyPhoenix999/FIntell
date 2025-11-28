import requests
import random
import time
from datetime import datetime
from uuid import uuid4

AA_BASE = "http://localhost:8000/aa"
ACCOUNT_ID = "ACC123001234"
VUA = "maverick@aa"  # default VUA for testing

HEADERS = {
    "client_id": "demo",
    "client_secret": "demo",
    "Content-Type": "application/json"
}

# ------------------------------------------------------------
# REALISTIC MERCHANT GROUPS
# ------------------------------------------------------------

SPEND_CATEGORIES = {
    "Food": [
        ("SWIGGY", "UPI", "Food Delivery - Swiggy"),
        ("ZOMATO", "UPI", "Food Delivery - Zomato"),
        ("STARBUCKS", "CARD", "Starbucks Coffee"),
        ("DOMINOS", "UPI", "Dominos Pizza"),
        ("KFC", "UPI", "KFC Order")
    ],
    "Groceries": [
        ("ZEPTO", "UPI", "Zepto Groceries"),
        ("BLINKIT", "UPI", "Blinkit Order"),
        ("BIG BASKET", "CARD", "BB Groceries"),
    ],
    "Transport": [
        ("UBER", "CARD", "Uber Ride"),
        ("OLA", "UPI", "OLA Ride"),
        ("RED BUS", "UPI", "Bus Booking"),
        ("IRCTC", "CARD", "Railway Ticket")
    ],
    "Shopping": [
        ("AMAZON", "CARD", "Amazon Shopping"),
        ("FLIPKART", "CARD", "Flipkart Purchase"),
        ("NYKAA", "UPI", "Nykaa Order")
    ],
    "Bills": [
        ("BESCOM", "UPI", "Electricity Bill"),
        ("AIRTEL", "CARD", "Airtel Recharge"),
        ("JIO", "UPI", "Jio Recharge"),
        ("BROADBAND", "UPI", "Internet Bill")
    ],
    "Subscriptions": [
        ("NETFLIX", "CARD", "Netflix Subscription"),
        ("SPOTIFY", "CARD", "Spotify Subscription"),
        ("YOUTUBE", "UPI", "YouTube Premium"),
        ("AMAZON PRIME", "CARD", "Amazon Prime")
    ]
}


# ------------------------------------------------------------
# CREATE ACCOUNT IF MISSING
# ------------------------------------------------------------

def ensure_account_exists():
    """
    Mock AA has no account-checking API,
    so we try adding the account; if exists, AA returns harmless message.
    """

    payload = {
        "vua": VUA,
        "accountId": ACCOUNT_ID
    }

    print("📌 Ensuring account exists:", ACCOUNT_ID)

    r = requests.post(f"{AA_BASE}/mock/bank/add-account", json=payload, headers=HEADERS)

    if r.status_code == 200:
        print("✅ Account ready in AA:", r.text)
    else:
        print("⚠️ Unexpected response while adding account:", r.text)


# ------------------------------------------------------------
# GENERATE RANDOM TRANSACTION
# ------------------------------------------------------------

def get_random_transaction():
    category = random.choice(list(SPEND_CATEGORIES.keys()))
    merchant, mode, narration = random.choice(SPEND_CATEGORIES[category])

    # realistic amount ranges
    if category == "Food":
        amount = random.uniform(150, 900)
    elif category == "Groceries":
        amount = random.uniform(200, 2000)
    elif category == "Transport":
        amount = random.uniform(80, 2000)
    elif category == "Shopping":
        amount = random.uniform(300, 5000)
    elif category == "Bills":
        amount = random.uniform(100, 2500)
    elif category == "Subscriptions":
        amount = random.uniform(99, 799)

    return {
        "accountId": ACCOUNT_ID,
        "amount": round(amount, 2),
        "narration": narration,
        "txnType": "DEBIT",
        "days_ago": 0,
        "mode": mode,
        "merchant": merchant,
        "category": category
    }


# ------------------------------------------------------------
# PUSH TRANSACTION TO MOCK AA
# ------------------------------------------------------------

def push_transaction(tx):
    r = requests.post(
        f"{AA_BASE}/mock/bank/add-transaction",
        json=tx,
        headers=HEADERS
    )

    print(f"→ Sent: {tx['merchant']} | ₹{tx['amount']} | {tx['category']}")
    print("  Response:", r.text)


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

def run_realtime_generator(interval_seconds=20):
    ensure_account_exists()

    print("\n🚀 Real-time Transaction Generator Started")
    print(f"Generating new transactions every {interval_seconds} seconds...")
    print("Press CTRL+C to stop.\n")

    while True:
        tx = get_random_transaction()
        push_transaction(tx)
        time.sleep(interval_seconds)


# ------------------------------------------------------------
# ENTRY
# ------------------------------------------------------------

if __name__ == "__main__":
    run_realtime_generator(interval_seconds=20)
