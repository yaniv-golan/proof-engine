from proof_citations.latex_text import latex_to_text


def test_latex_to_text_strips_simple_commands():
    assert "hello world" in latex_to_text(r"\textbf{hello} world").lower()


def test_latex_to_text_converts_greek_macros():
    # \mu should become μ (U+03BC) — scientific text relies on this
    assert "\u03bc" in latex_to_text(r"$\mu$m particle")
