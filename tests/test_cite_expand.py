import pytest
from pathlib import Path
from tools.lib.cite_expander import expand, check, expand_style
from tools.lib.proof_cache import ResolvedReference


def _odrzywolek():
    return ResolvedReference(
        identifier_type="arxiv", identifier_value="2603.21852",
        canonical_url="https://arxiv.org/abs/2603.21852",
        title="All elementary functions from a single binary operator",
        authors=["Andrzej Odrzywo\u0142ek"], year=2026,
        venue="arXiv preprint", version="v2",
        resolved_at="x", source_api="x", raw={},
    )


def test_full_style_renders_markdown_link_with_identifier():
    out = expand_style(_odrzywolek(), "full")
    assert "https://arxiv.org/abs/2603.21852" in out
    assert "Odrzywo\u0142ek" in out
    assert "All elementary functions" in out


def test_short_style_renders_surname_year():
    out = expand_style(_odrzywolek(), "short")
    assert out.startswith("[")
    assert "Odrzywo\u0142ek (2026)" in out
    assert "https://arxiv.org/abs/2603.21852" in out


def test_inline_style_bare_identifier():
    out = expand_style(_odrzywolek(), "inline")
    assert out.strip() == "arXiv:2603.21852"


def test_expand_replaces_token():
    cache = {"arxiv:2603.21852": _odrzywolek()}
    text = "See {{cite:arxiv:2603.21852}}."
    out = expand(text, cache)
    assert "{{cite:" not in out
    assert "Odrzywo\u0142ek" in out
    assert "<!-- cite-source: arxiv:2603.21852 -->" in out


def test_expand_idempotent_on_already_rendered():
    cache = {"arxiv:2603.21852": _odrzywolek()}
    text = "{{cite:arxiv:2603.21852}}"
    once = expand(text, cache)
    twice = expand(once, cache)
    assert once == twice


def test_check_detects_unexpanded_token():
    cache = {"arxiv:2603.21852": _odrzywolek()}
    errors = check("{{cite:arxiv:2603.21852}}", cache)
    assert errors
    assert any("unexpanded" in e.lower() for e in errors)


def test_check_detects_drift_from_cache():
    cache = {"arxiv:2603.21852": _odrzywolek()}
    hand_edited = (
        "[R. Cheng, \"wrong\"](https://arxiv.org/abs/2603.21852) "
        "<!-- cite-source: arxiv:2603.21852 -->"
    )
    errors = check(hand_edited, cache)
    assert errors
    assert any("drift" in e.lower() or "diverge" in e.lower() for e in errors)


def test_force_reexpands_after_cache_change():
    cache_v1 = {"arxiv:2603.21852": _odrzywolek()}
    text = "{{cite:arxiv:2603.21852}}"
    once = expand(text, cache_v1)

    new_ref = _odrzywolek()
    new_ref.title = "All elementary functions (updated title)"
    cache_v2 = {"arxiv:2603.21852": new_ref}

    noop = expand(once, cache_v2)
    assert noop == once

    forced = expand(once, cache_v2, force=True)
    assert "updated title" in forced
