import os

# Absolute path to backend root directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Single shared DB file
FIU_DB = os.path.join(BASE_DIR, "fiu.db")

print(">>> GLOBAL DB:", FIU_DB)
