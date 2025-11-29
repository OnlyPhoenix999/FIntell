# save_win/generate_results.py

import sqlite3
import os
from math import ceil
from mock_leaderboard import main as generate_leaderboard

SAVEWIN_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "savewin.db"))


def get_prize_pool():
    """Sum of all interest earned by all users."""
    conn = sqlite3.connect(SAVEWIN_DB)
    cur = conn.cursor()

    cur.execute("SELECT SUM(interest) FROM interest_log")
    total_interest = cur.fetchone()[0] or 0

    conn.close()

    print(f"\n>>> Total Prize Pool from Interest: ₹{round(total_interest, 2)}\n")
    return round(total_interest, 2)


def split_prize_pool(leaderboard, pool):
    if pool <= 0:
        print("No prize pool available (interest = 0).")
        return []

    n = len(leaderboard)
    winners_count = max(1, ceil(n * 0.10))

    winners = leaderboard[:winners_count]

    # Weighted distribution (1/rank)
    weights = [1 / (i + 1) for i in range(winners_count)]
    weight_total = sum(weights)

    results = []
    for i, winner in enumerate(winners):
        share = round(pool * (weights[i] / weight_total), 2)
        results.append({
            "rank": i + 1,
            "userId": winner["userId"],
            "score": winner["score"],
            "prize": share
        })

    return results


def print_results(results):
    print("\n==================== PAYOUT RESULTS ====================")
    for r in results:
        print(f"Rank {r['rank']} | {r['userId']} | Score {r['score']} | Prize: ₹{r['prize']}")
    print("========================================================\n")


def main():
    lb = generate_leaderboard()
    pool = get_prize_pool()
    results = split_prize_pool(lb, pool)
    print_results(results)


if __name__ == "__main__":
    main()
