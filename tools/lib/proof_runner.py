"""Run proof.py and extract JSON summary."""

import json
import os
import subprocess
import sys


def run_proof_and_extract_json(proof_py_path):
    """Run a proof.py script and extract the JSON summary.

    Scrubs sensitive environment variables before running.
    Returns (proof_data_dict, None) on success or (None, error_string) on failure.
    """
    env = dict(os.environ)
    env.pop("GITHUB_TOKEN", None)
    env.pop("ACTIONS_RUNTIME_TOKEN", None)

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
        return json.loads(json_str), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in proof.py output: {e}"
