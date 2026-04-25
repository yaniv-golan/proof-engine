import http.server
import os
import socketserver
import threading
from contextlib import contextmanager
from pathlib import Path

import pytest

from proof_engine_registry.config import Registry
from proof_engine_registry.emit import emit_registry_files

from proof_engine_wiki.ingest import ingest_page, IngestResult


REG_FIXTURES = Path(__file__).resolve().parents[2] / "proof-engine-registry" / "tests" / "fixtures" / "proofs"


@contextmanager
def _local_registry(tmp_path):
    out = tmp_path / "registry"
    emit_registry_files(
        proofs_dir=REG_FIXTURES, output_dir=out,
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
                yield [Registry(name="local", url=f"http://127.0.0.1:{port}")]
            finally:
                httpd.shutdown()
    finally:
        os.chdir(original)


def test_ingest_registry_only_hits_use_existing_proof(tmp_path):
    # Claim text must match the Phase 1b registry fixture's claim_natural
    # exactly ("The sky is blue.") so the lookup is a guaranteed hit.
    page = tmp_path / "claims.md"
    page.write_text("The sky is {{prove: The sky is blue.}}.")

    with _local_registry(tmp_path) as registries:
        result = ingest_page(
            page,
            registries=registries,
            registry_only=True,
        )

    assert isinstance(result, IngestResult)
    assert len(result.markers) == 1
    assert result.resolved_from_registry == 1
    assert result.generated == 0
    assert result.misses == 0
    # Rewritten content should contain a link and an image (badge).
    rewritten = page.read_text()
    assert "](http://127.0.0.1" in rewritten  # link to registry proof URL
    assert "badge.svg" in rewritten


def test_ingest_registry_only_reports_misses(tmp_path):
    page = tmp_path / "claims.md"
    page.write_text("A claim: {{prove: definitely not in registry}}.")
    with _local_registry(tmp_path) as registries:
        result = ingest_page(
            page, registries=registries, registry_only=True,
        )
    assert result.misses == 1
    assert result.resolved_from_registry == 0
    # Page is unchanged on miss in registry-only mode — the marker stays.
    assert "{{prove: definitely not in registry}}" in page.read_text()


def test_ingest_dry_run_does_not_write(tmp_path):
    page = tmp_path / "claims.md"
    page.write_text("X {{prove: The sky is blue.}} Y")
    original = page.read_text()
    with _local_registry(tmp_path) as registries:
        result = ingest_page(
            page, registries=registries, registry_only=True, dry_run=True,
        )
    assert result.resolved_from_registry == 1
    assert page.read_text() == original  # untouched
