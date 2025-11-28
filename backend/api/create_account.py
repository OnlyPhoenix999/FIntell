import requests

BASE_URL = "http://localhost:8000/aa"
HEADERS = {"Content-Type": "application/json"}

data = {
    "vua": "maverick@mockaa",
    "accountId": "ACC123001234",
    "fiType": "DEPOSIT",
    "fiSubType": "SAVINGS",
    "fipId": "MOCKBANK01"
}

r = requests.post(f"{BASE_URL}/mock/bank/add-account", json=data, headers=HEADERS)
print(r.text)
