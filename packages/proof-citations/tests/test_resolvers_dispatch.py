"""Tests for proof_citations.resolvers dispatch layer."""

from unittest.mock import MagicMock

import pytest

from proof_citations.resolvers import (
    resolve,
    register_backend,
    get_backend,
    InMemoryCache,
)
from proof_citations.resolvers.base import ResolvedRecord, now_iso


def _fake_backend(value, *, session):
    return ResolvedRecord(
        identifier_type="fake",
        identifier_value=value,
        canonical_url=f"fake://{value}",
        title=f"Title for {value}",
        resolved_at=now_iso(),
        source_api="fake",
    )


@pytest.fixture
def fake_registered():
    register_backend("fake", _fake_backend)
    yield
    # Don't unregister — tests are idempotent and registration is process-scope


class TestResolveDispatch:
    def test_resolve_tuple(self, fake_registered):
        r = resolve(("fake", "abc"))
        assert r.identifier_value == "abc"

    def test_resolve_string(self, fake_registered):
        r = resolve("fake:abc")
        assert r.identifier_value == "abc"

    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="no backend registered"):
            resolve(("nonexistent_type", "x"))

    def test_bad_string_format_raises(self):
        with pytest.raises(ValueError, match="must be 'type:value'"):
            resolve("no_colon_here")

    def test_cache_hit_skips_backend(self, fake_registered):
        cache = InMemoryCache()
        first = resolve(("fake", "x"), cache=cache)
        # Now poison the cache to verify second call uses it
        from unittest.mock import patch
        with patch("proof_citations.resolvers._BACKENDS") as backends:
            backends.__getitem__.side_effect = AssertionError("should not be called")
            backends.get.return_value = None
            # Wait — we need cache hit to short-circuit before backend lookup
            # The function checks cache first
            second = resolve(("fake", "x"), cache=cache)
            assert second is first

    def test_cache_miss_calls_backend_and_stores(self, fake_registered):
        cache = InMemoryCache()
        r = resolve(("fake", "y"), cache=cache)
        assert cache.get("fake:y") is r
        assert len(cache) == 1


class TestPubMedAutoRegistered:
    """The registry __init__ should auto-register the pubmed backend at import."""

    def test_pmid_backend_registered(self):
        backend = get_backend("pmid")
        assert backend is not None
        # Should be the pubmed.resolve_pmid function
        from proof_citations.resolvers.pubmed import resolve_pmid
        assert backend is resolve_pmid

    def test_pmc_backend_registered(self):
        backend = get_backend("pmc")
        assert backend is not None
        from proof_citations.resolvers.pubmed import resolve_pmc
        assert backend is resolve_pmc
