"""Tests for oa_lookup.py — DOI extraction and Unpaywall OA discovery."""

from unittest.mock import patch, MagicMock
import json


# ---------------------------------------------------------------------------
# DOI extraction
# ---------------------------------------------------------------------------

def test_extract_doi_from_doi_org_url():
    from scripts.oa_lookup import extract_doi
    assert extract_doi("https://doi.org/10.1234/example.2024") == "10.1234/example.2024"


def test_extract_doi_from_dx_doi_url():
    from scripts.oa_lookup import extract_doi
    assert extract_doi("https://dx.doi.org/10.1038/nature12373") == "10.1038/nature12373"


def test_extract_doi_from_explicit_field():
    from scripts.oa_lookup import extract_doi
    assert extract_doi("https://some-journal.com/article", doi="10.1234/test") == "10.1234/test"


def test_extract_doi_no_doi_returns_none():
    from scripts.oa_lookup import extract_doi
    assert extract_doi("https://example.com/no-doi-here") is None


def test_extract_doi_explicit_field_takes_precedence():
    from scripts.oa_lookup import extract_doi
    result = extract_doi("https://doi.org/10.1234/from-url", doi="10.1234/from-field")
    assert result == "10.1234/from-field"


# ---------------------------------------------------------------------------
# Unpaywall lookup
# ---------------------------------------------------------------------------

def test_lookup_oa_url_returns_best_url():
    from scripts.oa_lookup import lookup_oa_url
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "best_oa_location": {
            "url_for_pdf": "https://arxiv.org/pdf/2024.12345.pdf",
            "url_for_landing_page": "https://arxiv.org/abs/2024.12345",
        }
    }
    mock_resp.raise_for_status = MagicMock()

    mock_requests = MagicMock()
    mock_requests.get.return_value = mock_resp

    with patch("proof_citations.oa_lookup.requests", mock_requests):
        result = lookup_oa_url("10.1234/test", email="test@example.com")
    assert result == "https://arxiv.org/abs/2024.12345"
    # Verify it prefers landing page over PDF
    assert "unpaywall.org" in mock_requests.get.call_args[0][0]


def test_lookup_oa_url_falls_back_to_pdf():
    from scripts.oa_lookup import lookup_oa_url
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "best_oa_location": {
            "url_for_pdf": "https://arxiv.org/pdf/2024.12345.pdf",
            "url_for_landing_page": None,
        }
    }
    mock_resp.raise_for_status = MagicMock()

    mock_requests = MagicMock()
    mock_requests.get.return_value = mock_resp

    with patch("proof_citations.oa_lookup.requests", mock_requests):
        result = lookup_oa_url("10.1234/test", email="test@example.com")
    assert result == "https://arxiv.org/pdf/2024.12345.pdf"


def test_lookup_oa_url_no_oa_returns_none():
    from scripts.oa_lookup import lookup_oa_url
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"best_oa_location": None}
    mock_resp.raise_for_status = MagicMock()

    mock_requests = MagicMock()
    mock_requests.get.return_value = mock_resp

    with patch("proof_citations.oa_lookup.requests", mock_requests):
        result = lookup_oa_url("10.1234/test", email="test@example.com")
    assert result is None


def test_lookup_oa_url_api_error_returns_none():
    from scripts.oa_lookup import lookup_oa_url
    import requests as real_req
    mock_requests = MagicMock()
    mock_requests.get.side_effect = real_req.exceptions.ConnectionError("fail")
    mock_requests.exceptions = real_req.exceptions

    with patch("proof_citations.oa_lookup.requests", mock_requests):
        result = lookup_oa_url("10.1234/test", email="test@example.com")
    assert result is None


def test_lookup_oa_url_no_email_returns_none():
    from scripts.oa_lookup import lookup_oa_url
    result = lookup_oa_url("10.1234/test", email=None)
    assert result is None
