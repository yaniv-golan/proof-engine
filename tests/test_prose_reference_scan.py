import pytest
from tools.lib.prose_reference_scan import pass1_identifiers


def test_pass1_finds_arxiv_bare():
    hits = pass1_identifiers("see arXiv:2603.21852 for context")
    assert len(hits) == 1
    assert hits[0].identifier_type == "arxiv"
    assert hits[0].identifier_value == "2603.21852"


def test_pass1_finds_arxiv_in_link_target():
    text = "[Odrzywo\u0142ek (2026)](https://arxiv.org/abs/2603.21852) showed..."
    hits = pass1_identifiers(text)
    types = {(h.identifier_type, h.identifier_value) for h in hits}
    assert ("arxiv", "2603.21852") in types


def test_pass1_finds_doi_in_link_target():
    text = "see [Planck (2020)](https://doi.org/10.1051/0004-6361/201833910)"
    hits = pass1_identifiers(text)
    types = {(h.identifier_type, h.identifier_value) for h in hits}
    assert ("doi", "10.1051/0004-6361/201833910") in types


def test_pass1_finds_swhid():
    text = "archived at swh:1:dir:" + "0" * 40
    hits = pass1_identifiers(text)
    assert any(h.identifier_type == "swhid" for h in hits)


def test_pass1_empty():
    assert pass1_identifiers("no citations here") == []


def test_pass1_tracks_span_for_windowing():
    text = "earlier text... see arXiv:2603.21852 afterwards"
    hits = pass1_identifiers(text)
    assert len(hits) == 1
    assert hits[0].span[0] < hits[0].span[1]
    assert text[hits[0].span[0]:hits[0].span[1]].startswith("arXiv:")


from tools.lib.prose_reference_scan import check_authors
from tools.lib.reference_resolver import ResolvedReference


def _odrzywolek_ref():
    return ResolvedReference(
        identifier_type="arxiv", identifier_value="2603.21852",
        canonical_url="https://arxiv.org/abs/2603.21852",
        title="All elementary functions from a single binary operator",
        authors=["Andrzej Odrzywo\u0142ek"], year=2026,
        venue="arXiv preprint", version="v2",
        resolved_at="2026-04-17T00:00:00Z",
        source_api="export.arxiv.org/api/query", raw={},
    )


def test_eml_regression_cheng_vs_odrzywolek():
    """The exact failure that motivated this design."""
    ok, errs = check_authors("R. Cheng", _odrzywolek_ref())
    assert not ok
    assert any("cheng" in e.lower() for e in errs)


def test_eml_regression_correct_attribution_passes():
    ok, errs = check_authors("A. Odrzywo\u0142ek", _odrzywolek_ref())
    assert ok, errs
