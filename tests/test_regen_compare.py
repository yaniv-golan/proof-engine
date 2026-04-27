import json
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).parent.parent  # tests/ → repo root


@pytest.fixture
def draft_dir(tmp_path):
    d = tmp_path / "draft"
    d.mkdir()
    d.write_text = None  # not a method on Path — we'll write files directly
    return d


def _write_proof_json(draft_dir, claim, verdict):
    (draft_dir / "proof.json").write_text(json.dumps({
        "claim_natural": claim,
        "verdict": verdict,
    }))
    (draft_dir / "agent_result.json").write_text(json.dumps({
        "slug": "test", "claim": claim, "status": "ok",
        "verdict": verdict if isinstance(verdict, str) else verdict.get("value"),
        "claim_natural_in_proof": claim,
        "stripped_proof_json_keys": [],
        "iterations": 5, "model_used": "qwen/qwen3-coder:free",
        "fallback_triggered": False, "started_at": "2026-01-01T00:00:00+00:00",
        "ended_at": "2026-01-01T00:05:00+00:00",
    }))


def _old_claim_file(tmp_path, claim):
    p = tmp_path / ".old_claim"
    p.write_text(claim)
    return p


def _run(draft_dir, old_claim_file, old_verdict, strict=False, tmp_path=None):
    cmd = [
        sys.executable, "tools/regen_compare.py",
        "--slug", "test-slug",
        "--draft-dir", str(draft_dir),
        "--old-claim-file", str(old_claim_file),
        "--old-verdict", old_verdict,
    ]
    if strict:
        cmd.append("--strict-claim")
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))


def test_exact_match_exits_0(tmp_path):
    d = tmp_path / "draft"
    d.mkdir()
    _write_proof_json(d, "The sky is blue.", "PROVED")
    ocf = _old_claim_file(tmp_path, "The sky is blue.")
    r = _run(d, ocf, "PROVED")
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["claim_match"] is True
    assert out["verdict_changed"] is False


def test_whitespace_drift_exits_0(tmp_path):
    d = tmp_path / "draft"
    d.mkdir()
    _write_proof_json(d, "The sky is blue.", "PROVED")
    ocf = _old_claim_file(tmp_path, "The  sky  is  blue.")   # extra spaces
    r = _run(d, ocf, "PROVED")
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["claim_match"] is True


def test_strict_claim_fails_on_mismatch(tmp_path):
    d = tmp_path / "draft"
    d.mkdir()
    _write_proof_json(d, "The sky is blue.", "PROVED")
    ocf = _old_claim_file(tmp_path, "The sky is green.")
    r = _run(d, ocf, "PROVED", strict=True)
    assert r.returncode == 2


def test_verdict_dict_to_display(tmp_path):
    d = tmp_path / "draft"
    d.mkdir()
    _write_proof_json(d, "X.", {"value": "PROVED", "qualified": True,
                                "qualifier": "unverified_citations", "reason": None})
    ocf = _old_claim_file(tmp_path, "X.")
    r = _run(d, ocf, "PROVED")
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["verdict_new"] == "PROVED (with unverified citations)"
    assert out["verdict_changed"] is True


def test_no_strict_mismatch_exits_0(tmp_path):
    d = tmp_path / "draft"
    d.mkdir()
    _write_proof_json(d, "The sky is blue.", "PROVED")
    ocf = _old_claim_file(tmp_path, "The sky is green.")
    r = _run(d, ocf, "PROVED", strict=False)
    assert r.returncode == 0
    out = json.loads(r.stdout)
    assert out["claim_match"] is False


def test_script_error_exits_1(tmp_path):
    """Missing or malformed proof.json → exit code 1 (script error), not 0 or 2."""
    d = tmp_path / "draft"
    d.mkdir()
    # Write a malformed proof.json (not valid JSON)
    (d / "proof.json").write_text("this is not json")
    ocf = _old_claim_file(tmp_path, "Some claim.")
    r = _run(d, ocf, "PROVED")
    assert r.returncode == 1   # exit 1 = script error, not 0 (match) or 2 (mismatch)
