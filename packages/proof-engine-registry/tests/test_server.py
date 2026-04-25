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
