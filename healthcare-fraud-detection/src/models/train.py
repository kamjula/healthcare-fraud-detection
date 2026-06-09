"""Train a gradient-boosting classifier to estimate fraud probability per claim.

Uses scikit-learn's HistGradientBoostingClassifier (no external OpenMP/libomp
dependency, so it runs anywhere scikit-learn installs).
"""
from __future__ import annotations

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

from src.config import MODEL_PATH, ensure_dirs
from src.features.engineer import FEATURE_COLUMNS


def train(df: pd.DataFrame, label_col: str = "is_fraud",
          random_state: int = 42) -> dict:
    """Train the model on a feature-engineered frame and persist it."""
    if label_col not in df.columns:
        raise ValueError(f"Training requires a '{label_col}' label column.")

    X = df[FEATURE_COLUMNS]
    y = df[label_col].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=random_state)

    # class_weight="balanced" handles the fraud class imbalance.
    model = HistGradientBoostingClassifier(
        max_iter=200,
        max_depth=4,
        learning_rate=0.1,
        class_weight="balanced",
        random_state=random_state,
    )
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    preds = (proba >= 0.5).astype(int)
    metrics = {
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
        "report": classification_report(y_test, preds, zero_division=0),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }

    ensure_dirs()
    joblib.dump({"model": model, "features": FEATURE_COLUMNS}, MODEL_PATH)
    return metrics


def load_model(path=MODEL_PATH):
    """Load a persisted model bundle."""
    return joblib.load(path)
