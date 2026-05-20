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
from tools.lib.proof_cache import ResolvedReference


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


from tools.lib.prose_reference_scan import check_title_jaccard


def test_title_jaccard_passes_on_prefix():
    ok = check_title_jaccard(
        "all elementary functions",
        "All elementary functions from a single binary operator",
    )
    assert ok


def test_title_jaccard_fails_on_wrong_title():
    ok = check_title_jaccard(
        "The elementary function arithmetic",
        "All elementary functions from a single binary operator",
    )
    assert not ok


def test_pass2_detects_wrong_author_near_identifier():
    from tools.lib.prose_reference_scan import pass2_attribution_check, pass1_identifiers
    text = (
        'R. Cheng, "The elementary function arithmetic" '
        '(arXiv:2603.21852) introduced this binary operator.'
    )
    hits = pass1_identifiers(text)
    errors = pass2_attribution_check(text, hits, {"arxiv:2603.21852": _odrzywolek_ref()})
    assert errors
    assert any("cheng" in e.message.lower() or "odrzywolek" in e.message.lower() for e in errors)


def test_pass2_accepts_correct_attribution():
    from tools.lib.prose_reference_scan import pass2_attribution_check, pass1_identifiers
    text = 'A. Odrzywo\u0142ek, "All elementary functions..." (arXiv:2603.21852) introduced...'
    hits = pass1_identifiers(text)
    errors = pass2_attribution_check(text, hits, {"arxiv:2603.21852": _odrzywolek_ref()})
    assert not errors, [e.message for e in errors]
