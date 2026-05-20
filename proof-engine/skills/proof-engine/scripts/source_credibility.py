"""Backward-compat shim. Real implementation in proof-citations."""

try:
    from proof_citations.source_credibility import (  # noqa: F401
        assess_credibility,
        assess_all,
        hostname_ends_with,
    )
except ImportError as exc:
    raise ImportError(
        "proof-engine scripts require the 'proof-citations' PyPI package. "
        "Install with: pip install proof-citations"
    ) from exc

__all__ = ["assess_credibility", "assess_all", "hostname_ends_with"]
