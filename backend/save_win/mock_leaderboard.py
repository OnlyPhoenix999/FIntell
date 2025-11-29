# save_win/mock_leaderboard.py

import sqlite3
import os
import random

SAVEWIN_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "savewin.db"))


def load_users():
    """Load all users with their balance + tokens."""
    conn = sqlite3.connect(SAVEWIN_DB)
    cur = conn.cursor()

    cur.execute("SELECT userId, balance, tokens FROM wallet")
    rows = cur.fetchall()

    conn.close()

    return [
        {"userId": user, "balance": balance, "tokens": tokens}
        for user, balance, tokens in rows
    ]


def simulate_quiz_game(users, num_players=10):
    """
    Randomly selects players and assigns quiz scores.
    Higher balance could give slightly better odds (skill effect).
    """

    if len(users) == 0:
        print("No users found in savewin.db")
        return []

    # Pick random subset of players
    players = random.sample(users, min(num_players, len(users)))

    leaderboard = []

    for player in players:
        base_skill = random.randint(1, 70)
        balance_bonus = int(player["balance"] // 500)  # more savings = more knowledge?
        final_score = base_skill + random.randint(0, balance_bonus)

        leaderboard.append({
            "userId": player["userId"],
            "score": final_score,
            "balance": player["balance"],
            "tokens": player["tokens"]
        })

    # Sort highest score first
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return leaderboard


def print_leaderboard(lb):
    if not lb:
        print("Leaderboard is empty.")
        return

    print("\n==================== LEADERBOARD ====================")
    for idx, row in enumerate(lb, start=1):
        print(f"{idx}. {row['userId']} | Score: {row['score']} | Balance: ₹{row['balance']} | Tokens: {row['tokens']}")
    print("=====================================================\n")


def main():
    print("\n>>> Generating Mock Save&Win Leaderboard...\n")

    users = load_users()
    leaderboard = simulate_quiz_game(users, num_players=random.randint(5, 15))
    print_leaderboard(leaderboard)

    return leaderboard


if __name__ == "__main__":
    main()
