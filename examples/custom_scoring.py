#!/usr/bin/env python3
"""Custom scoring example: configure thresholds and scoring parameters.

This example shows how to customize the scoring thresholds
and baseline strength for different evaluation contexts.
"""

from redteamkit.agent import AgentRole, Critique
from redteamkit.scoring import HypothesisScorer, Verdict


def main() -> None:
    # Default thresholds: robust ≥ 0.75, conditional ≥ 0.50, weak ≥ 0.25
    default_scorer = HypothesisScorer()

    # Strict thresholds for high-stakes decisions
    strict_scorer = HypothesisScorer(
        thresholds={"robust": 0.85, "conditional": 0.65, "weak": 0.35}
    )

    # Create sample critiques with varying severity
    mild_critique = Critique(
        agent_id="agent-mild",
        role=AgentRole.CONTRARIAN,
        hypothesis_id="H-001",
        challenges=["Minor concern about timing"],
        confidence=0.3,
    )

    severe_critique = Critique(
        agent_id="agent-severe",
        role=AgentRole.STRESS_TESTER,
        hypothesis_id="H-001",
        challenges=["Critical flaw 1", "Critical flaw 2", "Critical flaw 3"],
        weaknesses=["No market validation", "Untested assumptions"],
        counter_evidence=["Competitor data contradicts claim"],
        confidence=0.85,
    )

    # Score with different criteria
    print("=== Default Scoring ===")
    for label, critiques in [("mild", [mild_critique]), ("severe", [severe_critique])]:
        result = default_scorer.score("H-001", critiques, baseline_strength=0.7)
        print(f"  {label}: verdict={result.verdict.value}, score={result.composite_score:.4f}")

    print("\n=== Strict Scoring ===")
    for label, critiques in [("mild", [mild_critique]), ("severe", [severe_critique])]:
        result = strict_scorer.score("H-001", critiques, baseline_strength=0.7)
        print(f"  {label}: verdict={result.verdict.value}, score={result.composite_score:.4f}")

    # Score with no critiques (uses baseline only)
    print("\n=== Baseline Only (no critiques) ===")
    for label, baseline in [("conservative", 0.5), ("optimistic", 0.8)]:
        result = default_scorer.score("H-002", [], baseline_strength=baseline)
        print(f"  {label} (baseline={baseline}): "
              f"verdict={result.verdict.value}, score={result.composite_score:.4f}")

    print("\n=== Verdict Descriptions ===")
    for v in Verdict:
        print(f"  {v.value}")


if __name__ == "__main__":
    main()
