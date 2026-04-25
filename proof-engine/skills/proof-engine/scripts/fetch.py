"""Backward-compat shim. Real implementation lives in proof-citations package.

Kept so that existing proofs and skill scripts that `from scripts.fetch import
fetch_page` continue to work unchanged.
"""

from proof_citations.fetch import (  # noqa: F401
    fetch_page,
    extract_pdf_text,
    try_wayback,
    try_github_raw,
)

__all__ = ["fetch_page", "extract_pdf_text", "try_wayback", "try_github_raw"]
