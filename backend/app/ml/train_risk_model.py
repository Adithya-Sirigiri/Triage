"""
Trains the escalation-risk model on structured, partial-information
features from simulated ticket lifecycles. Uses gradient boosting
with one-hot encoding for categorical fields (urgency, category).
"""
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

DATA_PATH = "app/ml/data/risk_training_data.csv"
MODEL_DIR = "app/ml/models"

FEATURE_COLUMNS = [
    "urgency", "category", "hours_open", "is_assigned",
    "has_first_response", "hours_since_last_update", "sla_breached_so_far",
]


def train():
    df = pd.read_csv(DATA_PATH)

    # Split by ticket_id, not by row — snapshots from the SAME ticket
    # must stay entirely in train or entirely in test, otherwise the
    # model could see one snapshot of a ticket in training and a
    # later snapshot of the SAME ticket in test, which is leakage
    # (same lesson learned the hard way in Phase 3).
    ticket_ids = df["ticket_id"].unique()
    train_ids, test_ids = train_test_split(ticket_ids, test_size=0.2, random_state=42)

    train_df = df[df["ticket_id"].isin(train_ids)]
    test_df = df[df["ticket_id"].isin(test_ids)]

    X_train, y_train = train_df[FEATURE_COLUMNS], train_df["escalated"]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df["escalated"]

    print(f"Train: {len(X_train)} rows ({len(train_ids)} tickets) | "
          f"Test: {len(X_test)} rows ({len(test_ids)} tickets)\n")

    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["urgency", "category"]),
    ], remainder="passthrough")

    pipeline = Pipeline([
        ("preprocess", preprocessor),
        ("model", GradientBoostingClassifier(n_estimators=150, max_depth=4, random_state=42)),
    ])

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    probs = pipeline.predict_proba(X_test)[:, 1]

    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(f"ROC-AUC: {roc_auc_score(y_test, probs):.3f}\n")
    print(classification_report(y_test, preds, zero_division=0))

    joblib.dump(pipeline, f"{MODEL_DIR}/risk_model.joblib")
    print(f"Saved -> {MODEL_DIR}/risk_model.joblib")


if __name__ == "__main__":
    train()