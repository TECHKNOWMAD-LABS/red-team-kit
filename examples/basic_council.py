#!/usr/bin/env python3
"""Basic example: run an adversarial council session on a hypothesis.

This example creates a council with all default agent roles, runs a session,
and prints the verdict and score breakdown.
"""

from redteamkit import AdversarialCouncil

def main() -> None:
    # Create a council with all 6 default adversarial roles
    council = AdversarialCouncil()
    print(f"Council created: {council}")
    print(f"Agents: {[a.role.value for a in council.agents]}\n")

    # Run a session to evaluate a hypothesis
    record = council.run_session(
        hypothesis_id="H-001-revenue-growth",
        challenges_per_agent=["Market saturation risk", "Competitor response unknown"],
        weaknesses_per_agent=["No sensitivity analysis on growth rate"],
        confidence=0.6,
    )

    # Print results
    print(f"Session ID: {record.session_id}")
    print(f"Critiques received: {len(record.critiques)}")
    print()

    if record.score:
        print(f"Verdict: {record.score.verdict.value}")
        print(f"Composite score: {record.score.composite_score:.4f}")
        print(f"Breakdown:")
        bd = record.score.breakdown
        print(f"  Evidence strength:   {bd.evidence_strength:.4f}")
        print(f"  Assumption quality:  {bd.assumption_quality:.4f}")
        print(f"  Counter resilience:  {bd.counter_resilience:.4f}")
        print(f"  Internal consistency: {bd.internal_consistency:.4f}")
        if record.score.notes:
            print(f"Notes: {record.score.notes}")

    print()
    for critique in record.critiques:
        print(f"Agent {critique.agent_id} ({critique.role.value}):")
        print(f"  Challenges: {critique.challenges}")
        print(f"  Weaknesses: {critique.weaknesses}")
        print(f"  Confidence: {critique.confidence}")


if __name__ == "__main__":
    main()
