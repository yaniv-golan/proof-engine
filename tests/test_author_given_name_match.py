import pytest
from tools.lib.prose_reference_scan import check_authors
from tools.lib.proof_cache import ResolvedReference


def _mk(authors, year=2024):
    return ResolvedReference(
        identifier_type="arxiv", identifier_value="x",
        canonical_url="x", title="x", authors=authors, year=year,
        venue=None, version=None, resolved_at="x", source_api="x", raw={},
    )


def test_exact_initial_matches_resolved_given():
    ok, errs = check_authors("A. Odrzywo\u0142ek", _mk(["Andrzej Odrzywo\u0142ek"]))
    assert ok, errs


def test_wrong_initial_fails():
    ok, errs = check_authors("R. Smith", _mk(["John Smith"]))
    assert not ok and any("initial" in e.lower() or "given" in e.lower() for e in errs)


def test_full_given_mismatch_fails():
    ok, errs = check_authors("Jane Smith", _mk(["John Smith"]))
    assert not ok


def test_et_al_requires_three_authors():
    ok, errs = check_authors("Odrzywo\u0142ek et al.", _mk(["Andrzej Odrzywo\u0142ek"]))
    assert not ok and any("et al" in e.lower() for e in errs)


def test_partial_prose_single_resolved_of_many_passes():
    ok, errs = check_authors(
        "Gao et al.",
        _mk(["Luyu Gao", "Aman Madaan", "Shuyan Zhou", "Uri Alon", "Pengfei Liu"]),
    )
    assert ok, errs


def test_hallucinated_coauthor_fails():
    ok, errs = check_authors("A. Odrzywo\u0142ek and R. Cheng", _mk(["Andrzej Odrzywo\u0142ek"]))
    assert not ok and any("cheng" in e.lower() for e in errs)


def test_mirzadeh_et_al_passes():
    ok, errs = check_authors(
        "Mirzadeh et al.",
        _mk(["Iman Mirzadeh", "Keivan Alizadeh", "Hooman Shahrokhi",
             "Oncel Tuzel", "Samy Bengio", "Mehrdad Farajtabar"]),
    )
    assert ok, errs


def test_j_gao_et_al_fails_on_luyu_gao_paper():
    ok, errs = check_authors(
        "J. Gao et al.",
        _mk(["Luyu Gao", "Aman Madaan", "Shuyan Zhou", "Uri Alon", "Pengfei Liu"]),
    )
    assert not ok


def test_surname_only_no_given_claim_passes():
    ok, errs = check_authors("Smith", _mk(["John Smith"]))
    assert ok
