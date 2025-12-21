from __future__ import annotations

from typing import Dict, Any

try:
    import wandb  # type: ignore
except Exception:  # pragma: no cover
    wandb = None


class TrainingMonitor:
    def __init__(self, project: str = "token-movement-llm"):
        self.project = project
        if wandb is not None:
            try:
                wandb.init(project=project)
            except Exception:
                pass

    def log_training_progress(self, epoch: int, metrics: Dict[str, Any]) -> None:
        if wandb is not None:
            try:
                wandb.log({"epoch": epoch, **metrics})
            except Exception:
                pass
        # Always write to local log file
        print({"epoch": epoch, **metrics})
