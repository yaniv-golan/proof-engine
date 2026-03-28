from tools.lib.verdict import normalize_verdict, VERDICT_TAXONOMY


def test_proved_normalizes():
    result = normalize_verdict("PROVED")
    assert result == {
        "raw": "PROVED",
        "category": "proved",
        "badge_color": "green",
        "filter_value": "proved",
        "rating": 5,
    }


def test_proved_with_unverified_citations():
    result = normalize_verdict("PROVED (with unverified citations)")
    assert result["category"] == "proved-qualified"
    assert result["badge_color"] == "amber"
    assert result["filter_value"] == "proved"
    assert result["rating"] == 4


def test_disproved():
    result = normalize_verdict("DISPROVED")
    assert result["category"] == "disproved"
    assert result["badge_color"] == "red"
    assert result["filter_value"] == "disproved"
    assert result["rating"] == 1


def test_disproved_with_unverified_citations():
    result = normalize_verdict("DISPROVED (with unverified citations)")
    assert result["category"] == "disproved-qualified"
    assert result["badge_color"] == "red"
    assert result["filter_value"] == "disproved"
    assert result["rating"] == 2


def test_partially_verified():
    result = normalize_verdict("PARTIALLY VERIFIED")
    assert result["category"] == "partial"
    assert result["badge_color"] == "amber"
    assert result["filter_value"] == "partial"
    assert result["rating"] == 3


def test_undetermined():
    result = normalize_verdict("UNDETERMINED")
    assert result["category"] == "undetermined"
    assert result["badge_color"] == "gray"
    assert result["filter_value"] == "undetermined"
    assert result["rating"] == 3


def test_supported():
    result = normalize_verdict("SUPPORTED")
    assert result["category"] == "supported"
    assert result["badge_color"] == "blue"
    assert result["filter_value"] == "supported"
    assert result["rating"] == 4


def test_supported_with_unverified_citations():
    result = normalize_verdict("SUPPORTED (with unverified citations)")
    assert result["category"] == "supported-qualified"
    assert result["badge_color"] == "blue"
    assert result["filter_value"] == "supported"
    assert result["rating"] == 3


def test_unknown_verdict_raises():
    import pytest
    with pytest.raises(ValueError, match="Unknown verdict"):
        normalize_verdict("MAYBE")


def test_taxonomy_has_all_verdicts():
    assert len(VERDICT_TAXONOMY) == 8
