"""Diagnostics: call /health and /status in-process using TestClient.

This avoids starting a network server and quickly validates route wiring and
startup logging.
"""
import os
import sys

# Ensure repo root on sys.path
repo_root = os.path.dirname(os.path.dirname(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from fastapi.testclient import TestClient

from api.main import app


def main():
    client = TestClient(app)
    h = client.get("/health")
    s = client.get("/status")
    print("GET /health ->", h.status_code)
    try:
        print(h.json())
    except Exception:
        print(h.text)

    print("GET /status ->", s.status_code)
    try:
        print(s.json())
    except Exception:
        print(s.text)


if __name__ == "__main__":
    main()
