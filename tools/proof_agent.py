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
