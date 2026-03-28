import pytest
from tools.lib.tagger import auto_tag, canonicalize_tag, TAG_KEYWORDS


def test_canonicalize_lowercase():
    assert canonicalize_tag("Economics") == "economics"


def test_canonicalize_spaces_to_hyphens():
    assert canonicalize_tag("AI Safety") == "ai-safety"


def test_canonicalize_underscores_to_hyphens():
    assert canonicalize_tag("ai_safety") == "ai-safety"


def test_canonicalize_strips_whitespace():
    assert canonicalize_tag("  history  ") == "history"


def test_canonicalize_collapses_hyphens():
    assert canonicalize_tag("foo--bar") == "foo-bar"


def test_canonicalize_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        canonicalize_tag("   ")


def test_canonicalize_invalid_chars_raises():
    with pytest.raises(ValueError, match="invalid"):
        canonicalize_tag("hello@world")


def test_auto_tag_gdp():
    tags = auto_tag("US real GDP grew by 5000% since 1913")
    assert "economics" in tags


def test_auto_tag_brain():
    tags = auto_tag("The adult brain does not generate new neurons")
    assert "neuroscience" in tags


def test_auto_tag_multiple():
    tags = auto_tag("GDP growth affects brain development research funding")
    assert "economics" in tags
    assert "neuroscience" in tags


def test_auto_tag_no_match():
    tags = auto_tag("The sky is blue")
    assert tags == []


def test_auto_tag_returns_canonical_slugs():
    tags = auto_tag("CPI inflation data")
    for tag in tags:
        assert tag == canonicalize_tag(tag)


def test_auto_tag_deduplicates():
    tags = auto_tag("GDP and CPI and inflation")
    assert tags.count("economics") == 1
