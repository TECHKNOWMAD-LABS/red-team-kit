"""Tests for the ReportGenerator module."""

import json

from redteamkit.agent import AgentRole
from redteamkit.council import AdversarialCouncil
from redteamkit.report import Report, ReportGenerator


def _make_sessions(count: int = 2):
    council = AdversarialCouncil(roles=[AgentRole.CONTRARIAN, AgentRole.STRESS_TESTER])
    for i in range(count):
        council.run_session(f"H-RPT-{i:03d}", confidence=0.5)
    return council.sessions


def test_report_generation():
    sessions = _make_sessions(2)
    gen = ReportGenerator()
    report = gen.generate(sessions)
    assert isinstance(report, Report)
    assert len(report.sections) > 0
    assert report.metadata["session_count"] == 2


def test_report_to_json():
    sessions = _make_sessions(1)
    gen = ReportGenerator(title="Test Report")
    report = gen.generate(sessions)
    raw = report.to_json()
    parsed = json.loads(raw)
    assert parsed["title"] == "Test Report"


def test_report_to_dict():
    sessions = _make_sessions(1)
    gen = ReportGenerator()
    report = gen.generate(sessions)
    d = report.to_dict()
    assert "sections" in d
    assert "summary" in d


def test_report_summary_text():
    sessions = _make_sessions(3)
    gen = ReportGenerator()
    report = gen.generate(sessions)
    assert "3" in report.summary
