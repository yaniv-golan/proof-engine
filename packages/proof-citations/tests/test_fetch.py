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


def test_fetch_page_treats_recaptcha_as_failure_and_uses_snapshot():
    """HTTP 200 reCAPTCHA pages must fall through to snapshot fallback.

    Regression for cowork sandbox issue (v1.42.0): PMC and Frontiers serve a
    200-status reCAPTCHA when fingerprint looks bot-like. The previous
    fallback chain treated this as a successful fetch and quote verification
    failed with "not_found" instead of using the provided snapshot.
    """
    with _fixture_server() as base:
        page_text, fetch_mode, error = fetch_page(
            f"{base}/recaptcha_page.html",
            snapshot="<html><body>real article body</body></html>",
        )
    # The crucial regression check: live fetch returned 200, the OLD code
    # would have returned fetch_mode="live" with the CAPTCHA page as the body.
    # The fix recognizes the block-page and falls through to snapshot.
    assert fetch_mode == "snapshot"
    assert "real article body" in page_text
    # On a successful snapshot, error is None per the existing contract.
    assert error is None


def test_fetch_page_treats_cloudflare_challenge_as_failure():
    """Cloudflare browser-check pages (HTTP 200) must fall through to snapshot."""
    with _fixture_server() as base:
        page_text, fetch_mode, error = fetch_page(
            f"{base}/cloudflare_challenge.html",
            snapshot="<html><body>real article body</body></html>",
        )
    assert fetch_mode == "snapshot"
    assert "real article body" in page_text


def test_fetch_page_prefer_snapshot_skips_live_fetch_when_snapshot_present():
    """prefer_snapshot=True uses snapshot before trying live fetch."""
    with _fixture_server() as base:
        page_text, fetch_mode, error = fetch_page(
            f"{base}/sample.html",  # would succeed live
            snapshot="<html>preferred snapshot</html>",
            prefer_snapshot=True,
        )
    assert fetch_mode == "snapshot"
    assert page_text == "<html>preferred snapshot</html>"
    assert error is None


def test_fetch_page_prefer_snapshot_falls_back_to_live_when_no_snapshot():
    """prefer_snapshot=True still falls back to live fetch if snapshot is empty."""
    with _fixture_server() as base:
        page_text, fetch_mode, error = fetch_page(
            f"{base}/sample.html",
            snapshot=None,
            prefer_snapshot=True,
        )
    assert fetch_mode == "live"
    assert "hello world" in page_text.lower()


def test_fetch_page_resolves_snapshot_file_against_snapshot_base_dir(tmp_path):
    """Relative snapshot_file paths must be anchored to snapshot_base_dir,
    not the caller's CWD — so a published proof.py re-runs from any CWD.
    """
    import os
    snap_dir = tmp_path / "snapshots"
    snap_dir.mkdir()
    (snap_dir / "B1_snapshot.txt").write_text(
        "The verbatim quote that should be found.", encoding="utf-8"
    )

    # Change CWD away from tmp_path to prove the relative path doesn't
    # depend on CWD when snapshot_base_dir is supplied.
    original = os.getcwd()
    os.chdir("/tmp")
    try:
        page_text, fetch_mode, err = fetch_page(
            "https://example-blocked.test/article",
            skip_live_fetch=True,
            snapshot_file="snapshots/B1_snapshot.txt",
            snapshot_base_dir=str(tmp_path),
        )
    finally:
        os.chdir(original)

    assert page_text is not None
    assert fetch_mode == "snapshot"
    assert "verbatim quote" in page_text


def test_fetch_page_absolute_snapshot_file_ignores_snapshot_base_dir(tmp_path):
    """Absolute snapshot_file paths are taken verbatim — back-compat with
    callers that pre-resolve paths."""
    snap = tmp_path / "absolute.txt"
    snap.write_text("absolute path content", encoding="utf-8")

    page_text, fetch_mode, err = fetch_page(
        "https://example-blocked.test/article",
        skip_live_fetch=True,
        snapshot_file=str(snap),  # absolute
        snapshot_base_dir="/nonexistent",  # ignored because path is absolute
    )
    assert page_text is not None
    assert fetch_mode == "snapshot"
    assert "absolute path content" in page_text
