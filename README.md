# Red Team Kit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

Adversarial hypothesis testing framework. A council of red-team agents challenges your strategic, financial, or operational hypotheses and scores them for robustness.

## Features

- **Six adversarial agent roles** — Devil's Advocate, Contrarian, Stress Tester, Assumption Hunter, Blind Spot Finder, Scenario Explorer — each attacks hypotheses from a distinct cognitive angle.
- **Quantified scoring** — four weighted dimensions (evidence strength, assumption quality, counter-resilience, internal consistency) produce a composite 0–1 score with a `ROBUST / CONDITIONAL / WEAK / REFUTED` verdict.
- **52 production hypotheses** — curated YAML corpus spanning financial, market, strategic, operational, temporal, and cross-domain categories for benchmarking and regression testing.
- **Pluggable LLM backend** — defaults to OpenAI-compatible APIs; swap any endpoint via env vars (`REDTEAM_LLM_BASE_URL`, `REDTEAM_LLM_MODEL`, `REDTEAM_LLM_API_KEY`).
- **Structured reports** — export session results as JSON or dict with per-hypothesis breakdowns and verdict distribution summaries.
- **Composable council** — add or remove agents at runtime; run single-hypothesis sessions or batch the full hypothesis corpus.

## Quick Start

```bash
pip install -e ".[dev]"
export REDTEAM_LLM_API_KEY="sk-..."   # OpenAI or compatible
```

```python
from redteamkit.council import AdversarialCouncil
from redteamkit.report import ReportGenerator

# Define a hypothesis
hypothesis = {
    "id": "h001",
    "title": "Enterprise pricing at $500/seat is defensible",
    "statement": "Customers will accept $500/seat pricing given the ROI demonstrated in pilots.",
    "assumptions": ["Pilots are representative of production load", "Competitors won't reprice"],
}

# Run the adversarial council
council = AdversarialCouncil()
session = council.run_session(hypothesis)

# Score and report
report = ReportGenerator().generate(session)
print(report.summary)         # "Verdict: CONDITIONAL (score: 0.61)"
print(report.to_json())       # Full JSON report
```

Run the test suite:

```bash
pytest
```

## Architecture

```
red-team-kit/
├── redteamkit/
│   ├── agent.py      # AgentRole enum, Critique model, RedTeamAgent
│   ├── council.py    # AdversarialCouncil — orchestrates agents, holds SessionRecord
│   ├── scoring.py    # HypothesisScorer — 4-dimension weighted scoring, Verdict enum
│   ├── llm.py        # LLMConfig, LLMClient (sync/async httpx), prompt builders
│   └── report.py     # ReportGenerator — JSON/dict export, verdict distribution
├── hypotheses/       # 52 YAML hypothesis files (financial, market, strategic, …)
└── tests/            # pytest suite — 6 modules, full unit coverage
```

**Data flow:**

```
Hypothesis YAML
      │
      ▼
AdversarialCouncil.run_session()
      │  spawns one RedTeamAgent per role
      │  each agent calls LLMClient → returns Critique
      ▼
HypothesisScorer.score(critiques)
      │  evidence_strength  × 0.30
      │  assumption_quality × 0.25
      │  counter_resilience × 0.25
      │  internal_consistency × 0.20
      ▼
SessionRecord  →  ReportGenerator  →  JSON / dict
```

## Configuration

| Env var | Default | Description |
|---|---|---|
| `REDTEAM_LLM_API_KEY` | — | API key (required for LLM calls) |
| `REDTEAM_LLM_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible base URL |
| `REDTEAM_LLM_MODEL` | `gpt-4o` | Model name |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch conventions, test requirements, and the PR checklist.

---

Built by [TechKnowMad Labs](https://techknowmad.ai)
