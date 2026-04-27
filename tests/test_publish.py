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


def test_stage_proof_copies_doi_json(source_dir):
    """doi.json should be staged as an optional artifact."""
    (source_dir / "doi.json").write_text(json.dumps({
        "doi": "10.5281/zenodo.123",
        "zenodo_id": "123",
        "concept_doi": "10.5281/zenodo.100",
        "concept_zenodo_id": "100",
        "claim_natural": "Test claim",
        "minted_at": "2026-04-07",
    }))
    staging = stage_proof(source_dir)
    try:
        assert (Path(staging) / "doi.json").exists()
    finally:
        shutil.rmtree(staging)


def test_finalize_force_preserves_doi_json(source_dir, tmp_path):
    """When force-replacing, doi.json from existing proof is preserved if claim matches."""
    target = tmp_path / "site" / "proofs" / "test-claim"
    target.mkdir(parents=True)
    (target / "proof.py").write_text("old")
    (target / "proof.json").write_text(json.dumps({"claim_natural": "Test claim"}))
    (target / "doi.json").write_text(json.dumps({
        "doi": "10.5281/zenodo.123",
        "zenodo_id": "123",
        "concept_doi": "10.5281/zenodo.100",
        "concept_zenodo_id": "100",
        "claim_natural": "Test claim",
        "minted_at": "2026-04-07",
    }))
    staging = stage_proof(source_dir)
    finalize_proof(staging, target, force=True)
    assert (target / "doi.json").exists()
    doi = json.loads((target / "doi.json").read_text())
    assert doi["doi"] == "10.5281/zenodo.123"


def test_finalize_force_rejects_doi_claim_mismatch(source_dir, tmp_path):
    """When force-replacing, doi.json is NOT preserved if claim_natural differs."""
    target = tmp_path / "site" / "proofs" / "test-claim"
    target.mkdir(parents=True)
    (target / "proof.py").write_text("old")
    (target / "proof.json").write_text(json.dumps({"claim_natural": "Different claim entirely"}))
    (target / "doi.json").write_text(json.dumps({
        "doi": "10.5281/zenodo.123",
        "zenodo_id": "123",
        "concept_doi": "10.5281/zenodo.100",
        "concept_zenodo_id": "100",
        "claim_natural": "Different claim entirely",
        "minted_at": "2026-04-07",
    }))
    staging = stage_proof(source_dir)
    # The incoming proof has claim_natural "Test claim" (from fixture's proof.json)
    # The existing doi.json has claim_natural "Different claim entirely"
    with pytest.raises(ValueError, match="DOI was minted for a different claim"):
        finalize_proof(staging, target, force=True)


def test_finalize_force_no_doi_json_works(source_dir, tmp_path):
    """Force-replace works fine when there's no existing doi.json."""
    target = tmp_path / "site" / "proofs" / "test-claim"
    target.mkdir(parents=True)
    (target / "proof.py").write_text("old")
    staging = stage_proof(source_dir)
    finalize_proof(staging, target, force=True)
    assert (target / "proof.py").exists()
    assert not (target / "doi.json").exists()


def test_finalize_force_whitespace_drift_passes(source_dir, tmp_path):
    """DOI claim with only whitespace difference should NOT raise ValueError."""
    target = tmp_path / "site" / "proofs" / "test-claim"
    target.mkdir(parents=True)
    (target / "proof.py").write_text("old")
    (target / "proof.json").write_text(json.dumps({"claim_natural": "Test claim"}))
    (target / "doi.json").write_text(json.dumps({
        "doi": "10.5281/zenodo.123",
        "zenodo_id": "123",
        "concept_doi": "10.5281/zenodo.100",
        "concept_zenodo_id": "100",
        "claim_natural": "Test  claim",   # extra space — whitespace-only drift
        "minted_at": "2026-04-07",
    }))
    staging = stage_proof(source_dir)
    # Should NOT raise — whitespace-only drift is allowed
    finalize_proof(staging, target, force=True)
    assert (target / "doi.json").exists()


def test_finalize_force_real_drift_raises(source_dir, tmp_path):
    """A genuinely different DOI claim must raise ValueError — not silently overwritten."""
    target = tmp_path / "site" / "proofs" / "test-claim"
    target.mkdir(parents=True)
    (target / "proof.py").write_text("old")
    (target / "proof.json").write_text(json.dumps({"claim_natural": "Test claim"}))
    (target / "doi.json").write_text(json.dumps({
        "doi": "10.5281/zenodo.999",
        "zenodo_id": "999",
        "concept_doi": "10.5281/zenodo.100",
        "concept_zenodo_id": "100",
        "claim_natural": "An entirely different claim",
        "minted_at": "2026-04-07",
    }))
    staging = stage_proof(source_dir)
    with pytest.raises(ValueError, match="DOI was minted for a different claim"):
        finalize_proof(staging, target, force=True)
