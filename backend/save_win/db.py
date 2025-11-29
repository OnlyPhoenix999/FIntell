# save_win/db.py

import sqlite3
import os
from datetime import datetime

# Path for the Save & Win module DB
SAVEWIN_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "savewin.db"))


def init_savewin_db():
    """Initializes the Save & Win database with required tables."""
    conn = sqlite3.connect(SAVEWIN_DB)
    cur = conn.cursor()

    # Wallet table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wallet (
            userId TEXT PRIMARY KEY,
            balance REAL DEFAULT 0,
            tokens INTEGER DEFAULT 0,
            last_updated TEXT
        );
    """)

    # Transactions table (for deposits)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userId TEXT,
            amount REAL,
            timestamp TEXT
        );
    """)

    conn.commit()
    conn.close()
    print(">>> Save&Win DB initialized at:", SAVEWIN_DB)


def update_wallet(user_id: str, amount: float):
    """
    Adds money to user's wallet and awards tokens.
    1 token per ₹100 saved.
    """
    conn = sqlite3.connect(SAVEWIN_DB)
    cur = conn.cursor()

    now = datetime.utcnow().isoformat() + "Z"
    tokens_awarded = int(amount // 100)

    # Insert or update wallet
    cur.execute("""
        INSERT INTO wallet (userId, balance, tokens, last_updated)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(userId) DO UPDATE SET
            balance = balance + excluded.balance,
            tokens = tokens + excluded.tokens,
            last_updated = excluded.last_updated;
    """, (user_id, amount, tokens_awarded, now))

    # Log transaction
    cur.execute("""
        INSERT INTO transactions (userId, amount, timestamp)
        VALUES (?, ?, ?)
    """, (user_id, amount, now))

    conn.commit()
    conn.close()

    return tokens_awarded
