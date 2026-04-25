"""Backward-compat shim. Real implementation in proof-citations."""

from proof_citations.oa_lookup import (  # noqa: F401
    extract_doi,
    lookup_oa_url,
)

__all__ = ["extract_doi", "lookup_oa_url"]
