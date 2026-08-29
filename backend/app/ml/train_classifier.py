"""
Trains two classifiers (category, urgency) on the synthetic ticket
dataset, using a shared TF-IDF text representation. Evaluates both
on a held-out test set and saves the trained artifacts to disk.
"""
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score

DATA_PATH = "app/ml/data/training_data.csv"
MODEL_DIR = "app/ml/models"


def train():
    df = pd.read_csv(DATA_PATH)
    df["text"] = df["subject"].fillna("") + " " + df["description"].fillna("")

    X = df["text"]
    y_category = df["category"]
    y_urgency = df["urgency"]

    X_train, X_test, y_cat_train, y_cat_test, y_urg_train, y_urg_test = train_test_split(
        X, y_category, y_urgency, test_size=0.2, random_state=42, stratify=y_category
    )

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words="english")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("=" * 60)
    print("Training CATEGORY classifier...")
    print("=" * 60)
    category_model = GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42)
    category_model.fit(X_train_vec, y_cat_train)
    cat_preds = category_model.predict(X_test_vec)
    print(f"Category accuracy: {accuracy_score(y_cat_test, cat_preds):.3f}\n")
    print(classification_report(y_cat_test, cat_preds, zero_division=0))

    print("=" * 60)
    print("Training URGENCY classifier...")
    print("=" * 60)
    urgency_model = GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42)
    urgency_model.fit(X_train_vec, y_urg_train)
    urg_preds = urgency_model.predict(X_test_vec)
    print(f"Urgency accuracy: {accuracy_score(y_urg_test, urg_preds):.3f}\n")
    print(classification_report(y_urg_test, urg_preds, zero_division=0))

    joblib.dump(vectorizer, f"{MODEL_DIR}/tfidf_vectorizer.joblib")
    joblib.dump(category_model, f"{MODEL_DIR}/category_model.joblib")
    joblib.dump(urgency_model, f"{MODEL_DIR}/urgency_model.joblib")
    print(f"\nSaved vectorizer + both models -> {MODEL_DIR}/")


if __name__ == "__main__":
    train()