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


def _validate_claim_holds(source_code: str) -> ProofValidator:
    """Write source to temp file, run claim_holds check, return validator."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(source_code)
        f.flush()
        v = ProofValidator(f.name)
        v.check_claim_holds_computed()
    os.unlink(f.name)
    return v


CLAIM_HOLDS_VIA_COMPARE = '''
claim_holds = compare(age, ">", 70)
'''

CLAIM_HOLDS_HARDCODED_TRUE = '''
claim_holds = True
'''

CLAIM_HOLDS_HARDCODED_FALSE = '''
claim_holds = False
'''

CLAIM_HOLDS_VIA_VARIABLE = '''
has_support = False
claim_holds = has_support
'''

CLAIM_HOLDS_VIA_BOOL_EXPR = '''
claim_holds = n_confirming >= 3
'''

CLAIM_HOLDS_COMPOUND = '''
sc1_claim_holds = compare(val_sc1, ">=", 80)
sc2_claim_holds = compare(val_sc2, ">=", 3)
overall_claim_holds = sc1_claim_holds and sc2_claim_holds
'''

CLAIM_HOLDS_COMPOUND_HARDCODED = '''
sc1_claim_holds = True
overall_claim_holds = sc1_claim_holds and sc2_claim_holds
'''

SUBCLAIM_HOLDS_VIA_COMPARE = '''
subclaim_a_holds = compare(n_methods, "==", 0)
subclaim_b_holds = not (adult_plasticity and reopening)
overall_claim_holds = subclaim_a_holds and subclaim_b_holds
'''

SUBCLAIM_HOLDS_HARDCODED = '''
subclaim_a_holds = False
subclaim_b_holds = False
overall_claim_holds = subclaim_a_holds and subclaim_b_holds
'''


def test_claim_holds_via_compare_passes():
    v = _validate_claim_holds(CLAIM_HOLDS_VIA_COMPARE)
    assert len(v.issues) == 0

def test_claim_holds_hardcoded_true_fails():
    v = _validate_claim_holds(CLAIM_HOLDS_HARDCODED_TRUE)
    assert len(v.issues) > 0

def test_claim_holds_hardcoded_false_fails():
    v = _validate_claim_holds(CLAIM_HOLDS_HARDCODED_FALSE)
    assert len(v.issues) > 0

def test_claim_holds_via_variable_warns():
    v = _validate_claim_holds(CLAIM_HOLDS_VIA_VARIABLE)
    assert len(v.warnings) > 0

def test_claim_holds_via_bool_expr_warns():
    v = _validate_claim_holds(CLAIM_HOLDS_VIA_BOOL_EXPR)
    assert len(v.warnings) > 0

def test_claim_holds_compound_passes():
    v = _validate_claim_holds(CLAIM_HOLDS_COMPOUND)
    assert len(v.issues) == 0

def test_claim_holds_compound_hardcoded_fails():
    v = _validate_claim_holds(CLAIM_HOLDS_COMPOUND_HARDCODED)
    assert len(v.issues) > 0

def test_subclaim_holds_via_compare_passes():
    v = _validate_claim_holds(SUBCLAIM_HOLDS_VIA_COMPARE)
    assert any("subclaim_a_holds" in msg for msg in v.passed)

def test_subclaim_holds_hardcoded_fails():
    v = _validate_claim_holds(SUBCLAIM_HOLDS_HARDCODED)
    assert len(v.issues) > 0
