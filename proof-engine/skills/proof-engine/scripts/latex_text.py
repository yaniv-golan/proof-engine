"""Backward-compat shim. Real implementation in proof-citations."""

try:
    from proof_citations.latex_text import latex_to_text, _LATEX_SYMBOLS  # noqa: F401
except ImportError as exc:
    raise ImportError(
        "proof-engine scripts require the 'proof-citations' PyPI package. "
        "Install with: pip install proof-citations"
    ) from exc

__all__ = ["latex_to_text"]
