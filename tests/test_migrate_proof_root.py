"""Unit tests for tools/migrate-proof-root.py."""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "tools" / "migrate-proof-root.py"

LEGACY = '''\
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
'''

MIGRATED = '''\
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)
'''


def run(tmp_path: Path) -> str:
    proof = tmp_path / "proof.py"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(proof)],
        capture_output=True, text=True, check=True,
    )
    return proof.read_text()


def test_rewrites_legacy(tmp_path):
    (tmp_path / "proof.py").write_text(LEGACY)
    assert run(tmp_path) == MIGRATED


def test_idempotent_on_migrated(tmp_path):
    (tmp_path / "proof.py").write_text(MIGRATED)
    assert run(tmp_path) == MIGRATED


def test_leaves_nonmatching_untouched(tmp_path):
    unrelated = "print('hello')\n"
    (tmp_path / "proof.py").write_text(unrelated)
    assert run(tmp_path) == unrelated


LEGACY_JOIN = '''\
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PROOF_ENGINE_ROOT = os.path.join(_REPO_ROOT, "proof-engine", "skills", "proof-engine")
sys.path.insert(0, PROOF_ENGINE_ROOT)
'''

MIGRATED_FROM_JOIN = '''\
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)
'''


def test_rewrites_os_path_join_form(tmp_path):
    """Handle the 4 historical proofs using __file__-traversal via _REPO_ROOT."""
    (tmp_path / "proof.py").write_text(LEGACY_JOIN)
    assert run(tmp_path) == MIGRATED_FROM_JOIN


def test_preserves_repo_root_line(tmp_path):
    """_REPO_ROOT may be used for other lookups (e.g. VERSION); must survive."""
    (tmp_path / "proof.py").write_text(LEGACY_JOIN)
    out = run(tmp_path)
    assert "_REPO_ROOT = os.path.dirname" in out


def test_idempotent_on_join_migrated(tmp_path):
    (tmp_path / "proof.py").write_text(MIGRATED_FROM_JOIN)
    assert run(tmp_path) == MIGRATED_FROM_JOIN
