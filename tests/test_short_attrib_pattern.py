import pytest
from tools.lib.prose_reference_scan import pass1_identifiers, pass2_attribution_check
from tools.lib.proof_cache import ResolvedReference


def _odrzywolek_ref(authors=None):
    return ResolvedReference(
        identifier_type="arxiv", identifier_value="2603.21852",
        canonical_url="https://arxiv.org/abs/2603.21852",
        title="All elementary functions from a single binary operator",
        authors=authors or ["Andrzej Odrzywo\u0142ek"], year=2026,
        venue="arXiv", version=None, resolved_at="x", source_api="x", raw={},
    )


def test_link_short_form_et_al_on_single_author_fails():
    text = "[Odrzywo\u0142ek et al. (2026)](https://arxiv.org/abs/2603.21852)"
    errors = pass2_attribution_check(text, pass1_identifiers(text),
                                      {"arxiv:2603.21852": _odrzywolek_ref()})
    assert errors


def test_link_short_form_hallucinated_author_fails():
    text = "[Cheng (2026)](https://arxiv.org/abs/2603.21852)"
    errors = pass2_attribution_check(text, pass1_identifiers(text),
                                      {"arxiv:2603.21852": _odrzywolek_ref()})
    assert errors


def test_link_short_form_year_mismatch_fails():
    text = "[Mirzadeh et al. (2023)](https://arxiv.org/abs/2410.05229)"
    ref = ResolvedReference(
        identifier_type="arxiv", identifier_value="2410.05229",
        canonical_url="x", title="GSM-Symbolic",
        authors=[f"A{i} Mirzadeh" for i in range(6)],
        year=2024, venue="arXiv", version=None, resolved_at="x",
        source_api="x", raw={},
    )
    errors = pass2_attribution_check(text, pass1_identifiers(text),
                                      {"arxiv:2410.05229": ref})
    assert any("year" in e.message.lower() for e in errors)


def test_link_short_form_correct_passes():
    text = "[Odrzywo\u0142ek (2026)](https://arxiv.org/abs/2603.21852)"
    errors = pass2_attribution_check(text, pass1_identifiers(text),
                                      {"arxiv:2603.21852": _odrzywolek_ref()})
    assert not errors, [e.message for e in errors]
