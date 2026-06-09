"""Load claims data from CSV or Parquet files."""
from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from src.data.schema import validate_claims


def load_claims(path: Union[str, Path]) -> pd.DataFrame:
    """Load a claims file and return a validated DataFrame."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Claims file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".parquet":
        df = pd.read_parquet(path)
    elif suffix in {".csv", ".txt"}:
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported file type '{suffix}'. Use .csv or .parquet.")

    return validate_claims(df)
