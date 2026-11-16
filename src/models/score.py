"""Score claims: combine ML fraud probability with the rule score."""
from __future__ import annotations

import pandas as pd

from src.config import load_rules
from src.models.train import load_model


def score(df: pd.DataFrame, rules_cfg: dict | None = None) -> pd.DataFrame:
    """Add ml_probability, rule_score (assumed present), and final_risk_score.

    `df` must already have engineered features and rule columns applied.
    """
    cfg = rules_cfg or load_rules()
    bundle = load_model()
    model, features = bundle["model"], bundle["features"]

    df = df.copy()
    df["ml_probability"] = model.predict_proba(df[features])[:, 1].round(4)

    ml_w = cfg["scoring"]["ml_weight"]
    rule_w = cfg["scoring"]["rule_weight"]
    threshold = cfg["scoring"]["flag_threshold"]

    df["final_risk_score"] = (
        ml_w * df["ml_probability"] + rule_w * df["rule_score"]).round(4)
    df["flagged"] = (df["final_risk_score"] >= threshold).astype(int)
    return df.sort_values("final_risk_score", ascending=False)
