"""Unit tests for tools/migrate-proof-root.py (walk-up migration)."""
import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "tools" / "migrate-proof-root.py"

_spec = importlib.util.spec_from_file_location("migrate_proof_root", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
migrate = _mod.migrate
CANONICAL_MARKER = _mod.CANONICAL_MARKER
REPO_ROOT_ALIAS = _mod.REPO_ROOT_ALIAS


VARIANT_A = '''\
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date
'''

VARIANT_D = '''\
import os
import sys

# Path to proof-engine scripts — relative to docs/examples/<name>/proof.py
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PROOF_ENGINE_ROOT = os.path.join(_REPO_ROOT, "proof-engine", "skills", "proof-engine")
sys.path.insert(0, PROOF_ENGINE_ROOT)

version = open(os.path.join(_REPO_ROOT, "VERSION")).read().strip()
'''

VARIANT_C = '''\
import os
import sys

# Find repo root by walking up from this file until we find VERSION
_here = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = _here
for _ in range(10):
    if os.path.isfile(os.path.join(_REPO_ROOT, "VERSION")):
        break
    _REPO_ROOT = os.path.dirname(_REPO_ROOT)
PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)

version = open(os.path.join(_REPO_ROOT, "VERSION")).read().strip()
'''


def _run(tmp_path, src):
    p = tmp_path / "proof.py"
    p.write_text(src)
    new_text, _, status, _ = migrate(p)
    return new_text, status


def test_variant_a_patched(tmp_path):
    new_text, status = _run(tmp_path, VARIANT_A)
    assert status == "patched"
    assert CANONICAL_MARKER in new_text
    assert "/Users/yaniv/" not in new_text
    assert REPO_ROOT_ALIAS not in new_text  # no _REPO_ROOT used downstream


def test_variant_d_patched_with_alias(tmp_path):
    new_text, status = _run(tmp_path, VARIANT_D)
    assert status == "patched"
    assert CANONICAL_MARKER in new_text
    assert REPO_ROOT_ALIAS in new_text  # _REPO_ROOT read downstream for VERSION
    # The prefix dirname^4 line should be gone
    assert "os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))" not in new_text


def test_variant_c_patched_with_alias(tmp_path):
    new_text, status = _run(tmp_path, VARIANT_C)
    assert status == "patched"
    assert CANONICAL_MARKER in new_text
    assert REPO_ROOT_ALIAS in new_text
    assert "_here" not in new_text  # the whole loop is gone
    assert "for _ in range(10):" not in new_text


def test_already_canonical_skipped(tmp_path):
    src = VARIANT_A.replace(
        'PROOF_ENGINE_ROOT = os.environ.get(\n    "PROOF_ENGINE_ROOT",\n    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",\n)',
        'PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")\nif not PROOF_ENGINE_ROOT:\n    _d = os.path.dirname(os.path.abspath(__file__))\n    while _d != os.path.dirname(_d):\n        if os.path.isdir(os.path.join(_d, "proof-engine", "skills", "proof-engine", "scripts")):\n            PROOF_ENGINE_ROOT = os.path.join(_d, "proof-engine", "skills", "proof-engine")\n            break\n        _d = os.path.dirname(_d)\n    if not PROOF_ENGINE_ROOT:\n        raise RuntimeError("PROOF_ENGINE_ROOT not set and skill dir not found via walk-up from proof.py")',
    )
    new_text, status = _run(tmp_path, src)
    assert status == "already"
    assert new_text == src


def test_idempotent(tmp_path):
    """Running twice yields same output as running once."""
    p = tmp_path / "proof.py"
    p.write_text(VARIANT_A)
    once, _, _, _ = migrate(p)
    p.write_text(once)
    twice, _, status, _ = migrate(p)
    assert status == "already"
    assert once == twice


def test_preserves_code_after_block(tmp_path):
    new_text, _ = _run(tmp_path, VARIANT_A)
    assert "from datetime import date" in new_text
