"""
Isolates the subject field to check whether it carries stronger
category-distinguishing signal than the (apparently templated)
description field. Quick, targeted follow-up to the main EDA.
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_PATH = "app/ml/data/training_data.csv"


def check_subjects():
    df = pd.read_csv(DATA_PATH)

    print("=" * 60)
    print("SAMPLE SUBJECTS PER CATEGORY (first 5 each)")
    print("=" * 60)
    for cat in df["category"].unique():
        print(f"\n--- {cat} ---")
        samples = df[df["category"] == cat]["subject"].head(5).tolist()
        for s in samples:
            print(f"  {s}")

    print("\n" + "=" * 60)
    print("SUBJECT UNIQUENESS")
    print("=" * 60)
    print(f"Total subjects: {len(df)}")
    print(f"Unique subjects: {df['subject'].nunique()}")
    print(f"Duplicate subject rate: {(1 - df['subject'].nunique() / len(df)) * 100:.1f}%")

    print("\n" + "=" * 60)
    print("MOST DISTINCTIVE WORDS PER CATEGORY — SUBJECT ONLY")
    print("=" * 60)
    for cat in df["category"].unique():
        subset = df[df["category"] == cat]["subject"].fillna("")
        vec = TfidfVectorizer(max_features=10, stop_words="english")
        vec.fit(subset)
        print(f"{cat}: {list(vec.get_feature_names_out())}")


if __name__ == "__main__":
    check_subjects()