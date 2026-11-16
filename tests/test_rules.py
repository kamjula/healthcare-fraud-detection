"""Tests for the rule engine."""
import pandas as pd

from src.features.engineer import build_features
from src.rules.engine import apply_rules


def _toy_claims():
    # Two providers: one imaging-heavy (fraud-like), one normal.
    rows = []
    # Imaging-heavy provider: 30 imaging claims.
    for i in range(30):
        rows.append({
            "claim_id": f"A{i:04d}", "provider_id": "PRV1", "npi": 1,
            "provider_specialty": "Radiology", "patient_id": f"P{i}",
            "cpt_code": 70450, "icd10_code": "R51.9",
            "claim_date": "2024-01-01", "units": 1,
            "billed_amount": 800.0, "paid_amount": 300.0,
        })
    # Normal provider: 30 office visits.
    for i in range(30):
        rows.append({
            "claim_id": f"B{i:04d}", "provider_id": "PRV2", "npi": 2,
            "provider_specialty": "Family Practice", "patient_id": f"Q{i}",
            "cpt_code": 99213, "icd10_code": "Z00.00",
            "claim_date": "2024-02-01", "units": 1,
            "billed_amount": 150.0, "paid_amount": 90.0,
        })
    return pd.DataFrame(rows)


def test_imaging_overutilization_flags_heavy_imager():
    df = build_features(_toy_claims())
    flagged = apply_rules(df)
    prv1 = flagged[flagged["provider_id"] == "PRV1"]
    prv2 = flagged[flagged["provider_id"] == "PRV2"]
    assert prv1["flag_imaging_overutilization"].all() == 1
    assert prv2["flag_imaging_overutilization"].sum() == 0


def test_excessive_units_flag():
    df = build_features(_toy_claims())
    df.loc[0, "units"] = 20
    flagged = apply_rules(df)
    assert flagged.loc[0, "flag_excessive_units"] == 1


def test_rule_score_is_normalized():
    df = build_features(_toy_claims())
    flagged = apply_rules(df)
    assert flagged["rule_score"].between(0, 1).all()
