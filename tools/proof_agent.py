"""Generic OpenRouter agent loop for proof regeneration.

Usage: see module docstring in __main__ block.
"""

import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# KNOWN_PROOF_JSON_KEYS — single source of truth via proof_runner (Task 1)
# ---------------------------------------------------------------------------
from tools.lib.proof_runner import KNOWN_PROOF_JSON_KEYS

_PROOF_JSON_MARKER = "=== PROOF SUMMARY (JSON) ==="

# ---------------------------------------------------------------------------
# AgentResult
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    slug: str
    claim: str
    status: str
    iterations: int = 0
    model_used: str = ""
    fallback_triggered: bool = False
    proof_json_written: bool = False
    artifacts_written: list = field(default_factory=list)
    verdict: str | None = None
    claim_natural_in_proof: str | None = None
    stripped_proof_json_keys: list = field(default_factory=list)
    error: str | None = None
    started_at: str = ""
    ended_at: str = ""


# ---------------------------------------------------------------------------
# Sandbox
# ---------------------------------------------------------------------------

_SCRUB_KEYS = (
    "OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
    "GITHUB_TOKEN", "GH_TOKEN",
    "ACTIONS_RUNTIME_TOKEN", "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
    "ACTIONS_ID_TOKEN_REQUEST_URL", "ACTIONS_CACHE_URL",
    "ZENODO_TOKEN", "ZENODO_SANDBOX_TOKEN",
    "APP_TOKEN",
)

_WRITE_WHITELIST = frozenset({
    "proof.py", "proof.md", "proof_audit.md",
    "proof_narrative.md", "proof.json", "notes.md",
})
_OLD_READ_WHITELIST = frozenset({
    "proof.py", "proof.md", "proof_audit.md", "proof_narrative.md",
    "proof.json", "meta.yaml", "depends_on_resolved.json",
})

_MAX_READ_BYTES = 200_000
_MAX_IO_BYTES   = 16_384   # stdout/stderr cap for run_bash


class Sandbox:
    def __init__(self, output_dir: Path, skill_dir: Path,
                 old_proof_dir: Path | None = None):
        self.output_dir    = output_dir.resolve()
        self.skill_dir     = skill_dir.resolve()
        self.old_proof_dir = old_proof_dir.resolve() if old_proof_dir else None
        self.tmpdir = Path(tempfile.mkdtemp(prefix=f"proof-agent-{output_dir.name}-"))

    def _scrub_env(self) -> dict:
        env = dict(os.environ)
        for k in _SCRUB_KEYS:
            env.pop(k, None)
        env["HOME"] = str(self.tmpdir)
        env["PROOF_ENGINE_ROOT"] = str(self.skill_dir)
        repo_root = Path(__file__).resolve().parent.parent
        env["PYTHONPATH"] = str(repo_root)
        return env

    def _safe_path(self, base: Path, rel: str) -> Path:
        p = (base / rel).resolve()
        if not p.is_relative_to(base) and p != base:
            raise ValueError(f"path escapes sandbox: {rel!r}")
        return p

    def read_old_proof_file(self, rel: str, max_bytes: int = _MAX_READ_BYTES) -> dict:
        if self.old_proof_dir is None:
            return {"ok": False, "error": "no old proof dir"}
        if Path(rel).name not in _OLD_READ_WHITELIST:
            return {"ok": False, "error": f"filename not in read whitelist: {Path(rel).name!r}"}
        try:
            p = self._safe_path(self.old_proof_dir, rel)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        if not p.is_file():
            return {"ok": False, "error": f"{'is a directory' if p.is_dir() else 'file not found'}: {rel}"}
        content = p.read_bytes()
        if len(content) > max_bytes:
            return {"ok": False, "error": f"file too large ({len(content)} bytes > {max_bytes})"}
        return {"ok": True, "content": content.decode("utf-8", errors="replace")}

    def read_skill_file(self, rel: str, max_bytes: int = _MAX_READ_BYTES) -> dict:
        try:
            p = self._safe_path(self.skill_dir, rel)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        if not p.is_file():
            return {"ok": False, "error": f"{'is a directory' if p.is_dir() else 'file not found'}: {rel}"}
        content = p.read_bytes()
        if len(content) > max_bytes:
            return {"ok": False, "error": f"file too large ({len(content)} bytes > {max_bytes})"}
        return {"ok": True, "content": content.decode("utf-8", errors="replace")}

    def read_file(self, rel: str, max_bytes: int = _MAX_READ_BYTES) -> dict:
        try:
            p = self._safe_path(self.output_dir, rel)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        if not p.is_file():
            return {"ok": False, "error": f"{'is a directory' if p.is_dir() else 'file not found'}: {rel}"}
        content = p.read_bytes()
        if len(content) > max_bytes:
            return {"ok": False, "error": f"file too large ({len(content)} bytes > {max_bytes})"}
        return {"ok": True, "content": content.decode("utf-8", errors="replace")}

    def write_file(self, rel: str, content: str) -> dict:
        if Path(rel).name not in _WRITE_WHITELIST:
            return {"ok": False, "error": f"filename not in write whitelist: {Path(rel).name!r}"}
        try:
            p = self._safe_path(self.output_dir, rel)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        written = p.read_text(encoding="utf-8")
        if len(written) != len(content):
            return {
                "ok": False,
                "error": (
                    f"write truncated: wrote {len(content)} chars, "
                    f"read back {len(written)} chars (disk error). "
                    "Split the content into smaller chunks and write incrementally."
                ),
            }
        return {"ok": True}

    def list_dir(self, rel: str = ".") -> dict:
        try:
            p = self._safe_path(self.output_dir, rel)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        if not p.is_dir():
            return {"ok": False, "error": f"not a directory: {rel}"}
        entries = [e.name for e in sorted(p.iterdir())]
        return {"ok": True, "entries": entries}

    def run_bash(self, cmd: str, timeout: int = 120) -> dict:
        if not cmd or not cmd.strip():
            return {"ok": False, "error": "empty command",
                    "exit_code": -1, "stdout": "", "stderr": ""}
        try:
            args = shlex.split(cmd)
        except ValueError as e:
            return {"ok": False, "error": f"shlex parse error: {e}",
                    "exit_code": -1, "stdout": "", "stderr": ""}
        try:
            r = subprocess.run(
                args,
                shell=False,
                cwd=str(self.output_dir),
                env=self._scrub_env(),
                capture_output=True,
                timeout=timeout,
            )
            stdout = r.stdout.decode("utf-8", errors="replace")[:_MAX_IO_BYTES]
            stderr = r.stderr.decode("utf-8", errors="replace")[:_MAX_IO_BYTES]
            ok = r.returncode == 0
            return {"ok": ok, "exit_code": r.returncode,
                    "stdout": stdout, "stderr": stderr}
        except subprocess.TimeoutExpired as e:
            stdout = (e.stdout or b"").decode("utf-8", errors="replace")[:_MAX_IO_BYTES]
            stderr = (e.stderr or b"").decode("utf-8", errors="replace")[:_MAX_IO_BYTES]
            return {"ok": False, "exit_code": -1, "error": "timeout",
                    "stdout": stdout, "stderr": stderr}
        except (FileNotFoundError, PermissionError, OSError) as e:
            return {"ok": False, "exit_code": -1,
                    "error": f"command not found or not executable: {e}",
                    "stdout": "", "stderr": ""}

    def run_proof_py(self, timeout: int = 600) -> dict:
        proof_path = self.output_dir / "proof.py"
        if not proof_path.exists():
            return {"ok": False, "exit_code": -1, "error": "proof.py not found",
                    "stdout": "", "stderr": "", "proof_data": None, "stripped_keys": []}
        try:
            r = subprocess.run(
                [sys.executable, str(proof_path)],
                cwd=str(self.output_dir),
                env=self._scrub_env(),
                capture_output=True,
                timeout=timeout,
            )
            stdout = r.stdout.decode("utf-8", errors="replace")
            stderr = r.stderr.decode("utf-8", errors="replace")
            if r.returncode != 0:
                return {"ok": False, "exit_code": r.returncode,
                        "stdout": stdout[:_MAX_IO_BYTES],
                        "stderr": stderr[:_MAX_IO_BYTES],
                        "proof_data": None, "stripped_keys": []}
            idx = stdout.find(_PROOF_JSON_MARKER)
            if idx == -1:
                return {"ok": False, "exit_code": r.returncode,
                        "error": "missing JSON summary marker",
                        "stdout": stdout[:_MAX_IO_BYTES],
                        "stderr": stderr[:_MAX_IO_BYTES],
                        "proof_data": None, "stripped_keys": []}
            json_str = stdout[idx + len(_PROOF_JSON_MARKER):].strip()
            try:
                proof_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                return {"ok": False, "exit_code": r.returncode,
                        "error": f"JSON parse error: {e}",
                        "stdout": stdout[:_MAX_IO_BYTES],
                        "stderr": stderr[:_MAX_IO_BYTES],
                        "proof_data": None, "stripped_keys": []}
            unknown = sorted(set(proof_data.keys()) - KNOWN_PROOF_JSON_KEYS)
            return {"ok": True, "exit_code": 0,
                    "stdout": stdout[:_MAX_IO_BYTES],
                    "stderr": stderr[:_MAX_IO_BYTES],
                    "proof_data": proof_data, "stripped_keys": unknown}
        except subprocess.TimeoutExpired as e:
            stdout = (e.stdout or b"").decode("utf-8", errors="replace")[:_MAX_IO_BYTES]
            stderr = (e.stderr or b"").decode("utf-8", errors="replace")[:_MAX_IO_BYTES]
            return {"ok": False, "exit_code": -1, "error": "timeout",
                    "stdout": stdout, "stderr": stderr,
                    "proof_data": None, "stripped_keys": []}


# ---------------------------------------------------------------------------
# OpenRouter client
# ---------------------------------------------------------------------------

import time
import requests as _requests  # use requests for (connect, read) split timeout

_OPENROUTER_BASE = "https://openrouter.ai/api/v1"
# Seconds to wait before each retry attempt.
# Sequence length = 4 → 4 retries → 5 total attempts (initial + 4 retries).
# After all 5 attempts fail on the primary model with QuotaError,
# switch to fallback model once and restart the same backoff sequence.
# 4 retries match the 4 backoff values listed in spec §3.7.
_BACKOFF = (1, 4, 16, 64)   # waits for attempts 2–5 (attempt 1 has no wait)


class QuotaError(Exception):
    """Rate-limit / quota exhaustion — triggers model fallback after 4 retries."""


class CapError(QuotaError):
    """Per-run LLM call cap reached — subclass of QuotaError so isinstance()
    can distinguish it from a genuine quota/rate-limit error without fragile
    string matching on the exception message."""


class AuthError(Exception):
    """Invalid or missing API key — do not retry."""


class NetworkError(Exception):
    """Transient network failure — retry same model; do NOT switch to fallback."""


class OpenRouterClient:
    def __init__(self, api_key: str, model: str, fallback_model: str | None = None,
                 api_base: str = _OPENROUTER_BASE, max_llm_calls: int = 150):
        self.api_key = api_key
        self.model = model
        self.fallback_model = fallback_model
        self.api_base = api_base.rstrip("/")
        self.max_llm_calls = max_llm_calls
        self._total_attempts = 0   # all HTTP attempts (retries + iterations)
        self._calls = 0            # successful LLM calls
        self._using_fallback = False

    @property
    def current_model(self) -> str:
        return self.fallback_model if self._using_fallback else self.model

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Send a chat-completion request; retry on transient errors.

        Retry policy (spec §3.7):
          - 401: raise AuthError immediately, no retry.
          - 429/402/quota: backoff 1s, 4s, 16s, 64s (4 retries = 5 attempts).
            After 4 failures on primary model, switch to fallback once and
            restart the backoff sequence. After fallback exhaustion: raise QuotaError.
          - Network errors (OSError): same backoff, no model switch.
          - Per-run cap: raise CapError immediately.
        """
        if self._calls >= self.max_llm_calls:
            raise CapError(f"Per-run LLM call cap ({self.max_llm_calls}) reached")

        try:
            return self._attempt_with_backoff(messages, tools)
        except QuotaError as primary_exc:
            if self.fallback_model and not self._using_fallback:
                self._using_fallback = True
                try:
                    return self._attempt_with_backoff(messages, tools)
                except (QuotaError, NetworkError) as e:
                    raise QuotaError(
                        f"Fallback model {self.fallback_model!r} also failed: {e}"
                    ) from e
            raise
        # NetworkError propagates directly — no fallback switch.

    def _attempt_with_backoff(self, messages: list[dict],
                              tools: list[dict] | None) -> dict:
        """Try up to 5 attempts (initial + 4 backoff retries). Raise on exhaustion."""
        last_exc: Exception | None = None
        for wait in [0] + list(_BACKOFF):
            if self._total_attempts >= self.max_llm_calls:
                raise CapError(f"Per-run LLM call cap ({self.max_llm_calls}) reached")
            if wait:
                time.sleep(wait)
            self._total_attempts += 1
            try:
                resp = self._post(messages, tools)
                self._calls += 1
                return resp
            except AuthError:
                raise
            except QuotaError as e:
                last_exc = e
            except NetworkError as e:
                last_exc = e
        # Preserve the error type: network failures stay NetworkError;
        # quota failures stay QuotaError. Only QuotaError triggers fallback.
        if isinstance(last_exc, NetworkError):
            raise NetworkError(
                f"Network failure after {len(_BACKOFF)+1} attempts: {last_exc}"
            ) from last_exc
        raise QuotaError(
            f"Quota/rate-limit after {len(_BACKOFF)+1} attempts: {last_exc}"
        ) from last_exc

    def _post(self, messages: list[dict], tools: list[dict] | None) -> dict:
        body = {"model": self.current_model, "messages": messages}
        if tools:
            body["tools"] = tools
        try:
            resp = _requests.post(
                f"{self.api_base}/chat/completions",
                json=body,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=(10, 120),   # (connect_timeout, read_timeout) — spec §3.7
            )
        except _requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {e}") from e
        if resp.status_code == 401:
            raise AuthError(f"401 Unauthorized: {resp.text[:500]}")
        if resp.status_code in (402, 429) or "insufficient_quota" in resp.text.lower():
            raise QuotaError(f"HTTP {resp.status_code}: {resp.text[:500]}")
        # Permanent client errors (wrong model name, bad request, etc.) — no retry.
        if resp.status_code in (400, 403, 404, 405, 422):
            raise AuthError(f"Permanent HTTP {resp.status_code}: {resp.text[:500]}")
        if resp.status_code >= 400:
            # 5xx and remaining 4xx are transient — NetworkError so we retry.
            raise NetworkError(f"HTTP {resp.status_code}: {resp.text[:500]}")
        try:
            data = resp.json()
        except Exception as e:
            # Server returned 200 but non-JSON body (can happen during outages).
            raise NetworkError(f"Non-JSON response: {resp.text[:200]}") from e
        # OpenRouter returns HTTP 200 with {"error": {"code": ..., "message": ...}}
        # for upstream rate-limit and model-unavailable errors — not a 4xx.
        if isinstance(data.get("error"), dict):
            err = data["error"]
            code = err.get("code", 0)
            msg = err.get("message", str(err))[:500]
            # code 429 or any "rate" string → quota; everything else → transient
            if code == 429 or "rate" in str(code).lower() or "rate" in msg.lower():
                raise QuotaError(f"OpenRouter 200-error (rate limit): {msg}")
            raise NetworkError(f"OpenRouter 200-error (code={code}): {msg}")
        return data
