import sqlite3
import time
from typing import List, Dict, Any

from app.agent.loader import load_transactions
from app.agent.categorizer import categorize_batch
from app.agent.subscriptions import detect_subscriptions
from app.agent.anomalies import detect_anomalies
from app.agent.predictor import predict_future
from app.agent.insights import generate_insights
from app.db_config import FIU_DB

# ------------------------------------------------------------
# HELPER: Load all user IDs
# ------------------------------------------------------------

def load_all_users() -> List[str]:
    """
    Returns list of all userIds that have synced transactions.
    """
    conn = sqlite3.connect(FIU_DB)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT userId FROM transactions")
    users = [row[0] for row in cur.fetchall()]

    conn.close()
    return users


# ------------------------------------------------------------
# HELPER: Save insights into DB
# ------------------------------------------------------------

def save_insights(user_id: str, insights: Dict[str, Any]):
    conn = sqlite3.connect(FIU_DB)
    cur = conn.cursor()

    # Create table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS insights (
            userId TEXT,
            generatedAt TEXT,
            insightsJson TEXT
        );
    """)

    cur.execute("""
        INSERT INTO insights (userId, generatedAt, insightsJson)
        VALUES (?, ?, ?)
    """, (
        user_id,
        insights["generated_at"],
        str(insights)   # stored as string (simple storage)
    ))

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# MAIN AGENT LOOP (single run)
# ------------------------------------------------------------

def run_agent_once():
    print("\n[AGENT] Starting agent run...")

    users = load_all_users()
    if not users:
        print("[AGENT] No users found. Nothing to do.")
        return

    print(f"[AGENT] Found {len(users)} users.")

    for user_id in users:
        print(f"\n[AGENT] Processing user: {user_id}")

        # 1. Load & categorize transactions
        txns = load_transactions(user_id)
        if not txns:
            print("[AGENT] No transactions for this user.")
            continue

        txns = categorize_batch(txns)

        # 2. Detect subscriptions
        subs = detect_subscriptions(txns)

        # 3. Detect anomalies
        anomalies = detect_anomalies(txns)

        # 4. Predict future
        prediction = predict_future(txns)

        # 5. Generate insights
        insights = generate_insights(txns, subs, anomalies, prediction)

        # 6. Save insights per user
        save_insights(user_id, insights)

        print(f"[AGENT] Insights generated and saved for user {user_id}")

    print("\n[AGENT] Agent run completed.")


# ------------------------------------------------------------
# CONTINUOUS MODE (optional auto-loop)
# ------------------------------------------------------------

def run_agent_forever(interval_seconds: int = 60):
    print(f"[AGENT] Continuous mode activated (every {interval_seconds}s).")
    while True:
        run_agent_once()
        time.sleep(interval_seconds)


# ------------------------------------------------------------
# DIRECT EXECUTION
# ------------------------------------------------------------

if __name__ == "__main__":
    # Run once if script is executed directly
    run_agent_once()
