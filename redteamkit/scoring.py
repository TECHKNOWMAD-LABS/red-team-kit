"""Scoring engine for evaluating hypothesis robustness under adversarial review."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from redteamkit.agent import Critique


class Verdict(str, Enum):
    ROBUST = "robust"
    CONDITIONAL = "conditional"
    WEAK = "weak"
    REFUTED = "refuted"


class ScoreBreakdown(BaseModel):
    evidence_strength: float = Field(ge=0.0, le=1.0)
    assumption_quality: float = Field(ge=0.0, le=1.0)
    counter_resilience: float = Field(ge=0.0, le=1.0)
    internal_consistency: float = Field(ge=0.0, le=1.0)

    @property
    def composite(self) -> float:
        weights = [0.3, 0.25, 0.25, 0.2]
        values = [
            self.evidence_strength,
            self.assumption_quality,
            self.counter_resilience,
            self.internal_consistency,
        ]
        return round(sum(w * v for w, v in zip(weights, values)), 4)


class HypothesisScore(BaseModel):
    hypothesis_id: str
    breakdown: ScoreBreakdown
    verdict: Verdict
    critique_count: int = 0
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def composite_score(self) -> float:
        return self.breakdown.composite


class HypothesisScorer:
    """Scores hypotheses based on critiques from adversarial agents."""

    VERDICT_THRESHOLDS: dict[str, float] = {
        "robust": 0.75,
        "conditional": 0.50,
        "weak": 0.25,
    }

    def __init__(self, thresholds: dict[str, float] | None = None) -> None:
        if thresholds:
            self.VERDICT_THRESHOLDS = {**self.VERDICT_THRESHOLDS, **thresholds}

    def score(
        self,
        hypothesis_id: str,
        critiques: list[Critique],
        *,
        baseline_strength: float = 0.7,
    ) -> HypothesisScore:
        """Score a hypothesis given a list of critiques."""
        if not critiques:
            breakdown = ScoreBreakdown(
                evidence_strength=baseline_strength,
                assumption_quality=baseline_strength,
                counter_resilience=baseline_strength,
                internal_consistency=baseline_strength,
            )
        else:
            avg_confidence = sum(c.confidence for c in critiques) / len(critiques)
            total_challenges = sum(len(c.challenges) for c in critiques)
            total_weaknesses = sum(len(c.weaknesses) for c in critiques)
            total_counter = sum(len(c.counter_evidence) for c in critiques)

            evidence_strength = max(0.0, baseline_strength - total_counter * 0.05)
            assumption_quality = max(0.0, baseline_strength - total_weaknesses * 0.06)
            counter_resilience = max(0.0, 1.0 - avg_confidence)
            internal_consistency = max(0.0, baseline_strength - total_challenges * 0.04)

            breakdown = ScoreBreakdown(
                evidence_strength=min(1.0, evidence_strength),
                assumption_quality=min(1.0, assumption_quality),
                counter_resilience=min(1.0, counter_resilience),
                internal_consistency=min(1.0, internal_consistency),
            )

        verdict = self._determine_verdict(breakdown.composite)
        notes = self._generate_notes(critiques)

        return HypothesisScore(
            hypothesis_id=hypothesis_id,
            breakdown=breakdown,
            verdict=verdict,
            critique_count=len(critiques),
            notes=notes,
        )

    def _determine_verdict(self, composite: float) -> Verdict:
        if composite >= self.VERDICT_THRESHOLDS["robust"]:
            return Verdict.ROBUST
        if composite >= self.VERDICT_THRESHOLDS["conditional"]:
            return Verdict.CONDITIONAL
        if composite >= self.VERDICT_THRESHOLDS["weak"]:
            return Verdict.WEAK
        return Verdict.REFUTED

    def _generate_notes(self, critiques: list[Critique]) -> list[str]:
        notes: list[str] = []
        all_weaknesses = [w for c in critiques for w in c.weaknesses]
        if len(all_weaknesses) > 3:
            notes.append(f"High weakness count ({len(all_weaknesses)}) across critiques")
        high_conf = [c for c in critiques if c.confidence > 0.8]
        if high_conf:
            notes.append(f"{len(high_conf)} agent(s) expressed high-confidence challenges")
        return notes
