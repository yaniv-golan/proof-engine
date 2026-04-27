"""Queue library and CLI for the daily proof-regen pipeline.

CLI usage:
  python tools/regen_queue.py seed      --site-dir site [--queue-file tools/regen-queue.yaml]
  python tools/regen_queue.py pick-next --json [--queue-file tools/regen-queue.yaml]
  python tools/regen_queue.py mark <slug> --status <s> [--pr N] [--error STR] [--queue-file ...]
  python tools/regen_queue.py report [--queue-file tools/regen-queue.yaml]
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

VALID_STATUSES = {"pending", "in_progress", "pr_open", "merged", "failed",
                  "quota_blocked", "skipped"}
_DEFAULT_QUEUE = Path("tools/regen-queue.yaml")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(queue_file: Path) -> dict:
    return yaml.safe_load(queue_file.read_text())


def _save(queue_file: Path, data: dict) -> None:
    content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    tmp = queue_file.with_suffix(".yaml.tmp")
    with open(tmp, "w") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(queue_file)


def seed(proofs_dir: Path, queue_file: Path) -> None:
    """Idempotently populate queue with all slugs found in proofs_dir."""
    slugs = sorted(p.name for p in proofs_dir.iterdir() if p.is_dir())
    if queue_file.exists():
        data = _load(queue_file)
        existing = {p["slug"] for p in data["proofs"]}
        for slug in slugs:
            if slug not in existing:
                data["proofs"].append(_blank_entry(slug))
    else:
        data = {
            "version": 1,
            "generated_at": _now()[:10],
            "proofs": [_blank_entry(s) for s in slugs],
        }
    _save(queue_file, data)


def _blank_entry(slug: str) -> dict:
    return {"slug": slug, "status": "pending", "attempts": 0,
            "last_run": None, "last_error": None, "pr": None, "notes": None}


def pick_next(queue_file: Path) -> dict | None:
    """Return the next pending entry (lowest attempts, then alpha slug), or None."""
    data = _load(queue_file)
    candidates = [p for p in data["proofs"] if p["status"] == "pending"]
    if not candidates:
        return None
    candidates.sort(key=lambda p: (p["attempts"], p["slug"]))
    return candidates[0]


def mark(queue_file: Path, slug: str, status: str, *,
         pr: int | None = None, error: str | None = None) -> None:
    """Update queue entry for slug."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status {status!r}. Must be one of {sorted(VALID_STATUSES)}")
    data = _load(queue_file)
    entry = next((p for p in data["proofs"] if p["slug"] == slug), None)
    if entry is None:
        raise KeyError(f"Slug not found in queue: {slug}")
    if status == "in_progress":
        entry["attempts"] = entry.get("attempts", 0) + 1
        entry["last_run"] = _now()
        if entry["attempts"] >= 3:
            entry["status"] = "failed"
            entry["last_error"] = error or "max attempts reached"
            _save(queue_file, data)
            return
    entry["status"] = status
    if pr is not None:
        entry["pr"] = pr
    if error is not None:
        entry["last_error"] = error
    _save(queue_file, data)


def report(queue_file: Path) -> str:
    data = _load(queue_file)
    from collections import Counter
    counts = Counter(p["status"] for p in data["proofs"])
    lines = ["Regen Queue Report", "=" * 40]
    for s in ("pending", "in_progress", "pr_open", "merged", "failed",
              "quota_blocked", "skipped"):
        lines.append(f"  {s:15s}: {counts.get(s, 0)}")
    lines.append(f"  {'TOTAL':15s}: {len(data['proofs'])}")
    failed = [p for p in data["proofs"] if p["status"] == "failed"]
    if failed:
        lines.append("\nFailed slugs:")
        for p in failed:
            lines.append(f"  {p['slug']}  (attempts={p['attempts']}, error={p['last_error']})")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-file", type=Path, default=_DEFAULT_QUEUE)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_seed = sub.add_parser("seed")
    p_seed.add_argument("--site-dir", type=Path, default=Path("site"))

    p_pick = sub.add_parser("pick-next")
    p_pick.add_argument("--json", dest="as_json", action="store_true")

    p_mark = sub.add_parser("mark")
    p_mark.add_argument("slug")
    p_mark.add_argument("--status", required=True)
    p_mark.add_argument("--pr", type=int)
    p_mark.add_argument("--error")

    sub.add_parser("report")

    args = parser.parse_args()

    if args.cmd == "seed":
        proofs_dir = args.site_dir / "proofs"
        seed(proofs_dir, args.queue_file)
        print(f"Seeded {args.queue_file}")
        return 0

    if args.cmd == "pick-next":
        try:
            entry = pick_next(args.queue_file)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2
        if entry is None:
            return 1
        if args.as_json:
            print(json.dumps(entry, separators=(",", ":")))
        else:
            print(entry["slug"])
        return 0

    if args.cmd == "mark":
        try:
            mark(args.queue_file, args.slug, args.status, pr=args.pr, error=args.error)
        except (ValueError, KeyError, yaml.YAMLError, OSError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2
        return 0

    if args.cmd == "report":
        print(report(args.queue_file))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
