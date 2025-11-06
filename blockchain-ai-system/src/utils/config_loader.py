from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Mapping

import yaml


class ConfigLoader:
    """Load YAML configuration files with environment variable interpolation."""

    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path

    def load(self, relative_path: str) -> Mapping[str, Any]:
        config_path = self._base_path.joinpath(relative_path)
        with config_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return self._resolve_env_tokens(data)

    def _resolve_env_tokens(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {key: self._resolve_env_tokens(value) for key, value in data.items()}
        if isinstance(data, list):
            return [self._resolve_env_tokens(item) for item in data]
        if isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            return os.getenv(env_var)
        return data


def load_system_config(base_dir: Path) -> Dict[str, Any]:
    loader = ConfigLoader(base_dir)
    return {
        "networks": loader.load("config/blockchain_networks.yaml"),
        "models": loader.load("config/ai_models.yaml"),
    }
