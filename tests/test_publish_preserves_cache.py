import json
from pathlib import Path
from tools.lib.publish import stage_proof, finalize_proof, OPTIONAL_ARTIFACTS


def test_depends_on_resolved_in_optional_artifacts():
    assert "depends_on_resolved.json" in OPTIONAL_ARTIFACTS


def test_force_republish_preserves_cache(tmp_path):
    live = tmp_path / "site" / "proofs" / "foo"
    live.mkdir(parents=True)
    for f in ("proof.py", "proof.md", "proof_audit.md", "proof_narrative.md"):
        (live / f).write_text("# v1")
    (live / "depends_on_resolved.json").write_text(
        json.dumps({"arxiv:x": {"identifier_type": "arxiv", "identifier_value": "x",
                                 "canonical_url": "u", "title": "t", "authors": [],
                                 "year": 2020, "venue": None, "version": None,
                                 "resolved_at": "r", "source_api": "s", "raw": {}}}, indent=2)
    )

    incoming = tmp_path / "incoming"
    incoming.mkdir()
    for f in ("proof.py", "proof.md", "proof_audit.md", "proof_narrative.md"):
        (incoming / f).write_text("# v2")

    proofs_dir = live.parent
    staging = stage_proof(incoming, proofs_dir=proofs_dir)
    finalize_proof(staging, live, force=True)

    assert (live / "depends_on_resolved.json").exists()
    data = json.loads((live / "depends_on_resolved.json").read_text())
    assert "arxiv:x" in data
