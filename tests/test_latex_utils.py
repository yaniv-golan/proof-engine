# tests/test_latex_utils.py
"""Tests for tools.lib.latex_utils — LaTeX-to-Unicode conversion."""
import pytest
from tools.lib.latex_utils import strip_latex


class TestGreekLetters:
    def test_alpha(self):
        assert strip_latex(r"\(\alpha\)") == "\u03B1"

    def test_pi(self):
        assert strip_latex(r"\(\pi\)") == "\u03C0"

    def test_lambda(self):
        assert strip_latex(r"\(\lambda\)") == "\u03BB"

    def test_eta(self):
        assert strip_latex(r"\(\eta\)") == "\u03B7"

    def test_uppercase_omega(self):
        assert strip_latex(r"\(\Omega\)") == "\u03A9"

    def test_uppercase_sigma(self):
        assert strip_latex(r"\(\Sigma\)") == "\u03A3"


class TestOperators:
    def test_geq(self):
        assert strip_latex(r"\(\geq\)") == "\u2265"

    def test_leq(self):
        assert strip_latex(r"\(\leq\)") == "\u2264"

    def test_neq(self):
        assert strip_latex(r"\(\neq\)") == "\u2260"

    def test_cdot(self):
        assert strip_latex(r"\(\cdot\)") == "\u00B7"

    def test_times(self):
        assert strip_latex(r"\(\times\)") == "\u00D7"

    def test_pm(self):
        assert strip_latex(r"\(\pm\)") == "\u00B1"

    def test_infty(self):
        assert strip_latex(r"\(\infty\)") == "\u221E"


class TestSubscripts:
    def test_single_letter(self):
        assert strip_latex(r"\(\alpha_i\)") == "\u03B1\u1D62"

    def test_single_digit(self):
        assert strip_latex(r"\(x_0\)") == "x\u2080"

    def test_braced_digits(self):
        assert strip_latex(r"\(x_{12}\)") == "x\u2081\u2082"

    def test_subscript_j(self):
        assert strip_latex(r"\(\alpha_j\)") == "\u03B1\u2C7C"


class TestSuperscripts:
    def test_squared(self):
        assert strip_latex(r"\(x^2\)") == "x\u00B2"

    def test_cubed(self):
        assert strip_latex(r"\(x^3\)") == "x\u00B3"

    def test_braced_exponent(self):
        assert strip_latex(r"\(x^{10}\)") == "x\u00B9\u2070"

    def test_superscript_n(self):
        assert strip_latex(r"\(x^n\)") == "x\u207F"


class TestFracAndSqrt:
    def test_frac(self):
        assert strip_latex(r"\(\frac{1}{2}\)") == "1/2"

    def test_sqrt(self):
        assert strip_latex(r"\(\sqrt{x}\)") == "\u221Ax"


class TestDelimiters:
    def test_inline_delimiters_stripped(self):
        result = strip_latex(r"\(\alpha\)")
        assert r"\(" not in result
        assert r"\)" not in result

    def test_display_delimiters_stripped(self):
        result = strip_latex(r"\[x^2 + y^2\]")
        assert r"\[" not in result
        assert r"\]" not in result

    def test_mixed_text_and_math(self):
        result = strip_latex(r"The rate \(\alpha_i\) is positive")
        assert result == "The rate \u03B1\u1D62 is positive"

    def test_multiple_math_blocks(self):
        result = strip_latex(r"\(\alpha\) and \(\beta\)")
        assert "\u03B1" in result
        assert "\u03B2" in result


class TestPassthrough:
    def test_plain_text_unchanged(self):
        assert strip_latex("Hello world") == "Hello world"

    def test_currency_preserved(self):
        assert strip_latex("$5 million") == "$5 million"

    def test_multiple_currency_preserved(self):
        text = "$5 million in Series A at a $25 million valuation"
        assert strip_latex(text) == text

    def test_empty_string(self):
        assert strip_latex("") == ""


class TestEdgeCases:
    def test_unknown_command(self):
        result = strip_latex(r"\(\foo{x}\)")
        # Unknown commands stripped, content preserved
        assert "x" in result

    def test_nested_braces(self):
        result = strip_latex(r"\(\frac{a+b}{c}\)")
        assert "a+b" in result
        assert "c" in result

    def test_empty_delimiters(self):
        assert strip_latex(r"\(\)") == ""

    def test_braces_stripped(self):
        result = strip_latex(r"\({x}\)")
        assert "{" not in result
        assert "}" not in result
        assert "x" in result


class TestSymbolTableSync:
    """Ensure _LATEX_SYMBOLS in latex_utils.py stays in sync with latex_text.py."""

    def test_shared_symbols_match(self):
        import importlib.util
        from pathlib import Path

        # Import latex_text.py from the skill scripts path
        spec = importlib.util.spec_from_file_location(
            "latex_text",
            Path(__file__).parent.parent
            / "proof-engine/skills/proof-engine/scripts/latex_text.py",
        )
        latex_text = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(latex_text)

        from tools.lib.latex_utils import _LATEX_SYMBOLS as site_symbols

        # latex_utils may have extra entries (e.g. \sum, \prod, \sqrt)
        # but every entry in latex_text must appear in latex_utils
        canonical = dict(latex_text._LATEX_SYMBOLS)
        site = dict(site_symbols)
        for cmd, char in canonical.items():
            assert cmd in site, f"{cmd} in latex_text.py but missing from latex_utils.py"
            assert site[cmd] == char, (
                f"{cmd} maps to {char!r} in latex_text.py "
                f"but {site[cmd]!r} in latex_utils.py"
            )
