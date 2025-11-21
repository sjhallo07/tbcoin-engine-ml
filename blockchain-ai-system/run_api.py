"""Run the FastAPI server for the Blockchain AI System.

Usage:
  python run_api.py --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
   
   
    args = parser.parse_args()
    

    project_root = Path(__file__).resolve().parent
    # Ensure `src` is on the import path
    sys.path.insert(0, str(project_root / "src"))

    import uvicorn  # type: ignore

    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    uvicorn.run("api.server:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
