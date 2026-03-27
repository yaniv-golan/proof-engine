"""Tests for validate_proof.py — validator improvements."""
import os
import tempfile
from scripts.validate_proof import ProofValidator


def _validate(source_code: str) -> ProofValidator:
    """Write source to temp file, run validator, return it."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_rule6_independent_crosscheck()
    os.unlink(f.name)
    return v


DESCRIPTIVE_KEYS_SOURCE = '''
empirical_facts = {
    "azevedo_2009": {
        "quote": "...", "url": "...", "source_name": "Azevedo et al.",
    },
    "oxford_brain_2025": {
        "quote": "...", "url": "...", "source_name": "Oxford",
    },
    "ucla_bri": {
        "quote": "...", "url": "...", "source_name": "UCLA",
    },
}
'''

SINGLE_SOURCE = '''
empirical_facts = {
    "only_source": {
        "quote": "...", "url": "...", "source_name": "Only One",
    },
}
'''

TEMPLATE_KEYS_SOURCE = '''
empirical_facts = {
    "source_a": {
        "quote": "...", "url": "...", "source_name": "Source A",
    },
    "source_b": {
        "quote": "...", "url": "...", "source_name": "Source B",
    },
}
'''

NO_EMPIRICAL = '''
from scripts.computations import compare
result = compare(5, ">", 3)
'''


def test_rule6_descriptive_keys_counted():
    """Descriptive keys (azevedo_2009, etc.) should be counted as 3 sources."""
    v = _validate(DESCRIPTIVE_KEYS_SOURCE)
    assert len(v.issues) == 0
    assert any("3 distinct" in msg for msg in v.passed)


def test_rule6_single_source_warns():
    """Single source should produce a warning."""
    v = _validate(SINGLE_SOURCE)
    assert len(v.warnings) > 0


def test_rule6_template_keys_counted():
    """Template-style keys (source_a, source_b) should still work."""
    v = _validate(TEMPLATE_KEYS_SOURCE)
    assert len(v.issues) == 0
    assert any("2 distinct" in msg for msg in v.passed)


def test_rule6_no_empirical_pure_math():
    """Pure math proof should pass without sources."""
    v = _validate(NO_EMPIRICAL)
    assert len(v.issues) == 0
