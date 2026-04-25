"""Claim hashing per Registry Protocol v0.1.

normalize(claim) and hash_claim(claim) are load-bearing for protocol
compatibility. Any change to the algorithm is a protocol major version bump.
"""

import hashlib
import re
import unicodedata


_WHITESPACE = re.compile(r"\s+")
_TRAILING_PUNCT = re.compile(r"[.!?]+$")


def normalize_claim(claim: str) -> str:
    """Normalize claim text per Protocol v0.1 §Claim hashing."""
    claim = unicodedata.normalize("NFC", claim)
    claim = claim.lower()
    claim = _WHITESPACE.sub(" ", claim).strip()
    claim = _TRAILING_PUNCT.sub("", claim)
    return claim


def hash_claim(claim: str) -> str:
    """SHA-256 hex digest of the normalized claim."""
    normalized = normalize_claim(claim)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
