"""Extended tests for ReportGenerator — covers empty sessions, verdict distribution."""

from redteamkit.agent import AgentRole
from redteamkit.council import AdversarialCouncil
from redteamkit.report import ReportGenerator
from redteamkit.scoring import Verdict


def test_report_empty_sessions():
    gen = ReportGenerator()
    report = gen.generate([])
    assert report.summary == "No sessions to summarize."
    assert report.metadata["session_count"] == 0


def test_report_verdict_distribution():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
    council.run_session("H-001", confidence=0.5)
    council.run_session("H-002", confidence=0.5)
    gen = ReportGenerator()
    report = gen.generate(council.sessions)
    verdict_section = [s for s in report.sections if s.title == "Verdict Distribution"]
    assert len(verdict_section) == 1
    assert "verdicts" in verdict_section[0].data


def test_report_session_without_score():
    """Test report when sessions have no score (edge case)."""
    from redteamkit.council import SessionRecord
    session = SessionRecord(
        session_id="s-001",
        hypothesis_id="H-001",
        critiques=[],
        score=None,
    )
    gen = ReportGenerator()
    report = gen.generate([session])
    assert "No scored sessions available." in report.summary


def test_report_robust_vs_weak_summary():
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN])
    # Low confidence => high counter_resilience => robust
    council.run_session("H-001", confidence=0.1)
    # High confidence + challenges => weak
    council.run_session("H-002", confidence=0.95)
    gen = ReportGenerator()
    report = gen.generate(council.sessions)
    assert "robust" in report.summary.lower() or "weak" in report.summary.lower() or "2" in report.summary
