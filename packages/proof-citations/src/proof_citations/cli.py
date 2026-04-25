"""Command-line entry point for proof-citations.

    proof-citations verify --url URL --quote "QUOTE" --fact-id B1
    proof-citations verify --facts facts.json
"""

import argparse
import json
import sys

from proof_citations import verify_citation, verify_all_citations


def _cmd_verify(args) -> int:
    if args.facts:
        with open(args.facts) as f:
            facts = json.load(f)
        results = verify_all_citations(facts)
        # verify_all_citations returns a dict (per verify_citations.py).
        # Emit as-is, and compute exit from statuses.
        sys.stdout.write(
            json.dumps(results, indent=2 if args.pretty else None) + "\n"
        )
        statuses = [r.get("status") for r in results.values()] \
            if isinstance(results, dict) else []
        return 0 if statuses and all(s == "verified" for s in statuses) else 1

    if not args.url or not args.quote:
        sys.stderr.write("error: --url and --quote are required (or --facts)\n")
        return 2

    result = verify_citation(args.url, args.quote, args.fact_id)
    if args.json:
        sys.stdout.write(
            json.dumps(result, indent=2 if args.pretty else None, default=str)
            + "\n"
        )
    else:
        sys.stdout.write(f"{result.get('status')}: {args.url}\n")
    return 0 if result.get("status") == "verified" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="proof-citations")
    sub = parser.add_subparsers(dest="cmd", required=True)

    verify = sub.add_parser("verify", help="Verify a quote appears at a URL.")
    verify.add_argument("--url")
    verify.add_argument("--quote")
    verify.add_argument("--fact-id", default="B1",
                        help="Identifier used in messages (default: B1).")
    verify.add_argument("--facts", help="Path to JSON file of facts to verify.")
    verify.add_argument("--json", action="store_true", help="Emit JSON.")
    verify.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    verify.set_defaults(func=_cmd_verify)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
