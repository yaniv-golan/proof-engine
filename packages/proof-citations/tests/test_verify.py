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
