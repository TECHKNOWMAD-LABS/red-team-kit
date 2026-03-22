"""RedTeamKit — Adversarial hypothesis testing framework."""

from redteamkit.agent import RedTeamAgent
from redteamkit.council import AdversarialCouncil
from redteamkit.llm import LLMClient
from redteamkit.report import ReportGenerator
from redteamkit.scoring import HypothesisScorer

__all__ = [
    "AdversarialCouncil",
    "HypothesisScorer",
    "LLMClient",
    "RedTeamAgent",
    "ReportGenerator",
]
__version__ = "0.1.0"
