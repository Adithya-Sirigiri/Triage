# Ticket Classification Model — Notes

## Data
Trained on a synthetic dataset (`generate_training_data.py`) built from
combinatorial sentence construction: category-specific issue phrases
combined with urgency-specific openers/closers.

## Known limitation
Because each issue phrase is deterministically tied to one category
(and each opener/closer to one urgency), the resulting text has very
clean, separable signal — which is why test accuracy reaches ~100%.
This reflects the synthetic data's structure, not real-world ticket
text, which is far messier and more ambiguous. A production version
of this system would need to be retrained on real historical tickets
(with a NLP pipeline like the one already built here) to get an honest
accuracy figure once real usage data becomes available.

## Why this approach was chosen
An initial attempt used a real Kaggle dataset, but EDA revealed the
ticket text had no genuine relationship to its labels (a templating
issue in that dataset). Rather than train a classifier with no real
signal, a synthetic dataset was built where the text-label
relationship is explicit and verifiable — a legitimate, standard
approach for bootstrapping ML systems before real usage data exists.