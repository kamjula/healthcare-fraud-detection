"""Claims data schema definition and validation."""
from __future__ import annotations

import pandas as pd

# Columns every claims file must provide.
REQUIRED_COLUMNS = [
    "claim_id",
    "provider_npi",
    "patient_id",
    "cpt_code",
    "icd10_code",
    "billed_amount",
    "paid_amount",
    "units",
    "service_date",
    "provider_specialty",
]

# Optional label used only for model training.
LABEL_COLUMN = "is_fraud"


class SchemaError(ValueError):
    """Raised when a claims DataFrame does not match the expected schema."""


def validate_claims(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalise a claims DataFrame.

    Returns a cleaned copy with correct dtypes. Raises SchemaError on problems.
    """
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(f"Missing required columns: {missing}")

    df = df.copy()

    df["service_date"] = pd.to_datetime(df["service_date"], errors="coerce")
    if df["service_date"].isna().any():
        raise SchemaError("Some service_date values could not be parsed as dates.")

    for col in ("cpt_code", "units"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise SchemaError(f"Column '{col}' contains non-numeric values.")
        df[col] = df[col].astype(int)

    for col in ("billed_amount", "paid_amount"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise SchemaError(f"Column '{col}' contains non-numeric values.")

    df["provider_npi"] = df["provider_npi"].astype(str)
    df["patient_id"] = df["patient_id"].astype(str)
    df["claim_id"] = df["claim_id"].astype(str)

    return df
