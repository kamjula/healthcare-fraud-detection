"""Command-line interface for the healthcare fraud detection pipeline.

Examples:
    python -m src.cli score data/sample_claims.csv
    python -m src.cli train data/sample_claims.csv
    python -m src.cli investigate data/sample_claims.csv C0006
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.models.train import train
from src.pipeline.scoring import flagged_only, score_claims

_SUMMARY_COLS = ["claim_id", "provider_npi", "patient_id", "fraud_score", "rule_score", "model_score"]


def _triggered_rules(row) -> list[str]:
    triggered = []
    for col in row.index:
        if col.startswith("rule_") and not col.endswith("_weight") and col != "rule_score":
            if row[col] == 1:
                triggered.append(col[len("rule_"):])
    return triggered


def _cmd_score(args) -> None:
    scored = score_claims(args.claims_file, flag_threshold=args.threshold)
    out = Path(args.output)
    scored.to_csv(out, index=False)
    flagged = flagged_only(scored)
    print(f"Scored {len(scored)} claims. Flagged {len(flagged)} for review.")
    print(f"Full results written to: {out}\n")
    if not flagged.empty:
        print(flagged[_SUMMARY_COLS].head(20).to_string(index=False))


def _cmd_train(args) -> None:
    path = train(args.claims_file, model_path=args.model_output)
    print(f"Model trained and saved to: {path}")


def _cmd_investigate(args) -> None:
    scored = score_claims(args.claims_file)
    match = scored[scored["claim_id"] == str(args.claim_id)]
    if match.empty:
        print(f"Claim {args.claim_id} not found.")
        return
    rec = match.iloc[0]
    print(f"Claim {args.claim_id}")
    print(f"  Provider: {rec['provider_npi']}   Patient: {rec['patient_id']}")
    print(f"  Billed: ${rec['billed_amount']:.2f}   CPT: {rec['cpt_code']}   Units: {rec['units']}")
    print(
        f"  Fraud score: {rec['fraud_score']:.3f} "
        f"(rules {rec['rule_score']:.3f}, model {rec['model_score']:.3f})"
    )
    triggered = _triggered_rules(rec)
    print(f"  Triggered rules: {', '.join(triggered) if triggered else 'none'}")
    print(f"  Flagged: {'YES' if rec['flagged'] else 'no'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Healthcare fraud detection pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    s = sub.add_parser("score", help="Score a claims file and write results")
    s.add_argument("claims_file")
    s.add_argument("--output", default="scored_claims.csv")
    s.add_argument("--threshold", type=float, default=None)
    s.set_defaults(func=_cmd_score)

    t = sub.add_parser("train", help="Train the ML model on labelled claims")
    t.add_argument("claims_file")
    t.add_argument("--model-output", default=None)
    t.set_defaults(func=_cmd_train)

    i = sub.add_parser("investigate", help="Show the scoring breakdown for one claim")
    i.add_argument("claims_file")
    i.add_argument("claim_id")
    i.set_defaults(func=_cmd_investigate)

    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
