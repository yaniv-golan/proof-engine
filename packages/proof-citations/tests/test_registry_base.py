"""Tests for proof_citations.registry.base — Author, ResolvedRecord, caches."""

import json
from pathlib import Path

import pytest

from proof_citations.registry.base import (
    Author,
    ResolvedRecord,
    InMemoryCache,
    FileCache,
    ResolutionError,
    now_iso,
)


class TestAuthor:
    def test_minimal_author(self):
        a = Author(family="Smith")
        assert a.family == "Smith"
        assert a.given == ""
        assert a.orcid is None
        assert a.display() == "Smith"

    def test_full_author(self):
        a = Author(family="Doe", given="Jane", orcid="0000-0002-1825-0097")
        assert a.display() == "Doe, J."

    def test_display_with_multi_given(self):
        a = Author(family="Doe", given="Jane Q")
        assert a.display() == "Doe, J.Q."

    def test_matches_loose(self):
        a = Author(family="Smith")
        assert a.matches("J. Smith and others")
        assert a.matches("SMITH")
        assert not a.matches("Jones")

    def test_from_full_name_comma_form(self):
        a = Author.from_full_name("Smith, Jane")
        assert a.family == "Smith"
        assert a.given == "Jane"

    def test_from_full_name_western_order(self):
        a = Author.from_full_name("Jane Smith")
        assert a.family == "Smith"
        assert a.given == "Jane"

    def test_from_full_name_single_token(self):
        a = Author.from_full_name("Plato")
        assert a.family == "Plato"
        assert a.given == ""

    def test_from_full_name_empty(self):
        a = Author.from_full_name("")
        assert a.family == ""


class TestResolvedRecord:
    def _sample(self) -> ResolvedRecord:
        return ResolvedRecord(
            identifier_type="pmid",
            identifier_value="12345",
            canonical_url="https://pubmed.ncbi.nlm.nih.gov/12345/",
            title="Example study",
            authors=[Author(family="Smith", given="J")],
            year=2020,
            venue="J Example",
            doi="10.1234/test",
            pmid="12345",
            resolved_at=now_iso(),
            source_api="test",
            raw={"some": "payload"},
        )

    def test_cache_key(self):
        r = self._sample()
        assert r.cache_key() == "pmid:12345"

    def test_to_dict_round_trip(self):
        r = self._sample()
        d = r.to_dict()
        r2 = ResolvedRecord.from_dict(d)
        assert r2.title == r.title
        assert r2.year == r.year
        assert r2.cache_key() == r.cache_key()
        assert len(r2.authors) == 1
        assert r2.authors[0].family == "Smith"

    def test_to_dict_drops_raw_when_asked(self):
        r = self._sample()
        d = r.to_dict(include_raw=False)
        assert "raw" not in d or d["raw"] == {} or d["raw"] is None
        # Crucially, must not crash on the rest
        r2 = ResolvedRecord.from_dict(d)
        assert r2.title == "Example study"

    def test_from_dict_drops_unknown_keys(self):
        d = self._sample().to_dict()
        d["future_field_that_doesnt_exist_yet"] = "value"
        # Must not raise — forwards-compat policy
        r2 = ResolvedRecord.from_dict(d)
        assert r2.title == "Example study"

    def test_authors_string_fallback(self):
        """Old caches may have authors as list[str]. Loading must not crash."""
        d = self._sample().to_dict()
        d["authors"] = ["Smith J", "Doe A"]
        r2 = ResolvedRecord.from_dict(d)
        assert len(r2.authors) == 2
        assert r2.authors[0].family in ("Smith", "Smith J", "J")


class TestInMemoryCache:
    def test_empty_returns_none(self):
        c = InMemoryCache()
        assert c.get("pmid:1") is None

    def test_put_then_get(self):
        c = InMemoryCache()
        r = ResolvedRecord(
            identifier_type="pmid", identifier_value="1",
            canonical_url="https://example.com/1",
        )
        c.put("pmid:1", r)
        assert c.get("pmid:1") is r
        assert c.get("pmid:2") is None

    def test_len_reflects_stores(self):
        c = InMemoryCache()
        for i in range(5):
            r = ResolvedRecord(
                identifier_type="pmid", identifier_value=str(i),
                canonical_url=f"https://example.com/{i}",
            )
            c.put(f"pmid:{i}", r)
        assert len(c) == 5


class TestFileCache:
    def test_default_path_under_xdg_cache_home(self, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
        c = FileCache()
        assert c.path.parent == tmp_path / "proof-citations"

    def test_explicit_path(self, tmp_path):
        cache_file = tmp_path / "my_cache.json"
        c = FileCache(path=cache_file)
        assert c.path == cache_file

    def test_get_missing_returns_none(self, tmp_path):
        c = FileCache(path=tmp_path / "cache.json")
        assert c.get("pmid:1") is None

    def test_put_then_get_persists(self, tmp_path):
        c = FileCache(path=tmp_path / "cache.json")
        r = ResolvedRecord(
            identifier_type="pmid", identifier_value="1",
            canonical_url="https://example.com/1",
            title="T",
        )
        c.put("pmid:1", r)
        assert (tmp_path / "cache.json").exists()

        # Create a fresh instance to confirm persistence
        c2 = FileCache(path=tmp_path / "cache.json")
        got = c2.get("pmid:1")
        assert got is not None
        assert got.title == "T"

    def test_include_raw_default_false(self, tmp_path):
        c = FileCache(path=tmp_path / "cache.json")
        r = ResolvedRecord(
            identifier_type="pmid", identifier_value="1",
            canonical_url="https://example.com/1",
            raw={"big_payload": "x" * 1000},
        )
        c.put("pmid:1", r)
        payload = json.loads((tmp_path / "cache.json").read_text())
        # raw should be empty {} or omitted in the persisted form
        record = payload["records"]["pmid:1"]
        assert not record.get("raw")

    def test_include_raw_true(self, tmp_path):
        c = FileCache(path=tmp_path / "cache.json", include_raw=True)
        r = ResolvedRecord(
            identifier_type="pmid", identifier_value="1",
            canonical_url="https://example.com/1",
            raw={"big_payload": "x" * 100},
        )
        c.put("pmid:1", r)
        payload = json.loads((tmp_path / "cache.json").read_text())
        assert payload["records"]["pmid:1"]["raw"] == {"big_payload": "x" * 100}

    def test_corrupt_cache_treated_as_empty(self, tmp_path):
        path = tmp_path / "cache.json"
        path.write_text("this is not json")
        c = FileCache(path=path)
        assert c.get("pmid:1") is None
        # Should now be able to write without crashing
        c.put("pmid:1", ResolvedRecord(
            identifier_type="pmid", identifier_value="1",
            canonical_url="https://example.com/1",
        ))
        assert c.get("pmid:1") is not None


class TestResolutionError:
    def test_default_kind(self):
        e = ResolutionError("oops")
        assert e.kind == "fetch_failed"

    def test_explicit_kind(self):
        e = ResolutionError("nope", kind="not_found")
        assert e.kind == "not_found"

    def test_invalid_kind_raises(self):
        with pytest.raises(ValueError):
            ResolutionError("?", kind="invented")

    def test_details_preserved(self):
        e = ResolutionError("x", kind="rate_limited", details={"status": 429})
        assert e.details == {"status": 429}
