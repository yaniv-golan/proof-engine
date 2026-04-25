"""Integration tests for `proof-engine verify`.

These exercise the CLI's control flow — registry check, short-circuit,
exit code mapping — without invoking the real proof-generation pipeline
(which requires a live LLM). Proof generation is tested end-to-end in
Task 5 with a separately gated integration test.
"""

import http.server
import json
import os
import shutil
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_FIXTURES = REPO_ROOT / "packages" / "proof-engine-registry" / "tests" / "fixtures" / "proofs"


@pytest.fixture
def local_registry(tmp_path):
    """Serve REGISTRY_FIXTURES as a registry on a random local port."""
    from proof_engine_registry.emit import emit_registry_files
    out = tmp_path / "registry"
    emit_registry_files(
        proofs_dir=REGISTRY_FIXTURES, output_dir=out,
        base_url="http://127.0.0.1:0", registry_name="Test",
    )
    original = Path.cwd()
    os.chdir(out)
    try:
        with socketserver.TCPServer(("127.0.0.1", 0),
                                    http.server.SimpleHTTPRequestHandler) as httpd:
            port = httpd.server_address[1]
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            try:
                yield f"http://127.0.0.1:{port}"
            finally:
                httpd.shutdown()
    finally:
        os.chdir(original)


def _write_registries_toml(tmp_path: Path, url: str) -> None:
    cfg_dir = tmp_path / "proof-engine"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "registries.toml").write_text(f"""
[[registry]]
name = "local"
url = "{url}"
""")


def test_registry_hit_short_circuits(tmp_path, local_registry, monkeypatch):
    _write_registries_toml(tmp_path, local_registry)
    env = {**os.environ, "XDG_CONFIG_HOME": str(tmp_path)}
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "verify_cli.py"),
         "--claim", "The sky is blue.",
         "--registry-only",
         "--json"],
        capture_output=True, text=True, env=env, timeout=15,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["source"] == "registry"
    assert payload["registry_hit"]["slug"] == "sample-claim"
    assert payload["generated"] is None


def test_registry_miss_returns_exit_3_when_registry_only(tmp_path, local_registry):
    _write_registries_toml(tmp_path, local_registry)
    env = {**os.environ, "XDG_CONFIG_HOME": str(tmp_path)}
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "verify_cli.py"),
         "--claim", "A claim that is definitely not in the registry.",
         "--registry-only",
         "--json"],
        capture_output=True, text=True, env=env, timeout=15,
    )
    assert result.returncode == 3, result.stderr
    payload = json.loads(result.stdout)
    assert payload["source"] == "error" or payload["registry_hit"] is None


def test_no_registries_configured_errors_cleanly(tmp_path):
    env = {**os.environ, "XDG_CONFIG_HOME": str(tmp_path)}
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "verify_cli.py"),
         "--claim", "x", "--registry-only", "--json"],
        capture_output=True, text=True, env=env, timeout=15,
    )
    # No registries configured + --registry-only → exit 3 with a clear error.
    assert result.returncode == 3
    payload = json.loads(result.stdout)
    assert any("registries" in e.lower() or "registry" in e.lower()
               for e in payload["errors"])
