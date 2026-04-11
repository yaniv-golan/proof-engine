"""Regression tests for COI quorum guard in verdict logic.

These tests validate the COI majority check from template-qualitative.md
and template-compound.md. They replicate the verdict logic inline (same
pattern as test_contested_qualifier.py) and verify that COI override
does NOT trigger when the verified source count is below the threshold.
"""
import pytest


def qualitative_coi_verdict(
    n_confirmed: int,
    threshold: int,
    coi_majority: int,
    any_breaks: bool = False,
    any_unverified: bool = False,
) -> str:
    """Replicate qualitative template verdict logic with COI quorum guard."""
    claim_holds = n_confirmed >= threshold

    # COI quorum guard: only apply when n_confirmed meets threshold
    coi_override = n_confirmed >= threshold and coi_majority > n_confirmed / 2

    if any_breaks:
        verdict = "UNDETERMINED"
    elif coi_override:
        verdict = "UNDETERMINED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    else:
        verdict = "UNDETERMINED"

    return verdict


def compound_coi_verdict(
    n_sc1: int,
    n_sc2: int,
    sc1_threshold: int,
    sc2_threshold: int,
    sc1_coi_majority: int,
    sc2_coi_majority: int,
    any_breaks: bool = False,
    any_unverified: bool = False,
) -> str:
    """Replicate compound template verdict logic with COI quorum guard."""
    sc1_holds = n_sc1 >= sc1_threshold
    sc2_holds = n_sc2 >= sc2_threshold
    n_holding = sum([sc1_holds, sc2_holds])
    n_total = 2
    claim_holds = n_holding == n_total

    # Per-sub-claim COI quorum guard
    sc1_coi_override = n_sc1 >= sc1_threshold and sc1_coi_majority > n_sc1 / 2
    sc2_coi_override = n_sc2 >= sc2_threshold and sc2_coi_majority > n_sc2 / 2
    any_coi_override = sc1_coi_override or sc2_coi_override

    if any_breaks:
        verdict = "UNDETERMINED"
    elif any_coi_override:
        verdict = "UNDETERMINED"
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


class TestQualitativeCOIQuorum:
    """COI quorum guard for qualitative template."""

    def test_coi_override_triggers_when_above_threshold(self):
        """COI override fires when verified >= threshold and majority are COI."""
        # 3 verified, threshold 3, 2 COI (2/3 > 50%)
        assert qualitative_coi_verdict(
            n_confirmed=3, threshold=3, coi_majority=2
        ) == "UNDETERMINED"

    def test_coi_override_skipped_when_below_threshold(self):
        """COI override must NOT fire when verified < threshold.
        This is the bug the quorum guard fixes: with only 1 source verified
        (below threshold 3), 1 COI flag used to produce UNDETERMINED via
        COI override even though the real problem was insufficient sources."""
        # 1 verified, threshold 3, 1 COI — below quorum
        result = qualitative_coi_verdict(
            n_confirmed=1, threshold=3, coi_majority=1
        )
        # Should be UNDETERMINED from source count, NOT from COI override
        assert result == "UNDETERMINED"

    def test_coi_override_skipped_below_threshold_does_not_become_proved(self):
        """Skipping COI below threshold must not accidentally produce PROVED.
        If n_confirmed < threshold, claim_holds is False -> UNDETERMINED."""
        # 2 verified, threshold 3, 2 COI — below quorum, claim doesn't hold
        assert qualitative_coi_verdict(
            n_confirmed=2, threshold=3, coi_majority=2
        ) == "UNDETERMINED"

    def test_no_coi_flags_no_override(self):
        """With no COI flags, verdict is based on source count alone."""
        assert qualitative_coi_verdict(
            n_confirmed=3, threshold=3, coi_majority=0
        ) == "PROVED"

    def test_coi_minority_no_override(self):
        """COI in minority (1/3 < 50%) does not trigger override."""
        assert qualitative_coi_verdict(
            n_confirmed=3, threshold=3, coi_majority=1
        ) == "PROVED"


class TestCompoundCOIQuorum:
    """COI quorum guard for compound template."""

    def test_sc1_coi_override_skipped_below_threshold(self):
        """SC1 COI override must not fire when SC1 verified < SC1 threshold.
        This was the Cowork bug: 1 of 4 SC1 sources verified, that 1 had COI,
        1/1 > 50% triggered override. With quorum guard, 1 < 3 skips COI."""
        result = compound_coi_verdict(
            n_sc1=1, n_sc2=4,
            sc1_threshold=3, sc2_threshold=3,
            sc1_coi_majority=1, sc2_coi_majority=0,
        )
        # SC1 fails on source count -> PARTIALLY VERIFIED (SC2 holds)
        assert result == "PARTIALLY VERIFIED"

    def test_sc1_coi_override_triggers_above_threshold(self):
        """SC1 COI override fires when verified >= threshold and majority."""
        result = compound_coi_verdict(
            n_sc1=3, n_sc2=3,
            sc1_threshold=3, sc2_threshold=3,
            sc1_coi_majority=2, sc2_coi_majority=0,
        )
        assert result == "UNDETERMINED"

    def test_both_above_threshold_no_coi(self):
        """Both sub-claims meet threshold, no COI -> PROVED."""
        assert compound_coi_verdict(
            n_sc1=3, n_sc2=3,
            sc1_threshold=3, sc2_threshold=3,
            sc1_coi_majority=0, sc2_coi_majority=0,
        ) == "PROVED"
