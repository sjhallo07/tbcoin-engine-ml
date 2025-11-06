from __future__ import annotations

from pathlib import Path

from flask import Flask

from ..utils.config_loader import load_system_config
from .routes import api_blueprint


def create_app(base_dir: Path | None = None) -> Flask:
    """Create and configure the Flask application instance."""
    base = base_dir or Path(__file__).resolve().parents[2]
    config = load_system_config(base)

    app = Flask(__name__)
    app.config["SYSTEM_CONFIG"] = config
    app.register_blueprint(api_blueprint)
    return app
