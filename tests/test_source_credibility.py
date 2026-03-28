"""Tests for source_credibility.py — domain classification."""
from scripts.source_credibility import assess_credibility


def test_iopscience_is_academic():
    """IOPscience (Astrophysical Journal Letters) should be tier 4 academic."""
    result = assess_credibility("https://iopscience.iop.org/article/10.3847/2041-8213/example")
    assert result["tier"] >= 4, f"Expected tier >= 4, got {result}"
    assert result["source_type"] == "academic"


def test_aanda_is_academic():
    """Astronomy & Astrophysics journal should be tier 4 academic."""
    result = assess_credibility("https://www.aanda.org/articles/aa/full_html/2020/01/example")
    assert result["tier"] >= 4, f"Expected tier >= 4, got {result}"
    assert result["source_type"] == "academic"


def test_brainfacts_is_reference():
    """BrainFacts.org (Society for Neuroscience) should be tier 3 reference."""
    result = assess_credibility("https://www.brainfacts.org/the-brain-facts-book")
    assert result["tier"] >= 3, f"Expected tier >= 3, got {result}"


def test_simplypsychology_is_reference():
    """SimplyPsychology (educational resource) should be tier 3 reference."""
    result = assess_credibility("https://www.simplypsychology.org/memory.html")
    assert result["tier"] >= 3, f"Expected tier >= 3, got {result}"


def test_physicsworld_is_reference():
    """Physics World (IOP publishing) should be tier 3 reference."""
    result = assess_credibility("https://physicsworld.com/a/example-article")
    assert result["tier"] >= 3, f"Expected tier >= 3, got {result}"


def test_existing_nature_still_academic():
    """Regression: nature.com should still be tier 4."""
    result = assess_credibility("https://www.nature.com/articles/example")
    assert result["tier"] == 4
    assert result["source_type"] == "academic"


def test_existing_wikipedia_still_reference():
    """Regression: wikipedia should still be tier 3."""
    result = assess_credibility("https://en.wikipedia.org/wiki/Example")
    assert result["tier"] == 3
    assert result["source_type"] == "reference"
