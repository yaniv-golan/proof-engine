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
