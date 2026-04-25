"""Static JSON emitter for the Registry Protocol.

Reads a directory of proof subdirectories (each containing proof.json in v3
format, and optionally a sibling doi.json) and writes protocol-compliant
JSON to an output directory. Used by tools/build-site.py (public registry)
and by the self-hosted server's rebuild path.

v3 proof.json shape (observed in site/proofs/*/proof.json):
  - slug: NOT a field — derived from the directory name.
  - claim_natural: claim text with inline LaTeX (e.g., "\\(x^2\\)").
  - verdict: {value, qualified, qualifier, reason}. Protocol verdict string
    is verdict.value; if qualified, append " with <qualifier>".
  - evidence: dict keyed by fact id (A1, A2, B1, S1, ...).
  - generator.generated_at: source of the generated_at timestamp.
  - DOI: NOT in proof.json — read from sibling doi.json if present.
  - confidence: NOT a field — derived (1.0 unqualified, 0.5 qualified).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from proof_engine_registry import __protocol_version__
from proof_engine_registry.hashing import hash_claim
from proof_engine_registry.schema import (
    Discovery, Index, IndexEntry, RegistryProof, to_json,
)


# Match inline LaTeX: \( ... \), \[ ... \], $$ ... $$, $ ... $.
# We strip the delimiters and keep the inner source — good enough for
# claim display; renderers can re-parse the LaTeX if desired.
_INLINE_LATEX = re.compile(
    r"\\\((?P<a>.+?)\\\)|\\\[(?P<b>.+?)\\\]|\$\$(?P<c>.+?)\$\$|\$(?P<d>[^$]+?)\$",
    re.DOTALL,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _strip_latex(text: str) -> str:
    """Strip inline-LaTeX delimiters while preserving the expression text."""
    def _repl(m: re.Match) -> str:
        return m.group("a") or m.group("b") or m.group("c") or m.group("d") or ""
    return _INLINE_LATEX.sub(_repl, text)


# Public helpers — exported so Phase 2's verdict_parser and any future
# consumer can reuse the v3-proof.json field mappings without duplicating them.


def claim_text(proof: dict) -> str:
    """Plain-text claim extracted from `claim_natural` (LaTeX delimiters stripped)."""
    return _strip_latex(proof.get("claim_natural", "")).strip()


def verdict_string(proof: dict) -> str:
    """Protocol verdict string.

    Handles BOTH proof.json shapes:
      - v3: `verdict = {value, qualified, qualifier, reason}` — the norm.
      - v2 (legacy, one proof at time of writing): `verdict = "PROVED"` as a
        plain string. Treated as unqualified.

    Qualified verdicts are rendered in the canonical parenthesized form
    `"VALUE (with humanized qualifier)"` — matching the keys in
    `tools/lib/verdict.py::VERDICT_TAXONOMY` that the rest of the repo uses.
    Real proofs store qualifiers with underscores (e.g., "unverified_citations");
    we humanize to spaces here for the public string.
    """
    v = proof.get("verdict")
    if isinstance(v, str):
        return v  # v2 legacy — already a plain verdict.
    if not isinstance(v, dict):
        return "UNDETERMINED"
    value = v.get("value", "UNDETERMINED")
    if v.get("qualified") and v.get("qualifier"):
        humanized = str(v["qualifier"]).replace("_", " ").strip()
        return f"{value} (with {humanized})"
    return value


def confidence_from_proof(proof: dict) -> float:
    """Derived confidence: 1.0 unqualified, 0.5 qualified.

    Tolerates v2 (string) verdicts — always unqualified → 1.0.
    """
    v = proof.get("verdict")
    if isinstance(v, dict) and v.get("qualified"):
        return 0.5
    return 1.0


def _load_doi(proof_dir: Path) -> Optional[str]:
    doi_path = proof_dir / "doi.json"
    if not doi_path.exists():
        return None
    try:
        data = json.loads(doi_path.read_text())
    except json.JSONDecodeError:
        return None
    return data.get("doi")


def _generated_at(proof: dict) -> str:
    gen = proof.get("generator") or {}
    return gen.get("generated_at", "")


def _extract_fact_ids(proof: dict) -> list[str]:
    """Fact IDs are the keys of the evidence dict, sorted for determinism."""
    evidence = proof.get("evidence") or {}
    return sorted(evidence.keys())


def _extract_source_urls(proof: dict) -> list[str]:
    """Collect source URLs from every evidence entry that has one.

    Real v3 shape (verified across site/proofs/*/proof.json): each evidence
    entry carries a nested `source = {name, url, quote, ...}` object. NOT
    a top-level `source_url`. For defensive robustness against hand-written
    or legacy proofs, we accept both shapes and prefer the nested form.

    Ordered-dedup, sorted by fact id for determinism.
    """
    evidence = proof.get("evidence") or {}
    seen: dict[str, None] = {}
    for fact_id in sorted(evidence.keys()):
        entry = evidence[fact_id] or {}
        # v3 nested shape: evidence[id].source.url
        source = entry.get("source")
        if isinstance(source, dict):
            url = source.get("url")
            if url and url not in seen:
                seen[url] = None
        # Defensive fallback: a flat top-level source_url (not observed in
        # real proofs but some older generators might emit it).
        flat = entry.get("source_url")
        if flat and flat not in seen:
            seen[flat] = None
    return list(seen.keys())


def _proof_to_index_entry(proof: dict, slug: str, doi: Optional[str],
                          base_url: str) -> IndexEntry:
    claim = claim_text(proof)
    return IndexEntry(
        claim_hash=hash_claim(claim),
        slug=slug,
        claim=claim,
        verdict=verdict_string(proof),
        confidence=confidence_from_proof(proof),
        doi=doi,
        proof_url=f"{base_url}/proofs/{slug}/",
        badge_url=f"{base_url}/proofs/{slug}/badge.json",
        generated_at=_generated_at(proof),
    )


def _proof_to_registry_proof(proof: dict, slug: str, doi: Optional[str],
                             base_url: str) -> RegistryProof:
    entry = _proof_to_index_entry(proof, slug, doi, base_url)
    return RegistryProof(
        claim_hash=entry.claim_hash,
        slug=entry.slug,
        claim=entry.claim,
        verdict=entry.verdict,
        confidence=entry.confidence,
        doi=entry.doi,
        proof_url=entry.proof_url,
        badge_url=entry.badge_url,
        generated_at=entry.generated_at,
        fact_ids=_extract_fact_ids(proof),
        source_urls=_extract_source_urls(proof),
        narrative_summary=None,  # v3 proof.json has no narrative field;
                                 # narrative lives in proof_narrative.md
                                 # (out of scope for the index).
    )


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def emit_registry_files(
    proofs_dir: Path,
    output_dir: Path,
    base_url: str,
    registry_name: str,
    publishes_supported: bool = False,
    auth_required: bool = False,
    fixed_timestamp: Optional[str] = None,
) -> None:
    """Write the full registry tree under `output_dir`.

    `fixed_timestamp` forces a deterministic `generated_at` for reproducible
    builds — set it for tests and for CI where output must be stable across
    runs.
    """
    base_url = base_url.rstrip("/")
    ts = fixed_timestamp or _now_iso()

    # Load proofs. `proofs_dir` contains one subdirectory per proof, each
    # holding `proof.json` (required) and optionally `doi.json`.
    loaded: list[tuple[str, dict, Optional[str]]] = []  # (slug, proof, doi)
    for proof_json in sorted(Path(proofs_dir).glob("*/proof.json")):
        proof_dir = proof_json.parent
        slug = proof_dir.name
        proof = json.loads(proof_json.read_text())
        doi = _load_doi(proof_dir)
        loaded.append((slug, proof, doi))

    # Sort for determinism (already sorted by glob on slug, but be explicit).
    loaded.sort(key=lambda t: t[0])

    entries = [
        _proof_to_index_entry(p, slug, doi, base_url)
        for slug, p, doi in loaded
    ]

    discovery = Discovery(
        protocol_version=__protocol_version__,
        name=registry_name,
        homepage=base_url,
        publishes_supported=publishes_supported,
        auth_required=auth_required,
        proof_count=len(entries),
        generated_at=ts,
        signing_key=None,
    )
    _write_json(output_dir / ".well-known" / "proof-registry.json",
                to_json(discovery))

    index = Index(
        protocol_version=__protocol_version__,
        generated_at=ts,
        entries=entries,
    )
    _write_json(output_dir / "index.json", to_json(index))

    for entry in entries:
        _write_json(output_dir / "claims" / f"{entry.claim_hash}.json",
                    to_json(entry))

    for slug, proof, doi in loaded:
        rp = _proof_to_registry_proof(proof, slug, doi, base_url)
        _write_json(output_dir / "proofs" / f"{slug}.json", to_json(rp))
