"""
Simulates realistic ticket lifecycles to generate training data for
the escalation-risk model. Unlike a static rule-based score, this
produces genuinely stochastic, correlated-noise outcomes: delays are
drawn from distributions shaped by urgency, a fluctuating team-load
factor affects all tickets in a time window (simulating real bursts),
and escalation is a probabilistic outcome, not a deterministic rule.

Critically, training examples are SNAPSHOTS taken partway through a
ticket's life — the model learns to predict eventual escalation from
partial, in-progress information, matching how it will actually be
used in production (scoring a ticket that hasn't been resolved yet).
"""
import numpy as np
import pandas as pd

np.random.seed(42)

CATEGORIES = ["billing", "technical", "account", "bug_report", "feature_request", "general"]
URGENCIES = ["low", "medium", "high", "critical"]
URGENCY_WEIGHT = {"low": 0.15, "medium": 0.35, "high": 0.65, "critical": 0.9}

# SLA targets in hours (from our seeded SLA rules, converted from minutes)
SLA_FIRST_RESPONSE_HOURS = {"critical": 0.5, "high": 1.0, "medium": 4.0, "low": 8.0}


def simulate_team_load(n_days: int) -> np.ndarray:
    """
    A slowly-drifting 'how overloaded is the team today' factor per
    simulated day, so nearby tickets share correlated delay noise —
    not just independent per-ticket randomness. Random walk, clipped.
    """
    load = np.zeros(n_days)
    load[0] = 0.3
    for i in range(1, n_days):
        load[i] = np.clip(load[i - 1] + np.random.normal(0, 0.08), 0.0, 1.0)
    return load


def simulate_ticket(ticket_id: int, day_index: int, team_load: float) -> list[dict]:
    urgency = np.random.choice(URGENCIES, p=[0.30, 0.32, 0.23, 0.15])
    category = np.random.choice(CATEGORIES)
    u_weight = URGENCY_WEIGHT[urgency]

    # Assignment delay: faster for urgent tickets, slower when team is overloaded.
    assign_mean = (3.0 * (1 - u_weight) + 0.3) * (1 + team_load * 1.5)
    hours_to_assign = np.random.exponential(assign_mean)

    # First response delay, added on top of assignment.
    response_mean = (SLA_FIRST_RESPONSE_HOURS[urgency] * 0.8) * (1 + team_load * 1.2)
    hours_to_response = hours_to_assign + np.random.exponential(response_mean)

    sla_target = SLA_FIRST_RESPONSE_HOURS[urgency]
    breached_sla = hours_to_response > sla_target
    breach_ratio = hours_to_response / sla_target  # how far over/under SLA

    # Probabilistic escalation — combines real signal with genuine
    # randomness, so it's not a clean deterministic function.
    escalation_prob = np.clip(
        0.05
        + u_weight * 0.35
        + (0.25 if breached_sla else 0.0)
        + min(breach_ratio / 4, 0.25)
        + team_load * 0.10
        + np.random.normal(0, 0.07),
        0.02, 0.95,
    )
    will_escalate = np.random.random() < escalation_prob
    hours_to_outcome = hours_to_response + np.random.exponential(6 if will_escalate else 20)

    # Take 2-3 snapshots across the ticket's life BEFORE the outcome —
    # this is what the model actually trains on: partial information.
    snapshots = []
    snapshot_points = sorted(np.random.uniform(0.15, 0.9, size=np.random.randint(2, 4)))
    for frac in snapshot_points:
        snap_time = frac * hours_to_outcome
        is_assigned = int(snap_time >= hours_to_assign)
        has_response = int(snap_time >= hours_to_response)
        hours_since_response = max(0, snap_time - hours_to_response) if has_response else 0

        snapshots.append({
            "ticket_id": ticket_id,
            "urgency": urgency,
            "category": category,
            "hours_open": round(snap_time, 2),
            "is_assigned": is_assigned,
            "has_first_response": has_response,
            "hours_since_last_update": round(hours_since_response if has_response else snap_time, 2),
            "sla_breached_so_far": int(has_response and breached_sla),
            "team_load_at_time": round(team_load, 2),
            "escalated": int(will_escalate),
        })
    return snapshots


def generate_dataset(n_tickets: int = 4000, n_days: int = 90) -> pd.DataFrame:
    team_load = simulate_team_load(n_days)
    all_rows = []
    for i in range(n_tickets):
        day = np.random.randint(0, n_days)
        rows = simulate_ticket(i, day, team_load[day])
        all_rows.extend(rows)
    df = pd.DataFrame(all_rows)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv("app/ml/data/risk_training_data.csv", index=False)
    print(f"Generated {len(df)} snapshot rows from simulated ticket lifecycles")
    print(f"\nEscalation rate: {df['escalated'].mean():.1%}")
    print("\nEscalation rate by urgency:")
    print(df.groupby("urgency")["escalated"].mean().round(3))
    print("\nEscalation rate by SLA breach status:")
    print(df.groupby("sla_breached_so_far")["escalated"].mean().round(3))