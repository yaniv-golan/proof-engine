"""Tests for computations.py — cross_check tolerance fixes."""
from scripts.computations import cross_check


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
