"""Feature engineering for claim-level and provider-level fraud signals."""
from __future__ import annotations

import pandas as pd

# Radiology CPT codes fall in this range; used to flag imaging claims.
IMAGING_CPT_MIN = 70010
IMAGING_CPT_MAX = 79999

# Columns fed to the ML model. Keep in sync with training.
FEATURE_COLUMNS = [
    "billed_amount",
    "units",
    "paid_ratio",
    "is_imaging",
    "provider_total_claims",
    "provider_avg_billed",
    "provider_claims_per_patient",
    "provider_imaging_ratio",
]


def add_claim_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add per-claim derived features."""
    df = df.copy()
    df["is_imaging"] = df["cpt_code"].between(IMAGING_CPT_MIN, IMAGING_CPT_MAX).astype(int)
    df["paid_ratio"] = 0.0
    positive = df["billed_amount"] > 0
    df.loc[positive, "paid_ratio"] = df.loc[positive, "paid_amount"] / df.loc[positive, "billed_amount"]
    return df


def add_provider_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add provider-level aggregate features, merged back onto each claim row."""
    df = add_claim_features(df)
    grp = df.groupby("provider_npi")
    provider = pd.DataFrame(
        {
            "provider_total_claims": grp["claim_id"].size(),
            "provider_avg_billed": grp["billed_amount"].mean(),
            "provider_distinct_patients": grp["patient_id"].nunique(),
            "provider_imaging_claims": grp["is_imaging"].sum(),
        }
    )
    provider["provider_claims_per_patient"] = (
        provider["provider_total_claims"] / provider["provider_distinct_patients"]
    )
    provider["provider_imaging_ratio"] = (
        provider["provider_imaging_claims"] / provider["provider_total_claims"]
    )
    return df.merge(provider, on="provider_npi", how="left")


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Build the numeric feature matrix used by the ML model."""
    enriched = add_provider_features(df)
    return enriched[FEATURE_COLUMNS].fillna(0.0)
