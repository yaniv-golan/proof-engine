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


import pytest


# --- Parametrized tests for all new domains ---

NEW_GOVERNMENT_DOMAINS = [
    ("unrwa.org", "UNRWA"),
    ("ungeneva.org", "UN Geneva"),
    ("wfp.org", "World Food Programme"),
    ("unesco.org", "UNESCO"),
    ("unodc.org", "UN Office on Drugs and Crime"),
    ("unhabitat.org", "UN-Habitat"),
    ("unwomen.org", "UN Women"),
    ("unaids.org", "UNAIDS"),
    ("unido.org", "UNIDO"),
    ("unctad.org", "UNCTAD"),
    ("unops.org", "UNOPS"),
    ("reliefweb.int", "ReliefWeb"),
    ("ohchr.org", "OHCHR"),
]


@pytest.mark.parametrize("domain,label", NEW_GOVERNMENT_DOMAINS)
def test_un_agency_is_government(domain, label):
    """Each new UN agency domain should be tier 5 government."""
    result = assess_credibility(f"https://www.{domain}/example")
    assert result["tier"] == 5, f"{label} ({domain}): expected tier 5, got {result}"
    assert result["source_type"] == "government", f"{label} ({domain}): expected government, got {result['source_type']}"


NEW_NEWS_DOMAINS = [
    ("jpost.com", "Jerusalem Post"),
    ("semafor.com", "Semafor"),
    ("axios.com", "Axios"),
    ("themarkup.org", "The Markup"),
    ("restofworld.org", "Rest of World"),
    ("defector.com", "Defector"),
    ("theinformation.com", "The Information"),
]


@pytest.mark.parametrize("domain,label", NEW_NEWS_DOMAINS)
def test_new_news_outlet_is_major_news(domain, label):
    """Each new news outlet domain should be tier 3 major_news."""
    result = assess_credibility(f"https://www.{domain}/example")
    assert result["tier"] == 3, f"{label} ({domain}): expected tier 3, got {result}"
    assert result["source_type"] == "major_news", f"{label} ({domain}): expected major_news, got {result['source_type']}"


def test_un_int_subdomain_not_tier5():
    """Regression: *.un.int subdomains must NOT auto-promote to tier 5.

    un.int is intentionally excluded from known_domains because the subdomain
    matching in source_credibility.py would promote all *.un.int hosts
    (including member-state mission sites) to tier 5.
    """
    result = assess_credibility("https://missionofexample.un.int/statements")
    assert result["tier"] != 5, (
        f"*.un.int subdomain should NOT be tier 5 — got {result}"
    )
