"""Score claims with the trained model.

If no trained model is present, returns zero probabilities so the hybrid
pipeline can still operate on rules alone.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import pandas as pd

from src.config import settings
from src.features.engineering import build_feature_matrix


def predict_proba(df: pd.DataFrame, model_path: Optional[Union[str, Path]] = None) -> pd.Series:
    model_path = Path(model_path or settings.model_path)
    if not model_path.exists():
        return pd.Series(0.0, index=df.index)

    from xgboost import XGBClassifier  # imported lazily

    model = XGBClassifier()
    model.load_model(str(model_path))
    X = build_feature_matrix(df)
    proba = model.predict_proba(X)[:, 1]
    return pd.Series(proba, index=df.index)
