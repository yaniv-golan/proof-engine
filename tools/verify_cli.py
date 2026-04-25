#!/usr/bin/env python3
"""`proof-engine verify` — headless claim verification.

Flow:
  1. Optionally look up in configured registries.
  2. If --registry-only: emit the hit or exit 3.
  3. Otherwise, invoke tools/generate-proof.sh to produce a new proof.
  4. Parse the generated proof.json into a Verdict.
  5. Emit JSON to stdout, set exit code per verdict.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Allow running this file directly via `python3 tools/verify_cli.py ...`
# by ensuring the repo root is on sys.path so `tools.lib.*` resolves.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from proof_engine_registry.client import RegistryClient
from proof_engine_registry.config import load_registries
from proof_engine_registry.hashing import hash_claim

from tools.lib.cli_verdict import (
    Verdict, RegistryHit, error_verdict,
)
from tools.lib.cli_verdict_parser import parse_generated_proof


def _lookup_registry(claim: str) -> Verdict | None:
    registries = load_registries()
    if not registries:
        return None
    client = RegistryClient(registries)
    hit = client.lookup(claim)
    if hit is None:
        return None
    return Verdict(
        schema_version="1.0",
        claim=claim,
        claim_hash=hash_claim(claim),
        source="registry",
        verdict=hit.verdict,
        confidence=hit.confidence,
        registry_hit=RegistryHit(
            registry_name=hit.registry_name,
            slug=hit.slug,
            proof_url=hit.proof_url,
            doi=hit.doi,
        ),
        generated=None,
        errors=[],
    )


def _generate_proof(claim: str, model: str, output_dir: Path) -> Verdict:
    output_dir.mkdir(parents=True, exist_ok=True)
    script = REPO_ROOT / "tools" / "generate-proof.sh"
    started = time.time()
    # Put flags BEFORE `--` and the (untrusted) claim text AFTER, so a claim
    # that begins with `--` cannot be parsed as a flag.
    # generate-proof.sh must treat everything after `--` as the claim —
    # verify the script handles this (see companion patch to generate-proof.sh).
    proc = subprocess.run(
        [str(script), "--model", model,
         "--output-dir", str(output_dir),
         "--", claim],
        capture_output=True, text=True,
    )
    duration = time.time() - started
    if proc.returncode != 0:
        return error_verdict(
            claim=claim, claim_hash=hash_claim(claim),
            messages=[f"generate-proof.sh exit {proc.returncode}",
                      proc.stderr[-4000:]],
        )
    return parse_generated_proof(
        output_dir=output_dir, model=model, duration_seconds=duration,
    )


def _emit(verdict: Verdict, as_json: bool, pretty: bool) -> int:
    if as_json:
        payload = verdict.to_json()
        sys.stdout.write(json.dumps(payload, indent=2 if pretty else None,
                                    default=str) + "\n")
    else:
        sys.stdout.write(
            f"{verdict.verdict or 'ERROR'} "
            f"(confidence={verdict.confidence:.2f}, source={verdict.source})\n"
        )
        if verdict.registry_hit:
            sys.stdout.write(f"  → {verdict.registry_hit.proof_url}\n")
        if verdict.generated:
            sys.stdout.write(f"  → {verdict.generated.output_dir}\n")
        for e in verdict.errors:
            sys.stdout.write(f"  error: {e}\n")
    return verdict.exit_code()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="proof-engine verify")
    p.add_argument("--claim", required=True)
    p.add_argument("--registry-check", action="store_true",
                   help="Check configured registries before generating.")
    p.add_argument("--registry-only", action="store_true",
                   help="Only check registries; never generate. Exit 3 on miss.")
    p.add_argument("--model", choices=["opus", "sonnet"], default="opus")
    p.add_argument("--output-dir", default=None,
                   help="Where to write generated proof artifacts. "
                        "Default: ./proof-output-<claim-slug>-<timestamp>/")
    p.add_argument("--json", action="store_true")
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args(argv)

    # Registry check (implicit when --registry-only; explicit via --registry-check).
    do_registry = args.registry_check or args.registry_only
    if do_registry:
        hit = _lookup_registry(args.claim)
        if hit is not None:
            return _emit(hit, args.json, args.pretty)

    if args.registry_only:
        # No hit, and user forbade generation.
        err = error_verdict(
            claim=args.claim, claim_hash=hash_claim(args.claim),
            messages=["registry-only mode: no hit in any configured registry"],
        )
        _emit(err, args.json, args.pretty)
        return 3

    # Generate.
    output_dir = Path(args.output_dir) if args.output_dir else \
        Path(f"proof-output-{int(time.time())}")
    verdict = _generate_proof(args.claim, args.model, output_dir)
    return _emit(verdict, args.json, args.pretty)


if __name__ == "__main__":
    raise SystemExit(main())
