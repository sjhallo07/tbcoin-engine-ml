from fastapi.testclient import TestClient
import sys
import os

# Ensure repo root on sys.path
repo_root = os.path.dirname(os.path.dirname(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from api.main import app

client = TestClient(app)

resp_h = client.get("/health")
resp_s = client.get("/status")

print("GET /health ->", resp_h.status_code)
print(resp_h.json())
print()
print("GET /status ->", resp_s.status_code)
print(resp_s.json())
