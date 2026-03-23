#!/usr/bin/env python3
"""Batch example: evaluate multiple hypotheses in parallel and generate a report.

This example shows how to use run_batch() for parallel evaluation
and ReportGenerator to produce a structured assessment report.
"""

from redteamkit import AdversarialCouncil, ReportGenerator
from redteamkit.agent import AgentRole


def main() -> None:
    # Create a focused council with 3 specialist roles
    council = AdversarialCouncil(
        roles=[
            AgentRole.DEVILS_ADVOCATE,
            AgentRole.STRESS_TESTER,
            AgentRole.ASSUMPTION_HUNTER,
        ]
    )

    # Define hypotheses to evaluate
    hypotheses = [
        "H-001-market-size",
        "H-002-unit-economics",
        "H-003-competitive-moat",
        "H-004-team-capability",
        "H-005-regulatory-risk",
    ]

    print(f"Evaluating {len(hypotheses)} hypotheses with {len(council.agents)} agents each...\n")

    # Run all hypotheses in parallel using thread pool
    results = council.run_batch(hypotheses, confidence=0.5, max_workers=4)

    # Print individual results
    for record in results:
        verdict = record.score.verdict.value if record.score else "N/A"
        score = f"{record.score.composite_score:.4f}" if record.score else "N/A"
        print(f"  {record.hypothesis_id}: verdict={verdict}, score={score}")

    # Generate a comprehensive report
    print("\n--- Report ---\n")
    gen = ReportGenerator(title="Batch Assessment Report")
    report = gen.generate(council.sessions)

    print(f"Title: {report.title}")
    print(f"Generated: {report.generated_at}")
    print(f"Sessions: {report.metadata['session_count']}")
    print(f"Summary: {report.summary}")
    print()

    for section in report.sections:
        print(f"[{section.title}]")
        print(f"  {section.content[:200]}...")
        print()


if __name__ == "__main__":
    main()
