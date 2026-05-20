"""Tests for proof_citations.compare.compare_metadata."""

import pytest

from proof_citations.registry.base import Author, ResolvedRecord, now_iso
from proof_citations.compare import (
    compare_metadata,
    _normalize_doi,
    _normalize_journal,
    _normalize_text,
    _title_similarity,
)


def _record(**overrides) -> ResolvedRecord:
    """Build a `ResolvedRecord` for the Anderson 2013 paper used in the Ren audit (B3)."""
    defaults = dict(
        identifier_type="pmid",
        identifier_value="23260561",
        canonical_url="https://pubmed.ncbi.nlm.nih.gov/23260561/",
        title="Ureteroenteric anastomotic strictures after radical cystectomy-does operative approach matter?",
        authors=[Author(family="Anderson", given="C B"), Author(family="Morgan", given="T M")],
        year=2013,
        venue="The Journal of urology",
        publication_type="journal-article",
        published_date="2013-02",
        issn="0022-5347",
        doi="10.1016/j.juro.2012.09.034",
        pmid="23260561",
        volume="189",
        issue="2",
        pages="541-7",
        resolved_at=now_iso(),
        source_api="eutils.ncbi.nlm.nih.gov",
    )
    defaults.update(overrides)
    return ResolvedRecord(**defaults)


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_normalize_text_lowercases(self):
        assert _normalize_text("ABC") == "abc"

    def test_normalize_text_strips_punctuation(self):
        assert _normalize_text("Hello, World!") == "hello world"

    def test_normalize_text_collapses_whitespace(self):
        assert _normalize_text("foo   bar") == "foo bar"

    def test_normalize_doi_strips_prefix(self):
        assert _normalize_doi("https://doi.org/10.X/Y") == "10.x/y"
        assert _normalize_doi("doi:10.X/Y") == "10.x/y"
        assert _normalize_doi("10.X/Y") == "10.x/y"

    def test_normalize_journal_resolves_abbreviation(self):
        # J Urol → "the journal of urology" via the bundled lookup
        assert _normalize_journal("J Urol") == "the journal of urology"

    def test_normalize_journal_passthrough_for_unknown(self):
        assert _normalize_journal("Some Niche Journal") == "some niche journal"


class TestTitleSimilarity:
    def test_identical(self):
        assert _title_similarity("Hello World", "Hello World") == 1.0

    def test_punctuation_difference_near_one(self):
        # "X-does Y?" vs "X — does Y" should score very high
        s = _title_similarity(
            "Ureteroenteric strictures-does operative approach matter?",
            "Ureteroenteric strictures: does operative approach matter",
        )
        assert s > 0.85

    def test_completely_different_low(self):
        assert _title_similarity("Cat", "The history of ancient Rome") < 0.4

    def test_empty_inputs(self):
        assert _title_similarity("", "x") == 0.0
        assert _title_similarity("x", "") == 0.0


# ---------------------------------------------------------------------------
# compare_metadata verdicts
# ---------------------------------------------------------------------------

class TestCompareMetadataVerdicts:
    def test_genuine_all_fields_match(self):
        record = _record()
        result = compare_metadata(record, {
            "title": "Ureteroenteric anastomotic strictures after radical cystectomy-does operative approach matter?",
            "journal": "J Urol",
            "year": 2013,
            "doi": "10.1016/j.juro.2012.09.034",
        })
        assert result["verdict"] == "genuine"
        assert all(result["field_matches"].values())
        assert result["mismatches"] == []

    def test_metadata_chimera_b3_pattern(self):
        """Title matches; journal+year are forged (Ren B3 from the CITADEL audit)."""
        record = _record()
        result = compare_metadata(record, {
            "title": "Ureteroenteric anastomotic strictures after radical cystectomy: does operative approach matter?",
            "journal": "J Urol",   # matches (correctly cited journal)
            "year": 2023,           # WRONG — actual year is 2013
        })
        assert result["verdict"] == "metadata_chimera"
        assert result["field_matches"]["title"] is True
        assert result["field_matches"]["year"] is False
        mismatch_fields = [m["field"] for m in result["mismatches"]]
        assert "year" in mismatch_fields

    def test_metadata_chimera_b7_pattern(self):
        """Title matches; journal is forged (Goh 2015 PloS One → claimed J Urol 2024)."""
        record = ResolvedRecord(
            identifier_type="pmid", identifier_value="25825873",
            canonical_url="https://pubmed.ncbi.nlm.nih.gov/25825873/",
            title="Robotic versus open radical cystectomy: an updated systematic review and meta-analysis",
            authors=[Author(family="Goh"), Author(family="Gill")],
            year=2015,
            venue="PloS one",
            resolved_at=now_iso(), source_api="test",
        )
        result = compare_metadata(record, {
            "title": "Robotic versus open radical cystectomy: an updated systematic review and meta-analysis",
            "journal": "J Urol",  # WRONG — real is PLoS One
            "year": 2024,           # WRONG — real is 2015
        })
        assert result["verdict"] == "metadata_chimera"
        assert result["field_matches"]["title"] is True
        assert result["field_matches"]["journal"] is False

    def test_title_chimera(self):
        """PMID resolves but title is completely different (most Ren chimeras)."""
        record = _record(title="Urinary diversion: how experts divert")
        result = compare_metadata(record, {
            "title": "Radical cystectomy for bladder cancer: morbidity, mortality, and oncological outcomes",
            "year": 2015,  # matches
        })
        assert result["verdict"] == "title_chimera"

    def test_partial_match_title_in_ambiguous_band(self):
        """Title similarity in 0.50–0.85 band; other fields disagree."""
        record = _record(title="Bricker versus Wallace anastomosis: A meta-analysis of ureteroenteric stricture rates after ileal conduit")
        result = compare_metadata(record, {
            "title": "Bricker versus Wallace anastomosis: a meta-analysis of stricture rates",
            "year": 2024,  # disagree
        })
        assert result["verdict"] == "partial_match"

    def test_no_expected(self):
        record = _record()
        result = compare_metadata(record, {})
        assert result["verdict"] == "no_expected"

    def test_no_expected_none(self):
        record = _record()
        result = compare_metadata(record, None)
        assert result["verdict"] == "no_expected"


class TestCompareMetadataDOI:
    def test_doi_match_strict_lowercase(self):
        record = _record(doi="10.1016/J.X.2020.001")
        result = compare_metadata(record, {"title": _record().title, "doi": "10.1016/j.x.2020.001"})
        assert result["field_matches"]["doi"] is True

    def test_doi_match_strips_url_prefix(self):
        record = _record(doi="10.1016/j.x.2020.001")
        result = compare_metadata(record, {"title": _record().title, "doi": "https://doi.org/10.1016/j.x.2020.001"})
        assert result["field_matches"]["doi"] is True


class TestCompareMetadataJournal:
    def test_issn_match_overrides_name(self):
        record = _record(venue="Different Name", issn="0022-5347")
        result = compare_metadata(record, {
            "title": _record().title,
            "journal": "J Urol",
            "issn": "0022-5347",
        })
        assert result["field_matches"]["journal"] is True

    def test_journal_abbrev_lookup(self):
        record = _record()  # venue "The Journal of urology"
        result = compare_metadata(record, {"title": _record().title, "journal": "J Urol"})
        assert result["field_matches"]["journal"] is True


class TestCompareMetadataAuthors:
    def test_first_author_match(self):
        record = _record()  # Anderson + Morgan
        result = compare_metadata(record, {
            "title": _record().title,
            "authors": ["Anderson"],
        })
        assert result["field_matches"]["authors"] is True

    def test_first_author_mismatch(self):
        record = _record()
        result = compare_metadata(record, {
            "title": _record().title,
            "authors": ["Smith"],
        })
        assert result["field_matches"]["authors"] is False

    def test_authors_as_dicts(self):
        record = _record()
        result = compare_metadata(record, {
            "title": _record().title,
            "authors": [{"family": "Anderson"}],
        })
        assert result["field_matches"]["authors"] is True

    def test_authors_as_full_strings(self):
        record = _record()
        result = compare_metadata(record, {
            "title": _record().title,
            "authors": ["CB Anderson"],
        })
        assert result["field_matches"]["authors"] is True

    def test_no_authors_claimed_is_not_checked(self):
        record = _record()
        result = compare_metadata(record, {"title": _record().title, "authors": []})
        assert "authors" not in result["field_matches"]


class TestMessageFormatting:
    def test_genuine_message(self):
        record = _record()
        result = compare_metadata(record, {"title": _record().title, "year": 2013})
        assert "Genuine" in result["message"]
        assert "title, year" in result["message"]

    def test_metadata_chimera_message_mentions_similarity(self):
        record = _record()
        result = compare_metadata(record, {"title": _record().title, "year": 2099})
        assert "Metadata chimera" in result["message"]
        assert "similarity" in result["message"].lower()

    def test_title_chimera_message(self):
        record = _record(title="Some completely different paper")
        result = compare_metadata(record, {"title": _record().title})
        assert "Title chimera" in result["message"]
