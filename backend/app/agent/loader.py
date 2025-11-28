import sqlite3
from datetime import datetime
from typing import List, Dict, Any
from app.db_config import FIU_DB as DB_FILE

def _parse_iso(dt_str: str) -> datetime:
    """Parse ISO 8601 datetime string stored in the DB."""
    if dt_str.endswith("Z"):
        dt_str = dt_str[:-1]
    return datetime.fromisoformat(dt_str)


def load_transactions(user_id: str, limit: int = 200) -> List[Dict[str, Any]]:
    """
    Load the most recent transactions for a specific user from the FIU database.

    Returns a list of dicts:
    {
        "amount": float,
        "type": "DEBIT" | "CREDIT",
        "category": str,
        "merchant": str,
        "narration": str,
        "date": datetime
    }
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT amount, txnType, category, merchant, narration, valueDate
        FROM transactions
        WHERE userId = ?
        ORDER BY valueDate DESC
        LIMIT ?
        """,
        (user_id, limit),
    )

    rows = cur.fetchall()
    conn.close()

    txns: List[Dict[str, Any]] = []
    for amount, txn_type, category, merchant, narration, value_date in rows:
        txns.append(
            {
                "amount": float(amount),
                "type": txn_type,
                "category": category or "Uncategorized",
                "merchant": merchant or "",
                "narration": narration or "",
                "date": _parse_iso(value_date),
            }
        )

    return txns
