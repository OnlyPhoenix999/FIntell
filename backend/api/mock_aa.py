from fastapi import FastAPI, Header
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import random
import sqlite3
import json
import os

DB_FILE = "mockaa.db"

# ------------------------------
# Initialize SQLite
# ------------------------------

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        accountId TEXT PRIMARY KEY,
        vua TEXT,
        fiType TEXT,
        fiSubType TEXT,
        fipId TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        txnId TEXT PRIMARY KEY,
        accountId TEXT,
        amount REAL,
        txnType TEXT,
        valueDate TEXT,
        txnDate TEXT,
        narration TEXT,
        reference TEXT,
        balance REAL,
        mode TEXT,
        merchant TEXT,
        category TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS consents (
        consentHandle TEXT PRIMARY KEY,
        consentId TEXT,
        status TEXT,
        requestJson TEXT,
        created TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        sessionId TEXT PRIMARY KEY,
        consentHandle TEXT,
        created TEXT,
        format TEXT
    );
    """)

    conn.commit()
    conn.close()


init_db()
app = FastAPI(title="Mock AA with SQLite Persistence")


# -----------------------------------------------------------
# Models
# -----------------------------------------------------------

class ConsentDetailCustomer(BaseModel):
    id: str


class ConsentDetail(BaseModel):
    Customer: ConsentDetailCustomer
    consentStart: str
    consentExpiry: str
    consentMode: str
    fetchType: str
    DataLife: Dict[str, Any]
    Frequency: Dict[str, Any]
    DataRange: Dict[str, str]
    AccountIds: List[str] = []


class ConsentRequest(BaseModel):
    ver: str = "1.0"
    timestamp: str
    txnid: str
    ConsentDetail: ConsentDetail


class SessionRequest(BaseModel):
    consentId: str
    format: str = "json"


class AddAccount(BaseModel):
    vua: str
    accountId: str
    fiType: str = "DEPOSIT"
    fiSubType: str = "SAVINGS"
    fipId: str = "MOCKBANK01"


class AddTransaction(BaseModel):
    accountId: str
    amount: float
    narration: str
    txnType: str
    days_ago: int = 0
    mode: str = "UPI"
    merchant: str = "Mock Merchant"
    category: str = "General"


# -----------------------------------------------------------
# Helpers
# -----------------------------------------------------------

def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def parse_iso(dt_str):
    return datetime.fromisoformat(dt_str.replace("Z", ""))


# -----------------------------------------------------------
# STEP 1 — Create Consent
# -----------------------------------------------------------

@app.post("/aa/consents")
def create_consent(req: ConsentRequest):
    consent_handle = str(uuid4())
    consent_id = str(uuid4())

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO consents (consentHandle, consentId, status, requestJson, created)
        VALUES (?, ?, ?, ?, ?)
    """, (consent_handle, consent_id, "PENDING", json.dumps(req.dict()), now_iso()))
    conn.commit()
    conn.close()

    return {
        "ver": req.ver,
        "timestamp": now_iso(),
        "txnid": req.txnid,
        "ConsentHandle": consent_handle,
    }


# -----------------------------------------------------------
# STEP 2 — Poll Consent Status
# -----------------------------------------------------------

@app.get("/aa/consents/{handle}/status")
def consent_status(handle: str):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT consentId, status FROM consents WHERE consentHandle=?", (handle,))
    row = cur.fetchone()

    if not row:
        return {"ConsentStatus": "INVALID"}

    consentId = row[0]

    # auto-approve
    cur.execute("UPDATE consents SET status='ACTIVE' WHERE consentHandle=?", (handle,))
    conn.commit()
    conn.close()

    return {
        "ver": "1.0",
        "timestamp": now_iso(),
        "ConsentStatus": "ACTIVE",
        "ConsentId": consentId
    }


# -----------------------------------------------------------
# STEP 3 — Create Session
# -----------------------------------------------------------

@app.post("/aa/sessions")
def create_session(req: SessionRequest):

    consent_id = req.consentId

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT consentHandle FROM consents WHERE consentId=?", (consent_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return {"error": "Invalid consentId"}

    consent_handle = row[0]

    session_id = str(uuid4())

    cur.execute("""
        INSERT INTO sessions (sessionId, consentHandle, created, format)
        VALUES (?, ?, ?, ?)
    """, (session_id, consent_handle, now_iso(), req.format))

    conn.commit()
    conn.close()

    return {
        "ver": "1.0",
        "timestamp": now_iso(),
        "sessionId": session_id,
    }


# -----------------------------------------------------------
# STEP 4 — Fetch Data
# -----------------------------------------------------------

@app.get("/aa/sessions/{session_id}/fetch")
def fetch_data(session_id: str):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Validate session
    cur.execute("SELECT consentHandle FROM sessions WHERE sessionId=?", (session_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return {"error": "Invalid sessionId"}

    consent_handle = row[0]

    # Load consent JSON
    cur.execute("SELECT requestJson FROM consents WHERE consentHandle=?", (consent_handle,))
    consent_json = cur.fetchone()[0]

    consent_req = json.loads(consent_json)
    consent_detail = consent_req["ConsentDetail"]
    vua = consent_detail["Customer"]["id"]
    dr_from = parse_iso(consent_detail["DataRange"]["from"])
    dr_to = parse_iso(consent_detail["DataRange"]["to"])

    # Find accounts for VUA
    cur.execute("SELECT accountId, fiType, fiSubType, fipId FROM accounts WHERE vua=?", (vua,))
    acc_rows = cur.fetchall()

    FI_list = []

    for acc in acc_rows:
        acc_id, fiType, fiSubType, fipId = acc

        # Fetch transactions
        cur.execute("SELECT txnId, amount, txnType, valueDate, txnDate, narration, reference, balance, mode, merchant, category FROM transactions WHERE accountId=?", (acc_id,))
        rows = cur.fetchall()

        filtered = []
        for r in rows:
            value_dt = parse_iso(r[3])
            if dr_from <= value_dt <= dr_to:
                filtered.append(r)

        FI_list.append({
            "account": {
                "fiType": fiType,
                "fiSubType": fiSubType,
                "maskedAccNumber": acc_id[-4:],
                "fipId": fipId,
            },
            "transactions": [
                {
                    "txnId": r[0],
                    "amount": r[1],
                    "txnType": r[2],
                    "valueDate": r[3],
                    "txnDate": r[4],
                    "narration": r[5],
                    "reference": r[6],
                    "balance": r[7],
                    "mode": r[8],
                    "merchant": r[9],
                    "category": r[10],
                }
                for r in filtered
            ]
        })

    conn.close()

    return {
        "ver": "1.0",
        "timestamp": now_iso(),
        "FI": FI_list
    }


# -----------------------------------------------------------
# Mock FIP endpoints with persistence
# -----------------------------------------------------------

@app.post("/aa/mock/bank/add-account")
def mock_add_account(data: AddAccount):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO accounts (accountId, vua, fiType, fiSubType, fipId)
        VALUES (?, ?, ?, ?, ?)
    """, (data.accountId, data.vua, data.fiType, data.fiSubType, data.fipId))
    conn.commit()
    conn.close()

    return {"message": "Account added"}


@app.post("/aa/mock/bank/add-transaction")
def mock_add_transaction(data: AddTransaction):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT accountId FROM accounts WHERE accountId=?", (data.accountId,))
    if not cur.fetchone():
        conn.close()
        return {"error": "Account not found"}

    # Load existing transactions to compute balance
    cur.execute("SELECT amount, txnType FROM transactions WHERE accountId=?", (data.accountId,))
    rows = cur.fetchall()

    balance = 100000.0
    for amt, ttype in rows:
        if ttype == "DEBIT":
            balance -= amt
        else:
            balance += amt

    if data.txnType == "DEBIT":
        balance -= data.amount
    else:
        balance += data.amount

    value_dt = (datetime.utcnow() - timedelta(days=data.days_ago)).isoformat() + "Z"

    txn_id = str(uuid4())

    cur.execute("""
        INSERT INTO transactions
        (txnId, accountId, amount, txnType, valueDate, txnDate, narration, reference, balance, mode, merchant, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (txn_id, data.accountId, data.amount, data.txnType, value_dt, value_dt,
          data.narration, f"MOCKREF{random.randint(10000,99999)}",
          balance, data.mode, data.merchant, data.category))

    conn.commit()
    conn.close()

    return {"message": "Transaction added", "txnId": txn_id}
