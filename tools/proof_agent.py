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
        if self._total_attempts >= self.max_llm_calls:
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


# ---------------------------------------------------------------------------
# Tool definitions (OpenAI function-call format)
# ---------------------------------------------------------------------------

def _canon(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def canonical_display(v) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    base = v.get("value", "")
    if v.get("qualified") and v.get("qualifier") == "unverified_citations":
        return f"{base} (with unverified citations)"
    return base


TOOLS = [
    {"type": "function", "function": {
        "name": "read_skill_file",
        "description": "Read a file from the skill directory (SKILL.md, scripts/, references/). Read-only.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Relative path within the skill directory"}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a file from the output directory.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "read_old_proof_file",
        "description": "Read a file from the old proof directory (scaffold). Returns error if not available.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "write_file",
        "description": "Write a file to the output directory. Allowed: proof.py, proof.md, proof_audit.md, proof_narrative.md, proof.json, notes.md.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"]}}},
    {"type": "function", "function": {
        "name": "list_dir",
        "description": "List files in a directory under the output directory.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "default": "."}}, "required": []}}},
    {"type": "function", "function": {
        "name": "run_bash",
        "description": (
            "Run a shell command. LIMITATIONS: shell=False, no pipes/redirection/globs/env-var-expansion/$(...). "
            "One command per call. For multi-step work, write a helper script and run it. "
            "Use timeout=300 for validate_proof.py."
        ),
        "parameters": {"type": "object", "properties": {
            "cmd": {"type": "string"},
            "timeout": {"type": "integer", "default": 120}}, "required": ["cmd"]}}},
    {"type": "function", "function": {
        "name": "run_proof_py",
        "description": "Run proof.py and return exit_code, stdout, stderr, proof_data, stripped_keys.",
        "parameters": {"type": "object", "properties": {
            "timeout": {"type": "integer", "default": 600}}, "required": []}}},
    {"type": "function", "function": {
        "name": "terminate",
        "description": "Declare proof complete. Call only when all 5 artifacts exist, run_proof_py exited 0 with matching claim, and validate_proof.py passed.",
        "parameters": {"type": "object", "properties": {
            "reason": {"type": "string"}},
            "required": ["reason"]}}},
]


def _dispatch_tool(sandbox, name: str, args: dict) -> dict:
    try:
        if name == "read_skill_file":
            return sandbox.read_skill_file(args["path"])
        if name == "read_file":
            return sandbox.read_file(args["path"])
        if name == "read_old_proof_file":
            return sandbox.read_old_proof_file(args["path"])
        if name == "write_file":
            return sandbox.write_file(args["path"], args["content"])
        if name == "list_dir":
            return sandbox.list_dir(args.get("path", "."))
        if name == "run_bash":
            return sandbox.run_bash(args.get("cmd", ""), args.get("timeout", 120))
        if name == "run_proof_py":
            return sandbox.run_proof_py(args.get("timeout", 600))
        return {"ok": False, "error": f"unknown tool: {name}"}
    except KeyError as e:
        return {"ok": False, "error": f"missing required argument: {e}"}


def _build_system_prompt(slug: str, claim: str, output_dir, skill_dir, regen_mode: bool) -> str:
    mode = (
        "**Regeneration run** — `read_old_proof_file` is available. "
        "Start by reading the old `proof.py` as a scaffold."
    ) if regen_mode else (
        "**New proof run** — `read_old_proof_file` is not available; build from scratch."
    )
    return f"""You are regenerating an existing proof under the current Proof Engine skill.

Slug: {slug}
Claim (verbatim — preserve exactly): {claim}
Output directory: {output_dir}

Mode: {mode}

Read these skill files first (in order):
1. SKILL.md
2. references/hardening-rules.md
3. references/output-specs.md (if it exists)
4. List scripts/ to see what verification scripts are available.

Required artifacts (write all five):
- proof.py, proof.md, proof_audit.md, proof_narrative.md, proof.json

Valid verdict values: PROVED, DISPROVED, SUPPORTED, PARTIALLY VERIFIED, UNDETERMINED
(plus "(with unverified citations)" qualifier).

proof.json must use the v3 verdict object shape:
  {{"value": "PROVED", "qualified": false, "qualifier": null, "reason": null}}

Termination contract — call `terminate` only when ALL hold:
1. All five files exist.
2. `run_proof_py()` returned exit_code 0 AND proof_data.claim_natural matches the claim above (after whitespace normalization).
3. `validate_proof.py` passes — the dispatcher enforces this automatically when you call `terminate`.
   You may run it voluntarily for early feedback, but note that `run_bash` uses `shell=False`
   so `$PROOF_ENGINE_ROOT` will NOT expand. Write a helper `.sh` via `write_file` first if needed.
4. proof_data.verdict is a valid v3 verdict object.

Constraints:
- Do NOT modify claim_natural — preserve the exact string given above.
- Use $PROOF_ENGINE_ROOT env var for import paths, following the walk-up pattern in existing proofs.
- Honor all 9 hardening rules (see references/hardening-rules.md).
- `run_bash` uses shell=False. No pipes (`|`), redirection (`>`, `<`), globs (`*.py`),
  `&&`/`||` chaining, env-var expansion (`$VAR`), or command substitution `$(...)`. One command per call.
  For multi-step shell work, write a helper script via write_file then run it.
- Pass timeout=300 to run_bash when running validate_proof.py or heavy computations.
"""


_REQUIRED_ARTIFACTS = ("proof.py", "proof.md", "proof_audit.md", "proof_narrative.md", "proof.json")
_VALID_VERDICTS = {"PROVED", "DISPROVED", "SUPPORTED", "PARTIALLY VERIFIED", "UNDETERMINED"}


def _check_terminate(sandbox, claim: str, all_stripped: list) -> tuple:
    """Check termination preconditions.

    Returns (rejection_dict, run_result).
    - rejection_dict is non-None if any precondition failed.
    - run_result is the run_proof_py() result (for stripped_keys accumulation).
    """
    if not _canon(claim):
        return {"ok": False, "error": "claim argument is empty"}, None

    missing = [a for a in _REQUIRED_ARTIFACTS
               if not (sandbox.output_dir / a).exists()]
    if missing:
        return {"ok": False, "error": f"missing artifacts: {missing}"}, None

    run = sandbox.run_proof_py()
    if run.get("stripped_keys"):
        all_stripped.append(set(run["stripped_keys"]))

    if run["exit_code"] != 0:
        cause = run.get("error") or run.get("stderr", "")[:300]
        return (
            {"ok": False, "error": f"run_proof_py failed (exit {run['exit_code']}): {cause}"},
            run,
        )

    pd = run.get("proof_data") or {}
    cn = pd.get("claim_natural")
    if not isinstance(cn, str):
        return (
            {"ok": False,
             "error": f"claim_natural is missing or not a string (got {type(cn).__name__})"},
            run,
        )
    if _canon(cn) != _canon(claim):
        return (
            {"ok": False, "error": f"claim mismatch: proof has {cn!r}"},
            run,
        )

    v = pd.get("verdict")
    if not isinstance(v, dict):
        return (
            {"ok": False,
             "error": f"verdict must be a v3 dict (e.g. {{\"value\":\"PROVED\",\"qualified\":false,\"qualifier\":null,\"reason\":null}}), got {type(v).__name__}"},
            run,
        )
    base = v.get("value", "")
    if base not in _VALID_VERDICTS:
        return {"ok": False, "error": f"invalid verdict value: {base!r}"}, run
    if not isinstance(v.get("qualified"), bool):
        return {"ok": False, "error": f"verdict.qualified must be bool, got {v.get('qualified')!r}"}, run
    if v.get("qualifier") is not None and not isinstance(v.get("qualifier"), str):
        return {"ok": False, "error": f"verdict.qualifier must be str or null, got {v.get('qualifier')!r}"}, run
    _VALID_QUALIFIERS = {None, "unverified_citations"}
    if v.get("qualifier") not in _VALID_QUALIFIERS:
        return {"ok": False, "error": f"verdict.qualifier must be null or 'unverified_citations', got {v.get('qualifier')!r}"}, run
    if v.get("reason") is not None and not isinstance(v.get("reason"), str):
        return {"ok": False, "error": f"verdict.reason must be str or null, got {v.get('reason')!r}"}, run

    skill_dir_q = shlex.quote(str(sandbox.skill_dir))
    val = sandbox.run_bash(
        f"python {skill_dir_q}/scripts/validate_proof.py proof.py",
        timeout=300,
    )
    if val["exit_code"] != 0:
        if val.get("error") == "timeout":
            cause = "validate_proof.py timed out after 300s"
        else:
            cause = (val.get("stdout") or val.get("stderr") or "")[:300]
        return (
            {"ok": False, "error": f"validate_proof.py failed: {cause}"},
            run,
        )

    return None, run


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_agent(slug: str, claim: str, output_dir, skill_dir,
              model: str, fallback_model: str, api_key: str,
              api_base: str = _OPENROUTER_BASE,
              max_iterations: int = 80, max_llm_calls: int = 150,
              old_proof_dir=None,
              transcript_path=None) -> AgentResult:
    result = AgentResult(slug=slug, claim=claim, status="ok",
                         started_at=_now_iso())
    output_dir = Path(output_dir)
    skill_dir = Path(skill_dir)
    sandbox = Sandbox(output_dir=output_dir, skill_dir=skill_dir,
                      old_proof_dir=old_proof_dir)
    client = OpenRouterClient(api_key=api_key, model=model,
                              fallback_model=fallback_model,
                              api_base=api_base, max_llm_calls=max_llm_calls)
    system_prompt = _build_system_prompt(slug, claim, output_dir, skill_dir,
                                         regen_mode=old_proof_dir is not None)
    messages = [{"role": "system", "content": system_prompt}]
    all_stripped: list = []
    transcript: list = []

    def _record(entry: dict) -> None:
        transcript.append(entry)

    try:
        for iteration in range(max_iterations):
            result.iterations = iteration + 1
            try:
                resp = client.chat(messages, tools=TOOLS)
            except AuthError as e:
                result.status = "auth_error"
                result.error = str(e)
                result.model_used = client.current_model
                result.fallback_triggered = client._using_fallback
                _try_populate_result(result, output_dir, all_stripped)
                return result
            except QuotaError as e:
                if isinstance(e, CapError):
                    result.status = "quota_blocked"
                elif client._using_fallback:
                    result.status = "llm_error"
                else:
                    result.status = "quota_blocked"
                result.error = str(e)
                result.model_used = client.current_model
                result.fallback_triggered = client._using_fallback
                _try_populate_result(result, output_dir, all_stripped)
                return result
            except NetworkError as e:
                result.status = "llm_error"
                result.error = str(e)
                result.model_used = client.current_model
                result.fallback_triggered = client._using_fallback
                _try_populate_result(result, output_dir, all_stripped)
                return result

            result.model_used = client.current_model
            result.fallback_triggered = client._using_fallback

            choices = resp.get("choices") or []
            if not choices:
                result.status = "llm_error"
                result.error = f"LLM returned empty choices: {str(resp)[:200]}"
                _try_populate_result(result, output_dir, all_stripped)
                return result
            choice = choices[0]
            msg = choice.get("message")
            if not isinstance(msg, dict):
                result.status = "llm_error"
                result.error = f"LLM choice missing 'message' dict: {str(choice)[:200]}"
                _try_populate_result(result, output_dir, all_stripped)
                return result
            messages.append(msg)
            _record({"role": "assistant", "content": msg.get("content"),
                     "tool_calls": msg.get("tool_calls", []), "iteration": iteration})

            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                continue

            tool_results = []
            terminate_requested = False

            for tc in tool_calls:
                tc_id = tc.get("id", "unknown")
                fn = tc.get("function")
                if not isinstance(fn, dict) or not fn.get("name"):
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc_id,
                        "content": json.dumps({"ok": False,
                                               "error": f"malformed tool_call entry: {str(tc)[:200]}"}),
                    })
                    _record({"role": "tool", "tool_call_id": tc_id,
                             "error": "malformed tool_call entry"})
                    continue
                name = fn["name"]
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}

                if not isinstance(args, dict):
                    args = {}

                if name == "terminate":
                    rejection, _ = _check_terminate(sandbox, claim, all_stripped)
                    if rejection:
                        tool_result = rejection
                    else:
                        terminate_requested = True
                        tool_result = {"ok": True, "message": "Termination accepted."}
                elif name == "run_proof_py":
                    tool_result = _dispatch_tool(sandbox, name, args)
                    if tool_result.get("stripped_keys"):
                        all_stripped.append(set(tool_result["stripped_keys"]))
                else:
                    tool_result = _dispatch_tool(sandbox, name, args)

                _record({"role": "tool", "tool_call_id": tc_id,
                          "name": name, "result": tool_result})
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": json.dumps(tool_result),
                })

            messages.extend(tool_results)

            if terminate_requested:
                try:
                    pd = json.loads((output_dir / "proof.json").read_text())
                    result.verdict = canonical_display(pd.get("verdict", ""))
                    result.claim_natural_in_proof = pd.get("claim_natural")
                    result.proof_json_written = True
                    result.artifacts_written = [
                        a for a in _REQUIRED_ARTIFACTS if (output_dir / a).exists()
                    ]
                except Exception:
                    pass
                result.stripped_proof_json_keys = sorted(set().union(*all_stripped)) if all_stripped else []
                result.status = "ok"
                return result

        result.status = "gave_up"
        result.error = f"max iterations ({max_iterations}) reached without terminate"
        _try_populate_result(result, output_dir, all_stripped)
        return result

    finally:
        result.ended_at = _now_iso()
        if transcript_path:
            transcript_path = Path(transcript_path)
            transcript_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                transcript_path.write_text(
                    "\n".join(json.dumps(e) for e in transcript) + "\n"
                )
            except Exception:
                pass


def _try_populate_result(result, output_dir, all_stripped: list) -> None:
    """Populate result best-effort from any artifacts on disk."""
    output_dir = Path(output_dir)
    try:
        pd = json.loads((output_dir / "proof.json").read_text())
        result.verdict = canonical_display(pd.get("verdict", ""))
        result.claim_natural_in_proof = pd.get("claim_natural")
        result.proof_json_written = True
    except Exception:
        pass
    result.artifacts_written = [
        a for a in _REQUIRED_ARTIFACTS if (output_dir / a).exists()
    ]
    result.stripped_proof_json_keys = sorted(set().union(*all_stripped)) if all_stripped else []
    if result.status == "gave_up" and not result.artifacts_written:
        result.status = "invalid_output"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Proof regeneration agent")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--claim", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skill-dir", type=Path, required=True)
    parser.add_argument("--model", default="qwen/qwen3-coder:free")
    parser.add_argument("--fallback-model", default="openai/gpt-oss-120b:free")
    parser.add_argument("--max-iterations", type=int, default=80)
    parser.add_argument("--max-llm-calls", type=int, default=150)
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--result-json", type=Path)
    parser.add_argument("--old-proof-dir", type=Path)
    parser.add_argument("--api-base", default=_OPENROUTER_BASE)
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    args = parser.parse_args()

    _api_key = os.environ.pop(args.api_key_env, None)
    if not _api_key:
        print(f"ERROR: env var {args.api_key_env!r} is not set", file=sys.stderr)
        return 2

    if not args.claim.strip():
        print("ERROR: --claim must be a non-empty string", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)

    result = run_agent(
        slug=args.slug,
        claim=args.claim,
        output_dir=args.output_dir,
        skill_dir=args.skill_dir,
        model=args.model,
        fallback_model=args.fallback_model,
        api_key=_api_key,
        api_base=args.api_base,
        max_iterations=args.max_iterations,
        max_llm_calls=args.max_llm_calls,
        old_proof_dir=args.old_proof_dir,
        transcript_path=args.transcript,
    )

    if args.result_json:
        args.result_json.parent.mkdir(parents=True, exist_ok=True)
        args.result_json.write_text(json.dumps(asdict(result), indent=2))

    status_exit = {
        "ok": 0,
        "gave_up": 3,
        "invalid_output": 4,
        "llm_error": 2,
        "quota_blocked": 2,
        "auth_error": 2,
    }
    return status_exit.get(result.status, 1)


if __name__ == "__main__":
    sys.exit(main())
