from fastapi import FastAPI
import sqlite3
from typing import List, Dict, Any
import threading
import time
from app.db_config import FIU_DB

from app.agent.agent_loop import run_agent_once

app = FastAPI(title="FIU Backend + Agent")


# ------------------------------------------------------------
# BACKGROUND AGENT THREAD
# ------------------------------------------------------------

def agent_runner():
    """
    Runs forever, executing agent once every X seconds.
    """
    while True:
        print("[AGENT THREAD] Running agent...")
        try:
            run_agent_once()
        except Exception as e:
            print("[AGENT THREAD] Error:", e)

        time.sleep(30)  # run agent every 30 seconds (adjust as needed)


# ------------------------------------------------------------
# STARTUP EVENT — starts agent on server boot
# ------------------------------------------------------------

@app.on_event("startup")
def start_background_agent():
    thread = threading.Thread(target=agent_runner, daemon=True)
    thread.start()
    print("[SERVER] Agent thread started.")


# ------------------------------------------------------------
# DB helper
# ------------------------------------------------------------

def fetch_insights_for_user(user_id: str) -> List[Dict[str, Any]]:
    """
    Returns ALL insights for a user as Python dicts.
    Latest first.
    """
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
            # Stored as string, so eval safely
            insights_dict = eval(insightsJson)
            insights_list.append({
                "generatedAt": generatedAt,
                "insights": insights_dict
            })
        except Exception:
            continue

    return insights_list


# ------------------------------------------------------------
# API: Get latest insights for user
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# API: Get full insights history for user (optional)
# ------------------------------------------------------------

@app.get("/fiu/insights/{user_id}/history")
def get_insights_history(user_id: str):
    insights_list = fetch_insights_for_user(user_id)

    return {
        "userId": user_id,
        "count": len(insights_list),
        "history": insights_list
    }
