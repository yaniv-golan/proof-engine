import json
import threading
import time
from pathlib import Path

import pytest
import requests

from proof_engine_registry.server import RegistryServer


FIXTURES = Path(__file__).parent / "fixtures" / "proofs"


@pytest.fixture
def server(tmp_path):
    # Copy fixtures to a writable location so the server can also publish.
    import shutil
    writable = tmp_path / "proofs"
    shutil.copytree(FIXTURES, writable)

    srv = RegistryServer(
        proofs_dir=writable,
        name="Test Self-Hosted",
        base_url="http://127.0.0.1:0",  # rewritten after bind
        bind="127.0.0.1",
        port=0,
        auth_token="secret",
    )
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)  # give the server a moment to bind
    try:
        yield f"http://127.0.0.1:{srv.port}"
    finally:
        srv.shutdown()


def test_server_discovery(server):
    r = requests.get(f"{server}/.well-known/proof-registry.json", timeout=5)
    r.raise_for_status()
    assert r.json()["protocol_version"] == "0.1"
    assert r.json()["publishes_supported"] is True


def test_server_index(server):
    r = requests.get(f"{server}/index.json", timeout=5)
    r.raise_for_status()
    entries = r.json()["entries"]
    assert len(entries) == 1


def test_server_claim_lookup_miss_is_404(server):
    r = requests.get(f"{server}/claims/{'0' * 64}.json", timeout=5)
    assert r.status_code == 404


def _valid_v3_proof(claim: str) -> dict:
    """Return a minimal valid v3 proof.json body."""
    return {
        "format_version": 3,
        "claim_natural": claim,
        "evidence": {"A1": {"type": "computed", "label": "trivial"}},
        "verdict": {"value": "PROVED", "qualified": False,
                    "qualifier": None, "reason": None},
        "generator": {"name": "proof-engine", "version": "1.28.0",
                      "generated_at": "2026-04-24"},
    }


def test_server_publish_requires_auth(server):
    body = {
        "slug": "new-claim",
        "claim": "A fresh claim.",
        "proof_json": _valid_v3_proof("A fresh claim."),
    }
    r = requests.post(f"{server}/proofs", json=body, timeout=5)
    assert r.status_code == 401


def test_server_publish_with_auth(server):
    body = {
        "slug": "new-claim",
        "claim": "A fresh claim.",
        "proof_json": _valid_v3_proof("A fresh claim."),
    }
    r = requests.post(f"{server}/proofs", json=body,
                      headers={"Authorization": "Bearer secret"},
                      timeout=5)
    assert r.status_code == 201
    # Index now contains two entries — the seeded sample-claim plus new-claim.
    idx = requests.get(f"{server}/index.json", timeout=5).json()
    slugs = sorted(e["slug"] for e in idx["entries"])
    assert slugs == ["new-claim", "sample-claim"]


def test_server_publish_rejects_claim_mismatch(server):
    """If body.claim doesn't match proof_json.claim_natural, reject 400.

    Prevents silent drift where the registry indexes one claim string but
    the underlying proof argues a different one.
    """
    body = {
        "slug": "drift-case",
        "claim": "The outer claim.",
        "proof_json": _valid_v3_proof("A DIFFERENT inner claim."),
    }
    r = requests.post(f"{server}/proofs", json=body,
                      headers={"Authorization": "Bearer secret"},
                      timeout=5)
    assert r.status_code == 400


def test_server_head_method_works(server):
    """HEAD on read endpoints must return same status/headers as GET, no body."""
    r = requests.head(f"{server}/.well-known/proof-registry.json", timeout=5)
    assert r.status_code == 200
    assert r.headers.get("Content-Type") == "application/json"
    assert r.text == ""

    r = requests.head(f"{server}/index.json", timeout=5)
    assert r.status_code == 200
    assert r.text == ""

    # HEAD on a missing claim must still 404, not 501.
    r = requests.head(f"{server}/claims/{'0' * 64}.json", timeout=5)
    assert r.status_code == 404


def test_server_emits_cors_header_on_reads(server):
    """Browser-based wikis need Access-Control-Allow-Origin on reads."""
    r = requests.get(f"{server}/index.json", timeout=5)
    assert r.status_code == 200
    assert r.headers.get("Access-Control-Allow-Origin") == "*"


def test_server_options_preflight(server):
    """OPTIONS preflight returns 204 with the right CORS headers."""
    r = requests.options(
        f"{server}/index.json",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
        timeout=5,
    )
    assert r.status_code == 204
    assert r.headers.get("Access-Control-Allow-Origin") == "*"
    assert "GET" in r.headers.get("Access-Control-Allow-Methods", "")
    assert "Authorization" in r.headers.get("Access-Control-Allow-Headers", "")


def test_server_emits_cache_control_on_reads(server):
    r = requests.get(f"{server}/index.json", timeout=5)
    assert "max-age" in r.headers.get("Cache-Control", "")


def test_server_emits_etag_and_honors_if_none_match(server):
    r = requests.get(f"{server}/index.json", timeout=5)
    etag = r.headers.get("ETag")
    assert etag, "server should emit an ETag on reads"
    # Revalidate — server must return 304 with no body.
    r2 = requests.get(
        f"{server}/index.json",
        headers={"If-None-Match": etag},
        timeout=5,
    )
    assert r2.status_code == 304
    assert r2.content == b""


def test_server_does_not_log_authorization(capfd, server):
    """When --log-json is on (separate test fixture would set it), the
    server MUST NOT include the Authorization header in the log record.
    Default fixture has log_json=False so log is empty either way; this
    test asserts the absence positively to lock the contract."""
    r = requests.get(
        f"{server}/index.json",
        headers={"Authorization": "Bearer must-not-leak"},
        timeout=5,
    )
    assert r.status_code == 200
    captured = capfd.readouterr()
    assert "must-not-leak" not in captured.err
    assert "must-not-leak" not in captured.out


# RFC 7807 Problem Details — error responses must be application/problem+json
# with type/status/title/detail/code fields. The five tests below pin the
# shape across every error path the server can take.

def test_problem_shape_on_404_claim_lookup(server):
    r = requests.get(f"{server}/claims/{'0' * 64}.json", timeout=5)
    assert r.status_code == 404
    assert r.headers.get("Content-Type") == "application/problem+json"
    body = r.json()
    assert body["status"] == 404
    assert body["code"] == "not_found"
    assert body["title"] == "Resource not found"
    assert body["type"].endswith("/not-found")
    assert "detail" in body and isinstance(body["detail"], str)


def test_problem_shape_on_401_publish_without_auth(server):
    r = requests.post(f"{server}/proofs", json={}, timeout=5)
    assert r.status_code == 401
    assert r.headers.get("Content-Type") == "application/problem+json"
    body = r.json()
    assert body["code"] == "unauthorized"
    assert body["status"] == 401
    assert body["type"].endswith("/unauthorized")


def test_problem_shape_on_400_claim_mismatch(server):
    body = {
        "slug": "drift",
        "claim": "outer claim",
        "proof_json": {
            "format_version": 3,
            "claim_natural": "DIFFERENT inner claim",
            "evidence": {"A1": {"type": "computed", "label": "x"}},
            "verdict": {"value": "PROVED", "qualified": False,
                        "qualifier": None, "reason": None},
            "generator": {"name": "proof-engine", "version": "0",
                          "generated_at": "2026-04-25"},
        },
    }
    r = requests.post(
        f"{server}/proofs", json=body,
        headers={"Authorization": "Bearer secret"},
        timeout=5,
    )
    assert r.status_code == 400
    assert r.headers.get("Content-Type") == "application/problem+json"
    p = r.json()
    assert p["code"] == "bad_request"
    assert p["status"] == 400
    assert "claim_natural" in p["detail"] or "match" in p["detail"]


def test_problem_includes_no_stack_trace_or_secret(server):
    """detail is human-readable but MUST NOT echo the request body
    or expose a Python traceback. Use the real bearer so auth passes
    and we exercise the JSON-decode error path (not the auth path)."""
    r = requests.post(
        f"{server}/proofs",
        data="not valid json — should-not-leak-into-body",
        headers={
            "Authorization": "Bearer secret",
            "Content-Type": "application/json",
        },
        timeout=5,
    )
    assert r.status_code == 400
    body = r.text
    assert "should-not-leak-into-body" not in body
    assert "Traceback" not in body
    assert "  File " not in body  # python traceback marker


def test_problem_type_uri_uses_default_base(server):
    """The default fixture doesn't override problem_type_base, so type
    URIs use https://proofengine.info/errors/... — consumers can rely on
    a stable absolute URI even for the local dev server."""
    r = requests.get(f"{server}/claims/{'0' * 64}.json", timeout=5)
    body = r.json()
    assert body["type"].startswith("https://")
