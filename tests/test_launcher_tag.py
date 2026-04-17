"""Pin the launcher-tag derivation to VERSION so any drift between the
proof-site module and VERSION is caught by CI.

These tests are intentionally version-agnostic: they read VERSION at test time
and assert the module agrees. This means they pass both before and after the
Task 15 version bump — the derivation is what matters, not the specific value.
"""
import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_proof_site():
    """Return the tools.proof_site module, reusing a cached instance if present.

    test_mint_doi.py registers "tools.proof_site" at import time so its @patch
    decorators resolve. Re-registering here would create a second module object
    whose globals diverge from the @patch target, causing test-order pollution.
    """
    if "tools.proof_site" in sys.modules:
        return sys.modules["tools.proof_site"]
    spec = importlib.util.spec_from_file_location(
        "tools.proof_site",
        REPO_ROOT / "tools" / "proof-site.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["tools.proof_site"] = module
    spec.loader.exec_module(module)
    return module


def test_launcher_tag_matches_version_minor():
    proof_site = _load_proof_site()
    version = (REPO_ROOT / "VERSION").read_text().strip()
    major, minor, _patch = version.split(".")
    expected = f"v{major}.{minor}.0"
    assert proof_site.BINDER_LAUNCHER_TAG == expected, (
        f"BINDER_LAUNCHER_TAG={proof_site.BINDER_LAUNCHER_TAG!r} but VERSION={version!r} "
        f"implies launcher tag {expected!r}. "
        "Run tools/bump-version.sh instead of editing VERSION by hand."
    )


def test_launcher_tag_form():
    proof_site = _load_proof_site()
    assert re.fullmatch(r"v\d+\.\d+\.0", proof_site.BINDER_LAUNCHER_TAG), (
        f"Launcher tag must be v<MAJOR>.<MINOR>.0 (patch always 0); "
        f"got {proof_site.BINDER_LAUNCHER_TAG!r}."
    )
