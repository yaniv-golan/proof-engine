"""Backward-compat shim. Real implementation in proof-citations."""

from proof_citations.source_credibility import (  # noqa: F401
    assess_credibility,
    assess_all,
    hostname_ends_with,
)

__all__ = ["assess_credibility", "assess_all", "hostname_ends_with"]
