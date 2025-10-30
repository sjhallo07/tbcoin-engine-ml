"""Use FastAPI's TestClient to call /status without starting a network server.

This helps validate imports and route wiring locally in CI or dev environments.
"""
import os
import sys

# Ensure repo root on sys.path so `api` imports resolve when running from diagnostics
repo_root = os.path.dirname(os.path.dirname(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from fastapi.testclient import TestClient

from api.main import app


def main():
    client = TestClient(app)
    resp = client.get("/status")
    print("status code:", resp.status_code)
    print(resp.json())


if __name__ == "__main__":
    main()
