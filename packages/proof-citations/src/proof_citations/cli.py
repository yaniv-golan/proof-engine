"""Command-line entry point for proof-citations.

    proof-citations verify --url URL --quote "QUOTE" --fact-id B1
    proof-citations verify --facts facts.json
    proof-citations verify-records --input audit.json [--output report.json]
"""

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from typing import Any

from proof_citations import (
    verify_citation,
    verify_all_citations,
    verify_citation_record,
)
from proof_citations.registry.base import ResolvedRecord


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


def _to_json_safe(obj: Any) -> Any:
    """Convert ResolvedRecord / Author / dataclasses to JSON-safe dicts."""
    if isinstance(obj, ResolvedRecord):
        return obj.to_dict(include_raw=False)
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return {k: _to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_json_safe(v) for v in obj]
    return obj


def _cmd_verify_records(args) -> int:
    """Run `verify_citation_record` against a JSON list of citations.

    Input shape:
        {
          "references": [
            {"ref_id": "B1", "identifier": "pmid:12345",
             "expected": {"title": "...", "journal": "...", "year": 2021, "doi": "..."}}
          ]
        }
    """
    try:
        with open(args.input) as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(f"error: cannot read {args.input}: {e}\n")
        return 2

    refs = payload.get("references", [])
    if not isinstance(refs, list):
        sys.stderr.write("error: input file must have a top-level `references` list\n")
        return 2

    results = []
    for i, ref in enumerate(refs, 1):
        ref_id = ref.get("ref_id", f"R{i}")
        ident = ref.get("identifier")
        expected = ref.get("expected") or {}
        if not ident:
            results.append({
                "ref_id": ref_id,
                "status": "unresolvable",
                "verdict": "no_identifier",
                "message": "no identifier supplied",
            })
            continue
        if not args.quiet:
            sys.stderr.write(f"[{i}/{len(refs)}] {ref_id} {ident}…\n")
        res = verify_citation_record(ident, expected)
        results.append({"ref_id": ref_id, "identifier": ident, **_to_json_safe(res)})

    output = {
        "audit_method": payload.get("audit_method"),
        "audit_date": payload.get("audit_date"),
        "summary": _summarize(results),
        "results": results,
    }

    text = json.dumps(output, indent=2 if args.pretty else None, default=str)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text + "\n")
        if not args.quiet:
            sys.stderr.write(f"wrote {args.output}\n")
    else:
        sys.stdout.write(text + "\n")

    bad = [r for r in results if r.get("status") not in ("verified", "resolved")]
    return 1 if bad else 0


def _summarize(results: list[dict]) -> dict:
    from collections import Counter
    counts = Counter(r.get("status") for r in results)
    return {
        "total": len(results),
        "by_status": dict(counts),
        "verified": counts.get("verified", 0),
        "chimeras": (
            counts.get("metadata_chimera", 0)
            + counts.get("title_chimera", 0)
        ),
        "unresolvable": counts.get("unresolvable", 0),
        "fetch_failed": counts.get("fetch_failed", 0),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="proof-citations")
    sub = parser.add_subparsers(dest="cmd", required=True)

    verify = sub.add_parser("verify", help="Verify a quote appears at a URL.")
    verify.add_argument("--url",
                        help="The URL to fetch and verify against.")
    verify.add_argument("--quote",
                        help=("The exact quoted text, AS IT APPEARS on the page. "
                              "Pass literal Unicode characters; do NOT pre-escape "
                              "(e.g. backslash-x sequences land as literal backslashes "
                              "and will not match). Single-quote the whole argument "
                              "to preserve special chars."))
    verify.add_argument("--fact-id", default="B1",
                        help="Identifier used in messages (default: B1).")
    verify.add_argument("--facts", help="Path to JSON file of facts to verify.")
    verify.add_argument("--json", action="store_true", help="Emit JSON.")
    verify.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    verify.set_defaults(func=_cmd_verify)

    records = sub.add_parser(
        "verify-records",
        help="Resolve identifiers and check claimed bibliographic metadata.",
        description=(
            "Batch-verify a list of citations against authoritative registries. "
            "Reads a JSON file with a `references` list; each entry needs "
            "`ref_id`, `identifier` (e.g. 'pmid:12345' or 'doi:10.x/y'), and "
            "optional `expected` dict (title, journal, year, doi, authors). "
            "Catches metadata-chimera fraud (real identifier, fabricated "
            "bibliography) that pure quote-on-page verification misses."
        ),
    )
    records.add_argument("--input", required=True,
                         help="Path to a JSON file with a `references` list.")
    records.add_argument("--output", help="Write results to this file (default: stdout).")
    records.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    records.add_argument("--quiet", action="store_true", help="Suppress per-reference progress to stderr.")
    records.set_defaults(func=_cmd_verify_records)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
