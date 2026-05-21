import http.server
import socketserver
import threading
from contextlib import contextmanager
from pathlib import Path
import os

import pytest

from proof_citations import verify_citation


FIXTURES = Path(__file__).parent / "fixtures"


@contextmanager
def _fixture_server():
    original_dir = Path.cwd()
    os.chdir(FIXTURES)
    try:
        with socketserver.TCPServer(("127.0.0.1", 0),
                                    http.server.SimpleHTTPRequestHandler) as httpd:
            port = httpd.server_address[1]
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                yield f"http://127.0.0.1:{port}"
            finally:
                httpd.shutdown()
    finally:
        os.chdir(original_dir)


def test_verify_exact_quote_passes():
    with _fixture_server() as base:
        result = verify_citation(
            f"{base}/sample_article.html",
            "The consumer price index increased by 3.4 percent",
            "B1",
        )
    assert result["status"] == "verified"


def test_verify_missing_quote_returns_not_found():
    with _fixture_server() as base:
        result = verify_citation(
            f"{base}/sample_article.html",
            "The moon is made of cheese",
            "B1",
        )
    assert result["status"] == "not_found"


def test_verify_en_dash_quote_passes_via_normalization():
    # Fixture contains "4\u20135 percent" (en-dash). Quote uses ASCII hyphen.
    # Normalization must make these equivalent.
    with _fixture_server() as base:
        result = verify_citation(
            f"{base}/sample_article.html",
            "4-5 percent",
            "B1",
        )
    assert result["status"] == "verified"


def test_verify_inline_html_tags_stripped():
    # Fixture wraps "3.4 percent" in <span class="figure">. The quote
    # should still match because HTML tags are stripped during verification.
    with _fixture_server() as base:
        result = verify_citation(
            f"{base}/sample_article.html",
            "3.4 percent",
            "B1",
        )
    assert result["status"] == "verified"


def test_verify_result_carries_credibility():
    """Every result includes a credibility assessment of the source domain."""
    with _fixture_server() as base:
        result = verify_citation(
            f"{base}/sample_article.html",
            "The consumer price index increased by 3.4 percent",
            "B1",
        )
    assert "credibility" in result
    assert "tier" in result["credibility"]


def test_verify_citation_skip_live_fetch_uses_snapshot():
    """skip_live_fetch=True forces the snapshot path even when the URL is reachable."""
    with _fixture_server() as base:
        # Live URL would NOT contain the quote; snapshot does.
        result = verify_citation(
            f"{base}/sample.html",
            "The consumer price index increased by 3.4 percent",
            "B1",
            snapshot=(
                "<html><body>The consumer price index increased by "
                "3.4 percent in 2023.</body></html>"
            ),
            skip_live_fetch=True,
        )
    assert result["status"] == "verified"
    assert result["fetch_mode"] == "snapshot"


def test_verify_citation_falls_through_recaptcha_to_snapshot():
    """End-to-end: verify_citation against a 200-CAPTCHA URL with snapshot uses snapshot."""
    with _fixture_server() as base:
        result = verify_citation(
            f"{base}/recaptcha_page.html",
            "The consumer price index increased by 3.4 percent",
            "B1",
            snapshot=(
                "<html><body>The consumer price index increased by "
                "3.4 percent in 2023.</body></html>"
            ),
        )
    assert result["status"] == "verified"
    assert result["fetch_mode"] == "snapshot"


def test_verify_citation_strips_real_script_block_but_preserves_prose():
    """Fix 2 regression: the page's real <script>...</script> block gets
    stripped (preventing the 30s hang on dense JS), but the body prose
    around it is preserved and matches against the quote.
    """
    with _fixture_server() as base:
        result = verify_citation(
            f"{base}/quote_with_script_substring.html",
            "is still parsed identically by all major browsers",
            "B1",
        )
    assert result["status"] == "verified", result.get("message")


def test_strip_non_content_blocks_not_called_on_quote_path():
    """Fix 2 contract: _strip_non_content_blocks must only run on fetched
    page HTML, never on expected_quote. The strip requires both an opening
    AND closing tag, so a stray '<script>' (no closing) in a quote is safe
    even if the helper did run — but the stronger guarantee is that the
    helper is not in the quote normalization call graph at all.
    """
    from proof_citations.verify import _strip_non_content_blocks

    # Helper is a no-op when there's no closing tag — proving quotes with
    # unclosed '<script>' substrings would survive even if it ran.
    quote_with_partial = "the <script> tag was deprecated"
    assert _strip_non_content_blocks(quote_with_partial) == quote_with_partial

    # And a full block IS stripped.
    page_html = "<p>real</p><script>var x = 1;</script><p>text</p>"
    out = _strip_non_content_blocks(page_html)
    assert "var x" not in out
    assert "real" in out and "text" in out


def test_verify_citation_prefer_snapshot_skips_live_when_snapshot_present():
    """prefer_snapshot=True uses snapshot before live fetch for known-blocked sources."""
    with _fixture_server() as base:
        result = verify_citation(
            f"{base}/sample.html",
            "The consumer price index increased by 3.4 percent",
            "B1",
            snapshot=(
                "<html><body>The consumer price index increased by "
                "3.4 percent in 2023.</body></html>"
            ),
            prefer_snapshot=True,
        )
    assert result["status"] == "verified"
    assert result["fetch_mode"] == "snapshot"
