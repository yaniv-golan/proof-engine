"""proof-engine-wiki CLI: ingest | lint."""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

try:
    from proof_engine_wiki import __version__
except ImportError:
    __version__ = "0.1.0"

from proof_engine_wiki.ingest import ingest_page
from proof_engine_wiki.lint import lint_wiki


def _cmd_ingest(args) -> int:
    result = ingest_page(
        Path(args.path),
        registry_only=args.registry_only,
        dry_run=args.dry_run,
        model=args.model,
    )
    payload = {
        "path": str(result.path),
        "markers": len(result.markers),
        "resolved_from_registry": result.resolved_from_registry,
        "generated": result.generated,
        "misses": result.misses,
        "errors": result.errors,
    }
    if args.json:
        sys.stdout.write(json.dumps(payload, indent=2 if args.pretty else None) + "\n")
    else:
        sys.stdout.write(
            f"{result.path}: {len(result.markers)} markers, "
            f"{result.resolved_from_registry} resolved, "
            f"{result.generated} generated, "
            f"{result.misses} misses\n"
        )
    return 0 if result.misses == 0 and not result.errors else 1


def _cmd_lint(args) -> int:
    findings = lint_wiki(Path(args.path), skip_network=args.skip_network)
    payload = {
        "path": str(args.path),
        "findings": [
            {
                "path": str(f.path), "line": f.line,
                "kind": f.kind, "message": f.message, "detail": f.detail,
            }
            for f in findings
        ],
    }
    if args.json:
        sys.stdout.write(json.dumps(payload, indent=2 if args.pretty else None) + "\n")
    else:
        for f in findings:
            sys.stdout.write(f"{f.path}:{f.line}: [{f.kind}] {f.message}\n")
        if not findings:
            sys.stdout.write("clean\n")
    return 0 if not findings else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="proof-engine-wiki")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    ing = sub.add_parser("ingest", help="Extract {{prove:}} markers and resolve them.")
    ing.add_argument("path")
    ing.add_argument("--registry-only", action="store_true")
    ing.add_argument("--dry-run", action="store_true")
    ing.add_argument("--model", default="sonnet")
    ing.add_argument("--json", action="store_true")
    ing.add_argument("--pretty", action="store_true")
    ing.set_defaults(func=_cmd_ingest)

    lnt = sub.add_parser("lint", help="Scan a wiki for unresolved markers and stale proofs.")
    lnt.add_argument("path")
    lnt.add_argument("--skip-network", action="store_true",
                     help="Skip URL reachability checks.")
    lnt.add_argument("--json", action="store_true")
    lnt.add_argument("--pretty", action="store_true")
    lnt.set_defaults(func=_cmd_lint)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
