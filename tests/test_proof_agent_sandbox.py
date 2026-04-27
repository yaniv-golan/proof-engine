import os
import json
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def sandbox(tmp_path):
    from tools.proof_agent import Sandbox
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    return Sandbox(output_dir=output_dir, skill_dir=skill_dir)


@pytest.fixture
def sandbox_with_old(tmp_path):
    from tools.proof_agent import Sandbox
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    old_dir = tmp_path / "old"
    old_dir.mkdir()
    return Sandbox(output_dir=output_dir, skill_dir=skill_dir, old_proof_dir=old_dir)


_ALL_SCRUB_KEYS = [
    "OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
    "GITHUB_TOKEN", "GH_TOKEN",
    "ACTIONS_RUNTIME_TOKEN", "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
    "ACTIONS_ID_TOKEN_REQUEST_URL", "ACTIONS_CACHE_URL",
    "ZENODO_TOKEN", "ZENODO_SANDBOX_TOKEN",
    "APP_TOKEN",
]


def test_scrub_env_removes_all_listed_secrets(sandbox, monkeypatch):
    for k in _ALL_SCRUB_KEYS:
        monkeypatch.setenv(k, f"fake-{k}")
    env = sandbox._scrub_env()
    for k in _ALL_SCRUB_KEYS:
        assert k not in env, f"_scrub_env did not remove {k}"
    assert env["HOME"] == str(sandbox.tmpdir)
    assert env["PROOF_ENGINE_ROOT"] == str(sandbox.skill_dir)


def test_scrub_env_sets_proof_engine_root(sandbox):
    env = sandbox._scrub_env()
    assert env["PROOF_ENGINE_ROOT"] == str(sandbox.skill_dir)


def test_read_skill_file_reads_file(sandbox):
    (sandbox.skill_dir / "SKILL.md").write_text("# Skill")
    result = sandbox.read_skill_file("SKILL.md")
    assert result["ok"] is True
    assert result["content"] == "# Skill"


def test_read_skill_file_rejects_traversal(sandbox):
    result = sandbox.read_skill_file("../../etc/passwd")
    assert result["ok"] is False
    assert "escapes" in result["error"]


def test_safe_path_allows_valid(sandbox):
    p = sandbox._safe_path(sandbox.output_dir, "proof.py")
    assert p == sandbox.output_dir / "proof.py"


def test_safe_path_rejects_traversal(sandbox):
    with pytest.raises(ValueError, match="path escapes sandbox"):
        sandbox._safe_path(sandbox.output_dir, "../other/proof.py")


def test_safe_path_rejects_absolute(sandbox):
    with pytest.raises(ValueError, match="path escapes sandbox"):
        sandbox._safe_path(sandbox.output_dir, "/etc/passwd")


def test_read_old_proof_file_none_when_no_old_dir(sandbox):
    result = sandbox.read_old_proof_file("proof.py")
    assert result == {"ok": False, "error": "no old proof dir"}


def test_read_old_proof_file_rejects_non_whitelisted(sandbox_with_old):
    result = sandbox_with_old.read_old_proof_file("agent_result.json")
    assert result["ok"] is False
    assert "whitelist" in result["error"]


def test_read_old_proof_file_rejects_traversal(sandbox_with_old):
    result = sandbox_with_old.read_old_proof_file("../other-slug/proof.py")
    assert result["ok"] is False


def test_read_old_proof_file_reads_whitelisted(sandbox_with_old):
    (sandbox_with_old.old_proof_dir / "proof.py").write_text("# old proof")
    result = sandbox_with_old.read_old_proof_file("proof.py")
    assert result["ok"] is True
    assert result["content"] == "# old proof"
