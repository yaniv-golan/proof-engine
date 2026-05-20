"""Tests for tools.lib.proof_cache.

As of v1.37.0, the backends moved into `proof_citations.registry.*` and
this module's `_resolve_X` functions translate the new `ResolvedRecord`
back to the legacy `ResolvedReference` shape. Tests mock at the HTTPSession
layer so the translation logic is exercised end-to-end.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from tools.lib.proof_cache import (
    identifier_from_url,
    ResolvedReference,
    resolve,
)


@pytest.mark.parametrize("url,expected", [
    ("https://arxiv.org/abs/2603.21852",        ("arxiv", "2603.21852")),
    ("https://arxiv.org/abs/2603.21852v2",      ("arxiv", "2603.21852")),
    ("https://arxiv.org/html/2603.21852",       ("arxiv", "2603.21852")),
    ("https://arxiv.org/html/2603.21852v1/",    ("arxiv", "2603.21852")),
    ("https://ar5iv.labs.arxiv.org/html/2603.21852", ("arxiv", "2603.21852")),
    ("https://doi.org/10.1051/0004-6361/201833910",  ("doi",   "10.1051/0004-6361/201833910")),
    ("https://dx.doi.org/10.1051/0004-6361/201833910", ("doi", "10.1051/0004-6361/201833910")),
    ("https://iopscience.iop.org/article/10.1088/1475-7516/2020/09/010",
        ("doi", "10.1088/1475-7516/2020/09/010")),
    ("https://archive.softwareheritage.org/swh:1:dir:0000000000000000000000000000000000000000",
        ("swhid", "swh:1:dir:0000000000000000000000000000000000000000")),
    ("https://example.com/blog/post",           ("url", "https://example.com/blog/post")),
])
def test_identifier_from_url(url, expected):
    assert identifier_from_url(url) == expected


def test_identifier_from_url_empty():
    assert identifier_from_url("") is None
    assert identifier_from_url(None) is None


def _mock_session(*responses):
    """Build a mock HTTPSession whose .get() returns the given responses in order."""
    session = MagicMock()
    if len(responses) == 1:
        session.get.return_value = responses[0]
    else:
        session.get.side_effect = list(responses)
    return session


def _mock_response(*, status_code=200, json_data=None, text=""):
    resp = MagicMock(status_code=status_code, text=text)
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
    if json_data is not None:
        resp.json = MagicMock(return_value=json_data)
    return resp


_ARXIV_RESPONSE_TEXT = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2603.21852v2</id>
    <title>All elementary functions from a single binary operator</title>
    <published>2026-03-31T00:00:00Z</published>
    <updated>2026-04-05T00:00:00Z</updated>
    <author><name>Andrzej Odrzywołek</name></author>
  </entry>
</feed>
"""


def test_resolve_arxiv_populates_fields():
    """Translation: arxiv ResolvedRecord → legacy ResolvedReference."""
    mock_resp = _mock_response(text=_ARXIV_RESPONSE_TEXT)
    session = _mock_session(mock_resp)
    with patch("tools.lib.proof_cache.get_default_session", return_value=session):
        ref = resolve("arxiv", "2603.21852", refresh=True)
    assert isinstance(ref, ResolvedReference)
    assert ref.identifier_type == "arxiv"
    assert ref.identifier_value == "2603.21852"
    assert ref.title == "All elementary functions from a single binary operator"
    # Authors translate to "Given Family" strings
    assert ref.authors == ["Andrzej Odrzywołek"]
    assert ref.year == 2026
    assert ref.canonical_url == "https://arxiv.org/abs/2603.21852"
    assert ref.version == "v2"  # extracted from id_url, stored in raw
    assert ref.venue == "arXiv preprint"  # legacy venue label preserved
    assert ref.source_api == "export.arxiv.org/api/query"


def test_resolve_without_refresh_reads_cache(tmp_path):
    from tools.lib.proof_cache import save_cache, load_cache
    ref = ResolvedReference(
        identifier_type="arxiv", identifier_value="2603.21852",
        canonical_url="https://arxiv.org/abs/2603.21852",
        title="All elementary functions from a single binary operator",
        authors=["Andrzej Odrzywołek"], year=2026,
        venue="arXiv preprint", version="v2",
        resolved_at="2026-04-17T00:00:00Z",
        source_api="export.arxiv.org/api/query", raw={},
    )
    save_cache(tmp_path, {"arxiv:2603.21852": ref})
    cache = load_cache(tmp_path)
    assert "arxiv:2603.21852" in cache
    assert cache["arxiv:2603.21852"].title == ref.title
    assert cache["arxiv:2603.21852"].authors == ["Andrzej Odrzywołek"]


_DATACITE_RESPONSE = {
    "data": {
        "attributes": {
            "titles": [{"title": "Planck 2018 results VI"}],
            "publicationYear": 2020,
            "creators": [
                {"givenName": "Aäron", "familyName": "van den Oord"},
                {"givenName": "N.", "familyName": "Collaboration"},
            ],
            "publisher": "A&A",
        }
    }
}

_CROSSREF_RESPONSE = {
    "message": {
        "title": ["Crossref-only paper"],
        "published-print": {"date-parts": [[2019]]},
        "author": [{"given": "Jane", "family": "Smith"}],
        "container-title": ["Journal of Fallback"],
    }
}


def test_resolve_doi_datacite_primary():
    datacite_resp = _mock_response(status_code=200, json_data=_DATACITE_RESPONSE)
    session = _mock_session(datacite_resp)
    with patch("tools.lib.proof_cache.get_default_session", return_value=session):
        ref = resolve("doi", "10.1000/foo", refresh=True)
    assert ref.identifier_type == "doi"
    assert ref.title == "Planck 2018 results VI"
    assert ref.year == 2020
    assert "van den Oord" in ref.authors[0]
    assert ref.venue == "A&A"  # legacy: venue = publisher for DataCite
    assert ref.source_api == "api.datacite.org"


def test_resolve_doi_crossref_fallback_on_404():
    datacite_404 = _mock_response(status_code=404)
    crossref_ok = _mock_response(status_code=200, json_data=_CROSSREF_RESPONSE)
    session = _mock_session(datacite_404, crossref_ok)
    with patch("tools.lib.proof_cache.get_default_session", return_value=session):
        ref = resolve("doi", "10.1000/fallback", refresh=True)
    assert ref.title == "Crossref-only paper"
    assert ref.year == 2019
    assert ref.authors == ["Jane Smith"]
    assert ref.venue == "Journal of Fallback"
    assert ref.source_api == "api.crossref.org"


_SWH_RESPONSE = {
    "object_type": "directory",
    "object_id": "0" * 40,
    "origin_url": "https://github.com/yaniv-golan/proof-engine",
}


def test_resolve_swhid():
    resp = _mock_response(status_code=200, json_data=_SWH_RESPONSE)
    session = _mock_session(resp)
    with patch("tools.lib.proof_cache.get_default_session", return_value=session):
        ref = resolve("swhid", "swh:1:dir:" + "0" * 40, refresh=True)
    assert ref.identifier_type == "swhid"
    assert ref.title
    assert ref.source_api == "archive.softwareheritage.org/api/1/resolve"


_ISBN_RESPONSE = {
    "ISBN:9780262033848": {
        "title": "Introduction to Algorithms",
        "authors": [{"name": "Thomas H. Cormen"}, {"name": "Charles E. Leiserson"}],
        "publish_date": "2009",
        "publishers": [{"name": "MIT Press"}],
    }
}


def test_resolve_isbn():
    resp = _mock_response(status_code=200, json_data=_ISBN_RESPONSE)
    session = _mock_session(resp)
    with patch("tools.lib.proof_cache.get_default_session", return_value=session):
        ref = resolve("isbn", "9780262033848", refresh=True)
    assert ref.title == "Introduction to Algorithms"
    # `Author.from_full_name` parses 'Thomas H. Cormen' → family='Cormen', given='Thomas H.'
    # Legacy translation joins as 'Thomas H. Cormen'
    assert "Cormen" in ref.authors[0]
    assert ref.year == 2009
    assert ref.venue == "MIT Press"


def test_resolve_url_reads_og_meta():
    html = (
        '<html><head>'
        '<meta property="og:title" content="My Blog Post"/>'
        '<meta property="og:article:author" content="Jane Smith"/>'
        '<meta property="article:published_time" content="2024-03-01"/>'
        '</head><body></body></html>'
    )
    resp = _mock_response(status_code=200, text=html)
    session = _mock_session(resp)
    with patch("tools.lib.proof_cache.get_default_session", return_value=session):
        ref = resolve("url", "https://example.com/post", refresh=True)
    assert ref.title == "My Blog Post"
    assert ref.authors == ["Jane Smith"]
    assert ref.year == 2024


def test_collect_identifiers_from_meta_and_evidence(tmp_path):
    import json as _json
    from tools.lib.proof_cache import collect_identifiers
    (tmp_path / "meta.yaml").write_text(
        "tags: [math]\n"
        "depends_on:\n"
        "  - relation: References\n"
        "    identifiers:\n"
        "      - type: arxiv\n"
        "        value: '2603.21852'\n"
        "      - type: doi\n"
        "        value: '10.1051/0004-6361/201833910'\n"
        "      - type: slug\n"
        "        value: some-other-proof\n"
    )
    (tmp_path / "proof.json").write_text(_json.dumps({
        "claim_natural": "x",
        "evidence": {
            "B1": {"source": {"url": "https://arxiv.org/abs/1609.03499"}},
            "B2": {"source": {"url": "https://example.com/blog"}},
        }
    }))
    identifiers = collect_identifiers(tmp_path)
    assert ("arxiv", "2603.21852") in identifiers
    assert ("doi", "10.1051/0004-6361/201833910") in identifiers
    assert ("arxiv", "1609.03499") in identifiers
    assert ("url", "https://example.com/blog") in identifiers
    assert len(identifiers) == len(set(identifiers))
