"""Backward-compat shim. Real implementation in proof-citations."""

from proof_citations.latex_text import latex_to_text, _LATEX_SYMBOLS  # noqa: F401

__all__ = ["latex_to_text"]
