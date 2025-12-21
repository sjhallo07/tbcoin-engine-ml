#!/usr/bin/env python3
"""CLI runner for the Token History Training Pipeline.

Usage:
  python train_token_movement_model.py

Reads config from ml_models/token_history/config.yaml and executes a minimal training run.
"""
from __future__ import annotations

import yaml
from pathlib import Path

from ml_models.token_history import TokenHistoryTrainingPipeline, TrainingConfig


def main() -> None:
    cfg_path = Path("ml_models/token_history/config.yaml")
    if cfg_path.exists():
        config_dict = yaml.safe_load(cfg_path.read_text())
        cfg = config_dict.get("training_config", {})
    else:
        cfg = {}
    pipeline = TokenHistoryTrainingPipeline(cfg)
    model, metrics = pipeline.run_full_training()
    pipeline.save_results(model, metrics)
    print("Training finished. Metrics:", metrics)


if __name__ == "__main__":
    main()
