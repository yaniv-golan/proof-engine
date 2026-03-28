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
    assert "<code>" in html
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


def test_adds_nofollow_to_links():
    md = "[link](http://example.com)"
    html = render_markdown(md)
    assert 'rel="nofollow"' in html


def test_heading_ids_for_toc():
    md = "## My Heading"
    html = render_markdown(md)
    assert "id=" in html
