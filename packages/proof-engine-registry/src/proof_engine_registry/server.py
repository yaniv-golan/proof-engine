"""Reference HTTP server for self-hosted Proof Registry deployments.

Uses stdlib http.server only — no FastAPI — to keep the dependency footprint
minimal. For anything beyond a single-process dev/team server, put a real
reverse proxy in front (nginx/Caddy/Cloudflare) and point it at the static
output of `emit_registry_files`.
"""

from __future__ import annotations

import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

from proof_engine_registry import __protocol_version__
from proof_engine_registry.emit import emit_registry_files


_CLAIM_HASH_RE = re.compile(r"^/claims/([0-9a-f]{64})\.json$")
_PROOF_SLUG_RE = re.compile(r"^/proofs/([a-z0-9\-]+)\.json$")
_BADGE_JSON_RE = re.compile(r"^/proofs/([a-z0-9\-]+)/badge\.json$")
_BADGE_SVG_RE = re.compile(r"^/proofs/([a-z0-9\-]+)/badge\.svg$")


class RegistryServer:
    """Serves the registry protocol from a directory of `proof.json` files.

    On startup, emits static JSON to a temp "view" dir and serves from it.
    On publish, writes the new proof to the source dir and re-emits.
    """

    def __init__(
        self,
        proofs_dir: Path,
        name: str,
        base_url: str,
        bind: str = "127.0.0.1",
        port: int = 0,
        auth_token: Optional[str] = None,
    ):
        self.proofs_dir = Path(proofs_dir)
        self.name = name
        self.base_url = base_url
        self.auth_token = auth_token
        self._view_dir = self.proofs_dir.parent / ".registry-view"
        # Publish is serialized: concurrent POST /proofs requests would
        # otherwise race in `_rebuild_view` and interleave writes in
        # index.json (ThreadingHTTPServer dispatches on per-request threads).
        self._publish_lock = threading.Lock()
        self._rebuild_view()
        handler = _make_handler(self)
        self._httpd = ThreadingHTTPServer((bind, port), handler)
        # If the caller passed port=0, record the actual bound port.
        self.port = self._httpd.server_address[1]

    def _rebuild_view(self) -> None:
        emit_registry_files(
            proofs_dir=self.proofs_dir,
            output_dir=self._view_dir,
            base_url=self.base_url,
            registry_name=self.name,
            publishes_supported=self.auth_token is not None,
            auth_required=False,
        )

    def _check_auth(self, handler: BaseHTTPRequestHandler) -> bool:
        import hmac
        if self.auth_token is None:
            return False  # publish disabled
        header = handler.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return False
        presented = header[len("Bearer "):].strip()
        # Constant-time compare — defeats token-length / byte-wise timing
        # attacks. Both sides are encoded to bytes so compare_digest sees
        # stable-length inputs.
        return hmac.compare_digest(
            presented.encode("utf-8"),
            self.auth_token.encode("utf-8"),
        )

    def _serve_file(self, handler: BaseHTTPRequestHandler, path: Path,
                    content_type: str = "application/json",
                    head_only: bool = False) -> None:
        if not path.exists():
            self._serve_error(handler, 404, "not_found", f"not found: {path.name}",
                              head_only=head_only)
            return
        data = path.read_bytes()
        handler.send_response(200)
        handler.send_header("Content-Type", content_type)
        handler.send_header("Content-Length", str(len(data)))
        handler.end_headers()
        if not head_only:
            handler.wfile.write(data)

    def _serve_error(self, handler: BaseHTTPRequestHandler,
                     status: int, code: str, msg: str,
                     head_only: bool = False) -> None:
        body = json.dumps({"error": code, "message": msg}).encode("utf-8")
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(body)))
        handler.end_headers()
        if not head_only:
            handler.wfile.write(body)

    def handle_get(self, handler: BaseHTTPRequestHandler,
                   head_only: bool = False) -> None:
        """Serve a GET (or HEAD when head_only=True)."""
        path = handler.path
        if path == "/.well-known/proof-registry.json":
            self._serve_file(
                handler, self._view_dir / ".well-known" / "proof-registry.json",
                head_only=head_only,
            )
            return
        if path == "/index.json":
            self._serve_file(handler, self._view_dir / "index.json",
                             head_only=head_only)
            return
        m = _CLAIM_HASH_RE.match(path)
        if m:
            self._serve_file(handler, self._view_dir / "claims" / f"{m.group(1)}.json",
                             head_only=head_only)
            return
        m = _PROOF_SLUG_RE.match(path)
        if m:
            self._serve_file(handler, self._view_dir / "proofs" / f"{m.group(1)}.json",
                             head_only=head_only)
            return
        m = _BADGE_JSON_RE.match(path)
        if m:
            self._serve_file(
                handler,
                self._view_dir / "proofs" / m.group(1) / "badge.json",
                head_only=head_only,
            )
            return
        m = _BADGE_SVG_RE.match(path)
        if m:
            self._serve_file(
                handler,
                self._view_dir / "proofs" / m.group(1) / "badge.svg",
                content_type="image/svg+xml",
                head_only=head_only,
            )
            return
        self._serve_error(handler, 404, "not_found", f"no such path: {path}",
                          head_only=head_only)

    def handle_post_publish(self, handler: BaseHTTPRequestHandler) -> None:
        if not self._check_auth(handler):
            self._serve_error(handler, 401, "unauthorized", "missing or bad bearer token")
            return
        length = int(handler.headers.get("Content-Length", "0"))
        if length == 0 or length > 10 * 1024 * 1024:  # 10 MB cap
            self._serve_error(handler, 413, "too_large", "payload too large or empty")
            return
        raw = handler.rfile.read(length)
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            self._serve_error(handler, 400, "bad_request", "not valid JSON")
            return
        slug = body.get("slug")
        if not slug or not re.fullmatch(r"[a-z0-9\-]+", slug):
            self._serve_error(handler, 400, "bad_request", "invalid slug")
            return
        claim = body.get("claim")
        proof_json = body.get("proof_json") or {}
        inner_claim = proof_json.get("claim_natural")
        if not claim or not inner_claim:
            self._serve_error(handler, 400, "bad_request",
                              "both body.claim and proof_json.claim_natural are required")
            return
        # Silent-drift guard: outer claim MUST match inner claim_natural.
        # Without this, the index would advertise one claim while the proof
        # argues a different one.
        if claim.strip() != inner_claim.strip():
            self._serve_error(handler, 400, "bad_request",
                              "body.claim does not match proof_json.claim_natural")
            return
        # Serialize: mkdir/check/write/rebuild must be atomic w.r.t. other
        # publishers.
        with self._publish_lock:
            dest = self.proofs_dir / slug
            if dest.exists():
                self._serve_error(handler, 409, "conflict", "slug exists")
                return
            dest.mkdir(parents=True)
            (dest / "proof.json").write_text(
                json.dumps(proof_json, indent=2, sort_keys=True) + "\n"
            )
            try:
                self._rebuild_view()
            except Exception as exc:
                # Rebuild failed — undo the source write so the server stays
                # self-consistent. Logged to stderr via the handler's default
                # error formatter.
                import shutil as _shutil
                _shutil.rmtree(dest, ignore_errors=True)
                self._serve_error(
                    handler, 500, "rebuild_failed",
                    f"could not rebuild registry view: {exc}",
                )
                return
        # Send the new proof JSON as the response body, with 201 Created.
        view_path = self._view_dir / "proofs" / f"{slug}.json"
        if not view_path.exists():
            self._serve_error(handler, 500, "rebuild_failed",
                              "view did not produce expected proof file")
            return
        data = view_path.read_bytes()
        handler.send_response(201)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(data)))
        handler.end_headers()
        handler.wfile.write(data)

    def serve_forever(self) -> None:
        self._httpd.serve_forever()

    def shutdown(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()


def _make_handler(server: RegistryServer):
    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # quiet by default
            pass

        def do_GET(self):
            server.handle_get(self)

        def do_HEAD(self):
            # HEAD MUST mirror GET's status + headers but omit the body.
            # Required so `lint.py::_url_alive` (which uses `requests.head`)
            # can verify embedded proof URLs against a self-hosted server
            # without triggering 501 Not Implemented from stdlib's default.
            server.handle_get(self, head_only=True)

        def do_POST(self):
            if self.path == "/proofs":
                server.handle_post_publish(self)
            else:
                server._serve_error(self, 404, "not_found", f"no such path: {self.path}")

    return _Handler
