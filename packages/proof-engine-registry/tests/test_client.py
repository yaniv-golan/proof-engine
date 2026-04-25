import http.server
import json
import socketserver
import threading
from contextlib import contextmanager
from pathlib import Path

import pytest

from proof_engine_registry.client import RegistryClient, LookupHit
from proof_engine_registry.config import Registry
from proof_engine_registry.emit import emit_registry_files


FIXTURES = Path(__file__).parent / "fixtures" / "proofs"


def _make_handler(directory: Path):
    """SimpleHTTPRequestHandler bound to a specific directory.

    Uses the `directory=` constructor kwarg added in Python 3.7 so we don't
    have to chdir — that approach races between concurrent test servers.
    """
    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, fmt, *args):  # silence test output
            pass

    return _Handler


@contextmanager
def _serve_static(tmp_path: Path):
    emit_registry_files(
        proofs_dir=FIXTURES,
        output_dir=tmp_path,
        base_url="http://127.0.0.1:0",  # port filled in below
        registry_name="Test",
    )
    handler = _make_handler(tmp_path)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            yield f"http://127.0.0.1:{port}"
        finally:
            httpd.shutdown()


def test_client_discovery(tmp_path):
    with _serve_static(tmp_path) as url:
        client = RegistryClient([Registry(name="test", url=url)])
        disco = client.discovery(client.registries[0])
    from proof_engine_registry import __protocol_version__
    assert disco.protocol_version == __protocol_version__
    assert disco.proof_count == 1


def test_client_lookup_by_claim(tmp_path):
    with _serve_static(tmp_path) as url:
        client = RegistryClient([Registry(name="test", url=url)])
        hit = client.lookup("The sky is blue.")
    assert isinstance(hit, LookupHit)
    assert hit.slug == "sample-claim"
    assert hit.registry_name == "test"


def test_client_lookup_miss_returns_none(tmp_path):
    with _serve_static(tmp_path) as url:
        client = RegistryClient([Registry(name="test", url=url)])
        hit = client.lookup("Nothing claims this.")
    assert hit is None


@contextmanager
def _serve_dir(path):
    """Serve `path` on a random local port. Returns the base URL."""
    handler = _make_handler(path)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            yield f"http://127.0.0.1:{port}"
        finally:
            httpd.shutdown()


def test_client_iterates_registries_in_order(tmp_path):
    # Two identical local registries; lookup must return hit from first.
    emit_registry_files(
        proofs_dir=FIXTURES, output_dir=tmp_path / "a",
        base_url="http://a", registry_name="A",
    )
    emit_registry_files(
        proofs_dir=FIXTURES, output_dir=tmp_path / "b",
        base_url="http://b", registry_name="B",
    )
    with _serve_dir(tmp_path / "a") as a_url, _serve_dir(tmp_path / "b") as b_url:
        client = RegistryClient([
            Registry(name="first", url=a_url),
            Registry(name="second", url=b_url, fallback=True),
        ])
        hit = client.lookup("The sky is blue.")
        assert hit is not None
        assert hit.registry_name == "first"


def test_client_no_implicit_fallback(tmp_path):
    """A miss on registry N does NOT cascade to N+1 unless N+1.fallback=True.

    This rule is the load-bearing privacy guarantee for private/public
    registry pairs: a lookup miss on a private registry must not leak the
    claim text to the public registry.
    """
    # Empty registry (no proofs).
    empty_src = tmp_path / "empty-src"
    empty_src.mkdir()
    empty_out = tmp_path / "empty-out"
    emit_registry_files(
        proofs_dir=empty_src, output_dir=empty_out,
        base_url="http://empty", registry_name="Empty",
    )
    # Populated registry (has "The sky is blue.").
    populated_out = tmp_path / "populated-out"
    emit_registry_files(
        proofs_dir=FIXTURES, output_dir=populated_out,
        base_url="http://populated", registry_name="Populated",
    )

    with _serve_dir(empty_out) as empty_url, _serve_dir(populated_out) as pop_url:
        # Client configured: [empty (first), populated (second, NO fallback)].
        # The claim is in populated, but since fallback is False, the client
        # must NOT query populated after the empty miss.
        client = RegistryClient([
            Registry(name="empty", url=empty_url),
            Registry(name="populated", url=pop_url, fallback=False),
        ])
        assert client.lookup("The sky is blue.") is None


def test_client_explicit_fallback_cascades(tmp_path):
    """Sibling case: with fallback=True, a miss cascades correctly."""
    empty_src = tmp_path / "empty-src"
    empty_src.mkdir()
    empty_out = tmp_path / "empty-out"
    emit_registry_files(
        proofs_dir=empty_src, output_dir=empty_out,
        base_url="http://empty", registry_name="Empty",
    )
    populated_out = tmp_path / "populated-out"
    emit_registry_files(
        proofs_dir=FIXTURES, output_dir=populated_out,
        base_url="http://populated", registry_name="Populated",
    )

    with _serve_dir(empty_out) as empty_url, _serve_dir(populated_out) as pop_url:
        client = RegistryClient([
            Registry(name="empty", url=empty_url),
            Registry(name="populated", url=pop_url, fallback=True),
        ])
        hit = client.lookup("The sky is blue.")
        assert hit is not None
        assert hit.registry_name == "populated"
