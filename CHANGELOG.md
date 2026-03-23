# Changelog

## v0.1.0 — 2026-03-23

First release after 8 Edgecraft autonomous iteration cycles.

### Cycle 1: Test Coverage
- Created `conftest.py` with shared fixtures and mock helpers
- Added extended test suites for LLM (9 tests), council (5), report (4), scoring (6)
- Coverage improved from 91% to 99% across all modules

### Cycle 2: Error Hardening
- Input validation on `RedTeamAgent.critique()` — rejects empty hypothesis ID, invalid confidence
- Input validation on `AdversarialCouncil.run_session()` — rejects empty ID, empty agent list
- LLM client: message validation (non-empty, proper structure, non-blank content)
- Retry logic with exponential backoff (3 retries) on timeout, connect error, HTTP errors
- 13 error hardening tests added

### Cycle 3: Performance
- `arun_session()` — async parallel agent critiques with configurable semaphore
- `run_batch()` — thread-pool parallel evaluation of multiple hypotheses
- 9 performance tests verifying batch and async execution paths

### Cycle 4: Security
- Security scan: 0 hardcoded secrets, 0 injection vectors found
- URL scheme validation on `LLMConfig.base_url` — prevents SSRF (ftp://, file:// rejected)
- `.gitignore` blocking `.env`, `*.pem`, `credentials.json`
- 12 security tests covering secret handling, URL validation, input sanitization

### Cycle 5: CI/CD
- GitHub Actions workflow: Python 3.12, ruff lint, pytest with 90% coverage gate
- Pre-commit config: ruff (lint + format) and mypy hooks

### Cycle 6: Property-Based Testing
- 9 Hypothesis property tests across 6 strategies
- Verifies: score composites always in [0,1], weighted formula correctness, verdict validity,
  critique serialization round-trips, report generation stability

### Cycle 7: Examples + Documentation
- 3 working examples: `basic_council.py`, `batch_evaluation.py`, `custom_scoring.py`
- Complete docstrings on all 23 public classes, methods, and properties

### Cycle 8: Release Engineering
- Updated `pyproject.toml` with author, full dev dependencies
- Created `Makefile` with test, lint, format, security, clean targets
- Created `CHANGELOG.md`, `AGENTS.md`, `EVOLUTION.md`
- Tagged v0.1.0
