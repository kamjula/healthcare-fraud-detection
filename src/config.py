"""Central configuration: paths and loading the fraud-rules YAML."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

# Project root = two levels up from this file (src/config.py -> project/)
ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))
MODEL_DIR = Path(os.getenv("MODEL_DIR", ROOT / "models"))
CONFIG_DIR = ROOT / "config"

RULES_PATH = Path(os.getenv("RULES_PATH", CONFIG_DIR / "fraud_rules.yaml"))
MODEL_PATH = MODEL_DIR / "fraud_xgb.joblib"

# Radiology / imaging CPT code range used to detect imaging overutilization.
IMAGING_CPT_MIN = 70000
IMAGING_CPT_MAX = 79999


@lru_cache(maxsize=1)
def load_rules(path: str | os.PathLike | None = None) -> dict:
    """Load and cache the fraud-rules configuration."""
    rules_path = Path(path) if path else RULES_PATH
    with open(rules_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def ensure_dirs() -> None:
    """Create the data/ and models/ directories if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
