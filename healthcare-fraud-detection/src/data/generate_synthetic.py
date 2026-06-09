"""Generate synthetic healthcare claims with injected fraud patterns.

No real PHI is used. A subset of providers are made fraudulent and given
behaviours the rules/model should catch (imaging overutilization, upcoding,
duplicate billing, excessive units).
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from src.config import DATA_DIR, ensure_dirs

SPECIALTIES = [
    "Internal Medicine", "Radiology", "Cardiology", "Orthopedics",
    "Family Practice", "Dermatology", "Neurology",
]

# CPT samples: a mix of office visits, labs, and imaging (70000-79999).
OFFICE_CPT = [99213, 99214, 99215, 99203, 99204]
LAB_CPT = [80053, 85025, 80061, 83036]
IMAGING_CPT = [70450, 71250, 72148, 73721, 74176, 78815]  # CT / MRI / PET

ICD10 = ["E11.9", "I10", "M54.5", "J45.909", "R51.9", "Z00.00", "N39.0"]


def _base_amount(cpt: int, rng: np.random.Generator) -> float:
    if cpt in IMAGING_CPT:
        base = rng.uniform(400, 1800)
    elif cpt in LAB_CPT:
        base = rng.uniform(20, 120)
    else:
        base = rng.uniform(80, 300)
    return round(base * rng.uniform(0.85, 1.15), 2)


def generate(n_providers: int = 200, fraud_rate: float = 0.08,
             seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n_fraud = max(1, int(n_providers * fraud_rate))
    fraud_providers = set(rng.choice(n_providers, size=n_fraud, replace=False))

    rows = []
    claim_counter = 0
    for pid in range(n_providers):
        is_fraud_provider = pid in fraud_providers
        specialty = rng.choice(SPECIALTIES)
        npi = 1000000000 + pid
        n_claims = int(rng.integers(25, 120))

        for _ in range(n_claims):
            claim_counter += 1
            patient_id = int(rng.integers(1, n_providers * 30))

            # Fraudulent providers skew heavily toward imaging.
            if is_fraud_provider and rng.random() < 0.65:
                cpt = int(rng.choice(IMAGING_CPT))
            else:
                pool = OFFICE_CPT + LAB_CPT + IMAGING_CPT
                cpt = int(rng.choice(pool, p=_claim_mix_probs(len(pool))))

            billed = _base_amount(cpt, rng)
            units = 1
            # Upcoding / inflation behaviours for fraud providers.
            if is_fraud_provider and rng.random() < 0.30:
                billed = round(billed * rng.uniform(3.5, 6.0), 2)
            if is_fraud_provider and rng.random() < 0.10:
                units = int(rng.integers(13, 25))

            paid = round(billed * rng.uniform(0.25, 0.6), 2)
            date = pd.Timestamp("2024-01-01") + pd.Timedelta(
                days=int(rng.integers(0, 365)))

            rows.append({
                "claim_id": f"CLM{claim_counter:08d}",
                "provider_id": f"PRV{pid:05d}",
                "npi": npi,
                "provider_specialty": specialty,
                "patient_id": f"PAT{patient_id:06d}",
                "cpt_code": cpt,
                "icd10_code": str(rng.choice(ICD10)),
                "claim_date": date.date().isoformat(),
                "units": units,
                "billed_amount": billed,
                "paid_amount": paid,
                "is_fraud": int(is_fraud_provider),  # provider-level label
            })

    df = pd.DataFrame(rows)

    # Inject explicit duplicate-billing rows for a few fraud providers.
    dup_src = df[df["is_fraud"] == 1].sample(
        n=min(40, (df["is_fraud"] == 1).sum()), random_state=seed)
    dups = dup_src.copy()
    dups["claim_id"] = [f"CLM9{i:07d}" for i in range(len(dups))]
    df = pd.concat([df, dups], ignore_index=True)

    return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)


def _claim_mix_probs(n: int) -> np.ndarray:
    # Office visits and labs more common than imaging for honest providers.
    weights = np.array([3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1][:n],
                       dtype=float)
    return weights / weights.sum()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic claims.")
    parser.add_argument("--providers", type=int, default=200)
    parser.add_argument("--fraud-rate", type=float, default=0.08)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    ensure_dirs()
    df = generate(args.providers, args.fraud_rate, args.seed)
    out = DATA_DIR / "sample_claims.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} claims for {args.providers} providers -> {out}")


if __name__ == "__main__":
    main()
