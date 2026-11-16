"""Feature engineering for fraud detection.

Produces a claim-level feature table enriched with provider-level aggregates
and CPT-level benchmarks that the ML model and rules both consume.
"""
from __future__ import annotations

import pandas as pd

from src.config import IMAGING_CPT_MAX, IMAGING_CPT_MIN


def is_imaging(cpt_series: pd.Series) -> pd.Series:
    return cpt_series.between(IMAGING_CPT_MIN, IMAGING_CPT_MAX)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with engineered feature columns added."""
    df = df.copy()
    df["is_imaging"] = is_imaging(df["cpt_code"]).astype(int)
    df["billed_to_paid"] = df["billed_amount"] / df["paid_amount"].clip(lower=1)

    # CPT-level benchmark: how does this claim compare to its code's median?
    cpt_median = df.groupby("cpt_code")["billed_amount"].transform("median")
    df["cpt_median_billed"] = cpt_median
    df["billed_vs_cpt_median"] = df["billed_amount"] / cpt_median.clip(lower=1)

    # Provider-level aggregates.
    prov = df.groupby("provider_id").agg(
        provider_claim_count=("claim_id", "count"),
        provider_imaging_ratio=("is_imaging", "mean"),
        provider_avg_billed=("billed_amount", "mean"),
        provider_distinct_patients=("patient_id", "nunique"),
        provider_avg_billed_to_paid=("billed_to_paid", "mean"),
        provider_max_units=("units", "max"),
    ).reset_index()
    prov["patients_per_claim"] = (
        prov["provider_distinct_patients"] / prov["provider_claim_count"])

    df = df.merge(prov, on="provider_id", how="left")
    return df


FEATURE_COLUMNS = [
    "billed_amount", "paid_amount", "units", "is_imaging", "billed_to_paid",
    "billed_vs_cpt_median", "provider_claim_count", "provider_imaging_ratio",
    "provider_avg_billed", "provider_distinct_patients",
    "provider_avg_billed_to_paid", "provider_max_units", "patients_per_claim",
]
