import pytest
from tools.lib.prose_reference_scan import pass4_dangling_sweep, pass1_identifiers


def test_long_form_launder_attack_fails():
    """The motivating launder attack: correct linked citation far from naked misattribution."""
    text = (
        'R. Cheng, "The elementary function arithmetic" introduced this binary operator.\n'
        + "\n" * 50
        + "[Odrzywo\u0142ek (2026)](https://arxiv.org/abs/2603.21852) \u2014 canonical reference.\n"
    )
    hits = pass1_identifiers(text)
    errors = pass4_dangling_sweep(text, hits)
    assert errors
    assert any("cheng" in e.message.lower() for e in errors)


def test_short_form_dangling_fails():
    text = "Cheng (2026) showed that... see no identifier here.\n"
    hits = pass1_identifiers(text)
    errors = pass4_dangling_sweep(text, hits)
    assert errors
    assert any("cheng" in e.message.lower() for e in errors)


def test_identifier_carrying_attribution_is_not_dangling():
    text = 'R. Cheng, "x" (arXiv:2603.21852) introduced this.'
    hits = pass1_identifiers(text)
    errors = pass4_dangling_sweep(text, hits)
    assert not errors


def test_euler_historical_not_flagged():
    text = "Euler proved that e^(i\u03c0)+1=0."
    hits = pass1_identifiers(text)
    errors = pass4_dangling_sweep(text, hits)
    assert not errors


def test_short_form_escape_hatch_allowed():
    text = "<!-- not-a-citation-start --> In Smith's proof (2020 edition), ... <!-- not-a-citation-end -->"
    errors = pass4_dangling_sweep(text, [])
    assert not errors


def test_single_line_escape_hatch():
    text = "<!-- not-a-citation: Smith (2020 edition) --> Smith (2020 edition)"
    errors = pass4_dangling_sweep(text, [])
    assert not errors


def test_long_form_escape_hatch_disallowed():
    """Rev-8: quoted-title inside escape hatch still fails."""
    text = (
        '<!-- not-a-citation-start --> '
        'R. Cheng, "The elementary function arithmetic" '
        '<!-- not-a-citation-end -->'
    )
    errors = pass4_dangling_sweep(text, [])
    assert errors
    assert any("quoted-title" in e.message.lower() or "escape hatch" in e.message.lower() for e in errors)
