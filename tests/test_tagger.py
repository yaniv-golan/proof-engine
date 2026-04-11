import json
import pytest
from unittest.mock import patch, MagicMock

from tools.lib.tagger import canonicalize_tag, llm_tag, TAG_VOCABULARY, audit_vocabulary


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
