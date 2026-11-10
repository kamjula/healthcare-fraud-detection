# Healthcare Fraud Detection — Hybrid Rules + ML Claims Risk Scoring

A portfolio implementation of a **hybrid rule-based and machine-learning workflow** for prioritizing potentially suspicious healthcare claims for human review.

The repository uses **synthetic claims only**. It does not contain PHI and does not claim production fraud-detection accuracy.

![System architecture](images/system-architecture.png)

## What is actually implemented

- Synthetic claims generator with injected suspicious patterns
- Feature engineering at claim/provider level
- Configurable YAML fraud rules
- XGBoost classifier training and persisted model artifact
- Hybrid score combining ML probability and rule score
- Claim-level investigation CLI explaining why a record was flagged
- PostgreSQL schema and analytical SQL
- Dockerfile and one-command demo script
- pytest test suite

## Detection flow

```text
Synthetic claims
      │
      v
Validation / preparation
      │
      v
Feature engineering
      │
      ├──────────────> Configurable rules
      │
      └──────────────> XGBoost classifier
                         │
                         v
              Hybrid risk score
                         │
                         v
              Human-review shortlist
```

## Risk scoring

```text
final_risk_score = ml_weight * ml_probability
                 + rule_weight * rule_score
```

Thresholds and weights are stored in `config/fraud_rules.yaml`, so scoring behavior can be changed without editing model code.

## Repository layout

The runnable implementation lives in the nested project directory:

```text
healthcare-fraud-detection/
├── images/
│   └── system-architecture.png
└── healthcare-fraud-detection/
    ├── config/
    ├── data/
    ├── models/
    ├── scripts/
    ├── sql/
    ├── src/
    ├── tests/
    ├── Dockerfile
    └── requirements.txt
```

## Run the demo

```bash
git clone https://github.com/kamjula/healthcare-fraud-detection.git
cd healthcare-fraud-detection/healthcare-fraud-detection

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

bash scripts/run_demo.sh
```

Or run individual stages:

```bash
python -m src.data.generate_synthetic
python -m src.pipeline --train
python -m src.investigate --claim-id CLM00001234
```

Run tests:

```bash
pytest -q
```

## Important evaluation note

The synthetic generator intentionally creates separable fraud patterns, so the model can report a near-perfect ROC-AUC on that generated dataset.

That number is **not presented as real-world model performance**. On real claims, labels are noisy and scarce, data leakage is a serious risk, and proper temporal/external validation would be required.

## Stack

Python · Pandas · NumPy · scikit-learn · XGBoost · PyYAML · PostgreSQL · Docker · pytest

## Scope and limitations

- Synthetic data only
- Statistical/rule/model outputs are prioritization signals, not proof of fraud
- No clinical or payment decision should be made from this portfolio system
- Real claims would require HIPAA controls, access restrictions, audit logging, and a stronger validation strategy

## Author

**Sravani Kamjula** · AI/ML Engineer  
[LinkedIn](https://www.linkedin.com/in/sravani-kamjula/) · [Portfolio](https://sravaniportfoli.netlify.app/)
