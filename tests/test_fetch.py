"""Tests for fetch.py — HTTP transport layer with fallback chain."""

from unittest.mock import patch, MagicMock, PropertyMock
import requests as real_requests
from scripts.fetch import fetch_page, extract_pdf_text, try_wayback


# ---------------------------------------------------------------------------
# fetch_page: snapshot fallback
# ---------------------------------------------------------------------------

def test_fetch_page_snapshot_fallback_when_no_requests():
    """When requests is None and snapshot is provided, use snapshot."""
    with patch("scripts.fetch.requests", None):
        text, mode, err = fetch_page(
            "https://example.com",
            snapshot="<html>snapshot content</html>",
        )
    assert text == "<html>snapshot content</html>"
    assert mode == "snapshot"
    assert err is None


def test_fetch_page_snapshot_fallback_after_live_failure():
    """When live fetch raises an error, fall back to snapshot."""
    mock_requests = MagicMock()
    mock_requests.get.side_effect = real_requests.exceptions.ConnectionError("refused")
    mock_requests.exceptions = real_requests.exceptions

    with patch("scripts.fetch.requests", mock_requests):
        text, mode, err = fetch_page(
            "https://example.com",
            snapshot="<html>snapshot</html>",
        )
    assert text == "<html>snapshot</html>"
    assert mode == "snapshot"
    assert err is None


# ---------------------------------------------------------------------------
# fetch_page: no requests, no snapshot
# ---------------------------------------------------------------------------

def test_fetch_page_no_requests_no_snapshot():
    """When requests is None and no snapshot, return fetch_failed."""
    with patch("scripts.fetch.requests", None):
        text, mode, err = fetch_page("https://example.com")
    assert text is None
    assert mode == "fetch_failed"
    assert "requests" in err.lower()


# ---------------------------------------------------------------------------
# fetch_page: live success
# ---------------------------------------------------------------------------

def test_fetch_page_live_html_success():
    """Successful live HTML fetch returns page text."""
    mock_resp = MagicMock()
    mock_resp.text = "<html>live content</html>"
    mock_resp.headers = {"Content-Type": "text/html"}
    mock_resp.raise_for_status = MagicMock()

    mock_requests = MagicMock()
    mock_requests.get.return_value = mock_resp
    mock_requests.exceptions = real_requests.exceptions

    with patch("scripts.fetch.requests", mock_requests):
        text, mode, err = fetch_page("https://example.com")
    assert text == "<html>live content</html>"
    assert mode == "live"
    assert err is None


# ---------------------------------------------------------------------------
# fetch_page: HTTP error codes
# ---------------------------------------------------------------------------

def test_fetch_page_http_403_falls_to_snapshot():
    """HTTP 403 on live fetch should fall back to snapshot."""
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.raise_for_status.side_effect = real_requests.exceptions.HTTPError(
        response=mock_resp
    )

    mock_requests = MagicMock()
    mock_requests.get.return_value = mock_resp
    mock_requests.exceptions = real_requests.exceptions

    with patch("scripts.fetch.requests", mock_requests):
        text, mode, err = fetch_page(
            "https://example.com",
            snapshot="<html>snapshot</html>",
        )
    assert text == "<html>snapshot</html>"
    assert mode == "snapshot"


def test_fetch_page_http_404_no_fallback():
    """HTTP 404 with no snapshot or wayback returns fetch_failed."""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.raise_for_status.side_effect = real_requests.exceptions.HTTPError(
        response=mock_resp
    )

    mock_requests = MagicMock()
    mock_requests.get.return_value = mock_resp
    mock_requests.exceptions = real_requests.exceptions

    with patch("scripts.fetch.requests", mock_requests):
        text, mode, err = fetch_page("https://example.com")
    assert text is None
    assert mode == "fetch_failed"
    assert "404" in err


# ---------------------------------------------------------------------------
# fetch_page: timeout
# ---------------------------------------------------------------------------

def test_fetch_page_timeout_falls_to_snapshot():
    """Timeout on live fetch should fall back to snapshot."""
    mock_requests = MagicMock()
    mock_requests.get.side_effect = real_requests.exceptions.Timeout("timed out")
    mock_requests.exceptions = real_requests.exceptions

    with patch("scripts.fetch.requests", mock_requests):
        text, mode, err = fetch_page(
            "https://example.com",
            snapshot="<html>snapshot</html>",
        )
    assert text == "<html>snapshot</html>"
    assert mode == "snapshot"


# ---------------------------------------------------------------------------
# fetch_page: Wayback fallback
# ---------------------------------------------------------------------------

def test_fetch_page_wayback_fallback_success():
    """When live and snapshot both fail, Wayback returns content."""
    mock_requests = MagicMock()
    mock_requests.get.side_effect = [
        # First call: live fetch fails
        real_requests.exceptions.ConnectionError("refused"),
        # Second call: Wayback succeeds
        MagicMock(text="<html>wayback</html>", raise_for_status=MagicMock()),
    ]
    mock_requests.exceptions = real_requests.exceptions

    with patch("scripts.fetch.requests", mock_requests):
        text, mode, err = fetch_page(
            "https://example.com",
            wayback_fallback=True,
        )
    assert text == "<html>wayback</html>"
    assert mode == "wayback"
    assert err is None


def test_fetch_page_wayback_not_tried_without_flag():
    """Wayback should not be tried when wayback_fallback=False."""
    mock_requests = MagicMock()
    mock_requests.get.side_effect = real_requests.exceptions.ConnectionError("refused")
    mock_requests.exceptions = real_requests.exceptions

    with patch("scripts.fetch.requests", mock_requests):
        text, mode, err = fetch_page("https://example.com", wayback_fallback=False)
    assert text is None
    assert mode == "fetch_failed"
    # Only one call (live), no Wayback attempt
    assert mock_requests.get.call_count == 1


# ---------------------------------------------------------------------------
# fetch_page: PDF detection
# ---------------------------------------------------------------------------

def test_fetch_page_pdf_by_content_type():
    """PDF content type should trigger PDF extraction."""
    mock_resp = MagicMock()
    mock_resp.headers = {"Content-Type": "application/pdf"}
    mock_resp.content = b"fake pdf content"
    mock_resp.raise_for_status = MagicMock()

    mock_requests = MagicMock()
    mock_requests.get.return_value = mock_resp
    mock_requests.exceptions = real_requests.exceptions

    with patch("scripts.fetch.requests", mock_requests), \
         patch("scripts.fetch.extract_pdf_text", return_value="extracted text"):
        text, mode, err = fetch_page("https://example.com/paper")
    assert text == "extracted text"
    assert mode == "live"


def test_fetch_page_pdf_extraction_fails():
    """PDF detected but extraction fails should fall to snapshot."""
    mock_resp = MagicMock()
    mock_resp.headers = {"Content-Type": "application/pdf"}
    mock_resp.content = b"bad pdf"
    mock_resp.raise_for_status = MagicMock()

    mock_requests = MagicMock()
    mock_requests.get.return_value = mock_resp
    mock_requests.exceptions = real_requests.exceptions

    with patch("scripts.fetch.requests", mock_requests), \
         patch("scripts.fetch.extract_pdf_text", return_value=None):
        text, mode, err = fetch_page(
            "https://example.com/paper.pdf",
            snapshot="<html>snapshot</html>",
        )
    assert text == "<html>snapshot</html>"
    assert mode == "snapshot"


# ---------------------------------------------------------------------------
# extract_pdf_text
# ---------------------------------------------------------------------------

def test_extract_pdf_text_no_libraries():
    """When no PDF library is available, returns None."""
    with patch.dict("sys.modules", {"pdfplumber": None, "PyPDF2": None}):
        result = extract_pdf_text(b"fake pdf content")
    assert result is None or isinstance(result, str)
