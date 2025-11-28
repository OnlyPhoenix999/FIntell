import requests
import time
import uuid
from datetime import datetime, timedelta

# ------------------------
# CONFIG
# ------------------------
BASE_URL = "http://api.finvu.in/ConnectHub/V1/"
CLIENT_ID = "fp_test_871938b1a6381aedc8330d7f95151a9e40904894"
CLIENT_SECRET = "4d2667140ba7dec4c1440d1f455a382238e6fc3732e1344d09c3a3c276bdb0f6ff566d69"

# Helper – sandbox headers
def headers():
    return {
        "Content-Type": "application/json",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

# ------------------------
# STEP 1 — CREATE CONSENT
# ------------------------
def create_consent():
    consent_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    payload = {
        "ver": "1.0",
        "txnid": consent_id,
        "timestamp": now.isoformat() + "Z",
        "ConsentDetail": {
            "consentStart": now.isoformat() + "Z",
            "consentExpiry": (now + timedelta(days=30)).isoformat() + "Z",
            "consentMode": "STORE",
            "fetchType": "PERIODIC",
            "DataLife": { "unit": "MONTH", "value": 3 },
            "Frequency": { "unit": "DAY", "value": 1 },
            "DataRange": {
                "from": (now - timedelta(days=120)).isoformat() + "Z",
                "to": now.isoformat() + "Z"
            },
            "AccountIds": [], 
        }
    }

    print("\nCreating Consent…")
    r = requests.post(f"{BASE_URL}/consents", json=payload, headers=headers())
    print("Consent Response:", r.text)
    data = r.json()

    return data["ConsentHandle"]

# ------------------------
# STEP 2 — POLL CONSENT STATUS
# ------------------------
def wait_for_consent(consent_handle):
    print("\nWaiting for user to approve consent… (sandbox auto-approves)")

    while True:
        url = f"{BASE_URL}/consents/{consent_handle}/status"
        r = requests.get(url, headers=headers())
        resp = r.json()
        print("Status:", resp["ConsentStatus"])

        if resp["ConsentStatus"] == "ACTIVE":
            print("Consent Approved!")
            return resp["ConsentId"]

        time.sleep(2)

# ------------------------
# STEP 3 — CREATE DATA SESSION
# ------------------------
def create_session(consent_id):
    payload = {
        "ConsentId": consent_id,
        "DataFormat": "JSON"
    }

    print("\nCreating Data Session…")
    r = requests.post(f"{BASE_URL}/sessions", json=payload, headers=headers())
    print("Session Response:", r.text)

    data = r.json()
    return data["SessionId"]

# ------------------------
# STEP 4 — FETCH TRANSACTIONS
# ------------------------
def fetch_data(session_id):
    print("\nFetching Financial Data…")
    url = f"{BASE_URL}/sessions/{session_id}/fetch"
    r = requests.get(url, headers=headers())

    print("Raw Data:", r.text)
    return r.json()

# ------------------------
# RUN FLOW
# ------------------------
if __name__ == "__main__":
    handle = create_consent()
    consent_id = wait_for_consent(handle)
    session_id = create_session(consent_id)
    data = fetch_data(session_id)

    print("\n----------------- CLEAN TRANSACTIONS -----------------")

    # Extract sample Tx from sandbox-format data
    for fi in data.get("FI", []):
        txns = fi.get("transactions", [])
        for t in txns:
            print(f"{t['timestamp']} | {t['type']} | ₹{t['amount']} | {t['narration']}")
