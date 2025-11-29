# save_win/interest_simulator.py

import sqlite3
import os
from datetime import datetime

SAVEWIN_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "savewin.db"))

ANNUAL_INTEREST_RATE = 0.06
MONTHS = 4


def simulate_interest():
    """Applies 4 months of interest and logs interest for prize pool."""
    conn = sqlite3.connect(SAVEWIN_DB)
    cur = conn.cursor()

    # Create interest_log table if missing
    cur.execute("""
        CREATE TABLE IF NOT EXISTS interest_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId TEXT,
            interest REAL,
            timestamp TEXT
        );
    """)

    cur.execute("SELECT userId, balance FROM wallet")
    rows = cur.fetchall()

    if not rows:
        print("No wallets found.")
        conn.close()
        return

    print("\n>>> Running 4-month interest simulation...\n")

    for user_id, balance in rows:
        if balance <= 0:
            continue

        interest = round(balance * (ANNUAL_INTEREST_RATE * (MONTHS / 12)), 2)
        new_balance = balance + interest
        now = datetime.utcnow().isoformat() + "Z"

        # Update balance
        cur.execute("""
            UPDATE wallet SET balance = ? WHERE userId = ?
        """, (new_balance, user_id))

        # Log interest for prize pool
        cur.execute("""
            INSERT INTO interest_log (userId, interest, timestamp)
            VALUES (?, ?, ?)
        """, (user_id, interest, now))

        print(f"{user_id}: Interest ₹{interest} → New Balance ₹{new_balance}")

    conn.commit()
    conn.close()
    print("\n>>> Interest simulation completed.\n")


if __name__ == "__main__":
    simulate_interest()
