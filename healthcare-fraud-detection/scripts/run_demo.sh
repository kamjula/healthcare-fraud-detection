#!/usr/bin/env bash
# Run the full demo locally end-to-end.
set -euo pipefail

echo "==> Generating synthetic claims"
python -m src.data.generate_synthetic --providers 200 --fraud-rate 0.08

echo "==> Running pipeline (train + score)"
python -m src.pipeline --train

echo "==> Investigating the top flagged claim"
TOP_CLAIM=$(python - <<'PY'
import pandas as pd
df = pd.read_csv("data/scored_claims.csv")
print(df.iloc[0]["claim_id"])
PY
)
python -m src.investigate --claim-id "$TOP_CLAIM"

echo "==> Done. See data/scored_claims.csv"
