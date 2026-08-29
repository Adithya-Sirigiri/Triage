"""
Loads the trained TF-IDF vectorizer and both classifiers once at
import time (not per-request — that would be slow), and exposes a
single function to classify new ticket text.
"""
import joblib
import os

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

_vectorizer = joblib.load(os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib"))
_category_model = joblib.load(os.path.join(MODEL_DIR, "category_model.joblib"))
_urgency_model = joblib.load(os.path.join(MODEL_DIR, "urgency_model.joblib"))


def classify_ticket(subject: str, description: str) -> dict:
    """
    Takes raw ticket text, returns predicted category + urgency.
    Uses the same subject+description concatenation the model was
    trained on, so inference matches training exactly.
    """
    text = f"{subject or ''} {description or ''}"
    vec = _vectorizer.transform([text])

    category = _category_model.predict(vec)[0]
    urgency = _urgency_model.predict(vec)[0]

    return {
        "category": category,
        "urgency": urgency,
    }