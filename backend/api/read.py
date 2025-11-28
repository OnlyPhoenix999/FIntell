import sqlite3

DB_FILE = "mockaa.db"

def read_latest_transactions(limit=5):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    query = f"""
    SELECT txnId, accountId, amount, txnType, valueDate, narration, merchant, category
    FROM transactions
    ORDER BY valueDate DESC
    LIMIT {limit};
    """

    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    return rows


if __name__ == "__main__":
    txns = read_latest_transactions()

    print("\nLatest Transactions:\n")
    for t in txns:
        print(f"TxnID: {t[0]}")
        print(f"Account: {t[1]}")
        print(f"Amount: {t[2]}  Type: {t[3]}")
        print(f"Date:   {t[4]}")
        print(f"Narration: {t[5]}")
        print(f"Merchant:  {t[6]}")
        print(f"Category:  {t[7]}")
        print("-" * 40)
