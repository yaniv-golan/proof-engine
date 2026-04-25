import json
from pathlib import Path

from proof_engine_registry.emit import emit_registry_files


FIXTURES = Path(__file__).parent / "fixtures" / "proofs"


def test_emit_creates_discovery(tmp_path):
    emit_registry_files(
        proofs_dir=FIXTURES,
        output_dir=tmp_path,
        base_url="https://example.com",
        registry_name="Test",
    )
    from proof_engine_registry import __protocol_version__
    disco = json.loads((tmp_path / ".well-known" / "proof-registry.json").read_text())
    assert disco["protocol_version"] == __protocol_version__
    assert disco["name"] == "Test"
    assert disco["proof_count"] == 1


def test_emit_creates_index(tmp_path):
    emit_registry_files(
        proofs_dir=FIXTURES,
        output_dir=tmp_path,
        base_url="https://example.com",
        registry_name="Test",
    )
    from proof_engine_registry import __protocol_version__
    index = json.loads((tmp_path / "index.json").read_text())
    assert index["protocol_version"] == __protocol_version__
    assert len(index["entries"]) == 1
    entry = index["entries"][0]
    # Slug is derived from the proof directory name.
    assert entry["slug"] == "sample-claim"
    # Claim comes from claim_natural; LaTeX is stripped to plain text.
    assert entry["claim"] == "The sky is blue."
    # Verdict string is verdict.value (unqualified fixture).
    assert entry["verdict"] == "SUPPORTED"
    assert len(entry["claim_hash"]) == 64
    # Unqualified proofs get confidence 1.0.
    assert entry["confidence"] == 1.0
    # DOI sourced from sibling doi.json.
    assert entry["doi"] == "10.5281/zenodo.9999999"


def test_emit_creates_claim_hash_lookup(tmp_path):
    emit_registry_files(
        proofs_dir=FIXTURES,
        output_dir=tmp_path,
        base_url="https://example.com",
        registry_name="Test",
    )
    claims_dir = tmp_path / "claims"
    files = list(claims_dir.glob("*.json"))
    assert len(files) == 1
    entry = json.loads(files[0].read_text())
    assert entry["slug"] == "sample-claim"
    assert files[0].stem == entry["claim_hash"]


def test_emit_creates_per_proof_file(tmp_path):
    emit_registry_files(
        proofs_dir=FIXTURES,
        output_dir=tmp_path,
        base_url="https://example.com",
        registry_name="Test",
    )
    proof_json = json.loads((tmp_path / "proofs" / "sample-claim.json").read_text())
    assert proof_json["slug"] == "sample-claim"
    # fact_ids are the evidence dict keys, sorted for determinism.
    assert proof_json["fact_ids"] == ["B1"]
    # source_urls pulls from evidence.*.source.url (the nested v3 shape).
    assert proof_json["source_urls"] == ["https://example.com/rayleigh"]


def test_emit_handles_qualified_verdict(tmp_path):
    """qualified=true → canonical 'VALUE (with humanized qualifier)' string.

    Real proofs store qualifiers with underscores (e.g., 'unverified_citations').
    The emit layer humanizes to spaces so the output string matches the
    canonical keys in tools/lib/verdict.py::VERDICT_TAXONOMY.
    """
    qualified_dir = tmp_path / "source" / "qualified-claim"
    qualified_dir.mkdir(parents=True)
    (qualified_dir / "proof.json").write_text(json.dumps({
        "format_version": 3,
        "claim_natural": "X is qualified.",
        "evidence": {"A1": {"type": "computed", "label": "x"}},
        "verdict": {
            "value": "SUPPORTED", "qualified": True,
            "qualifier": "unverified_citations", "reason": "URL unreachable",
        },
        "generator": {"name": "proof-engine", "version": "1.28.0",
                      "generated_at": "2026-04-24"},
    }))
    out = tmp_path / "out"
    emit_registry_files(
        proofs_dir=tmp_path / "source", output_dir=out,
        base_url="https://example.com", registry_name="Test",
    )
    index = json.loads((out / "index.json").read_text())
    entry = index["entries"][0]
    # Canonical form — matches VERDICT_TAXONOMY keys.
    assert entry["verdict"] == "SUPPORTED (with unverified citations)"
    # Qualified proofs get confidence 0.5.
    assert entry["confidence"] == 0.5


def test_emit_tolerates_v2_string_verdict(tmp_path):
    """Legacy v2 proofs use `verdict: "DISPROVED"` as a string.

    One such proof exists in the repo at time of writing
    (site/proofs/napoleon-bonaparte-*). Emit must not crash on it — coerce
    the string as the final verdict value with no qualifier.
    """
    d = tmp_path / "source" / "v2-proof"
    d.mkdir(parents=True)
    # Mirror the real napoleon-bonaparte proof: format_version: 2 +
    # verdict as a plain string. emit must branch on shape
    # (isinstance(verdict, str)), not on format_version.
    (d / "proof.json").write_text(json.dumps({
        "format_version": 2,
        "claim_natural": "A legacy claim.",
        "evidence": {"A1": {"type": "computed", "label": "x"}},
        "verdict": "DISPROVED",  # v2 string shape
        "generator": {"name": "proof-engine", "version": "0.1.0",
                      "generated_at": "2025-01-01"},
    }))
    out = tmp_path / "out"
    emit_registry_files(
        proofs_dir=tmp_path / "source", output_dir=out,
        base_url="https://example.com", registry_name="Test",
    )
    entry = json.loads((out / "index.json").read_text())["entries"][0]
    assert entry["verdict"] == "DISPROVED"
    assert entry["confidence"] == 1.0  # v2 string treated as unqualified


def test_emit_handles_missing_doi_file(tmp_path):
    """No doi.json → entry.doi is null."""
    d = tmp_path / "source" / "no-doi"
    d.mkdir(parents=True)
    (d / "proof.json").write_text(json.dumps({
        "format_version": 3,
        "claim_natural": "No DOI here.",
        "evidence": {"A1": {"type": "computed", "label": "x"}},
        "verdict": {"value": "PROVED", "qualified": False,
                    "qualifier": None, "reason": None},
        "generator": {"name": "proof-engine", "version": "1.28.0",
                      "generated_at": "2026-04-24"},
    }))
    out = tmp_path / "out"
    emit_registry_files(
        proofs_dir=tmp_path / "source", output_dir=out,
        base_url="https://example.com", registry_name="Test",
    )
    entry = json.loads((out / "index.json").read_text())["entries"][0]
    assert entry["doi"] is None


def test_emit_writes_badge_json_per_proof(tmp_path):
    import json
    emit_registry_files(
        proofs_dir=FIXTURES, output_dir=tmp_path,
        base_url="https://example.com", registry_name="Test",
    )
    badge = json.loads((tmp_path / "proofs" / "sample-claim" / "badge.json").read_text())
    assert badge["schema_version"] == "1.0"
    assert badge["slug"] == "sample-claim"


def test_emit_writes_badge_svg_per_proof(tmp_path):
    emit_registry_files(
        proofs_dir=FIXTURES, output_dir=tmp_path,
        base_url="https://example.com", registry_name="Test",
    )
    svg = (tmp_path / "proofs" / "sample-claim" / "badge.svg").read_text()
    assert svg.startswith("<svg")
    assert "proof" in svg


def test_no_circular_import_between_emit_and_badge():
    """Regression test: emit.py and badge.py both reference each other.

    Loading either module first must succeed without ImportError. The
    convention is that badge.py imports field helpers from emit.py at
    module scope, while emit.py imports badge functions lazily (inside
    emit_registry_files). Flipping the direction would re-introduce
    the cycle.

    Runs in a subprocess so reloading proof_engine_registry doesn't
    pollute sys.modules for sibling tests (dataclasses imported under
    a different module identity break == comparisons elsewhere).
    """
    import subprocess, sys
    for first in ("proof_engine_registry.emit", "proof_engine_registry.badge"):
        result = subprocess.run(
            [sys.executable, "-c", f"import {first}"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, (
            f"importing {first} first failed:\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )


def test_emit_is_deterministic(tmp_path):
    """Running emit twice on the same input produces byte-identical output
    (required for the public site's git history to stay clean)."""
    a = tmp_path / "a"
    b = tmp_path / "b"
    emit_registry_files(
        proofs_dir=FIXTURES, output_dir=a,
        base_url="https://example.com", registry_name="Test",
        fixed_timestamp="2026-04-24T00:00:00Z",
    )
    emit_registry_files(
        proofs_dir=FIXTURES, output_dir=b,
        base_url="https://example.com", registry_name="Test",
        fixed_timestamp="2026-04-24T00:00:00Z",
    )
    for f in a.rglob("*.json"):
        rel = f.relative_to(a)
        assert f.read_bytes() == (b / rel).read_bytes(), f"diff in {rel}"
