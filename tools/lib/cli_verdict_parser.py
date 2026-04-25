"""Parse a generated proof's artifacts into a Verdict.

Consumes the real v3 proof.json shape (claim_natural, nested verdict,
sibling doi.json). Field-mapping helpers come from proof_engine_registry.emit
so the adapter logic lives in exactly one place.
"""

from __future__ import annotations

import json
from pathlib import Path

from proof_engine_registry.emit import (
    claim_text, verdict_string, confidence_from_proof,
)
from proof_engine_registry.hashing import hash_claim

from tools.lib.cli_verdict import GeneratedProof, Verdict, error_verdict


def parse_generated_proof(
    output_dir: Path,
    model: str,
    duration_seconds: float,
) -> Verdict:
    output_dir = Path(output_dir)
    proof_json_path = output_dir / "proof.json"
    if not proof_json_path.exists():
        return error_verdict(
            claim="", claim_hash="",
            messages=[f"no proof.json in {output_dir}"],
        )
    proof = json.loads(proof_json_path.read_text())
    claim = claim_text(proof)
    return Verdict(
        schema_version="1.0",
        claim=claim,
        claim_hash=hash_claim(claim) if claim else "",
        source="generated",
        verdict=verdict_string(proof),
        confidence=confidence_from_proof(proof),
        registry_hit=None,
        generated=GeneratedProof(
            output_dir=str(output_dir.resolve()),
            proof_py=str((output_dir / "proof.py").resolve()),
            proof_md=str((output_dir / "proof.md").resolve()),
            proof_audit_md=str((output_dir / "proof_audit.md").resolve()),
            proof_narrative_md=str((output_dir / "proof_narrative.md").resolve()),
            model=model,
            duration_seconds=duration_seconds,
        ),
        errors=[],
    )
