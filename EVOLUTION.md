# EVOLUTION.md — Edgecraft Iteration Log

## Repository: red-team-kit
## Date: 2026-03-23
## Protocol: Edgecraft v1.0 — 8 autonomous cycles

---

## Cycle 1: Test Coverage
**Timestamp**: 2026-03-23T06:00Z
**Layer focus**: L1/detection → L5/action → L6/grounding

**Findings**:
- `llm.py` at 67% coverage — sync `complete()`, async `acomplete()`, helper methods untested
- `council.py` at 94% — `__repr__`, `get_session(None)` paths missed
- `report.py` at 96% — empty sessions, no-score edge case
- `scoring.py` at 97% — extreme critiques, boundary values

**Actions**:
- Created `tests/conftest.py` with 8 shared fixtures (mock HTTP, sample critiques, etc.)
- Added `test_llm_extended.py` (9 tests) — mocked httpx for sync/async paths
- Added `test_council_extended.py` (5 tests) — repr, not-found, multiple sessions
- Added `test_report_extended.py` (4 tests) — empty sessions, no-score, verdict distribution
- Added `test_scoring_extended.py` (6 tests) — extreme values, boundary conditions

**Result**: 56 tests passing, coverage 91% → 99%

---

## Cycle 2: Error Hardening
**Timestamp**: 2026-03-23T06:03Z
**Layer focus**: L3/sub-noise → L5/action

**Findings**:
- `RedTeamAgent.critique()` accepts empty string hypothesis_id silently
- `RedTeamAgent.critique()` accepts confidence outside [0,1] (Pydantic catches it late)
- `AdversarialCouncil.run_session()` no guard against empty agent list
- `LLMClient.complete()` no message validation, no retry on transient failures

**Actions**:
- Added validation guards to `agent.py`, `council.py`
- Added message validation to `LLMClient` — checks non-empty, dict type, required keys
- Added retry logic (3 retries, exponential backoff) for timeout/connect/HTTP errors
- Added `test_error_hardening.py` (13 tests)

**Result**: 69 tests passing, all edge cases now raise clear `ValueError`/`TypeError`

---

## Cycle 3: Performance
**Timestamp**: 2026-03-23T06:06Z
**Layer focus**: L4/conjecture → L6/grounding

**Findings**:
- Council `run_session()` evaluates agents sequentially — parallelizable
- No batch processing capability for multiple hypotheses
- Agent critiques are CPU-bound (fast), but LLM calls (when integrated) will be I/O-bound

**Actions**:
- Added `arun_session()` — async parallel critiques with `asyncio.gather` + semaphore
- Added `run_batch()` — `ThreadPoolExecutor` for parallel hypothesis evaluation
- Added `test_performance.py` (9 tests) — async, batch, timing assertions

**Result**: 78 tests passing, batch of 10 hypotheses completes <2s

---

## Cycle 4: Security
**Timestamp**: 2026-03-23T06:08Z
**Layer focus**: L2/noise → L5/action

**Findings**:
- 0 hardcoded API keys, tokens, or secrets in source
- 0 injection vectors (no eval, exec, os.system, subprocess)
- 0 SQL injection points (no database layer)
- False positives: `test-key-000` in conftest, `risk-measurement` YAML tag
- Missing `.gitignore` — risk of committing `.env` or credential files
- `LLMConfig.base_url` accepted any scheme including `file://` (SSRF risk)

**Actions**:
- Created `.gitignore` blocking secrets, build artifacts, IDE files
- Added `field_validator` on `base_url` — only `https://` and `http://` allowed
- Added `test_security.py` (12 tests) — secret handling, SSRF prevention, injection resistance

**Result**: 90 tests passing, SSRF vector closed, secret hygiene verified

---

## Cycle 5: CI/CD
**Timestamp**: 2026-03-23T06:10Z
**Layer focus**: L5/action

**Actions**:
- Created `.github/workflows/ci.yml`:
  - Python 3.12 on ubuntu-latest
  - `ruff check` for linting
  - `pytest -v --cov` for testing
  - 90% coverage threshold gate
- Created `.pre-commit-config.yaml`:
  - ruff (lint + format)
  - mypy (type checking)

**Result**: CI pipeline active on every push and PR

---

## Cycle 6: Property-Based Testing
**Timestamp**: 2026-03-23T06:11Z
**Layer focus**: L3/sub-noise → L6/grounding

**Findings**:
- Hypothesis library ran ~225 random examples across 6 strategies
- Zero failures found — code handles all valid random inputs correctly

**Tests added** (9 property tests):
- `ScoreBreakdown.composite` always in [0.0, 1.0]
- Composite matches weighted formula for any 4 floats in [0,1]
- Scorer returns valid verdict for any critique combination
- Empty critiques never crash the scorer
- Agent critique preserves all fields through round-trip
- Reset always clears regardless of critique count
- JSON serialization → deserialization preserves `Critique` equality
- Dict serialization → deserialization preserves `Critique` equality
- Report generation stable for 0–10 sessions

**Result**: 99 tests passing, no new edge cases discovered

---

## Cycle 7: Examples + Documentation
**Timestamp**: 2026-03-23T06:12Z
**Layer focus**: L5/action

**Actions**:
- Created `examples/basic_council.py` — single hypothesis evaluation with full output
- Created `examples/batch_evaluation.py` — parallel batch processing with report generation
- Created `examples/custom_scoring.py` — configurable thresholds and baseline strength
- All 3 examples tested and verified working
- Added docstrings to all 23 public classes, methods, and properties

**Result**: Full API surface documented, runnable examples for all key workflows

---

## Cycle 8: Release Engineering
**Timestamp**: 2026-03-23T06:13Z
**Layer focus**: L5/action → L7/flywheel

**Actions**:
- Updated `pyproject.toml` — added author, expanded dev dependencies
- Created `Makefile` — test, lint, format, security, clean targets
- Created `CHANGELOG.md` — all improvements from cycles 1–7
- Created `AGENTS.md` — autonomous development protocol documentation
- Created `EVOLUTION.md` — this file
- Tagged `v0.1.0`

---

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Tests | 32 | 99 |
| Coverage | 91% | 99% |
| Input validation | None | All public APIs |
| Retry logic | None | 3x exponential backoff |
| Security issues | 1 (SSRF) | 0 |
| CI/CD | None | GitHub Actions + pre-commit |
| Property tests | 0 | 9 (225+ random examples) |
| Examples | 0 | 3 working scripts |
| Docstring coverage | Partial | 100% public API |

**Total commits**: 20 (17 Edgecraft + 3 original)
**Files changed**: 20+
**Lines added**: ~1,500+
