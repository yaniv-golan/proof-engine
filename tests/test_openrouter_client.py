# tests/test_openrouter_client.py
import pytest
from unittest.mock import MagicMock, patch
import requests as _requests


def _resp(code, *, text="", json_data=None):
    """Build a mock requests.Response."""
    r = MagicMock()
    r.status_code = code
    r.text = text if json_data is None else ""
    if json_data is not None:
        r.json.return_value = json_data
        r.text = str(json_data)
    else:
        r.json.side_effect = ValueError("no json")
    return r


def _resp_ok(json_data):
    """Build a successful 200 response with JSON."""
    r = MagicMock()
    r.status_code = 200
    r.text = str(json_data)
    r.json.return_value = json_data
    return r


from tools.proof_agent import OpenRouterClient, AuthError, QuotaError, NetworkError, CapError


def _make_client(model="test-model", fallback=None, max_calls=150):
    return OpenRouterClient(
        api_key="sk-test",
        model=model,
        fallback_model=fallback,
        api_base="https://fake.openrouter.ai/api/v1",
        max_llm_calls=max_calls,
    )


def test_401_raises_auth_error_immediately():
    """401 must raise AuthError without any retry."""
    client = _make_client()
    with patch("requests.post", return_value=_resp(401, text="Unauthorized")) as mock_post:
        with pytest.raises(AuthError):
            client.chat([{"role": "user", "content": "hi"}])
    assert mock_post.call_count == 1   # single attempt, no retry


def test_429_retries_5_times_then_raises_quota_error():
    """429 triggers 4 retries (5 total attempts) then raises QuotaError."""
    client = _make_client()
    with patch("requests.post", return_value=_resp(429, text="rate limit")) as mock_post:
        with patch("time.sleep"):
            with pytest.raises(QuotaError):
                client.chat([{"role": "user", "content": "hi"}])
    assert mock_post.call_count == 5   # 1 initial + 4 retries


def test_429_falls_back_to_fallback_model_and_succeeds():
    """After primary model exhausts retries, fallback model succeeds."""
    client = _make_client(fallback="fallback-model")
    good_resp = _resp_ok({"choices": [{"message": {"content": "ok"}}]})
    call_count = 0

    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        body = kwargs.get("json", {})
        if body.get("model") == "test-model":
            return _resp(429, text="rate limit")
        return good_resp

    with patch("requests.post", side_effect=side_effect):
        with patch("time.sleep"):
            resp = client.chat([{"role": "user", "content": "hi"}])
    assert resp == good_resp.json.return_value
    assert client._using_fallback is True


def test_network_error_does_not_trigger_fallback():
    """NetworkError retries same model but never switches to fallback."""
    client = _make_client(fallback="fallback-model")
    with patch("requests.post",
               side_effect=_requests.exceptions.ConnectionError("conn refused")) as mock_post:
        with patch("time.sleep"):
            with pytest.raises(NetworkError):
                client.chat([{"role": "user", "content": "hi"}])
    assert client._using_fallback is False
    assert mock_post.call_count == 5   # 5 attempts on primary only


def test_per_run_cap_raises_quota_error_with_cap_message():
    """After max_llm_calls successful calls, next call raises CapError."""
    client = _make_client(max_calls=2)
    good = _resp_ok({"choices": [{"message": {"content": "ok"}}]})
    with patch("requests.post", return_value=good):
        client.chat([{"role": "user", "content": "1"}])
        client.chat([{"role": "user", "content": "2"}])
        with pytest.raises(QuotaError, match="cap"):
            client.chat([{"role": "user", "content": "3"}])


def test_non_json_200_raises_network_error():
    """A 200 with non-JSON body (common during outages) raises NetworkError."""
    client = _make_client()
    bad = MagicMock()
    bad.status_code = 200
    bad.text = "<html>Gateway Timeout</html>"
    bad.json.side_effect = ValueError("not json")
    with patch("requests.post", return_value=bad):
        with patch("time.sleep"):
            with pytest.raises(NetworkError):
                client.chat([{"role": "user", "content": "hi"}])


def test_permanent_4xx_raises_auth_error_no_retry():
    """400, 403, 404, 405, 422 must raise AuthError without retry."""
    for code in (400, 403, 404, 405, 422):
        client = _make_client()
        with patch("requests.post",
                   return_value=_resp(code, text="bad")) as mock_post:
            with pytest.raises(AuthError):
                client.chat([{"role": "user", "content": "hi"}])
        assert mock_post.call_count == 1, f"code {code} should not be retried"


def test_200_with_error_dict_rate_limit_raises_quota_error():
    """OpenRouter 200 with error.code=429 raises QuotaError (triggers fallback)."""
    client = _make_client(fallback="fallback-model")
    error_resp = _resp_ok({"error": {"code": 429, "message": "rate limit exceeded"}})
    with patch("requests.post", return_value=error_resp):
        with patch("time.sleep"):
            with pytest.raises(QuotaError):
                client.chat([{"role": "user", "content": "hi"}])


def test_200_with_error_dict_non_rate_raises_network_error():
    """OpenRouter 200 with error.code=503 raises NetworkError (retried, no fallback switch)."""
    client = _make_client(fallback="fallback-model")
    error_resp = _resp_ok({"error": {"code": 503, "message": "model unavailable"}})
    with patch("requests.post", return_value=error_resp):
        with patch("time.sleep"):
            with pytest.raises(NetworkError):
                client.chat([{"role": "user", "content": "hi"}])
    # NetworkError should NOT have triggered fallback
    assert client._using_fallback is False


# ---------------------------------------------------------------------------
# run_agent status-mapping tests
# These verify the QuotaError handler correctly maps to quota_blocked vs llm_error.
# ---------------------------------------------------------------------------

from tools.proof_agent import run_agent, CapError, AgentResult


def _make_client_raising(exc, using_fallback=False):
    """Return a mock OpenRouterClient whose chat() raises `exc`."""
    c = MagicMock()
    c.chat.side_effect = exc
    c._using_fallback = using_fallback
    c.current_model = "mock-model"
    c.fallback_triggered = using_fallback
    return c


def _run_agent_with_mock_client(client_mock, tmp_path, skill_dir):
    """Call run_agent patching OpenRouterClient constructor to return client_mock."""
    with patch("tools.proof_agent.OpenRouterClient", return_value=client_mock):
        return run_agent(
            slug="test-slug",
            claim="test claim",
            output_dir=tmp_path / "out",
            skill_dir=skill_dir,
            model="m",
            fallback_model="fb",
            api_key="sk-x",
        )


@pytest.fixture()
def skill_dir(tmp_path):
    """Minimal skill_dir: just needs to exist (no SKILL.md needed for these tests)."""
    d = tmp_path / "skill"
    d.mkdir()
    return d


def test_cap_error_maps_to_quota_blocked(tmp_path, skill_dir):
    """CapError (per-run cap hit) → status='quota_blocked', not 'llm_error'."""
    client = _make_client_raising(CapError("cap reached"), using_fallback=False)
    result = _run_agent_with_mock_client(client, tmp_path, skill_dir)
    assert result.status == "quota_blocked"


def test_cap_error_while_on_fallback_still_quota_blocked(tmp_path, skill_dir):
    """CapError while _using_fallback=True → still 'quota_blocked', not 'llm_error'."""
    client = _make_client_raising(CapError("cap reached mid-retry"), using_fallback=True)
    result = _run_agent_with_mock_client(client, tmp_path, skill_dir)
    assert result.status == "quota_blocked"


def test_quota_error_with_fallback_exhausted_maps_to_llm_error(tmp_path, skill_dir):
    """QuotaError (not CapError) while _using_fallback=True → 'llm_error'."""
    client = _make_client_raising(QuotaError("rate limit"), using_fallback=True)
    result = _run_agent_with_mock_client(client, tmp_path, skill_dir)
    assert result.status == "llm_error"


def test_quota_error_without_fallback_maps_to_quota_blocked(tmp_path, skill_dir):
    """QuotaError (not CapError) with no fallback attempted → 'quota_blocked'."""
    client = _make_client_raising(QuotaError("rate limit"), using_fallback=False)
    result = _run_agent_with_mock_client(client, tmp_path, skill_dir)
    assert result.status == "quota_blocked"


def test_malformed_tool_call_entry_does_not_crash_agent(tmp_path, skill_dir):
    """A tool_calls entry missing 'function' key is handled gracefully.

    The agent loop should record a clean error for the malformed entry and continue,
    not KeyError-crash with no result file.
    """
    malformed_response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {"id": "call_bad", "type": "function"},
                ],
            },
            "finish_reason": "tool_calls",
        }]
    }
    second_call_messages = []
    call_count = [0]

    def _chat_side_effect(messages, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return malformed_response
        second_call_messages.extend(messages)
        raise CapError("cap reached")

    client = MagicMock()
    client.chat.side_effect = _chat_side_effect
    client._using_fallback = False
    client.current_model = "mock-model"
    client.fallback_triggered = False

    result = _run_agent_with_mock_client(client, tmp_path, skill_dir)
    assert result.status == "quota_blocked"

    tool_msgs = [m for m in second_call_messages
                 if m.get("role") == "tool" and m.get("tool_call_id") == "call_bad"]
    assert len(tool_msgs) == 1
    import json as _json
    content = _json.loads(tool_msgs[0]["content"])
    assert content.get("ok") is False
    assert "malformed" in content.get("error", "")
