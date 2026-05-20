"""Backward-compat shim. Real implementation lives in proof-citations package.

Kept so that existing proofs and skill scripts that `from scripts.fetch import
fetch_page` continue to work unchanged.
"""

try:
    from proof_citations.fetch import (  # noqa: F401
        fetch_page,
        extract_pdf_text,
        try_wayback,
        try_github_raw,
    )
except ImportError as exc:
    raise ImportError(
        "proof-engine scripts require the 'proof-citations' PyPI package. "
        "Install with: pip install proof-citations"
    ) from exc

__all__ = ["fetch_page", "extract_pdf_text", "try_wayback", "try_github_raw"]
