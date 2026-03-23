# AGENTS.md — Autonomous Development Protocol

## Overview

This repository was developed using the **Edgecraft Protocol**, an autonomous multi-cycle
development methodology that iterates through 8 structured layers (L0–L7) to systematically
improve code quality, security, performance, and reliability.

## Protocol: Edgecraft Layers

| Layer | Name | Purpose |
|-------|------|---------|
| L0 | Attention | Identify what to focus on |
| L1 | Detection | Detect gaps, missing coverage, untested paths |
| L2 | Noise | Filter signal from noise (false positives, non-issues) |
| L3 | Sub-noise | Find subtle bugs that standard scans miss |
| L4 | Conjecture | Form hypotheses about improvements (performance, design) |
| L5 | Action | Implement the fix, feature, or improvement |
| L6 | Grounding | Verify with tests, measurements, and evidence |
| L7 | Flywheel | Document patterns reusable across repositories |

## Cycle Structure

Each cycle is a complete L0–L7 pass focused on one quality dimension:

1. **Test Coverage** — Find and fill gaps in test coverage
2. **Error Hardening** — Break the code with adversarial inputs, then fix
3. **Performance** — Identify parallelization and caching opportunities
4. **Security** — Scan for secrets, injection vectors, SSRF risks
5. **CI/CD** — Automate quality gates (lint, test, coverage threshold)
6. **Property-Based Testing** — Verify invariants with random inputs (Hypothesis)
7. **Examples + Docs** — Working examples and complete docstring coverage
8. **Release Engineering** — Package metadata, changelog, Makefile, tagging

## Agent Behavior

- **Fully autonomous**: No human intervention required during cycles
- **Self-healing**: If tests fail after a change, the agent fixes them before committing
- **Incremental commits**: Each change is committed separately with an Edgecraft layer prefix
- **Push after each cycle**: Remote stays in sync throughout the process
- **Evidence-based**: Performance claims include measurements; coverage claims include percentages

## Commit Convention

All commits follow the pattern:
```
L{N}/{layer-name}: {description}
```

Examples:
- `L1/detection: identify untested modules at 0% coverage`
- `L3/sub-noise: hypothesis found edge case — [description]`
- `L5/action: add input validation and error handling`
- `L6/grounding: N tests passing, coverage improved to N%`

## Reproduction

To run the same protocol on another repository:
1. Clone the target repo
2. Execute 8 cycles in sequence, each with a specific focus area
3. Run tests after every code change; fix failures before committing
4. Push after each cycle completes
5. Tag the final state as a version release

## Tools Used

- **pytest** + **pytest-cov** — Unit testing and coverage measurement
- **hypothesis** — Property-based testing with random input generation
- **ruff** — Fast Python linting and formatting
- **mypy** — Static type checking
- **GitHub Actions** — CI/CD pipeline
- **pre-commit** — Git hook automation
