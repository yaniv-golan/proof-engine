#!/usr/bin/env python3
"""One-shot migration: replace legacy PROOF_ENGINE_ROOT bootstrap blocks with the
canonical walk-up pattern across all proof.py files in site/proofs/ and docs/examples/.

The legacy block leaks the generating agent's filesystem path (yaniv local paths,
Claude Code plugin-cache paths, etc.). Walk-up makes the proof portable.

Handles these input shapes:
  - Variant A: `PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT", "/...")` (multi-line) + sys.path.insert
  - Variant A + `_REPO_ROOT = dirname^4(__file__)` prefix line
  - Variant C: `_here`/for-loop walk-up prefix + env.get
  - Variant D: no env.get; `_REPO_ROOT = dirname^4(...)` + `PROOF_ENGINE_ROOT = os.path.join(_REPO_ROOT, ...)`

Output: the canonical env-var + walk-up block from scripts-api.md.
If `_REPO_ROOT` is referenced AFTER the block, a compatibility alias is appended:
    _REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(PROOF_ENGINE_ROOT)))
(PROOF_ENGINE_ROOT = /<repo>/proof-engine/skills/proof-engine, so dirname^3 = /<repo>.)
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

CANONICAL_BLOCK = '''PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        if os.path.isdir(os.path.join(_d, "proof-engine", "skills", "proof-engine", "scripts")):
            PROOF_ENGINE_ROOT = os.path.join(_d, "proof-engine", "skills", "proof-engine")
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError("PROOF_ENGINE_ROOT not set and skill dir not found via walk-up from proof.py")
sys.path.insert(0, PROOF_ENGINE_ROOT)
'''

REPO_ROOT_ALIAS = "_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(PROOF_ENGINE_ROOT)))\n"

CANONICAL_MARKER = "while _d != os.path.dirname(_d):"
ANCHOR_LINE = "sys.path.insert(0, PROOF_ENGINE_ROOT)"


def is_bootstrap_line(line: str) -> bool:
    """True if the line is part of the legacy PROOF_ENGINE_ROOT bootstrap span."""
    s = line.strip()
    if s == "":
        return True
    if s.startswith("#"):
        return True
    if "_REPO_ROOT" in s or "_here" in s or "PROOF_ENGINE_ROOT" in s:
        return True
    if s == ")":
        return True
    if s == "break":
        return True
    if s.startswith("for _ in range("):
        return True
    if s.startswith("if os.path.isfile("):
        return True
    if s.startswith('"/') and (s.endswith('"') or s.endswith('",')):
        return True
    if s == '"PROOF_ENGINE_ROOT",':
        return True
    return False


def migrate(path: Path):
    old_text = path.read_text()
    lines = old_text.splitlines(keepends=True)

    if CANONICAL_MARKER in old_text:
        return old_text, old_text, "already", None

    anchor_idx = None
    for i, line in enumerate(lines):
        if line.rstrip("\n") == ANCHOR_LINE:
            anchor_idx = i
            break
    if anchor_idx is None:
        return old_text, old_text, "skip-no-anchor", None

    start_idx = anchor_idx
    i = anchor_idx - 1
    while i >= 0 and is_bootstrap_line(lines[i]):
        start_idx = i
        i -= 1

    # Trim leading blanks / unrelated comments from the captured span.
    while start_idx < anchor_idx:
        first = lines[start_idx].strip()
        if first == "":
            start_idx += 1
            continue
        if first.startswith("#"):
            lower = first.lower()
            if "proof_engine_root" not in lower and "proof-engine" not in lower and "repo root" not in lower:
                start_idx += 1
                continue
        break

    rest_text = "".join(lines[anchor_idx + 1 :])
    needs_repo_root = bool(re.search(r"\b_REPO_ROOT\b", rest_text))

    replacement = CANONICAL_BLOCK
    if needs_repo_root:
        replacement += REPO_ROOT_ALIAS

    new_lines = lines[:start_idx] + [replacement] + lines[anchor_idx + 1 :]
    new_text = "".join(new_lines)

    info = {
        "span_start_line": start_idx + 1,
        "span_end_line": anchor_idx + 1,
        "span_len": anchor_idx - start_idx + 1,
        "needs_repo_root": needs_repo_root,
    }
    return new_text, old_text, "patched", info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--root", default=".")
    parser.add_argument("--sample-diffs", type=int, default=2)
    parser.add_argument("--show-all", action="store_true", help="List per-file status in dry-run")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    targets = sorted(
        list((root / "site" / "proofs").glob("*/proof.py"))
        + list((root / "docs" / "examples").glob("*/proof.py"))
    )

    results = []
    for p in targets:
        new_text, old_text, status, info = migrate(p)
        results.append((p, new_text, old_text, status, info))

    counts = {"already": 0, "patched": 0, "skip-no-anchor": 0, "patched+repo_root": 0}
    for _, _, _, status, info in results:
        counts[status] += 1
        if status == "patched" and info and info.get("needs_repo_root"):
            counts["patched+repo_root"] += 1

    print(f"Target files: {len(targets)}")
    print(f"  already canonical: {counts['already']}")
    print(f"  patched:           {counts['patched']}")
    print(f"    (of which need _REPO_ROOT alias): {counts['patched+repo_root']}")
    print(f"  skip-no-anchor:    {counts['skip-no-anchor']}")

    if args.show_all:
        print()
        for p, _, _, status, info in results:
            extra = ""
            if info:
                extra = f" span={info['span_len']}L needs_repo_root={info['needs_repo_root']}"
            print(f"  {status:16s}  {p.relative_to(root)}{extra}")

    if args.dry_run:
        patched = [(p, n, o) for p, n, o, s, _ in results if s == "patched"]
        for p, n, o in patched[: args.sample_diffs]:
            print(f"\n--- DIFF: {p.relative_to(root)} ---")
            diff = difflib.unified_diff(
                o.splitlines(keepends=True),
                n.splitlines(keepends=True),
                fromfile="before",
                tofile="after",
                n=3,
            )
            sys.stdout.writelines(diff)
        return 0

    for p, new_text, old_text, status, _ in results:
        if status == "patched":
            p.write_text(new_text)
    print(f"\nWrote {counts['patched']} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
