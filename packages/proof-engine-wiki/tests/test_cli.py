import json
import subprocess
import sys

import pytest


def test_cli_help():
    r = subprocess.run(
        [sys.executable, "-m", "proof_engine_wiki.cli", "--help"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "ingest" in r.stdout
    assert "lint" in r.stdout


def test_cli_lint_empty_dir(tmp_path):
    r = subprocess.run(
        [sys.executable, "-m", "proof_engine_wiki.cli", "lint", str(tmp_path), "--json"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["findings"] == []


def test_cli_lint_finds_unresolved_marker(tmp_path):
    (tmp_path / "page.md").write_text("X {{prove: claim}} Y")
    r = subprocess.run(
        [sys.executable, "-m", "proof_engine_wiki.cli", "lint", str(tmp_path),
         "--skip-network", "--json"],
        capture_output=True, text=True,
    )
    # Findings present → exit code 1 (lint failed).
    assert r.returncode == 1
    payload = json.loads(r.stdout)
    kinds = [f["kind"] for f in payload["findings"]]
    assert "unresolved_marker" in kinds
