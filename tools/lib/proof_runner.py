"""Run proof.py and extract JSON summary."""

import json
import os
import subprocess
import sys
import typing
from pathlib import Path

# Resolve scripts path relative to this file's location (tools/lib/proof_runner.py)
# so it works regardless of CWD.
_skill_root = Path(__file__).resolve().parent.parent.parent / "proof-engine" / "skills" / "proof-engine"
_scripts = str(_skill_root / "scripts")
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)
from proof_types import ProofData, ProofDataV3

_KNOWN_KEYS = set(typing.get_type_hints(ProofData).keys()) | set(typing.get_type_hints(ProofDataV3).keys())


def run_proof_and_extract_json(proof_py_path):
    """Run a proof.py script and extract the JSON summary.

    Scrubs sensitive environment variables before running.
    Returns (proof_data_dict, None) on success or (None, error_string) on failure.
    """
    env = dict(os.environ)
    env.pop("GITHUB_TOKEN", None)
    env.pop("ACTIONS_RUNTIME_TOKEN", None)
    env.setdefault("PROOF_ENGINE_ROOT", str(_skill_root))

    result = subprocess.run(
        [sys.executable, str(proof_py_path)],
        capture_output=True, text=True, timeout=600, env=env,
    )
    if result.returncode != 0:
        return None, f"proof.py failed: {result.stderr[:500]}"

    marker = "=== PROOF SUMMARY (JSON) ==="
    output = result.stdout
    idx = output.find(marker)
    if idx == -1:
        return None, "proof.py output missing JSON summary marker"

    json_str = output[idx + len(marker):].strip()
    try:
        proof_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in proof.py output: {e}"

    # Strip unknown keys — defense-in-depth for proofs that bypass emit_proof_summary()
    unknown = set(proof_data.keys()) - _KNOWN_KEYS
    if unknown:
        print(
            f"WARNING: Stripping unknown keys from proof summary: {sorted(unknown)}. "
            f"Update ProofData in proof_types.py if these are intentional.",
            file=sys.stderr,
        )
        for k in unknown:
            del proof_data[k]

    return proof_data, None
