.PHONY: test lint format security clean

test:
	python -m pytest -v --tb=short --cov=redteamkit --cov-report=term-missing

lint:
	ruff check redteamkit/ tests/

format:
	ruff format redteamkit/ tests/

security:
	@echo "=== Secret scan ==="
	@grep -rn "sk-\|ghp_\|gho_\|AKIA\|AIza" --include="*.py" redteamkit/ tests/ || echo "No secrets found"
	@echo "=== Injection scan ==="
	@grep -rn "eval(\|exec(\|os\.system\|subprocess\." --include="*.py" redteamkit/ || echo "No injection vectors found"

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .coverage htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
