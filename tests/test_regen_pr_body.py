"""Tests for tools/regen_pr_body.py."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent  # tests/ → repo root


def _make_inputs(tmp_path, verdict="PROVED", qualified=False, qualifier=None,
                 stripped_keys=None, fallback=False):
    """Write the three input files and return their paths."""
    proof_dir = tmp_path / "proof"
    proof_dir.mkdir()

    proof_json = {
        "claim_natural": "Water boils at 100°C at sea level.",
        "verdict": {"value": verdict, "qualified": qualified,
                    "qualifier": qualifier, "reason": None},
        "fact_registry": {}, "claim_formal": {}, "key_results": {},
        "generator": {"name": "t", "version": "0", "repo": "r",
                      "generated_at": "2026-01-01"},
    }
    for name in ("proof.py", "proof.md", "proof_audit.md",
                 "proof_narrative.md", "proof.json"):
        (proof_dir / name).write_text(f"# {name}")
    (proof_dir / "proof.json").write_text(json.dumps(proof_json))

    now = datetime.now(timezone.utc)
    agent_json = {
        "slug": "boiling-point", "claim": "Water boils at 100°C at sea level.",
        "status": "ok", "iterations": 12, "model_used": "qwen/qwen3-coder:free",
        "fallback_triggered": fallback, "started_at": now.isoformat(),
        "ended_at": now.isoformat(), "error": None,
        "artifacts_written": ["proof.py", "proof.md"],
        "stripped_proof_json_keys": stripped_keys or [],
    }
    old_claim_file = tmp_path / "old_claim.txt"
    old_claim_file.write_text("Water boils at 100°C at sea level.")
    new_proof_json = proof_dir / "proof.json"
    agent_result = tmp_path / "agent_result.json"
    agent_result.write_text(json.dumps(agent_json))

    return old_claim_file, new_proof_json, agent_result


def _run(tmp_path, old_verdict="PROVED", **kwargs):
    old_claim_file, new_proof_json, agent_result = _make_inputs(tmp_path, **kwargs)
    result = subprocess.run(
        [sys.executable, "tools/regen_pr_body.py",
         "--slug", "boiling-point",
         "--old-verdict", old_verdict,
         "--old-claim-file", str(old_claim_file),
         "--new-proof-json", str(new_proof_json),
         "--agent-result", str(agent_result)],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
    )
    return result


def test_happy_path_exit_0_and_contains_required_sections(tmp_path):
    """Happy path: exit 0, stdout contains the six required sections."""
    result = _run(tmp_path)
    assert result.returncode == 0, result.stderr
    body = result.stdout
    assert "## Proof regen:" in body
    assert "## Verdict" in body
    assert "## Claim" in body
    assert "## Artifacts" in body
    assert "## Agent stats" in body
    assert "## Review checklist" in body


def test_verdict_change_flagged(tmp_path):
    """Verdict change from PROVED to SUPPORTED adds ⚠️ marker."""
    result = _run(tmp_path, old_verdict="PROVED", verdict="SUPPORTED")
    assert result.returncode == 0
    assert "⚠️ changed" in result.stdout


def test_no_verdict_change_no_flag(tmp_path):
    """Same old and new verdict → no ⚠️ marker in verdict row."""
    result = _run(tmp_path, old_verdict="PROVED", verdict="PROVED")
    assert result.returncode == 0
    assert "⚠️ changed" not in result.stdout


def test_stripped_keys_section_present_when_keys_stripped(tmp_path):
    """Stripped keys → warning section appears in output."""
    result = _run(tmp_path, stripped_keys=["extra_field", "another_key"])
    assert result.returncode == 0
    assert "Stripped proof.json keys" in result.stdout
    assert "`extra_field`" in result.stdout


def test_stripped_keys_section_absent_when_none(tmp_path):
    """No stripped keys → warning section absent."""
    result = _run(tmp_path, stripped_keys=[])
    assert result.returncode == 0
    assert "Stripped proof.json keys" not in result.stdout


def test_fallback_note_present_when_triggered(tmp_path):
    """fallback_triggered=True → '(fallback triggered)' in Agent stats."""
    result = _run(tmp_path, fallback=True)
    assert result.returncode == 0
    assert "fallback triggered" in result.stdout


def test_missing_input_files_exit_1(tmp_path):
    """Missing input files → exit 1 with error to stderr."""
    result = subprocess.run(
        [sys.executable, "tools/regen_pr_body.py",
         "--slug", "test", "--old-verdict", "PROVED",
         "--old-claim-file", str(tmp_path / "nope.txt"),
         "--new-proof-json", str(tmp_path / "nope.json"),
         "--agent-result", str(tmp_path / "nope2.json")],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 1
    assert result.stderr


def test_missing_agent_key_exit_1(tmp_path):
    """agent_result.json missing required key → exit 1."""
    old_claim_file, new_proof_json, agent_result = _make_inputs(tmp_path)
    data = json.loads(agent_result.read_text())
    del data["iterations"]
    agent_result.write_text(json.dumps(data))
    result = subprocess.run(
        [sys.executable, "tools/regen_pr_body.py",
         "--slug", "test", "--old-verdict", "PROVED",
         "--old-claim-file", str(old_claim_file),
         "--new-proof-json", str(new_proof_json),
         "--agent-result", str(agent_result)],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 1
    assert "missing required keys" in result.stderr
