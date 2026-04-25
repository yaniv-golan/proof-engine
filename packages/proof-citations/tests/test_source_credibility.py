from proof_citations.source_credibility import assess_credibility


def test_government_domain_is_high_credibility():
    # Real API: assess_credibility(url) -> dict with int tier (1-5).
    # Government .gov domain → tier 5, source_type 'government'.
    result = assess_credibility("https://www.bls.gov/cpi/data.htm")
    assert result["tier"] == 5
    assert result["source_type"] == "government"


def test_unknown_blog_is_low_credibility():
    # Unclassified domains return tier 2 with source_type 'unknown'.
    result = assess_credibility("https://random-blog.example/post/42")
    assert result["tier"] <= 2
    assert result["source_type"] in {"unknown", "commercial"}
