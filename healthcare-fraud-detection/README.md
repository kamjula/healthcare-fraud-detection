# Healthcare Fraud Detection

A hybrid **rule-based + machine-learning** system for detecting potentially
fraudulent healthcare claims, with a primary focus on **imaging
overutilization**. It ships with a synthetic data generator (no real PHI), so
the whole pipeline runs end-to-end out of the box.

## What it does

1. Generates (or loads) claims data with CPT codes, ICD-10 diagnoses, billed/paid
   amounts, units, and provider info.
2. Engineers claim-level and provider-level features (imaging ratio, billed-vs-CPT-median, billed-to-paid ratio, etc.).
3. Applies configurable **rules** (YAML) — imaging overutilization, high billed
   amount, excessive units, duplicate billing, upcoding.
4. Trains an **XGBoost** classifier to estimate a fraud probability per claim.
5. Combines the two into a **hybrid risk score** and flags claims for review.
6. Lets an analyst **drill down** on any claim to see why it scored the way it did.

## Project structure

```
healthcare-fraud-detection/
├── README.md
├── requirements.txt
├── Dockerfile
├── .dockerignore / .gitignore / .env.example
├── config/
│   └── fraud_rules.yaml          # thresholds + scoring weights
├── data/                         # generated CSVs (gitignored)
├── sql/
│   ├── 01_schema.sql             # claims / providers / scores tables
│   ├── 02_load_data.sql          # load the synthetic CSV
│   └── 03_fraud_queries.sql      # the rules expressed in pure SQL
├── src/
│   ├── config.py                 # paths + rules loader
│   ├── data/
│   │   ├── generate_synthetic.py # synthetic claims w/ injected fraud
│   │   └── prepare.py            # validation + cleaning
│   ├── features/engineer.py      # feature engineering
│   ├── rules/engine.py           # rule-based detection
│   ├── models/
│   │   ├── train.py              # XGBoost training
│   │   └── score.py              # ML prob + hybrid score
│   ├── pipeline.py               # end-to-end orchestration (CLI)
│   └── investigate.py            # single-claim drill-down (CLI)
├── tests/                        # pytest unit tests
└── scripts/run_demo.sh           # one-command demo
```

## Quick start

```bash
# 1. Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the full demo (generate -> train -> score -> investigate)
bash scripts/run_demo.sh
```

Or step by step:

```bash
python -m src.data.generate_synthetic     # writes data/sample_claims.csv
python -m src.pipeline --train            # trains model, writes data/scored_claims.csv
python -m src.investigate --claim-id CLM00001234
```

## Run with Docker

```bash
docker build -t fraud-detection .
docker run --rm -v "$(pwd)/data:/app/data" fraud-detection
```

## Run the tests

```bash
pytest -q
```

## How the hybrid score works

```
final_risk_score = ml_weight * ml_probability + rule_weight * rule_score
```

Weights and all rule thresholds live in `config/fraud_rules.yaml`, so you can
tune behaviour without touching code. Claims above `flag_threshold` are flagged.

## Using your own data

Replace the generator with a CSV that has these columns:

```
claim_id, provider_id, npi, provider_specialty, patient_id,
cpt_code, icd10_code, claim_date, units, billed_amount, paid_amount
```

An `is_fraud` column (provider- or claim-level label) is only needed to
**train** the model. Without it you can still run the rule engine.

## Notes & disclaimers

- The included data is **synthetic** and for demonstration only. Detected
  patterns are statistical signals, not proof of fraud — they're meant to
  prioritize human review.
- On this synthetic dataset the model reports a near-perfect ROC-AUC. That is
  **expected and not impressive** — the injected fraud behaviours are almost
  perfectly separable from the engineered features. On real claims, fraud is
  noisy, labels are scarce and unreliable, and performance is far lower. Treat
  the metric as a wiring check, not a result to quote.
- Before using real claims data, handle PHI per HIPAA: keep raw data out of
  version control (already in `.gitignore`), restrict access, and add audit
  logging.

## Tech stack

Python · pandas · scikit-learn · XGBoost · PyYAML · PostgreSQL (SQL scripts) · Docker
