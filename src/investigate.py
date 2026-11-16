"""Drill down on a single flagged claim for analyst review.

Usage:
    python -m src.investigate --claim-id CLM00001234
"""
from __future__ import annotations

import argparse

import pandas as pd

from src.config import DATA_DIR


def investigate(claim_id: str, scored_path: str | None = None) -> dict:
    """Return a structured explanation for why a claim scored as it did."""
    path = scored_path or (DATA_DIR / "scored_claims.csv")
    df = pd.read_csv(path)

    row = df.loc[df["claim_id"] == claim_id]
    if row.empty:
        raise ValueError(f"Claim {claim_id} not found in {path}")
    claim = row.iloc[0]

    provider_claims = df.loc[df["provider_id"] == claim["provider_id"]]
    return {
        "claim_id": claim_id,
        "provider_id": claim["provider_id"],
        "specialty": claim["provider_specialty"],
        "billed_amount": float(claim["billed_amount"]),
        "paid_amount": float(claim["paid_amount"]),
        "cpt_code": int(claim["cpt_code"]),
        "final_risk_score": float(claim["final_risk_score"]),
        "ml_probability": float(claim["ml_probability"]),
        "rule_score": float(claim["rule_score"]),
        "rules_fired": claim["rule_reasons"],
        "flagged": bool(claim["flagged"]),
        "provider_context": {
            "total_claims": int(len(provider_claims)),
            "imaging_ratio": round(
                float(provider_claims["is_imaging"].mean()), 3),
            "avg_billed": round(
                float(provider_claims["billed_amount"].mean()), 2),
            "flagged_claims": int(provider_claims["flagged"].sum()),
        },
    }


def _print_report(r: dict) -> None:
    print(f"\n{'='*52}\nINVESTIGATION REPORT: {r['claim_id']}\n{'='*52}")
    print(f"Provider {r['provider_id']} ({r['specialty']})")
    print(f"CPT {r['cpt_code']} | billed ${r['billed_amount']:.2f} | "
          f"paid ${r['paid_amount']:.2f}")
    print(f"\nFinal risk score : {r['final_risk_score']:.3f} "
          f"({'FLAGGED' if r['flagged'] else 'not flagged'})")
    print(f"  ML probability : {r['ml_probability']:.3f}")
    print(f"  Rule score     : {r['rule_score']:.3f}")
    print(f"  Rules fired    : {r['rules_fired']}")
    pc = r["provider_context"]
    print(f"\nProvider context: {pc['total_claims']} claims, "
          f"imaging ratio {pc['imaging_ratio']}, "
          f"avg billed ${pc['avg_billed']:.2f}, "
          f"{pc['flagged_claims']} flagged claims")
    print("=" * 52)


def main() -> None:
    parser = argparse.ArgumentParser(description="Investigate a claim.")
    parser.add_argument("--claim-id", required=True)
    args = parser.parse_args()
    _print_report(investigate(args.claim_id))


if __name__ == "__main__":
    main()
