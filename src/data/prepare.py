"""Load and clean raw claims into a validated DataFrame."""
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = [
    "claim_id", "provider_id", "npi", "provider_specialty", "patient_id",
    "cpt_code", "icd10_code", "claim_date", "units", "billed_amount",
    "paid_amount",
]


def load_claims(path: str) -> pd.DataFrame:
    """Read a claims CSV and run basic validation/cleaning."""
    df = pd.read_csv(path)
    return prepare(df)


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Validate columns, coerce types, and drop unusable rows."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()
    df["claim_date"] = pd.to_datetime(df["claim_date"], errors="coerce")
    for col in ["cpt_code", "units"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["billed_amount", "paid_amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows that cannot be scored.
    before = len(df)
    df = df.dropna(subset=["claim_id", "provider_id", "cpt_code",
                           "billed_amount", "claim_date"])
    df = df[df["billed_amount"] > 0]
    df["units"] = df["units"].fillna(1).clip(lower=1).astype(int)

    dropped = before - len(df)
    if dropped:
        print(f"[prepare] dropped {dropped} invalid rows ({before} -> {len(df)})")
    return df.reset_index(drop=True)
