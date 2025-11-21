#!/usr/bin/env python3
"""Project setup utility for the AI Blockchain Predictive System."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> bool:
    """Execute a shell command and report the result."""
    print(f"[setup] Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=check)
        return True
    except subprocess.CalledProcessError as exc:
        print(f"[setup] Command failed with return code {exc.returncode}: {cmd}")
        return False


def setup_project() -> None:
    """Prepare a local development environment for the project."""
    project_root = Path(__file__).resolve().parent.parent

    print("[setup] Configuring AI Blockchain Predictive System...")

    if sys.version_info < (3, 9):
        print("[setup] Python 3.9 or higher is required.")
        sys.exit(1)

    print("[setup] Creating virtual environment...")
    if not run_command("python -m venv venv"):
        print("[setup] Failed to create virtual environment.")
        sys.exit(1)

    if os.name == "nt":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"

    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        print("[setup] Installing dependencies...")
        if not run_command(f"{pip_cmd} install -r {requirements_file}"):
            print("[setup] Failed to install dependencies.")
            sys.exit(1)
    else:
        print("[setup] requirements.txt not found; skipping dependency installation.")

    env_file = project_root / ".env"
    env_template = project_root / ".env.template"
    if not env_file.exists() and env_template.exists():
        env_file.write_text(env_template.read_text())
        print("[setup] Created .env from template; update the values before running services.")

    init_script = project_root / "scripts" / "init_database.py"
    if init_script.exists():
        print("[setup] Initialising database (if supported)...")
        if not run_command(f"{python_cmd} -m scripts.init_database", check=False):
            print("[setup] Database initialisation reported an issue; inspect the logs above.")
    else:
        print("[setup] scripts/init_database.py not found; skipping database initialisation.")

    print("[setup] Setup completed successfully.")
    print()
    print("Next steps:")
    print("1. Update the .env file with the required API keys and configuration values.")
    print("2. Use docker compose or the provided scripts to start local services if needed.")
    print("3. Launch the API (for example: uvicorn main:app --reload).")
    print("4. Visit http://localhost:8000/docs for the interactive API documentation.")


if __name__ == "__main__":
    setup_project()
