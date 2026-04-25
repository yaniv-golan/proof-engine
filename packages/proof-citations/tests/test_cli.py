import json
import socket
import subprocess
import sys

import pytest


def _has_network() -> bool:
    try:
        socket.gethostbyname("example.com")
        return True
    except OSError:
        return False


needs_network = pytest.mark.skipif(
    not _has_network(),
    reason="example.com DNS resolution required for live CLI tests",
)


@needs_network
def test_cli_verify_prints_json():
    # --json flag prints machine-parseable output.
    proc = subprocess.run(
        [sys.executable, "-m", "proof_citations.cli", "verify",
         "--url", "https://example.com",
         "--quote", "Example Domain",
         "--fact-id", "B1",
         "--json"],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["status"] == "verified"


@needs_network
def test_cli_verify_exits_nonzero_on_quote_missing():
    proc = subprocess.run(
        [sys.executable, "-m", "proof_citations.cli", "verify",
         "--url", "https://example.com",
         "--quote", "definitely not on this page",
         "--fact-id", "B1",
         "--json"],
        capture_output=True, text=True, timeout=30,
    )
    # A quote that isn't on the page returns status="not_found" and exit 1.
    # Real-world statuses from verify_citation: verified | partial |
    # not_found | fetch_failed.
    assert proc.returncode != 0
    payload = json.loads(proc.stdout)
    assert payload["status"] == "not_found"
