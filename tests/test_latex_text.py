"""Tests for latex_text.py — LaTeX-to-text conversion."""
from scripts.latex_text import latex_to_text


def test_greek_letters():
    assert "\u03A9" in latex_to_text(r"\Omega")
    assert "\u03B1" in latex_to_text(r"\alpha")
    assert "\u03C0" in latex_to_text(r"\pi")


def test_operators():
    assert "\u00B1" in latex_to_text(r"\pm")
    assert "\u00D7" in latex_to_text(r"\times")
    assert "\u2248" in latex_to_text(r"\approx")


def test_mathrm_stripped():
    assert "m" == latex_to_text(r"\mathrm{m}").strip()


def test_subscript_flattened():
    result = latex_to_text(r"\Omega_{\mathrm{m}}")
    assert "\u03A9" in result
    assert "m" in result


def test_planck_expression():
    result = latex_to_text(r"\Omega_{\mathrm{m}}=0.315\pm 0.007")
    assert "0.315" in result
    assert "0.007" in result
    assert "\u03A9" in result
    assert "\u00B1" in result


def test_frac_to_slash():
    assert "1/2" in latex_to_text(r"\frac{1}{2}")
    assert "3/4" in latex_to_text(r"\frac{3}{4}")


def test_sqrt_to_text():
    assert "sqrt(x)" in latex_to_text(r"\sqrt{x}")


def test_unknown_commands_stripped_content_preserved():
    result = latex_to_text(r"\mathcal{O}(n)")
    assert "O" in result
    assert "n" in result


def test_empty_input():
    assert latex_to_text("") == ""


def test_plain_text_passthrough():
    assert latex_to_text("hello world") == "hello world"
