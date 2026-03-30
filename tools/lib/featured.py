"""Read/write/validate site/proofs/featured.json."""

import json
import os
import tempfile
from pathlib import Path

FEATURED_FILENAME = "featured.json"


def load_featured_slugs(proofs_dir: Path) -> set[str]:
    """Load featured slugs from featured.json in proofs_dir.

    Returns empty set if file doesn't exist.
    Raises ValueError on invalid JSON, non-array, duplicates, or dangling refs.
    """
    featured_path = Path(proofs_dir) / FEATURED_FILENAME
    if not featured_path.exists():
        return set()

    try:
        data = json.loads(featured_path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"featured.json is not valid JSON: {e}")

    if not isinstance(data, list):
        raise ValueError("featured.json must be a JSON array of strings")

    for item in data:
        if not isinstance(item, str):
            raise ValueError(f"featured.json entries must be strings, got: {type(item).__name__}")

    # Check for duplicates
    seen = set()
    for slug in data:
        if slug in seen:
            raise ValueError(f"featured.json contains duplicate slug: {slug}")
        seen.add(slug)

    # Check for dangling refs
    for slug in data:
        slug_dir = Path(proofs_dir) / slug
        if not slug_dir.is_dir() or not (slug_dir / "proof.json").exists():
            raise ValueError(
                f"featured.json references non-loadable proof: {slug} "
                f"(directory or proof.json missing)"
            )

    return set(data)


def save_featured_slugs(proofs_dir: Path, slugs: set[str]) -> None:
    """Write featured slugs to featured.json using atomic write.

    Validates all slugs are loadable, writes to temp file, validates
    the written content, then atomically renames over the target.
    Raises ValueError if any slug doesn't have a corresponding proof directory.
    """
    proofs_dir = Path(proofs_dir)
    # Validate all slugs exist
    for slug in slugs:
        slug_dir = proofs_dir / slug
        if not slug_dir.is_dir() or not (slug_dir / "proof.json").exists():
            raise ValueError(
                f"Cannot feature non-loadable proof: {slug} "
                f"(directory or proof.json missing)"
            )

    featured_path = proofs_dir / FEATURED_FILENAME
    sorted_slugs = sorted(slugs)
    content = json.dumps(sorted_slugs, indent=2) + "\n"

    # Atomic write: temp file + rename
    fd, tmp_path = tempfile.mkstemp(
        dir=str(proofs_dir), prefix=".featured-", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        # Validate the written file is parseable
        roundtrip = json.loads(Path(tmp_path).read_text())
        assert isinstance(roundtrip, list)
        Path(tmp_path).rename(featured_path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


def validate_featured(proofs_dir: Path) -> list[str]:
    """Validate featured.json and return list of error messages (empty = valid)."""
    errors = []
    featured_path = Path(proofs_dir) / FEATURED_FILENAME
    if not featured_path.exists():
        return errors

    try:
        data = json.loads(featured_path.read_text())
    except json.JSONDecodeError as e:
        return [f"featured.json is not valid JSON: {e}"]

    if not isinstance(data, list):
        return ["featured.json must be a JSON array"]

    seen = set()
    for slug in data:
        if not isinstance(slug, str):
            errors.append(f"featured.json entry is not a string: {slug}")
            continue
        if slug in seen:
            errors.append(f"featured.json contains duplicate: {slug}")
        seen.add(slug)
        slug_dir = Path(proofs_dir) / slug
        if not slug_dir.is_dir() or not (slug_dir / "proof.json").exists():
            errors.append(f"featured.json references non-loadable proof: {slug}")

    return errors
