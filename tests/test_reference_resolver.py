import pytest
import requests
from unittest.mock import patch, MagicMock
from tools.lib.reference_resolver import identifier_from_url, ResolvedReference, resolve


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


_ARXIV_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2603.21852v2</id>
    <title>All elementary functions from a single binary operator</title>
    <published>2026-03-31T00:00:00Z</published>
    <updated>2026-04-05T00:00:00Z</updated>
    <author><name>Andrzej Odrzywo\u0142ek</name></author>
  </entry>
</feed>
"""


def test_resolve_arxiv_populates_fields():
    mock_resp = MagicMock(status_code=200, text=_ARXIV_RESPONSE)
    mock_resp.raise_for_status = MagicMock()
    with patch("tools.lib.reference_resolver.requests.get", return_value=mock_resp) as mock_get:
        ref = resolve("arxiv", "2603.21852", refresh=True)
    assert mock_get.called
    assert isinstance(ref, ResolvedReference)
    assert ref.identifier_type == "arxiv"
    assert ref.identifier_value == "2603.21852"
    assert ref.title == "All elementary functions from a single binary operator"
    assert ref.authors == ["Andrzej Odrzywo\u0142ek"]
    assert ref.year == 2026
    assert ref.canonical_url == "https://arxiv.org/abs/2603.21852"
    assert ref.version == "v2"
    assert ref.source_api == "export.arxiv.org/api/query"


def test_resolve_without_refresh_reads_cache(tmp_path):
    from tools.lib.reference_resolver import save_cache, load_cache
    ref = ResolvedReference(
        identifier_type="arxiv", identifier_value="2603.21852",
        canonical_url="https://arxiv.org/abs/2603.21852",
        title="All elementary functions from a single binary operator",
        authors=["Andrzej Odrzywo\u0142ek"], year=2026,
        venue="arXiv preprint", version="v2",
        resolved_at="2026-04-17T00:00:00Z",
        source_api="export.arxiv.org/api/query", raw={},
    )
    save_cache(tmp_path, {"arxiv:2603.21852": ref})
    cache = load_cache(tmp_path)
    assert "arxiv:2603.21852" in cache
    assert cache["arxiv:2603.21852"].title == ref.title


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
    datacite_resp = MagicMock(status_code=200)
    datacite_resp.raise_for_status = MagicMock()
    datacite_resp.json = MagicMock(return_value=_DATACITE_RESPONSE)
    with patch("tools.lib.reference_resolver.requests.get", return_value=datacite_resp):
        ref = resolve("doi", "10.1000/foo", refresh=True)
    assert ref.identifier_type == "doi"
    assert ref.title == "Planck 2018 results VI"
    assert ref.year == 2020
    assert "van den Oord" in ref.authors[0]
    assert ref.raw["datacite"]["data"]["attributes"]["creators"][0]["familyName"] == "van den Oord"


def test_resolve_doi_crossref_fallback_on_404():
    datacite_404 = MagicMock(status_code=404)
    http_err = requests.exceptions.HTTPError()
    http_err.response = datacite_404
    datacite_404.raise_for_status = MagicMock(side_effect=http_err)
    crossref_ok = MagicMock(status_code=200)
    crossref_ok.raise_for_status = MagicMock()
    crossref_ok.json = MagicMock(return_value=_CROSSREF_RESPONSE)
    with patch("tools.lib.reference_resolver.requests.get",
               side_effect=[datacite_404, crossref_ok]):
        ref = resolve("doi", "10.1000/fallback", refresh=True)
    assert ref.title == "Crossref-only paper"
    assert ref.year == 2019
    assert ref.authors == ["Jane Smith"]


_SWH_RESPONSE = {
    "object_type": "directory",
    "object_id": "0" * 40,
    "origin_url": "https://github.com/yaniv-golan/proof-engine",
}


def test_resolve_swhid():
    resp = MagicMock(status_code=200)
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value=_SWH_RESPONSE)
    with patch("tools.lib.reference_resolver.requests.get", return_value=resp):
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
    resp = MagicMock(status_code=200)
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value=_ISBN_RESPONSE)
    with patch("tools.lib.reference_resolver.requests.get", return_value=resp):
        ref = resolve("isbn", "9780262033848", refresh=True)
    assert ref.title == "Introduction to Algorithms"
    assert "Thomas H. Cormen" in ref.authors
    assert ref.year == 2009


def test_resolve_url_reads_og_meta():
    html = (
        '<html><head>'
        '<meta property="og:title" content="My Blog Post"/>'
        '<meta property="og:article:author" content="Jane Smith"/>'
        '<meta property="article:published_time" content="2024-03-01"/>'
        '</head><body></body></html>'
    )
    resp = MagicMock(status_code=200, text=html)
    resp.raise_for_status = MagicMock()
    with patch("tools.lib.reference_resolver.requests.get", return_value=resp):
        ref = resolve("url", "https://example.com/post", refresh=True)
    assert ref.title == "My Blog Post"
    assert ref.authors == ["Jane Smith"]
    assert ref.year == 2024


def test_collect_identifiers_from_meta_and_evidence(tmp_path):
    import json as _json
    from tools.lib.reference_resolver import collect_identifiers
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
