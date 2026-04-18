"""Tests for computations.py — cross_check tolerance fixes."""
import typing
import pytest
from scripts.computations import (
    cross_check, compare,
    apply_verdict_qualifier, VALID_BASE_VERDICTS, QUALIFIABLE_VERDICTS,
    emit_proof_summary, KNOWN_SUMMARY_KEYS,
)
from scripts.proof_types import ProofData, ProofDataV3


def test_cross_check_exact_match_zero_tolerance_absolute():
    assert cross_check(3, 3, tolerance=0, mode="absolute") is True

def test_cross_check_exact_match_zero_tolerance_relative():
    assert cross_check(5.0, 5.0, tolerance=0, mode="relative") is True

def test_cross_check_near_match_zero_tolerance_absolute():
    assert cross_check(3, 4, tolerance=0, mode="absolute") is False

def test_cross_check_exact_match_small_tolerance():
    assert cross_check(3, 3, tolerance=0.01, mode="absolute") is True

def test_cross_check_within_tolerance():
    assert cross_check(9.883, 9.9, tolerance=0.05, mode="absolute") is True

def test_cross_check_outside_tolerance():
    assert cross_check(9.883, 9.9, tolerance=0.01, mode="absolute") is False

def test_cross_check_relative_within():
    assert cross_check(100, 101, tolerance=0.02, mode="relative") is True

def test_cross_check_relative_outside():
    assert cross_check(100, 110, tolerance=0.02, mode="relative") is False

def test_cross_check_both_zero():
    assert cross_check(0, 0, tolerance=0, mode="absolute") is True
    assert cross_check(0, 0, tolerance=0, mode="relative") is True


def test_compare_label_in_output(capsys):
    """compare() with label should print the label instead of 'compare'."""
    compare(3, ">=", 2, label="SC1: source count")
    captured = capsys.readouterr()
    assert "SC1: source count" in captured.out
    assert "3 >= 2 = True" in captured.out

def test_compare_no_label_prints_compare(capsys):
    compare(3, ">=", 2)
    captured = capsys.readouterr()
    assert "compare:" in captured.out

def test_compare_label_none_prints_compare(capsys):
    compare(3, ">=", 2, label=None)
    captured = capsys.readouterr()
    assert "compare:" in captured.out


def test_cross_check_unknown_mode_raises():
    """Unknown mode should raise ValueError, not silently use absolute."""
    with pytest.raises(ValueError, match="Unknown mode"):
        cross_check(1.0, 2.0, tolerance=0.5, mode="realtive")


def test_cross_check_valid_modes_still_work():
    """Explicit 'absolute' and 'relative' modes should still work."""
    assert cross_check(1.0, 1.0, tolerance=0, mode="absolute") is True
    assert cross_check(1.0, 1.0, tolerance=0, mode="relative") is True


# ---------------------------------------------------------------------------
# apply_verdict_qualifier tests
# ---------------------------------------------------------------------------

def test_apply_verdict_qualifier_proved_unverified():
    assert apply_verdict_qualifier("PROVED", True) == "PROVED (with unverified citations)"


def test_apply_verdict_qualifier_proved_verified():
    assert apply_verdict_qualifier("PROVED", False) == "PROVED"


def test_apply_verdict_qualifier_disproved_unverified():
    assert apply_verdict_qualifier("DISPROVED", True) == "DISPROVED (with unverified citations)"


def test_apply_verdict_qualifier_supported_unverified():
    assert apply_verdict_qualifier("SUPPORTED", True) == "SUPPORTED (with unverified citations)"


def test_apply_verdict_qualifier_partially_verified_unverified():
    """PARTIALLY VERIFIED never gets the suffix — it already signals incompleteness."""
    assert apply_verdict_qualifier("PARTIALLY VERIFIED", True) == "PARTIALLY VERIFIED"


def test_apply_verdict_qualifier_undetermined_unverified():
    """UNDETERMINED never gets the suffix."""
    assert apply_verdict_qualifier("UNDETERMINED", True) == "UNDETERMINED"


def test_apply_verdict_qualifier_invalid_raises():
    with pytest.raises(ValueError, match="Invalid base verdict"):
        apply_verdict_qualifier("PARTIALLY VERIFIED (with unverified citations)", True)


def test_apply_verdict_qualifier_typo_raises():
    with pytest.raises(ValueError, match="Invalid base verdict"):
        apply_verdict_qualifier("PROOVED", False)


def test_valid_base_verdicts_is_five():
    assert len(VALID_BASE_VERDICTS) == 5


def test_qualifiable_verdicts_is_three():
    assert len(QUALIFIABLE_VERDICTS) == 3
    assert QUALIFIABLE_VERDICTS == {"PROVED", "DISPROVED", "SUPPORTED"}


# ---------------------------------------------------------------------------
# emit_proof_summary tests
# ---------------------------------------------------------------------------

def test_emit_proof_summary_valid(capsys):
    """Valid summary prints marker + JSON."""
    summary = {
        "fact_registry": {},
        "claim_formal": {"subject": "X", "property": "Y", "operator": ">", "threshold": 0},
        "claim_natural": "Test claim",
        "verdict": "PROVED",
        "key_results": {"value": 1},
        "generator": {"name": "proof-engine", "version": "1.0.0",
                       "repo": "https://github.com/test", "generated_at": "2026-01-01"},
    }
    emit_proof_summary(summary)
    captured = capsys.readouterr()
    assert "=== PROOF SUMMARY (JSON) ===" in captured.out
    assert '"verdict": "PROVED"' in captured.out


def test_emit_proof_summary_unknown_key_raises():
    """Unknown keys should be rejected with a clear message."""
    summary = {
        "fact_registry": {},
        "claim_natural": "Test",
        "verdict": "PROVED",
        "key_results": {},
        "generator": {},
        "claim_formal": {},
        "computed_values": {"x": 1},
    }
    with pytest.raises(ValueError, match="Unknown keys.*computed_values"):
        emit_proof_summary(summary)


def test_emit_proof_summary_all_optional_keys_accepted(capsys):
    """All ProofData optional keys should be accepted."""
    summary = {
        "fact_registry": {},
        "claim_formal": {},
        "claim_natural": "Test",
        "verdict": "PROVED",
        "key_results": {},
        "generator": {},
        "citations": {},
        "extractions": {},
        "cross_checks": [],
        "adversarial_checks": [],
        "search_registry": {},
        "data_value_verification": {},
        "date_note": "As of 2026",
        "sub_claim_results": [],
        "verdict_note": "Note",
        "verdict_reason": "Reason",
    }
    emit_proof_summary(summary)
    captured = capsys.readouterr()
    assert "=== PROOF SUMMARY (JSON) ===" in captured.out


def test_known_summary_keys_matches_proof_data():
    """KNOWN_SUMMARY_KEYS must cover both ProofData (v1/v2) and ProofDataV3 TypedDicts."""
    expected = set(typing.get_type_hints(ProofData).keys()) | set(typing.get_type_hints(ProofDataV3).keys())
    assert KNOWN_SUMMARY_KEYS == expected


# ---------------------------------------------------------------------------
# apply_verdict_qualifier — structured (as_string=False) tests
# ---------------------------------------------------------------------------

def test_apply_verdict_qualifier_default_returns_string():
    """Default (as_string=True) preserves backward compat for existing proof.py files."""
    from scripts.computations import apply_verdict_qualifier
    result = apply_verdict_qualifier("PROVED", any_unverified=False)
    assert isinstance(result, str)
    assert result == "PROVED"


def test_apply_verdict_qualifier_default_with_unverified():
    from scripts.computations import apply_verdict_qualifier
    result = apply_verdict_qualifier("PROVED", any_unverified=True)
    assert result == "PROVED (with unverified citations)"


def test_apply_verdict_qualifier_as_dict():
    """as_string=False returns structured dict for v3 ProofSummaryBuilder."""
    from scripts.computations import apply_verdict_qualifier
    result = apply_verdict_qualifier("PROVED", any_unverified=False, as_string=False)
    assert isinstance(result, dict)
    assert result["value"] == "PROVED"
    assert result["qualified"] is False
    assert result["qualifier"] is None


def test_apply_verdict_qualifier_dict_with_unverified():
    from scripts.computations import apply_verdict_qualifier
    result = apply_verdict_qualifier("PROVED", any_unverified=True, as_string=False)
    assert result["value"] == "PROVED"
    assert result["qualified"] is True
    assert result["qualifier"] == "unverified_citations"


def test_apply_verdict_qualifier_partial_no_suffix():
    from scripts.computations import apply_verdict_qualifier
    result = apply_verdict_qualifier("PARTIALLY VERIFIED", any_unverified=True, as_string=False)
    assert result["value"] == "PARTIALLY VERIFIED"
    assert result["qualified"] is False
    assert result["qualifier"] is None


# ---------------------------------------------------------------------------
# prove_holds() — theorem-mode verdict helper
# ---------------------------------------------------------------------------


def test_prove_holds_true_returns_true():
    from scripts.computations import prove_holds
    assert prove_holds(True) is True


def test_prove_holds_false_returns_false():
    from scripts.computations import prove_holds
    assert prove_holds(False) is False


def test_prove_holds_none_raises_type_error():
    from scripts.computations import prove_holds
    with pytest.raises(TypeError, match="None"):
        prove_holds(None)


def test_prove_holds_truthy_values_coerce_via_bool():
    """bool() coercion means truthy values return True. Authors should avoid this
    by composing from real booleans, but the function won't silently fail."""
    from scripts.computations import prove_holds
    # All truthy → True (via bool())
    assert prove_holds("non-empty") is True
    assert prove_holds(1) is True
    assert prove_holds(2) is True
    assert prove_holds([1, 2]) is True
    # All falsy → False
    assert prove_holds("") is False
    assert prove_holds(0) is False
    assert prove_holds([]) is False


def test_prove_holds_numpy_bool_true():
    """np.bool_(True) should be treated as True — critical for numpy-heavy proofs."""
    np = pytest.importorskip("numpy")
    from scripts.computations import prove_holds
    assert prove_holds(np.bool_(True)) is True
    assert prove_holds(np.bool_(False)) is False
    assert prove_holds(np.array([True, True]).all()) is True


def test_prove_holds_prints_holds_format(capsys):
    from scripts.computations import prove_holds
    prove_holds(True, label="my theorem")
    captured = capsys.readouterr()
    assert "my theorem:" in captured.out
    assert "holds" in captured.out
    # Should NOT print threshold or operator noise
    assert "==" not in captured.out
    assert "None" not in captured.out


def test_compare_unchanged_regression():
    """Ensure compare() still works for all 6 operators."""
    assert compare(5, ">", 3) is True
    assert compare(3, ">=", 3) is True
    assert compare(3, "<", 5) is True
    assert compare(3, "<=", 3) is True
    assert compare(3, "==", 3) is True
    assert compare(3, "!=", 5) is True
