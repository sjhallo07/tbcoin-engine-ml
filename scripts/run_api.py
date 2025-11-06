"""Tiny runner that starts the FastAPI app with uvicorn.

Use this script when launching the API from the repository root. It calls
uvicorn.run which keeps the process alive in environments where `python -m
uvicorn` may exit unexpectedly.
"""
import os
import sys
import uvicorn


def main():
    # Ensure repository root is on sys.path so imports like `api.main` work
    repo_root = os.path.dirname(os.path.dirname(__file__))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()
