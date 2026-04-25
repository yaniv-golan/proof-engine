import http.server
import socketserver
import threading
from contextlib import contextmanager
from pathlib import Path

import pytest

from proof_citations.fetch import fetch_page


FIXTURES = Path(__file__).parent / "fixtures"


@contextmanager
def _fixture_server():
    """Serve tests/fixtures/ on a random local port."""
    handler = http.server.SimpleHTTPRequestHandler
    original_dir = Path.cwd()
    import os
    os.chdir(FIXTURES)
    try:
        with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
            port = httpd.server_address[1]
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                yield f"http://127.0.0.1:{port}"
            finally:
                httpd.shutdown()
    finally:
        os.chdir(original_dir)


def test_fetch_page_returns_body_for_html():
    with _fixture_server() as base:
        page_text, fetch_mode, error = fetch_page(f"{base}/sample.html")
    assert page_text is not None
    assert "hello world" in page_text.lower()
    assert fetch_mode == "live"
    assert error is None


def test_fetch_page_reports_failure_for_404_without_raising():
    # `fetch_page` has a Wayback fallback that kicks in when live fetch fails.
    # For fast local-404 tests, pass wayback_fallback=False (the default) and
    # a short timeout so the test doesn't hang on network hiccups.
    with _fixture_server() as base:
        page_text, fetch_mode, error = fetch_page(
            f"{base}/does-not-exist.html",
            timeout=3,
            wayback_fallback=False,
        )
    assert page_text is None
    assert fetch_mode == "fetch_failed"
    assert error is not None  # error_message describes the HTTP failure


def test_fetch_page_accepts_snapshot_fallback():
    """Passing a snapshot string returns it when live fetch is skipped."""
    page_text, fetch_mode, error = fetch_page(
        "https://127.0.0.1:1/will-not-fetch",
        snapshot="<html>snapshot body</html>",
        skip_live_fetch=True,
    )
    assert page_text == "<html>snapshot body</html>"
    assert fetch_mode == "snapshot"
    assert error is None
