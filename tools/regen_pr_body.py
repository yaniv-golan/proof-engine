"""Render Markdown PR body for a regen proof PR.

Reads:
  --slug             proof slug
  --old-verdict      display string of old verdict
  --old-claim-file   path to .old_claim file
  --new-proof-json   path to published site/proofs/<slug>/proof.json
  --agent-result     path to agent_result.json

Writes Markdown to stdout. Exits non-zero on any missing input.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _canon_display(v) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    base = v.get("value", "")
    if v.get("qualified") and v.get("qualifier") == "unverified_citations":
        return f"{base} (with unverified citations)"
    return base


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--slug", required=True)
    p.add_argument("--old-verdict", required=True)
    p.add_argument("--old-claim-file", type=Path, required=True)
    p.add_argument("--new-proof-json", type=Path, required=True)
    p.add_argument("--agent-result", type=Path, required=True)
    args = p.parse_args()

    errors = []
    for attr, path in [("old-claim-file", args.old_claim_file),
                        ("new-proof-json", args.new_proof_json),
                        ("agent-result", args.agent_result)]:
        if not path.exists():
            errors.append(f"Missing input --{attr}: {path}")
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    try:
        old_claim = args.old_claim_file.read_text().strip()
        new_proof = json.loads(args.new_proof_json.read_text())
        agent = json.loads(args.agent_result.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error reading inputs: {e}", file=sys.stderr)
        return 1

    new_verdict = _canon_display(new_proof.get("verdict", ""))
    old_verdict = args.old_verdict.strip()
    verdict_changed = old_verdict != new_verdict
    verdict_flag = " ⚠️ changed" if verdict_changed else ""

    slug = args.slug
    proof_dir = args.new_proof_json.parent

    # Artifact sizes
    artifact_lines = []
    for name in ["proof.py", "proof.md", "proof_audit.md", "proof_narrative.md", "proof.json"]:
        path = proof_dir / name
        size = path.stat().st_size if path.exists() else 0
        artifact_lines.append(f"- `{name}` ({size:,} bytes)")

    # Stripped keys warning
    stripped = agent.get("stripped_proof_json_keys") or []
    stripped_section = ""
    if stripped:
        keys_list = ", ".join(f"`{k}`" for k in stripped)
        stripped_section = f"""
## ⚠️ Stripped proof.json keys

The agent wrote proof.json keys that the current schema does not recognise; they were dropped:
{keys_list}

Check whether these are intentional new fields and update `proof_types.py` if so.
"""

    # Validate required agent_result keys — hard-fail per spec §3.10
    required_agent_keys = ["iterations", "model_used", "fallback_triggered",
                            "started_at", "ended_at", "stripped_proof_json_keys"]
    missing_keys = [k for k in required_agent_keys if k not in agent]
    if missing_keys:
        print(f"Error: agent_result.json missing required keys: {missing_keys}", file=sys.stderr)
        return 1

    # Agent stats
    started = agent["started_at"]
    ended = agent["ended_at"]
    elapsed = ""
    try:
        s = datetime.fromisoformat(started)
        e = datetime.fromisoformat(ended)
        secs = int((e - s).total_seconds())
        elapsed = f"{secs // 60}m {secs % 60}s"
    except Exception:
        elapsed = "unknown"

    fallback_note = " (fallback triggered)" if agent["fallback_triggered"] else ""

    body = f"""## Proof regen: `{slug}`

## Verdict

| | Verdict |
|---|---|
| Old | `{old_verdict}` |
| New | `{new_verdict}`{verdict_flag} |

## Claim

> {old_claim}

*(Verbatim from old proof — claim-equivalence gate passed before this PR was opened.)*

## Artifacts

{chr(10).join(artifact_lines)}
{stripped_section}
## Agent stats

- Iterations: {agent["iterations"]}
- Model: `{agent["model_used"]}`{fallback_note}
- Elapsed: {elapsed}

## Review checklist

- [ ] Sources look plausible (URLs resolve, quotes are faithful)
- [ ] Verdict matches the evidence presented
- [ ] No hardcoded dates or values (check hardening rules)
- [ ] Citations verified (or noted as unverified)
- [ ] Claim unchanged from original
"""
    print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
