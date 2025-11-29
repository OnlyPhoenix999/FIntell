import sqlite3
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from fastapi import FastAPI
import os
from save_win.db import init_savewin_db
from save_win.endpoints import router as savewin_router

# ------------------------------------------------------------
# CONFIG — Always use backend/fiu.db
# ------------------------------------------------------------
from app.db_config import FIU_DB

AA_BASE = "http://localhost:8000/aa"
CLIENT_ID = "demo"
CLIENT_SECRET = "demo"

from app.agent.agent_loop import run_agent_once

app = FastAPI(title="FIU Backend + Agent")

# ------------------------------------------------------------
# DATABASE INIT
# ------------------------------------------------------------

def init_db():
    conn = sqlite3.connect(FIU_DB)
    cur = conn.cursor()

    # Transaction table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            txnId TEXT PRIMARY KEY,
            userId TEXT,
            accountId TEXT,
            amount REAL,
            txnType TEXT,
            valueDate TEXT,
            narration TEXT,
            merchant TEXT,
            category TEXT
        );
    """)

    # Insights table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS insights (
            userId TEXT,
            generatedAt TEXT,
            insightsJson TEXT
        );
    """)

    conn.commit()
    conn.close()


init_db()


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def now_iso():
    return datetime.utcnow().isoformat() + "Z"


# ------------------------------------------------------------
# AA API CALLS (treat AA as external)
# ------------------------------------------------------------

def aa_create_consent(vua: str):
    # Use a single "now" for consistency
    now = datetime.utcnow()
    now_iso_str = now.isoformat() + "Z"

    payload = {
        "ver": "1.0",
        "txnid": str(uuid.uuid4()),
        "timestamp": now_iso_str,
        "ConsentDetail": {
            "Customer": {"id": vua},
            "consentStart": now_iso_str,
            # give a long expiry so you don't have to re-consent frequently
            "consentExpiry": (now + timedelta(days=365)).isoformat() + "Z",
            "consentMode": "STORE",
            "fetchType": "PERIODIC",
            "DataLife": {"unit": "MONTH", "value": 12},
            "Frequency": {"unit": "DAY", "value": 1},
            # Fetch last 90 days up to *now*
            "DataRange": {
                "from": (now - timedelta(days=90)).isoformat() + "Z",
                "to": now_iso_str
            },
            "AccountIds": []  # we're using all accounts for the VUA
        }
    }

    r = requests.post(
        f"{AA_BASE}/consents",
        json=payload,
        headers={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )

    # ---- defensive checks ----
    if r.status_code != 200:
        raise RuntimeError(f"AA /consents failed: {r.status_code} {r.text}")

    data = r.json()
    if "ConsentHandle" not in data:
        raise RuntimeError(f"AA /consents did not return ConsentHandle: {data}")

    return data["ConsentHandle"]

def aa_wait_for_consent(handle: str, timeout_seconds: int = 30):
    start = time.time()
    while True:
        r = requests.get(
            f"{AA_BASE}/consents/{handle}/status",
            headers={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
        )

        if r.status_code != 200:
            raise RuntimeError(f"AA /consents/{handle}/status failed: {r.status_code} {r.text}")

        data = r.json()
        status = data.get("ConsentStatus")

        if status == "ACTIVE":
            consent_id = data.get("ConsentId")
            if not consent_id:
                raise RuntimeError(f"AA returned ACTIVE but no ConsentId: {data}")
            return consent_id

        if status == "INVALID":
            raise RuntimeError(f"Consent became INVALID for handle {handle}: {data}")

        if time.time() - start > timeout_seconds:
            raise TimeoutError(f"Timed out waiting for consent {handle} to become ACTIVE. Last response: {data}")

        time.sleep(1)

def aa_create_session(consent_id: str):
    payload = {"consentId": consent_id, "format": "json"}

    r = requests.post(
        f"{AA_BASE}/sessions",
        json=payload,
        headers={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    )

    if r.status_code != 200:
        raise RuntimeError(f"AA /sessions failed: {r.status_code} {r.text}")

    data = r.json()
    if "sessionId" not in data:
        raise RuntimeError(f"AA /sessions did not return sessionId: {data}")

    return data["sessionId"]

def aa_fetch_data(session_id: str):
    r = requests.get(
        f"{AA_BASE}/sessions/{session_id}/fetch",
        headers={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET}
    )

    if r.status_code != 200:
        raise RuntimeError(f"AA /sessions/{session_id}/fetch failed: {r.status_code} {r.text}")

    data = r.json()

    # If AA returned an error payload, surface it instead of silently returning empty data
    if "error" in data:
        raise RuntimeError(f"AA fetch error for session {session_id}: {data}")

    return data

# ------------------------------------------------------------
# SAVE DATA TO FIU DB
# ------------------------------------------------------------

def save_fi_data(user_id, fi_response):
    conn = sqlite3.connect(FIU_DB)
    cur = conn.cursor()

    for fi in fi_response.get("FI", []):
        masked = fi["account"]["maskedAccNumber"]

        for t in fi["transactions"]:
            cur.execute("""
                INSERT OR IGNORE INTO transactions
                (txnId, userId, accountId, amount, txnType, valueDate, narration, merchant, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t["txnId"],
                user_id,
                masked,
                t["amount"],
                t["txnType"],
                t["valueDate"],
                t["narration"],
                t["merchant"],
                t["category"]
            ))

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# FIU API ENDPOINTS
# ------------------------------------------------------------

@app.on_event("startup")
def startup():
    init_savewin_db()

app.include_router(savewin_router)

@app.get("/fiu/sync/{user_id}/{vua}")
def sync_from_aa(user_id: str, vua: str):
    """
    Main AA → FIU → Database sync endpoint.
    Called by mobile app when user links their VUA.
    """
    handle = aa_create_consent(vua)
    consent_id = aa_wait_for_consent(handle)
    session_id = aa_create_session(consent_id)
    fi_data = aa_fetch_data(session_id)

    save_fi_data(user_id, fi_data)

    return {"message": "Synced successfully", "userId": user_id}


@app.get("/fiu/transactions/{user_id}")
def get_user_transactions(user_id: str):
    """
    Returns all transactions for a specific user.
    """
    conn = sqlite3.connect(FIU_DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT txnId, accountId, amount, txnType, valueDate, narration, merchant, category
        FROM transactions
        WHERE userId = ?
        ORDER BY valueDate DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "txnId": r[0],
            "accountId": r[1],
            "amount": r[2],
            "txnType": r[3],
            "valueDate": r[4],
            "narration": r[5],
            "merchant": r[6],
            "category": r[7],
        }
        for r in rows
    ]


# ------------------------------------------------------------
# INSIGHTS API
# ------------------------------------------------------------

def fetch_insights_for_user(user_id: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(FIU_DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT generatedAt, insightsJson
        FROM insights
        WHERE userId = ?
        ORDER BY generatedAt DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    insights_list = []
    for generatedAt, insightsJson in rows:
        try:
            insights_dict = eval(insightsJson)
            insights_list.append({
                "generatedAt": generatedAt,
                "insights": insights_dict
            })
        except:
            continue

    return insights_list


@app.get("/fiu/insights/{user_id}")
def get_latest_insights(user_id: str):
    insights_list = fetch_insights_for_user(user_id)

    if not insights_list:
        return {
            "userId": user_id,
            "latest": None,
            "message": "No insights found for this user."
        }

    return {
        "userId": user_id,
        "latest": insights_list[0]
    }


@app.get("/fiu/insights/{user_id}/history")
def get_insights_history(user_id: str):
    return {
        "userId": user_id,
        "history": fetch_insights_for_user(user_id)
    }


# ------------------------------------------------------------
# BACKGROUND AGENT THREAD
# ------------------------------------------------------------

def agent_runner():
    while True:
        print("[AGENT THREAD] Running agent...")
        try:
            run_agent_once()
        except Exception as e:
            print("[AGENT THREAD] ERROR:", e)

        time.sleep(30)  # every 30 seconds


@app.on_event("startup")
def start_background_agent():
    thread = threading.Thread(target=agent_runner, daemon=True)
    thread.start()
    print("[SERVER] Agent thread started.")
