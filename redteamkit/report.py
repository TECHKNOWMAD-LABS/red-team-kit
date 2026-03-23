"""Report generation from adversarial council sessions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from redteamkit.council import SessionRecord
from redteamkit.scoring import Verdict


class ReportSection(BaseModel):
    """A single section within an assessment report."""

    title: str
    content: str
    data: dict[str, Any] = Field(default_factory=dict)


class Report(BaseModel):
    """Complete assessment report with sections and summary."""

    title: str
    generated_at: str
    sections: list[ReportSection] = Field(default_factory=list)
    summary: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize the report to a JSON string."""
        return self.model_dump_json(indent=2)

    def to_dict(self) -> dict[str, Any]:
        """Convert the report to a plain dictionary."""
        return self.model_dump()


class ReportGenerator:
    """Generates structured reports from adversarial council sessions."""

    def __init__(self, title: str = "Red Team Assessment Report") -> None:
        self.title = title

    def generate(self, sessions: list[SessionRecord]) -> Report:
        """Build a report from one or more council sessions."""
        now = datetime.now(timezone.utc).isoformat()
        sections: list[ReportSection] = []

        sections.append(self._build_overview(sessions))

        for session in sessions:
            sections.append(self._build_session_section(session))

        sections.append(self._build_verdict_summary(sessions))

        summary = self._build_summary_text(sessions)

        return Report(
            title=self.title,
            generated_at=now,
            sections=sections,
            summary=summary,
            metadata={"session_count": len(sessions)},
        )

    def _build_overview(self, sessions: list[SessionRecord]) -> ReportSection:
        total_critiques = sum(len(s.critiques) for s in sessions)
        hypothesis_ids = [s.hypothesis_id for s in sessions]
        return ReportSection(
            title="Overview",
            content=(
                f"Assessed {len(sessions)} hypothesis(es) "
                f"with {total_critiques} total critiques."
            ),
            data={"hypothesis_ids": hypothesis_ids, "total_critiques": total_critiques},
        )

    def _build_session_section(self, session: SessionRecord) -> ReportSection:
        score_data: dict[str, Any] = {}
        if session.score:
            score_data = {
                "composite_score": session.score.composite_score,
                "verdict": session.score.verdict.value,
                "breakdown": session.score.breakdown.model_dump(),
                "notes": session.score.notes,
            }
        return ReportSection(
            title=f"Hypothesis: {session.hypothesis_id}",
            content=self._format_session_content(session),
            data=score_data,
        )

    def _format_session_content(self, session: SessionRecord) -> str:
        lines = [f"Session {session.session_id}"]
        lines.append(f"Critiques received: {len(session.critiques)}")
        if session.score:
            lines.append(f"Composite score: {session.score.composite_score:.4f}")
            lines.append(f"Verdict: {session.score.verdict.value}")
        for critique in session.critiques:
            lines.append(f"  Agent {critique.agent_id} ({critique.role.value}):")
            if critique.challenges:
                lines.append(f"    Challenges: {', '.join(critique.challenges)}")
            if critique.weaknesses:
                lines.append(f"    Weaknesses: {', '.join(critique.weaknesses)}")
        return "\n".join(lines)

    def _build_verdict_summary(self, sessions: list[SessionRecord]) -> ReportSection:
        verdicts: dict[str, int] = {}
        for session in sessions:
            if session.score:
                v = session.score.verdict.value
                verdicts[v] = verdicts.get(v, 0) + 1
        return ReportSection(
            title="Verdict Distribution",
            content=json.dumps(verdicts, indent=2),
            data={"verdicts": verdicts},
        )

    def _build_summary_text(self, sessions: list[SessionRecord]) -> str:
        if not sessions:
            return "No sessions to summarize."
        scored = [s for s in sessions if s.score]
        if not scored:
            return "No scored sessions available."
        robust_count = sum(1 for s in scored if s.score and s.score.verdict == Verdict.ROBUST)
        weak_count = sum(
            1 for s in scored if s.score and s.score.verdict in (Verdict.WEAK, Verdict.REFUTED)
        )
        return (
            f"Of {len(scored)} hypotheses assessed, "
            f"{robust_count} rated robust and {weak_count} rated weak or refuted."
        )
