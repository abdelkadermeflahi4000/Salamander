"""
Tests for loading patterns from YAML (future-proof).
Currently patterns are in Python. These tests will activate
when you move them to data/patterns/*.yaml.
"""

from __future__ import annotations

import pytest
from pathlib import Path

# Adjust if your YAML location is different
YAML_DIR = Path(__file__).resolve().parents[2] / "data" / "patterns"


@pytest.mark.skipif(not YAML_DIR.exists(), reason="YAML patterns directory not found")
def test_yaml_files_exist():
    files = list(YAML_DIR.glob("*.yaml")) + list(YAML_DIR.glob("*.yml"))
    assert len(files) > 0, "No YAML pattern files found"


@pytest.mark.skipif(not YAML_DIR.exists(), reason="YAML patterns directory not found")
def test_yaml_readable():
    import yaml  # requires PyYAML

    for path in YAML_DIR.glob("*.yaml"):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None


def test_python_patterns_still_work():
    """Fallback: as long as patterns live in Python, this must pass."""
    from salamander.core.patterns import ALL_PATTERNS
    assert len(ALL_PATTERNS) > 0
