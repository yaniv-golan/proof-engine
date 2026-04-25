"""Ingest: extract {{prove:}} markers, resolve or commission, rewrite page."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from proof_engine_registry.client import RegistryClient, LookupHit
from proof_engine_registry.config import Registry, load_registries

from proof_engine_wiki.markers import Marker, find_markers, replace_markers


@dataclass
class IngestResult:
    path: Path
    markers: list[Marker]
    resolved_from_registry: int = 0
    generated: int = 0
    misses: int = 0
    errors: list[str] = field(default_factory=list)


def _hit_to_embed(hit: LookupHit, claim_text: str) -> str:
    """Format a successful lookup as inline Markdown: link + badge."""
    return (
        f"[{claim_text}]({hit.proof_url}) "
        f"![proof]({hit.badge_url.replace('.json', '.svg')})"
    )


def ingest_page(
    path: Path,
    registries: Optional[list[Registry]] = None,
    *,
    registry_only: bool = False,
    dry_run: bool = False,
    model: str = "sonnet",
    proof_output_base: Optional[Path] = None,
) -> IngestResult:
    path = Path(path)
    original_text = path.read_text()
    markers = find_markers(original_text)

    result = IngestResult(path=path, markers=markers)
    if not markers:
        return result

    regs = registries if registries is not None else load_registries()
    client = RegistryClient(regs) if regs else None

    replacements: dict[tuple[int, int], str] = {}

    for m in markers:
        hit = client.lookup(m.claim) if client else None
        if hit is not None:
            replacements[m.span] = _hit_to_embed(hit, m.claim)
            result.resolved_from_registry += 1
            continue

        if registry_only:
            result.misses += 1
            continue

        # Commission a new proof via the Proof Engine verify CLI.
        if proof_output_base is None:
            proof_output_base = path.parent / ".proofs"
        proof_output_base.mkdir(parents=True, exist_ok=True)
        output_dir = proof_output_base / _slugify(m.claim)

        verdict = _invoke_verify(m.claim, model, output_dir)
        if verdict is None:
            result.errors.append(f"verify failed for: {m.claim[:80]}")
            result.misses += 1
            continue

        # After generation, the proof isn't yet in any registry; produce a
        # local link to the output dir until the user publishes.
        embed = (
            f"[{m.claim}]({output_dir.as_posix()}/proof.md) "
            f"<!-- Proof generated; run `proof-engine-wiki publish "
            f"{output_dir}` to add to your registry. -->"
        )
        replacements[m.span] = embed
        result.generated += 1

    if replacements and not dry_run:
        new_text = replace_markers(original_text, replacements)
        path.write_text(new_text)

    return result


def _slugify(text: str) -> str:
    import re
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "claim"


def _invoke_verify(claim: str, model: str, output_dir: Path) -> Optional[dict]:
    """Call `proof-engine verify` and parse the JSON verdict."""
    import json
    script = _find_verify_cli()
    if script is None:
        return None
    proc = subprocess.run(
        [sys.executable, str(script),
         "--claim", claim,
         "--model", model,
         "--output-dir", str(output_dir),
         "--json"],
        capture_output=True, text=True,
    )
    if not proc.stdout:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _find_verify_cli() -> Optional[Path]:
    """Locate the verify_cli.py script. Search the same repo first."""
    import os
    env_path = os.environ.get("PROOF_ENGINE_VERIFY_CLI")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p
    # Walk up from this file looking for tools/verify_cli.py in the repo.
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "tools" / "verify_cli.py"
        if candidate.exists():
            return candidate
    return None
