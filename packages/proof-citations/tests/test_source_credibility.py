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


def test_pubmed_typed_as_academic_database_not_government():
    """PubMed is .gov but is a biomedical literature database, not a
    government primary source. Mistyping it as 'government / tier 5' was
    flagged by the cowork sandbox (v1.42.0)."""
    result = assess_credibility("https://pubmed.ncbi.nlm.nih.gov/12345678/")
    assert result["source_type"] == "academic_database"
    assert result["tier"] == 4


def test_pmc_typed_as_academic_database_not_government():
    """Same as pubmed — pmc.ncbi.nlm.nih.gov hosts full-text peer-reviewed
    literature, not government policy/data."""
    result = assess_credibility("https://pmc.ncbi.nlm.nih.gov/articles/PMC12345/")
    assert result["source_type"] == "academic_database"
    assert result["tier"] == 4


def test_ncbi_parent_typed_as_academic_database():
    """The bare ncbi.nlm.nih.gov hostname (and any unknown subdomain)
    is still treated as academic, not government."""
    result = assess_credibility("https://ncbi.nlm.nih.gov/about/")
    assert result["source_type"] == "academic_database"
    assert result["tier"] == 4


def test_other_gov_domains_remain_government():
    """The override is targeted — bls.gov / nasa.gov / etc. still type
    as government (the prior behavior must not regress)."""
    for url in (
        "https://www.bls.gov/cpi/data.htm",
        "https://www.nasa.gov/missions/",
        "https://www.cdc.gov/flu/",  # CDC = government policy, not lit DB
    ):
        result = assess_credibility(url)
        assert result["source_type"] == "government", url
        assert result["tier"] == 5, url
