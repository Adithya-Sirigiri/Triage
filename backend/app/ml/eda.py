"""
Exploratory data analysis on the cleaned ticket dataset — run before
training so we understand what the model will actually be learning
from, and catch data issues (imbalance, duplicates, weak signal)
before they show up as confusing model behavior later.
"""
import pandas as pd

DATA_PATH = "app/ml/data/training_data.csv"


def run_eda():
    df = pd.read_csv(DATA_PATH)
    df["text"] = df["subject"].fillna("") + " " + df["description"].fillna("")
    df["text_length"] = df["text"].str.len()
    df["word_count"] = df["text"].str.split().str.len()

    print("=" * 60)
    print("BASIC SHAPE")
    print("=" * 60)
    print(f"Total rows: {len(df)}")
    print(f"Duplicate rows (full match): {df.duplicated().sum()}")
    print(f"Duplicate descriptions only: {df.duplicated(subset=['description']).sum()}")

    print("\n" + "=" * 60)
    print("CLASS BALANCE — CATEGORY")
    print("=" * 60)
    print(df["category"].value_counts())
    print(f"\nSmallest class: {df['category'].value_counts().min()} samples")
    print(f"Largest class: {df['category'].value_counts().max()} samples")
    print(f"Imbalance ratio: {df['category'].value_counts().max() / df['category'].value_counts().min():.2f}x")

    print("\n" + "=" * 60)
    print("CLASS BALANCE — URGENCY")
    print("=" * 60)
    print(df["urgency"].value_counts())
    print(f"Imbalance ratio: {df['urgency'].value_counts().max() / df['urgency'].value_counts().min():.2f}x")

    print("\n" + "=" * 60)
    print("TEXT LENGTH BY CATEGORY (word count)")
    print("=" * 60)
    print(df.groupby("category")["word_count"].agg(["mean", "median", "min", "max"]).round(1))

    print("\n" + "=" * 60)
    print("TEXT LENGTH BY URGENCY (word count)")
    print("=" * 60)
    print(df.groupby("urgency")["word_count"].agg(["mean", "median", "min", "max"]).round(1))

    print("\n" + "=" * 60)
    print("CATEGORY x URGENCY CROSS-TAB (counts)")
    print("=" * 60)
    print(pd.crosstab(df["category"], df["urgency"]))

    print("\n" + "=" * 60)
    print("CATEGORY x URGENCY CROSS-TAB (% within category)")
    print("=" * 60)
    print((pd.crosstab(df["category"], df["urgency"], normalize="index") * 100).round(1))

    print("\n" + "=" * 60)
    print("MOST DISTINCTIVE WORDS PER CATEGORY (simple check)")
    print("=" * 60)
    from sklearn.feature_extraction.text import TfidfVectorizer
    for cat in df["category"].unique():
        subset = df[df["category"] == cat]["text"]
        vec = TfidfVectorizer(max_features=10, stop_words="english")
        vec.fit(subset)
        print(f"{cat}: {list(vec.get_feature_names_out())}")


if __name__ == "__main__":
    run_eda()