"""Shared constants for the Binder launcher integration.

Lives in its own module so that both ``tools/proof-site.py`` (DOI-mode
minting) and ``tools/build-site.py`` (slug-mode rendering) can import
them without a cross-script import — ``proof-site.py`` has a hyphen in
its filename and is not importable as a Python module.
"""
from pathlib import Path


# Binder launcher repo. Pinned per (MAJOR, MINOR) of the main proof-engine
# version — each launcher tag maps 1:1 to a proof-engine minor release.
BINDER_LAUNCHER_REPO = "yaniv-golan/proof-engine-binder"


def _launcher_tag_from_version() -> str:
    """Derive the immutable launcher tag from VERSION.

    Patch bumps within a minor (e.g. 1.22.0 → 1.22.1) keep the launcher tag
    fixed at v<MAJOR>.<MINOR>.0 — within a minor, only one launcher image
    ever exists. Minor bumps (1.21.x → 1.22.0) move the tag automatically.
    """
    # This file is tools/lib/binder_config.py → repo root is two parents up.
    version_path = Path(__file__).resolve().parent.parent.parent / "VERSION"
    version = version_path.read_text().strip()
    major, minor, _patch = version.split(".")
    return f"v{major}.{minor}.0"


BINDER_LAUNCHER_TAG = _launcher_tag_from_version()
