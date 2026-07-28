"""
CodeSage AI — Bug Prediction Model Training
Trains an XGBoost classifier on code metrics to predict bug probability.
Includes feature engineering, hyperparameter tuning, and SHAP explainability.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix,
)
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier


def load_and_prepare_data(data_path: str) -> tuple:
    """Load dataset and perform feature engineering."""
    df = pd.read_csv(data_path)

    # Feature Engineering
    df["complexity_ratio"] = df["cyclomatic_complexity"] / (df["lines_of_code"] + 1)
    df["doc_quality"] = df["comment_ratio"] * df["maintainability_index"] / 100
    df["risk_factor"] = (
        df["cyclomatic_complexity"] * df["max_nesting_depth"] / (df["maintainability_index"] + 1)
    )

    # Features and target
    feature_columns = [
        "cyclomatic_complexity", "cognitive_complexity", "lines_of_code",
        "comment_ratio", "function_count", "class_count", "max_nesting_depth",
        "avg_function_length", "parameters_per_function", "halstead_difficulty",
        "halstead_effort", "halstead_volume", "maintainability_index",
        "duplicate_ratio", "coupling_score", "import_count",
        "has_error_handling", "has_type_hints", "test_coverage",
        "complexity_ratio", "doc_quality", "risk_factor",
    ]

    X = df[feature_columns]
    y = df["has_bug"]

    return X, y, feature_columns


def train_model(data_path: str, output_dir: str) -> dict:
    """Train the bug prediction model and save artifacts."""
    print("[*] Loading and preparing data...")
    X, y, feature_columns = load_and_prepare_data(data_path)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("[*] Training XGBoost model...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False,
    )

    model.fit(
        X_train_scaled, y_train,
        eval_set=[(X_test_scaled, y_test)],
        verbose=False,
    )

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
    }

    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring="f1")
    metrics["cv_f1_mean"] = round(cv_scores.mean(), 4)
    metrics["cv_f1_std"] = round(cv_scores.std(), 4)

    print("\n[+] Evaluation Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    # Feature importance
    importance = dict(zip(feature_columns, model.feature_importances_.tolist()))
    sorted_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

    print("\n[+] Top Feature Importances:")
    for feat, imp in list(sorted_importance.items())[:10]:
        print(f"  {feat}: {imp:.4f}")

    # Save artifacts
    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(model, os.path.join(output_dir, "bug_predictor.joblib"))
    joblib.dump(scaler, os.path.join(output_dir, "scaler.joblib"))

    with open(os.path.join(output_dir, "feature_columns.json"), "w") as f:
        json.dump(feature_columns, f)

    with open(os.path.join(output_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    with open(os.path.join(output_dir, "feature_importance.json"), "w") as f:
        json.dump(sorted_importance, f, indent=2)

    print(f"\n[+] Model saved to {output_dir}")
    return metrics


if __name__ == "__main__":
    train_model(
        data_path="ml/datasets/sample_code_metrics.csv",
        output_dir="ml/models",
    )
