"""Staging, validation, and finalization for proof publishing."""

import json
import shutil
import tempfile
from pathlib import Path

REQUIRED_ARTIFACTS = ["proof.py", "proof.md", "proof_audit.md"]
OPTIONAL_ARTIFACTS = ["proof.json", "thumbnail.png", "meta.yaml"]


def check_required_artifacts(source_dir: Path) -> list[str]:
    """Check that all required artifacts exist in source_dir.

    Returns list of error messages (empty = all present).
    """
    errors = []
    for name in REQUIRED_ARTIFACTS:
        if not (Path(source_dir) / name).exists():
            errors.append(f"Missing required artifact: {name}")
    return errors


def validate_thumbnail(thumbnail_path: Path) -> str | None:
    """Validate thumbnail is exactly 240x240. Returns error message or None."""
    from PIL import Image
    with Image.open(thumbnail_path) as img:
        if img.size != (240, 240):
            return (
                f"Thumbnail must be exactly 240x240 pixels, "
                f"got {img.size[0]}x{img.size[1]}"
            )
    return None


def stage_proof(source_dir: Path, proofs_dir: Path | None = None) -> str:
    """Copy proof artifacts to a temporary staging directory.

    Only copies known artifacts (required + optional). Extra files are ignored.
    If proofs_dir is provided, stages under proofs_dir's parent to ensure
    same-filesystem moves (required for atomic rename in finalize_proof).
    Returns the path to the staging directory.
    """
    source_dir = Path(source_dir)
    if proofs_dir is not None:
        staging_parent = Path(proofs_dir).parent
        staging_parent.mkdir(parents=True, exist_ok=True)
        staging = tempfile.mkdtemp(prefix=".proof-staging-", dir=str(staging_parent))
    else:
        staging = tempfile.mkdtemp(prefix="proof-site-staging-")
    staging_path = Path(staging)

    for name in REQUIRED_ARTIFACTS + OPTIONAL_ARTIFACTS:
        src = source_dir / name
        if src.exists():
            shutil.copy2(src, staging_path / name)

    return staging


def finalize_proof(staging_dir: str, target_dir: Path, force: bool = False) -> None:
    """Move staged proof to its final location.

    If force=True and target exists, uses atomic swap: rename old to backup,
    move new into place, then delete backup. If the move fails, the backup
    is renamed back so the old proof is preserved.
    Raises FileExistsError if target exists and force=False.
    """
    target_dir = Path(target_dir)
    staging_path = Path(staging_dir)

    target_dir.parent.mkdir(parents=True, exist_ok=True)

    if target_dir.exists():
        if not force:
            raise FileExistsError(f"Target already exists: {target_dir}")
        backup_dir = target_dir.with_name("." + target_dir.name + ".backup")
        target_dir.rename(backup_dir)
        try:
            shutil.move(str(staging_path), str(target_dir))
        except Exception:
            backup_dir.rename(target_dir)
            raise
        shutil.rmtree(backup_dir)
    else:
        shutil.move(str(staging_path), str(target_dir))
