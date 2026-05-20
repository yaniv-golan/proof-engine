"""Backward-compat shim. Real implementation in proof-citations."""

try:
    from proof_citations.oa_lookup import (  # noqa: F401
        extract_doi,
        lookup_oa_url,
    )
except ImportError as exc:
    raise ImportError(
        "proof-engine scripts require the 'proof-citations' PyPI package. "
        "Install with: pip install proof-citations"
    ) from exc

__all__ = ["extract_doi", "lookup_oa_url"]
