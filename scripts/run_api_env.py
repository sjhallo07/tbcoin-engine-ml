"""Run the FastAPI app with specific environment variables set for the process.

This helper sets SIMULATE_HTTP_POST=false by default so the running server will
perform real POSTs when `/relay` is called. Use only in local development with
controlled mock receivers.
"""
import os
import sys
import pathlib
import uvicorn


def main():
    # Force real POST behavior for this process
    os.environ.setdefault("SIMULATE_HTTP_POST", "false")

    # Ensure repo root is on sys.path and cwd so `import api` works when started
    # via Start-Process from another working directory.
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    os.chdir(repo_root)
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    # You can also set TEST_POST_URL here if you want a different default
    # os.environ.setdefault("TEST_POST_URL", "http://127.0.0.1:3000/messages")

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
