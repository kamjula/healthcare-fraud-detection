"""Hybrid scoring pipeline: rules + ML model -> ranked, flagged claims."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import pandas as pd

from src.config import settings
from src.data.loader import load_claims
from src.features.engineering import add_claim_features
from src.models.predict import predict_proba
from src.rules.engine import RuleEngine


def score_claims(
    claims_path: Union[str, Path],
    rules_path: Optional[Union[str, Path]] = None,
    model_path: Optional[Union[str, Path]] = None,
    flag_threshold: Optional[float] = None,
) -> pd.DataFrame:
    """Score every claim, returning the DataFrame sorted by fraud_score desc."""
    rules_path = rules_path or settings.rules_path
    flag_threshold = settings.flag_threshold if flag_threshold is None else flag_threshold

    df = load_claims(claims_path)
    df = add_claim_features(df)

    engine = RuleEngine.from_yaml(rules_path)
    scored = engine.evaluate(df)

    rule_w = float(engine.scoring.get("rule_weight", 0.5))
    model_w = float(engine.scoring.get("model_weight", 0.5))
    denom = (rule_w + model_w) or 1.0

    scored["model_score"] = predict_proba(df, model_path=model_path).values
    scored["fraud_score"] = (rule_w * scored["rule_score"] + model_w * scored["model_score"]) / denom
    scored["flagged"] = scored["fraud_score"] >= flag_threshold

    return scored.sort_values("fraud_score", ascending=False).reset_index(drop=True)


def flagged_only(scored: pd.DataFrame) -> pd.DataFrame:
    """Return just the flagged claims."""
    return scored[scored["flagged"]].copy()
