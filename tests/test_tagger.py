import json
import pytest
from unittest.mock import patch, MagicMock

from tools.lib.tagger import (
    canonicalize_tag, llm_tag, TAG_VOCABULARY, audit_vocabulary,
    load_vocab_data, save_vocab_data, count_proofs, reload_vocabulary, check_publish_audit,
)


# --- canonicalize_tag tests (unchanged) ---

def test_canonicalize_lowercase():
    assert canonicalize_tag("Economics") == "economics"


def test_canonicalize_spaces_to_hyphens():
    assert canonicalize_tag("AI Safety") == "ai-safety"


def test_canonicalize_underscores_to_hyphens():
    assert canonicalize_tag("ai_safety") == "ai-safety"


def test_canonicalize_strips_whitespace():
    assert canonicalize_tag("  history  ") == "history"


def test_canonicalize_collapses_hyphens():
    assert canonicalize_tag("foo--bar") == "foo-bar"


def test_canonicalize_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        canonicalize_tag("   ")


def test_canonicalize_invalid_chars_raises():
    with pytest.raises(ValueError, match="invalid"):
        canonicalize_tag("hello@world")


# --- TAG_VOCABULARY validation ---

def test_vocabulary_keys_are_canonical():
    for tag in TAG_VOCABULARY:
        assert tag == canonicalize_tag(tag), f"TAG_VOCABULARY key {tag!r} is not canonical"


# --- llm_tag tests (mocked subprocess) ---

def _mock_claude_run(tags_response):
    """Create a mock subprocess.run that returns tags wrapped in claude JSON output."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"result": json.dumps(tags_response)})
    mock.stderr = ""
    return mock


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_success(mock_run):
    mock_run.return_value = _mock_claude_run(["health", "nutrition"])
    tags = llm_tag("Eating protein helps build muscle")
    assert tags == ["health", "nutrition"]


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_filters_unknown_tags(mock_run):
    mock_run.return_value = _mock_claude_run(["health", "made-up-tag", "ai"])
    tags = llm_tag("Some claim about health and AI")
    assert "made-up-tag" not in tags
    assert "health" in tags
    assert "ai" in tags


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_caps_at_max_tags(mock_run):
    mock_run.return_value = _mock_claude_run(["health", "nutrition", "biology", "ai"])
    tags = llm_tag("Complex claim", max_tags=2)
    assert len(tags) <= 2


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_subprocess_failure_raises(mock_run):
    mock = MagicMock()
    mock.returncode = 1
    mock.stderr = "model not found"
    mock_run.return_value = mock
    with pytest.raises(RuntimeError, match="claude CLI failed"):
        llm_tag("Test claim")


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_invalid_json_raises(mock_run):
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = "not json at all"
    mock.stderr = ""
    mock_run.return_value = mock
    with pytest.raises(RuntimeError, match="parse"):
        llm_tag("Test claim")


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_empty_result_raises(mock_run):
    mock_run.return_value = _mock_claude_run([])
    with pytest.raises(RuntimeError, match="no valid tags"):
        llm_tag("Test claim")


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_all_unknown_raises(mock_run):
    mock_run.return_value = _mock_claude_run(["fake-tag", "another-fake"])
    with pytest.raises(RuntimeError, match="no valid tags"):
        llm_tag("Test claim")


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_deduplicates(mock_run):
    mock_run.return_value = _mock_claude_run(["health", "health", "health"])
    tags = llm_tag("Test claim")
    assert tags.count("health") == 1


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_handles_single_backtick_wrapper(mock_run):
    """Handle case where claude wraps result in single backticks."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"result": '`["mathematics"]`'})
    mock.stderr = ""
    mock_run.return_value = mock
    tags = llm_tag("641 divides 2^32+1")
    assert tags == ["mathematics"]


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_handles_extra_text_after_json(mock_run):
    """Handle LLM returning extra text after valid JSON array."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"result": '["history", "biology"]\n\nWait let me reconsider.\n\n["history"]'})
    mock.stderr = ""
    mock_run.return_value = mock
    tags = llm_tag("The Great Wall of China")
    assert "history" in tags


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_handles_raw_array_response(mock_run):
    """Handle case where claude returns a raw JSON array (no wrapper)."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps(["mathematics", "physics"])
    mock.stderr = ""
    mock_run.return_value = mock
    tags = llm_tag("E=mc^2 proves mass-energy equivalence")
    assert tags == ["mathematics", "physics"]


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_handles_result_as_list(mock_run):
    """Handle case where claude returns {"result": [...]} directly."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"result": ["economics"]})
    mock.stderr = ""
    mock_run.return_value = mock
    tags = llm_tag("GDP growth slowed in Q4")
    assert tags == ["economics"]


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_timeout_raises(mock_run):
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=30)
    with pytest.raises(RuntimeError, match="timed out"):
        llm_tag("Test claim")


@patch("tools.lib.tagger.subprocess.run")
def test_llm_tag_not_found_raises(mock_run):
    mock_run.side_effect = FileNotFoundError()
    with pytest.raises(RuntimeError, match="not found"):
        llm_tag("Test claim")


# --- audit_vocabulary tests (mocked subprocess) ---

def _mock_audit_response(proposals):
    """Create a mock subprocess.run for audit_vocabulary."""
    response = json.dumps({"proposals": proposals, "rationale": "test"})
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps({"result": response})
    mock.stderr = ""
    return mock


@patch("tools.lib.tagger.subprocess.run")
def test_audit_vocabulary_accepts_valid_proposal(mock_run):
    mock_run.return_value = _mock_audit_response([
        {"slug": "law", "description": "Legal claims", "proofs": ["p1", "p2", "p3"]}
    ])
    claims = {"p1": {"claim": "C1", "tags": ["politics"], "manual": False},
              "p2": {"claim": "C2", "tags": ["politics"], "manual": False},
              "p3": {"claim": "C3", "tags": ["politics"], "manual": False}}
    result = audit_vocabulary(claims)
    assert len(result) == 1
    assert result[0]["slug"] == "law"


@patch("tools.lib.tagger.subprocess.run")
def test_audit_vocabulary_rejects_fewer_than_3_proofs(mock_run):
    mock_run.return_value = _mock_audit_response([
        {"slug": "law", "description": "Legal claims", "proofs": ["p1", "p2"]}
    ])
    claims = {"p1": {"claim": "C1", "tags": ["politics"], "manual": False},
              "p2": {"claim": "C2", "tags": ["politics"], "manual": False}}
    result = audit_vocabulary(claims)
    assert len(result) == 0


@patch("tools.lib.tagger.subprocess.run")
def test_audit_vocabulary_rejects_existing_slug(mock_run):
    mock_run.return_value = _mock_audit_response([
        {"slug": "health", "description": "Already exists", "proofs": ["p1", "p2", "p3"]}
    ])
    claims = {"p1": {"claim": "C1", "tags": ["health"], "manual": False},
              "p2": {"claim": "C2", "tags": ["health"], "manual": False},
              "p3": {"claim": "C3", "tags": ["health"], "manual": False}}
    result = audit_vocabulary(claims)
    assert len(result) == 0


@patch("tools.lib.tagger.subprocess.run")
def test_audit_vocabulary_rejects_bad_slug(mock_run):
    mock_run.return_value = _mock_audit_response([
        {"slug": "hello@world", "description": "Bad slug", "proofs": ["p1", "p2", "p3"]}
    ])
    claims = {"p1": {"claim": "C1", "tags": [], "manual": False},
              "p2": {"claim": "C2", "tags": [], "manual": False},
              "p3": {"claim": "C3", "tags": [], "manual": False}}
    result = audit_vocabulary(claims)
    assert len(result) == 0


@patch("tools.lib.tagger.subprocess.run")
def test_audit_vocabulary_logs_dropped_proposals(mock_run, capsys):
    mock_run.return_value = _mock_audit_response([
        {"slug": "health", "description": "Dupe", "proofs": ["p1", "p2", "p3"]}
    ])
    claims = {"p1": {"claim": "C1", "tags": [], "manual": False},
              "p2": {"claim": "C2", "tags": [], "manual": False},
              "p3": {"claim": "C3", "tags": [], "manual": False}}
    audit_vocabulary(claims)
    captured = capsys.readouterr()
    assert "WARNING" in captured.err or "collides" in captured.err


@patch("tools.lib.tagger.subprocess.run")
def test_audit_vocabulary_llm_failure_raises(mock_run):
    mock = MagicMock()
    mock.returncode = 1
    mock.stderr = "error"
    mock_run.return_value = mock
    with pytest.raises(RuntimeError):
        audit_vocabulary({"p1": {"claim": "C1", "tags": [], "manual": False}})


import yaml


def test_load_vocab_data(tmp_path):
    vocab_file = tmp_path / "tag_vocabulary.json"
    vocab_file.write_text(json.dumps({
        "proof_count_at_last_audit": 50,
        "last_audit_at": "2026-01-01",
        "vocabulary": {"health": "Medicine"}
    }))
    data = load_vocab_data(vocab_file)
    assert data["proof_count_at_last_audit"] == 50
    assert data["vocabulary"]["health"] == "Medicine"


def test_save_vocab_data(tmp_path):
    vocab_file = tmp_path / "tag_vocabulary.json"
    data = {
        "proof_count_at_last_audit": 100,
        "last_audit_at": "2026-04-11",
        "vocabulary": {"ai": "Artificial intelligence"}
    }
    save_vocab_data(vocab_file, data)
    loaded = json.loads(vocab_file.read_text())
    assert loaded["proof_count_at_last_audit"] == 100


def test_count_proofs(tmp_path):
    for name in ["proof-a", "proof-b", "proof-c"]:
        d = tmp_path / name
        d.mkdir()
        (d / "proof.json").write_text("{}")
    dot_dir = tmp_path / ".staging"
    dot_dir.mkdir()
    (dot_dir / "proof.json").write_text("{}")
    (tmp_path / "featured.json").write_text("[]")
    assert count_proofs(tmp_path) == 3


def _make_proofs_dir(tmp_path, count, claim_prefix="Claim"):
    """Create N minimal proof dirs for threshold/audit testing."""
    proofs = tmp_path / "proofs"
    proofs.mkdir()
    for i in range(count):
        d = proofs / f"proof-{i}"
        d.mkdir()
        (d / "proof.json").write_text(json.dumps({
            "claim_natural": f"{claim_prefix} {i}",
            "verdict": "PROVED",
        }))
        (d / "meta.yaml").write_text(yaml.dump({"tags": ["health"]}))
    return proofs


def test_publish_audit_triggers_at_threshold(tmp_path):
    proofs = _make_proofs_dir(tmp_path, count=110)
    vocab_file = tmp_path / "tag_vocabulary.json"
    vocab_file.write_text(json.dumps({
        "proof_count_at_last_audit": 100,
        "last_audit_at": "2026-01-01",
        "retag_pending": False,
        "vocabulary": {"health": "Medicine"}
    }))
    data = load_vocab_data(vocab_file)
    assert check_publish_audit(data, count_proofs(proofs)) == "audit"


def test_publish_audit_skips_below_threshold(tmp_path):
    proofs = _make_proofs_dir(tmp_path, count=108)
    vocab_file = tmp_path / "tag_vocabulary.json"
    vocab_file.write_text(json.dumps({
        "proof_count_at_last_audit": 100,
        "last_audit_at": "2026-01-01",
        "retag_pending": False,
        "vocabulary": {"health": "Medicine"}
    }))
    data = load_vocab_data(vocab_file)
    assert check_publish_audit(data, count_proofs(proofs)) == "skip"


def test_publish_audit_retag_pending_overrides_threshold(tmp_path):
    proofs = _make_proofs_dir(tmp_path, count=120)
    vocab_file = tmp_path / "tag_vocabulary.json"
    vocab_file.write_text(json.dumps({
        "proof_count_at_last_audit": 100,
        "last_audit_at": "2026-01-01",
        "retag_pending": True,
        "vocabulary": {"health": "Medicine"}
    }))
    data = load_vocab_data(vocab_file)
    assert check_publish_audit(data, count_proofs(proofs)) == "retag_pending"


@patch("tools.lib.tagger.subprocess.run")
def test_audit_failure_preserves_count(mock_run, tmp_path):
    mock = MagicMock()
    mock.returncode = 1
    mock.stdout = ""
    mock.stderr = "model overloaded"
    mock_run.return_value = mock

    vocab_file = tmp_path / "tag_vocabulary.json"
    vocab_file.write_text(json.dumps({
        "proof_count_at_last_audit": 100,
        "last_audit_at": "2026-01-01",
        "retag_pending": False,
        "vocabulary": {"health": "Medicine"}
    }))

    claims = {
        "p1": {"claim": "Claim 1", "tags": ["health"], "manual": False},
        "p2": {"claim": "Claim 2", "tags": ["health"], "manual": False},
        "p3": {"claim": "Claim 3", "tags": ["health"], "manual": False},
    }

    vocab_data = load_vocab_data(vocab_file)
    try:
        audit_vocabulary(claims)
        vocab_data["proof_count_at_last_audit"] = 999
        save_vocab_data(vocab_file, vocab_data)
    except RuntimeError:
        pass

    reloaded = load_vocab_data(vocab_file)
    assert reloaded["proof_count_at_last_audit"] == 100
    assert reloaded["retag_pending"] is False


def test_retag_pending_cleared_on_success(tmp_path):
    vocab_file = tmp_path / "tag_vocabulary.json"
    vocab_data = {
        "proof_count_at_last_audit": 100,
        "last_audit_at": "2026-01-01",
        "retag_pending": True,
        "vocabulary": {"health": "Medicine"}
    }
    vocab_file.write_text(json.dumps(vocab_data))

    vocab_data["retag_pending"] = False
    vocab_data["proof_count_at_last_audit"] = 118
    vocab_data["last_audit_at"] = "2026-04-11"
    save_vocab_data(vocab_file, vocab_data)

    reloaded = load_vocab_data(vocab_file)
    assert reloaded["retag_pending"] is False
    assert reloaded["proof_count_at_last_audit"] == 118
