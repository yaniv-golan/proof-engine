import json
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest


FIXTURES = Path(__file__).parent / "fixtures" / "proofs"


def test_cli_serve_and_lookup(tmp_path, monkeypatch):
    import shutil
    writable = tmp_path / "proofs"
    shutil.copytree(FIXTURES, writable)
    port_file = tmp_path / "port.txt"

    proc = subprocess.Popen(
        [sys.executable, "-m", "proof_engine_registry.cli",
         "serve", str(writable), "--port", "0", "--print-port-to", str(port_file)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        # Wait up to 5s for the port file to appear.
        deadline = time.time() + 5
        while not port_file.exists() and time.time() < deadline:
            time.sleep(0.05)
        assert port_file.exists(), "server never wrote port file"
        port = int(port_file.read_text().strip())

        # Invoke `proof-registry lookup`.
        config_dir = tmp_path / "proof-engine"
        config_dir.mkdir()
        (config_dir / "registries.toml").write_text(f"""
[[registry]]
name = "local"
url = "http://127.0.0.1:{port}"
""")

        import os
        env = {**os.environ, "XDG_CONFIG_HOME": str(tmp_path)}

        r = subprocess.run(
            [sys.executable, "-m", "proof_engine_registry.cli",
             "lookup", "The sky is blue.", "--json"],
            capture_output=True, text=True, timeout=10, env=env,
        )
        assert r.returncode == 0, r.stderr
        payload = json.loads(r.stdout)
        assert payload["slug"] == "sample-claim"
    finally:
        proc.terminate()
        proc.wait(timeout=5)
