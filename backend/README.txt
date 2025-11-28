How to Run the System
Step 0 - Install requirements
pip install -r requirements.txt

Step 1 — Start the Mock AA server
cd backend
venv\Scripts\activate
python -m uvicorn api.mock_aa:app --reload

Step 2 — Start the FIU backend

Open a new terminal, then:

cd backend
venv\Scripts\activate
python -m uvicorn app.fiu_backend:app --reload --port 9000

Step 3 — Start the real-time transaction generator

Open another new terminal:

cd backend
venv\Scripts\activate
python .\api\mock_generator.py

Step 4 — Test the flow

Sync from AA → FIU:

http://localhost:9000/fiu/sync/maverick/maverick@aa

View transactions stored in FIU:

http://localhost:9000/fiu/transactions/maverick

View generated insights:

http://localhost:9000/fiu/insights/maverick