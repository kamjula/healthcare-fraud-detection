"""Rule-based fraud detection engine.

Each rule reads thresholds from the YAML config and adds a `flag_<rule>` column
plus a human-readable reason. The combined, normalized rule score feeds the
hybrid scorer alongside the ML probability.
"""
from __future__ import annotations

import pandas as pd

from src.config import load_rules


def apply_rules(df: pd.DataFrame, rules_cfg: dict | None = None) -> pd.DataFrame:
    """Apply all configured rules to a feature-engineered claims frame.

    Expects columns produced by features.engineer.build_features.
    Returns df with per-rule flag columns, `rule_score`, and `rule_reasons`.
    """
    cfg = rules_cfg or load_rules()
    rules = cfg["rules"]
    df = df.copy()
    weights: dict[str, float] = {}
    flag_cols: list[str] = []

    # imaging_overutilization (provider level)
    r = rules["imaging_overutilization"]
    p = r["params"]
    df["flag_imaging_overutilization"] = (
        (df["provider_imaging_ratio"] >= p["imaging_ratio_threshold"])
        & (df["provider_claim_count"] >= p["min_claims"])
    ).astype(int)
    weights["imaging_overutilization"] = r["weight"]
    flag_cols.append("flag_imaging_overutilization")

    # high_billed_amount (claim level)
    r = rules["high_billed_amount"]
    df["flag_high_billed_amount"] = (
        df["billed_vs_cpt_median"] >= r["params"]["multiple_of_cpt_median"]
    ).astype(int)
    weights["high_billed_amount"] = r["weight"]
    flag_cols.append("flag_high_billed_amount")

    # excessive_units (claim level)
    r = rules["excessive_units"]
    df["flag_excessive_units"] = (
        df["units"] > r["params"]["max_units"]
    ).astype(int)
    weights["excessive_units"] = r["weight"]
    flag_cols.append("flag_excessive_units")

    # duplicate_billing (claim level)
    r = rules["duplicate_billing"]
    dup_key = ["provider_id", "patient_id", "cpt_code", "claim_date"]
    df["flag_duplicate_billing"] = (
        df.duplicated(subset=dup_key, keep=False).astype(int))
    weights["duplicate_billing"] = r["weight"]
    flag_cols.append("flag_duplicate_billing")

    # upcoding_amount_vs_paid (provider level)
    r = rules["upcoding_amount_vs_paid"]
    p = r["params"]
    df["flag_upcoding_amount_vs_paid"] = (
        (df["provider_avg_billed_to_paid"] >= p["billed_to_paid_ratio"])
        & (df["provider_claim_count"] >= p["min_claims"])
    ).astype(int)
    weights["upcoding_amount_vs_paid"] = r["weight"]
    flag_cols.append("flag_upcoding_amount_vs_paid")

    # Weighted rule score, normalized to 0..1 by the max achievable weight.
    max_weight = sum(weights.values())
    weighted = sum(
        df[f"flag_{name}"] * w for name, w in weights.items())
    df["rule_score"] = (weighted / max_weight).round(4)

    # Human-readable reasons.
    reason_map = {
        "flag_imaging_overutilization": "imaging overutilization",
        "flag_high_billed_amount": "billed far above CPT median",
        "flag_excessive_units": "excessive units",
        "flag_duplicate_billing": "possible duplicate billing",
        "flag_upcoding_amount_vs_paid": "inflated billed-vs-paid pattern",
    }
    df["rule_reasons"] = df[flag_cols].apply(
        lambda row: "; ".join(
            reason_map[c] for c in flag_cols if row[c] == 1) or "none",
        axis=1,
    )
    return df
