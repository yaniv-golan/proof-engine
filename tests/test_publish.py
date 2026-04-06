import json
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch
from tools.lib.publish import (
    check_required_artifacts,
    validate_thumbnail,
    stage_proof,
    finalize_proof,
    REQUIRED_ARTIFACTS,
    OPTIONAL_ARTIFACTS,
)


@pytest.fixture
def source_dir(tmp_path):
    """Create a source dir with all required artifacts."""
    src = tmp_path / "source"
    src.mkdir()
    (src / "proof.py").write_text("# proof\nprint('hello')")
    (src / "proof.md").write_text("# Proof\n\n## Key Findings\n\n- X\n")
    (src / "proof_audit.md").write_text("# Audit\n")
    (src / "proof_narrative.md").write_text(
        "# Proof Narrative: Test claim\n\n"
        "## Verdict\n\n**Verdict: PROVED**\n\n"
        "Yes — confirmed beyond doubt in every way. "
        "The evidence is overwhelming and consistent across every source examined.\n\n"
        "## What was claimed?\n\n"
        "Test claim states something is true. It matters for testing "
        "and has real consequences for how we understand validity. "
        "Getting this right affects downstream decisions.\n\n"
        "## What did we find?\n\n"
        "We found strong evidence. Multiple sources confirmed the claim "
        "from different angles and methodologies. "
        "The data was consistent across all measurements taken "
        "over the full range of conditions tested. "
        "No contradictory evidence was found in any source. "
        "The primary computation matched theoretical predictions within tight tolerance. "
        "Secondary verification through independent calculation confirmed the same figure. "
        "Cross-referencing against published reference data showed agreement within one percent. "
        "Statistical significance exceeds conventional thresholds by a wide margin. "
        "Adversarial scenarios designed to break the conclusion all failed.\n\n"
        "## What should you keep in mind?\n\n"
        "This is a test claim with limited scope. "
        "Different framings might yield different results. "
        "The methodology is optimized for quantitative claims.\n\n"
        "## How was this verified?\n\n"
        "Verified through computation. "
        "See [the structured proof report](proof.md), "
        "[the full verification audit](proof_audit.md), "
        "or [re-run the proof yourself](proof.py).\n"
    )
    (src / "proof.json").write_text(json.dumps({
        "claim_natural": "Test claim",
        "verdict": "PROVED",
        "fact_registry": {},
        "claim_formal": {},
        "key_results": {},
        "generator": {
            "name": "proof-engine",
            "version": "1.0.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-03-30",
        },
    }))
    return src


def test_check_required_artifacts_all_present(source_dir):
    errors = check_required_artifacts(source_dir)
    assert errors == []


def test_check_required_artifacts_missing_proof_md(source_dir):
    (source_dir / "proof.md").unlink()
    errors = check_required_artifacts(source_dir)
    assert any("proof.md" in e for e in errors)


def test_check_required_artifacts_missing_multiple(source_dir):
    (source_dir / "proof.md").unlink()
    (source_dir / "proof_audit.md").unlink()
    errors = check_required_artifacts(source_dir)
    assert len(errors) == 2


def test_check_required_artifacts_missing_narrative(source_dir):
    (source_dir / "proof_narrative.md").unlink()
    errors = check_required_artifacts(source_dir)
    assert any("proof_narrative.md" in e for e in errors)


def test_validate_thumbnail_correct_size(tmp_path):
    from PIL import Image
    img = Image.new("RGB", (240, 240), "red")
    path = tmp_path / "thumbnail.png"
    img.save(path)
    assert validate_thumbnail(path) is None


def test_validate_thumbnail_wrong_size(tmp_path):
    from PIL import Image
    img = Image.new("RGB", (500, 300), "red")
    path = tmp_path / "thumbnail.png"
    img.save(path)
    error = validate_thumbnail(path)
    assert "240x240" in error


def test_stage_proof_copies_required(source_dir):
    staging = stage_proof(source_dir)
    try:
        assert (Path(staging) / "proof.py").exists()
        assert (Path(staging) / "proof.md").exists()
        assert (Path(staging) / "proof_audit.md").exists()
        assert (Path(staging) / "proof.json").exists()
    finally:
        shutil.rmtree(staging)


def test_stage_proof_copies_optional(source_dir):
    from PIL import Image
    img = Image.new("RGB", (240, 240), "red")
    img.save(source_dir / "thumbnail.png")
    staging = stage_proof(source_dir)
    try:
        assert (Path(staging) / "thumbnail.png").exists()
    finally:
        shutil.rmtree(staging)


def test_stage_proof_skips_extra_files(source_dir):
    (source_dir / "random.txt").write_text("junk")
    staging = stage_proof(source_dir)
    try:
        assert not (Path(staging) / "random.txt").exists()
    finally:
        shutil.rmtree(staging)


def test_finalize_proof_moves_to_target(source_dir, tmp_path):
    staging = stage_proof(source_dir)
    target = tmp_path / "site" / "proofs" / "test-claim"
    finalize_proof(staging, target)
    assert (target / "proof.py").exists()
    assert not Path(staging).exists()


def test_finalize_force_replaces_existing(source_dir, tmp_path):
    target = tmp_path / "site" / "proofs" / "test-claim"
    target.mkdir(parents=True)
    (target / "proof.py").write_text("old")
    (target / "old-file.txt").write_text("should be removed")
    staging = stage_proof(source_dir)
    finalize_proof(staging, target, force=True)
    assert (target / "proof.py").read_text() != "old"
    assert not (target / "old-file.txt").exists()
