"""Tests for feature engineering and data preparation."""
import pandas as pd
import pytest

from src.data.prepare import prepare
from src.features.engineer import build_features, is_imaging


def _minimal_df():
    return pd.DataFrame([{
        "claim_id": "C1", "provider_id": "PRV1", "npi": 1,
        "provider_specialty": "Radiology", "patient_id": "P1",
        "cpt_code": 70450, "icd10_code": "R51.9",
        "claim_date": "2024-01-01", "units": 1,
        "billed_amount": 800.0, "paid_amount": 300.0,
    }])


def test_is_imaging_detects_radiology_range():
    s = pd.Series([70450, 99213, 79999, 69999])
    assert list(is_imaging(s)) == [True, False, True, False]


def test_build_features_adds_expected_columns():
    feats = build_features(_minimal_df())
    for col in ["is_imaging", "billed_to_paid", "provider_imaging_ratio",
                "billed_vs_cpt_median"]:
        assert col in feats.columns


def test_prepare_rejects_missing_columns():
    bad = pd.DataFrame([{"claim_id": "C1"}])
    with pytest.raises(ValueError):
        prepare(bad)


def test_prepare_drops_nonpositive_billed():
    df = _minimal_df()
    df.loc[0, "billed_amount"] = 0
    assert len(prepare(df)) == 0
