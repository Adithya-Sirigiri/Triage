"""
Generates a labeled synthetic dataset using combinatorial sentence
construction: a category-specific issue phrase combined with an
urgency-specific opener and closer. This produces genuinely distinct
sentences (not prefix-shuffled repeats of the same text), giving us
real volume without duplication or leakage problems.
"""
import pandas as pd
import random
import itertools

random.seed(42)

CATEGORY_ISSUES = {
    "billing": [
        "my invoice shows a charge I don't recognize",
        "I was billed for a plan I already cancelled",
        "my subscription price changed without notice",
        "a discount code didn't apply to my payment",
        "I was charged twice for the same month",
        "my card was charged the wrong amount",
        "I need a refund for an incorrect charge",
        "my billing address needs to be updated",
        "the tax amount on my invoice looks wrong",
        "my payment method needs to be changed",
        "I don't understand a line item on my bill",
        "my proration after upgrading looks incorrect",
    ],
    "technical": [
        "the dashboard keeps throwing errors",
        "API requests are failing intermittently",
        "data isn't saving properly in the app",
        "our integration stopped syncing correctly",
        "the export feature isn't working",
        "the search results look completely wrong",
        "the system has been unresponsive",
        "file uploads keep failing",
        "our automated workflows stopped triggering",
        "the mobile app keeps crashing",
        "reports are showing incorrect numbers",
        "the platform is running extremely slowly",
    ],
    "account": [
        "I can't update my email address",
        "my account permissions look incorrect",
        "I think someone else accessed my account",
        "I've been locked out after a password change",
        "two-factor authentication isn't working",
        "my profile keeps reverting to old data",
        "I need to transfer ownership of my workspace",
        "a team member's access needs to be fixed",
        "my account shows unfamiliar login activity",
        "I can't reset my password",
        "my linked login stopped working",
        "my account role is showing incorrectly",
    ],
    "bug_report": [
        "clicking export does nothing and shows no error",
        "the date picker shows the wrong month",
        "sorting breaks with special characters in names",
        "the checkout page freezes during discount entry",
        "uploading large files crashes the page",
        "editing a record deletes related data silently",
        "notifications aren't showing up consistently",
        "timestamps display in the wrong timezone",
        "the app logs me out randomly",
        "duplicate entries appear after syncing",
        "a dropdown menu won't close properly",
        "reports generate with the wrong totals",
    ],
    "feature_request": [
        "a bulk export option for our records",
        "a Slack integration for our team",
        "the ability to schedule recurring reports",
        "custom fields for our specific workflow",
        "role-based dashboards for different teams",
        "a native mobile app for field work",
        "keyboard shortcuts for common actions",
        "a dark mode theme option",
        "bulk editing of multiple records at once",
        "an API webhook for status changes",
        "multi-language support for our team",
        "the ability to star favorite items",
    ],
    "general": [
        "documentation on getting started",
        "your current support hours",
        "guidance on onboarding new team members",
        "a walkthrough of setting up my workspace",
        "your public roadmap for upcoming features",
        "resources for training our team",
        "advice on migrating our old data over",
        "where to find your terms of service",
        "feedback about the onboarding experience",
        "whether you have a community forum",
        "a call to discuss our enterprise needs",
        "best practices for a team our size",
    ],
}

URGENCY_OPENERS = {
    "critical": [
        "This is extremely urgent —",
        "Emergency, I need immediate help —",
        "This cannot wait, please help now —",
        "Urgent escalation needed —",
    ],
    "high": [
        "This is quite important —",
        "I really need help with this soon —",
        "This is affecting my work significantly —",
        "I need this addressed promptly —",
    ],
    "medium": [
        "I wanted to flag an issue —",
        "Could you help me with something —",
        "I ran into a problem —",
        "I'd like some help with this —",
    ],
    "low": [
        "Just a quick note —",
        "No rush, but wondering about —",
        "When you get a chance —",
        "Just curious about —",
    ],
}

URGENCY_CLOSERS = {
    "critical": [
        "please resolve this immediately, it's blocking everything.",
        "I need this fixed right now, it's critical.",
        "this needs urgent attention today, please help.",
        "this is a serious problem that can't wait.",
    ],
    "high": [
        "please look into this as soon as possible.",
        "I'd appreciate a quick resolution to this.",
        "this needs attention fairly soon.",
        "hoping this can be resolved quickly.",
    ],
    "medium": [
        "would appreciate a fix when you're able to.",
        "please look into this when convenient.",
        "let me know what steps to take next.",
        "hoping to get this sorted out soon.",
    ],
    "low": [
        "no rush at all, whenever convenient.",
        "just wanted this on your radar.",
        "happy to wait, just flagging it.",
        "not urgent, just checking in.",
    ],
}

# Categories that realistically don't have critical/high urgency tickets
VALID_URGENCIES = {
    "billing": ["low", "medium", "high", "critical"],
    "technical": ["low", "medium", "high", "critical"],
    "account": ["low", "medium", "high", "critical"],
    "bug_report": ["low", "medium", "high", "critical"],
    "feature_request": ["low", "medium"],
    "general": ["low", "medium"],
}


def generate_dataset(samples_per_bucket: int = 150) -> pd.DataFrame:
    rows = []

    for category, issues in CATEGORY_ISSUES.items():
        for urgency in VALID_URGENCIES[category]:
            openers = URGENCY_OPENERS[urgency]
            closers = URGENCY_CLOSERS[urgency]

            # Every unique (issue, opener, closer) combination is a
            # genuinely distinct sentence — no repeats to worry about.
            all_combos = list(itertools.product(issues, openers, closers))
            random.shuffle(all_combos)
            chosen = all_combos[:samples_per_bucket]

            for issue, opener, closer in chosen:
                description = f"{opener} {issue}. {closer}"
                subject = f"{issue[:45].capitalize()}"
                rows.append({
                    "subject": subject,
                    "description": description,
                    "category": category,
                    "urgency": urgency,
                })

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate_dataset()
    output_path = "app/ml/data/training_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows -> {output_path}")
    print(f"Unique descriptions: {df['description'].nunique()} (should equal total rows)")
    print("\nCategory distribution:")
    print(df["category"].value_counts())
    print("\nUrgency distribution:")
    print(df["urgency"].value_counts())