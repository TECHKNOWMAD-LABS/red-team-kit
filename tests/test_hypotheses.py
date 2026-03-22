"""Tests for YAML hypothesis file integrity."""

from pathlib import Path

import yaml

HYPOTHESES_DIR = Path(__file__).parent.parent / "hypotheses"

EXPECTED_CATEGORIES = {
    "financial": 12,
    "market": 8,
    "operational": 8,
    "strategic": 8,
    "temporal": 4,
    "cross_domain": 4,
    "meta": 4,
    "synthesis": 4,
}

REQUIRED_FIELDS = {
    "id", "category", "title", "statement", "assumptions",
    "evidence_required", "risk_level", "tags",
}


def _load_all_hypotheses() -> list[tuple[Path, dict]]:
    results = []
    for yaml_path in sorted(HYPOTHESES_DIR.rglob("*.yaml")):
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        results.append((yaml_path, data))
    return results


def test_total_hypothesis_count():
    files = list(HYPOTHESES_DIR.rglob("*.yaml"))
    assert len(files) == 52


def test_category_file_counts():
    for category, expected_count in EXPECTED_CATEGORIES.items():
        cat_dir = HYPOTHESES_DIR / category
        assert cat_dir.exists(), f"Missing category directory: {category}"
        files = list(cat_dir.glob("*.yaml"))
        assert len(files) == expected_count, (
            f"{category}: expected {expected_count} files, found {len(files)}"
        )


def test_all_hypotheses_have_required_fields():
    for path, data in _load_all_hypotheses():
        missing = REQUIRED_FIELDS - set(data.keys())
        assert not missing, f"{path.name} missing fields: {missing}"


def test_no_hypothesis_mentions_forbidden_terms():
    for path, data in _load_all_hypotheses():
        content = yaml.dump(data).lower()
        assert "via negativa" not in content, f"{path} contains forbidden term"


def test_risk_levels_valid():
    valid = {"high", "medium", "low"}
    for path, data in _load_all_hypotheses():
        assert data["risk_level"] in valid, (
            f"{path.name} has invalid risk_level: {data['risk_level']}"
        )
