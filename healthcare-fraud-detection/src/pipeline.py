"""End-to-end pipeline: prepare -> features -> rules -> train -> score.

Usage:
    python -m src.pipeline --train      # generate (if needed), train, score
    python -m src.pipeline              # score using an existing model
"""
from __future__ import annotations

import argparse

import pandas as pd

from src.config import DATA_DIR, MODEL_PATH, ensure_dirs
from src.data.generate_synthetic import generate
from src.data.prepare import prepare
from src.features.engineer import build_features
from src.models.score import score
from src.models.train import train
from src.rules.engine import apply_rules


def _load_or_generate() -> pd.DataFrame:
    csv = DATA_DIR / "sample_claims.csv"
    if csv.exists():
        return pd.read_csv(csv)
    print("[pipeline] no data found, generating synthetic claims...")
    ensure_dirs()
    df = generate()
    df.to_csv(csv, index=False)
    return df


def run(do_train: bool) -> pd.DataFrame:
    raw = _load_or_generate()
    clean = prepare(raw)
    feats = build_features(clean)
    flagged = apply_rules(feats)

    if do_train or not MODEL_PATH.exists():
        if "is_fraud" not in feats.columns:
            raise SystemExit(
                "Cannot train: dataset has no 'is_fraud' label column.")
        print("[pipeline] training model...")
        metrics = train(feats)
        print(f"[pipeline] ROC-AUC: {metrics['roc_auc']}  "
              f"(train={metrics['n_train']}, test={metrics['n_test']})")
        print(metrics["report"])

    scored = score(flagged)
    out = DATA_DIR / "scored_claims.csv"
    scored.to_csv(out, index=False)

    n_flagged = int(scored["flagged"].sum())
    print(f"[pipeline] scored {len(scored):,} claims; "
          f"{n_flagged:,} flagged -> {out}")
    print("\nTop 10 highest-risk claims:")
    cols = ["claim_id", "provider_id", "final_risk_score",
            "ml_probability", "rule_score", "rule_reasons"]
    print(scored[cols].head(10).to_string(index=False))
    return scored


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the fraud pipeline.")
    parser.add_argument("--train", action="store_true",
                        help="(re)train the model before scoring")
    args = parser.parse_args()
    run(args.train)


if __name__ == "__main__":
    main()
