# save_win/simulator_deposits.py

import requests
import random
import time

BASE_URL = "http://localhost:9000/save_win/deposit"
USER_IDS = ["user1", "user2", "user3", "user4", "maverick"]


def simulate_deposits(iterations=100):
    """
    Calls deposit endpoint 50–100 times with random users and deposit amounts.
    """

    for i in range(iterations):
        user_id = random.choice(USER_IDS)
        amount = random.choice([50, 100, 150, 200, 250, 500, 1000])

        url = f"{BASE_URL}/{user_id}"
        payload = {"amount": amount}

        try:
            r = requests.post(url, params=payload)
            print(f"[{i+1}] Deposited ₹{amount} -> {user_id} | Response:", r.json())

        except Exception as e:
            print(f"[ERROR] Failed for {user_id}: {e}")



if __name__ == "__main__":
    print(">>> Starting Save&Win Deposit Simulator...")
    simulate_deposits(iterations=random.randint(50, 100))
    print(">>> Simulation Complete.")
