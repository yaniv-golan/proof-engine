import pytest
from tools.lib.sanitizer import render_markdown


def test_renders_paragraph():
    html = render_markdown("Hello world")
    assert "<p>Hello world</p>" in html


def test_renders_table():
    md = "| A | B |\n|---|---|\n| 1 | 2 |"
    html = render_markdown(md)
    assert "<table>" in html
    assert "<td>1</td>" in html


def test_renders_fenced_code():
    md = "```python\nprint('hi')\n```"
    html = render_markdown(md)
    assert "<code" in html
    assert "print" in html


def test_strips_script_tags():
    md = "Hello <script>alert('xss')</script> world"
    html = render_markdown(md)
    assert "<script>" not in html
    # Script content should not appear as executable — either stripped or escaped
    assert "alert('xss')" not in html or "&lt;script&gt;" in html


def test_strips_iframe():
    md = 'Hello <iframe src="evil.com"></iframe> world'
    html = render_markdown(md)
    assert "<iframe" not in html


def test_strips_onclick():
    md = '<a href="#" onclick="alert(1)">click</a>'
    html = render_markdown(md)
    assert "onclick" not in html


def test_allows_safe_tags():
    md = "**bold** and *italic* and [link](http://example.com)"
    html = render_markdown(md)
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html
    assert "<a " in html


def test_heading_ids_for_toc():
    md = "## My Heading"
    html = render_markdown(md)
    assert "id=" in html


def test_arithmatex_inline_preserved():
    """Inline math \\(...\\) should survive markdown+bleach in an arithmatex wrapper."""
    html = render_markdown(r"The rate \(\alpha_i\) is positive")
    assert "arithmatex" in html
    assert r"\alpha_i" in html


def test_arithmatex_display_preserved():
    """Display math \\[...\\] should survive markdown+bleach."""
    html = render_markdown(r"\[x^2 + y^2 = r^2\]")
    assert "arithmatex" in html
    assert r"x^2 + y^2 = r^2" in html


def test_arithmatex_underscore_not_emphasis():
    """Underscores inside math delimiters must not become <em> tags."""
    html = render_markdown(r"word \(\alpha_i\) word")
    assert "<em>" not in html
    assert r"\alpha_i" in html


def test_plain_markdown_unchanged_with_arithmatex():
    """Adding arithmatex must not break plain markdown rendering."""
    html = render_markdown("**bold** and *italic*")
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html


def test_currency_dollar_not_mangled():
    """Literal $ signs (currency) must not be interpreted as math.

    Dollar-sign math is disabled via inline_syntax/block_syntax config.
    """
    html = render_markdown("costs $5 million and $25 million")
    assert "$5 million" in html
    assert "arithmatex" not in html
