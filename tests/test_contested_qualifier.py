"""Regression tests for contested qualifier verdict logic.

These tests validate the verdict code pattern from template-compound.md's
contested qualifier adaptation. They don't import template code (it's Markdown);
instead they replicate the verdict logic inline and verify the critical paths.
"""
import pytest


def contested_qualifier_verdict(
    sc1_holds: bool,
    sc2_holds: bool,
    any_breaks: bool = False,
    any_coi_override: bool = False,
    any_unverified: bool = False,
) -> str:
    """Replicate the contested qualifier verdict logic from template-compound.md."""
    n_holding = sum([sc1_holds, sc2_holds])
    n_total = 2
    claim_holds = n_holding == n_total
    is_contested_qualifier = True  # Always true for these tests

    if any_breaks:
        verdict = "UNDETERMINED"
    elif any_coi_override:
        verdict = "UNDETERMINED"
    elif is_contested_qualifier and sc1_holds and not sc2_holds:
        if any_unverified:
            verdict = "DISPROVED (with unverified citations)"
        else:
            verdict = "DISPROVED"
    elif not claim_holds and n_holding > 0:
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds and n_holding == 0:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    return verdict


class TestContestedQualifierVerdict:
    """Core contested qualifier verdict paths."""

    def test_sc1_holds_sc2_fails_is_disproved(self):
        """The critical regression: SC1 holds + SC2 fails must produce DISPROVED,
        not PARTIALLY VERIFIED."""
        assert contested_qualifier_verdict(sc1_holds=True, sc2_holds=False) == "DISPROVED"

    def test_sc1_holds_sc2_fails_unverified(self):
        """SC1 holds + SC2 fails with unverified citations."""
        assert contested_qualifier_verdict(
            sc1_holds=True, sc2_holds=False, any_unverified=True
        ) == "DISPROVED (with unverified citations)"

    def test_both_hold_is_proved(self):
        """Both sub-claims hold -> PROVED."""
        assert contested_qualifier_verdict(sc1_holds=True, sc2_holds=True) == "PROVED"

    def test_both_hold_unverified(self):
        """Both hold with unverified citations."""
        assert contested_qualifier_verdict(
            sc1_holds=True, sc2_holds=True, any_unverified=True
        ) == "PROVED (with unverified citations)"

    def test_both_fail_is_undetermined(self):
        """Neither sub-claim holds -> UNDETERMINED."""
        assert contested_qualifier_verdict(sc1_holds=False, sc2_holds=False) == "UNDETERMINED"

    def test_breaks_proof_overrides(self):
        """any_breaks forces UNDETERMINED regardless of sub-claim state."""
        assert contested_qualifier_verdict(
            sc1_holds=True, sc2_holds=False, any_breaks=True
        ) == "UNDETERMINED"

    def test_coi_override_forces_undetermined(self):
        """COI override forces UNDETERMINED even when SC1 holds + SC2 fails."""
        assert contested_qualifier_verdict(
            sc1_holds=True, sc2_holds=False, any_coi_override=True
        ) == "UNDETERMINED"
