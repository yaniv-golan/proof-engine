"""Verdict dataclass — canonical JSON shape emitted by `proof-engine verify`."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


# Verdict strings can carry a qualifier suffix in canonical form
# (e.g., "SUPPORTED (with unverified citations)"). Match on the
# leading verdict-value word; ignore the parenthesized qualifier.
_PASS_PREFIXES = ("PROVED", "SUPPORTED", "PARTIALLY VERIFIED")
_FAIL_PREFIXES = ("DISPROVED", "UNDETERMINED")


def _verdict_family(v: Optional[str]) -> str:
    if not v:
        return "unknown"
    if any(v.startswith(p) for p in _PASS_PREFIXES):
        return "pass"
    if any(v.startswith(p) for p in _FAIL_PREFIXES):
        return "fail"
    return "unknown"


@dataclass(frozen=True)
class RegistryHit:
    registry_name: str
    slug: str
    proof_url: str
    doi: Optional[str]


@dataclass(frozen=True)
class GeneratedProof:
    output_dir: str
    proof_py: str
    proof_md: str
    proof_audit_md: str
    proof_narrative_md: str
    model: str
    duration_seconds: float


@dataclass(frozen=True)
class Verdict:
    schema_version: str
    claim: str
    claim_hash: str
    source: str  # "registry" | "generated" | "error"
    verdict: Optional[str]  # None for source="error" before a verdict exists
    confidence: float
    registry_hit: Optional[RegistryHit]
    generated: Optional[GeneratedProof]
    errors: list[str]

    def to_json(self) -> dict:
        return asdict(self)

    def exit_code(self) -> int:
        if self.errors and self.verdict is None:
            return 2
        family = _verdict_family(self.verdict)
        if family == "pass":
            return 0
        if family == "fail":
            return 1
        return 2


def error_verdict(claim: str, claim_hash: str, messages: list[str]) -> Verdict:
    return Verdict(
        schema_version="1.0",
        claim=claim, claim_hash=claim_hash,
        source="error",
        verdict=None,
        confidence=0.0,
        registry_hit=None, generated=None,
        errors=list(messages),
    )
