"""Run example prompts through the AIDecisionEngine and FastAPI endpoint.

This script demonstrates using "prompts" (feature dicts) and prints outputs
from both the local engine and the API route (TestClient) for comparison.
"""
import sys
import pathlib

# Ensure repo root is on sys.path so imports from project root work when this
# script runs from scripts/ directory.
repo_root = pathlib.Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ai_decision_engine import AIDecisionEngine
from fastapi.testclient import TestClient
from api.main import app
import json


PROMPTS = [
    {"price": 100, "trend": 0.02, "volume": 1000},
    {"price": 50, "trend": -0.05, "volume": 500},
    {"price": 75, "trend": 0.0, "volume": 200},
]


def run_local_engine(prompts):
    engine = AIDecisionEngine()
    engine.load_model()
    results = []
    for p in prompts:
        d = engine.predict(p)
        results.append(d)
    return results


def run_api_prompts(prompts):
    client = TestClient(app)
    results = []
    for p in prompts:
        resp = client.post('/api/v1/solana/decision', json={"features": p})
        if resp.status_code == 200:
            results.append(resp.json())
        else:
            results.append({"error": f"status {resp.status_code}", "body": resp.text})
    return results


def main():
    print("Running prompts through local engine...")
    local = run_local_engine(PROMPTS)
    print(json.dumps(local, ensure_ascii=False, indent=2))

    print("\nRunning prompts through API endpoint (/api/v1/solana/decision)...")
    api_results = run_api_prompts(PROMPTS)
    print(json.dumps(api_results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
