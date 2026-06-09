"""Tests for the rule engine."""
import pandas as pd

from src.rules.engine import RuleEngine

CONFIG = {
    "rules": {
        "high_billed_amount": {"enabled": True, "weight": 0.25, "threshold": 5000},
        "excessive_units": {"enabled": True, "weight": 0.20, "max_units": 20},
        "duplicate_claim": {"enabled": True, "weight": 0.25},
        "imaging_overutilization": {
            "enabled": True,
            "weight": 0.30,
            "imaging_cpt_min": 70010,
            "imaging_cpt_max": 79999,
            "max_imaging_per_patient": 3,
        },
    },
    "scoring": {"rule_weight": 0.5, "model_weight": 0.5, "flag_threshold": 0.5},
}


def _frame(rows):
    return pd.DataFrame(rows)


def test_high_billed_amount_fires_above_threshold():
    df = _frame([
        {"claim_id": "A", "provider_npi": "1", "patient_id": "p1", "cpt_code": 99213,
         "billed_amount": 9000, "units": 1, "service_date": pd.Timestamp("2024-01-01")},
    ])
    result = RuleEngine(CONFIG).evaluate(df)
    assert result.loc[0, "rule_high_billed_amount"] == 1


def test_excessive_units_does_not_fire_at_limit():
    df = _frame([
        {"claim_id": "A", "provider_npi": "1", "patient_id": "p1", "cpt_code": 96372,
         "billed_amount": 100, "units": 20, "service_date": pd.Timestamp("2024-01-01")},
    ])
    result = RuleEngine(CONFIG).evaluate(df)
    assert result.loc[0, "rule_excessive_units"] == 0


def test_duplicate_claim_flags_both_rows():
    df = _frame([
        {"claim_id": "A", "provider_npi": "1", "patient_id": "p1", "cpt_code": 99213,
         "billed_amount": 100, "units": 1, "service_date": pd.Timestamp("2024-02-01")},
        {"claim_id": "B", "provider_npi": "1", "patient_id": "p1", "cpt_code": 99213,
         "billed_amount": 100, "units": 1, "service_date": pd.Timestamp("2024-02-01")},
    ])
    result = RuleEngine(CONFIG).evaluate(df)
    assert result["rule_duplicate_claim"].sum() == 2


def test_imaging_overutilization_flags_high_ratio_provider():
    # Provider "1": 4 imaging claims across 1 patient => ratio 4 > 3 -> fires.
    rows = [
        {"claim_id": f"C{i}", "provider_npi": "1", "patient_id": "p1", "cpt_code": 70450 + i,
         "billed_amount": 1000, "units": 1, "service_date": pd.Timestamp("2024-01-0%d" % (i + 1))}
        for i in range(4)
    ]
    result = RuleEngine(CONFIG).evaluate(_frame(rows))
    assert result["rule_imaging_overutilization"].sum() == 4


def test_rule_score_is_normalised_between_zero_and_one():
    df = _frame([
        {"claim_id": "A", "provider_npi": "1", "patient_id": "p1", "cpt_code": 99213,
         "billed_amount": 9000, "units": 30, "service_date": pd.Timestamp("2024-01-01")},
    ])
    result = RuleEngine(CONFIG).evaluate(df)
    assert 0.0 <= result.loc[0, "rule_score"] <= 1.0
