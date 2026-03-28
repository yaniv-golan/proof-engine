"""Tests for computations.py — cross_check tolerance fixes."""
import pytest
from scripts.computations import cross_check, compare


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
