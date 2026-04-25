"""Conformance tests for any Registry Protocol v0.1 implementation.

Parametrized over (a) serving static JSON via http.server, and (b) the
reference RegistryServer.
"""

import http.server
import json
import shutil
import socketserver
import threading
import time
from contextlib import contextmanager
from pathlib import Path

import pytest
import requests

from proof_engine_registry.emit import emit_registry_files
from proof_engine_registry.server import RegistryServer


FIXTURES = Path(__file__).parent / "fixtures" / "proofs"


def _make_handler(directory: Path):
    """Bind SimpleHTTPRequestHandler to a specific directory (no chdir).

    Avoids races between concurrent test servers that would share `os.getcwd`.
    """
    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, fmt, *args):  # silence test output
            pass

    return _Handler


@contextmanager
def _static_server(tmp_path):
    out = tmp_path / "static"
    emit_registry_files(
        proofs_dir=FIXTURES, output_dir=out,
        base_url="http://127.0.0.1:0", registry_name="Static",
    )
    handler = _make_handler(out)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            yield f"http://127.0.0.1:{port}"
        finally:
            httpd.shutdown()


@contextmanager
def _reference_server(tmp_path):
    writable = tmp_path / "proofs"
    shutil.copytree(FIXTURES, writable)
    srv = RegistryServer(
        proofs_dir=writable, name="Reference",
        base_url="http://127.0.0.1:0", bind="127.0.0.1", port=0,
    )
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    time.sleep(0.1)
    try:
        yield f"http://127.0.0.1:{srv.port}"
    finally:
        srv.shutdown()


@pytest.fixture(params=["static", "reference"])
def registry(request, tmp_path):
    maker = {"static": _static_server, "reference": _reference_server}[request.param]
    with maker(tmp_path) as url:
        yield url


def test_discovery_document(registry):
    r = requests.get(f"{registry}/.well-known/proof-registry.json", timeout=5)
    assert r.status_code == 200
    j = r.json()
    assert j["protocol_version"].startswith("0.")


def test_index_shape(registry):
    r = requests.get(f"{registry}/index.json", timeout=5)
    assert r.status_code == 200
    j = r.json()
    assert "entries" in j
    assert all("claim_hash" in e for e in j["entries"])


def test_claim_lookup_present(registry):
    idx = requests.get(f"{registry}/index.json", timeout=5).json()
    hashes = [e["claim_hash"] for e in idx["entries"]]
    for h in hashes:
        r = requests.get(f"{registry}/claims/{h}.json", timeout=5)
        assert r.status_code == 200, f"claim {h} should be addressable"


def test_claim_lookup_missing_is_404(registry):
    r = requests.get(f"{registry}/claims/{'0' * 64}.json", timeout=5)
    assert r.status_code == 404


def test_proof_lookup_present(registry):
    idx = requests.get(f"{registry}/index.json", timeout=5).json()
    for entry in idx["entries"]:
        r = requests.get(f"{registry}/proofs/{entry['slug']}.json", timeout=5)
        assert r.status_code == 200
