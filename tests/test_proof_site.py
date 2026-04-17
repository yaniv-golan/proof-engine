"""Integration tests for tools/proof-site.py CLI."""

import json
import subprocess
import sys
import pytest
from pathlib import Path


TOOL_PATH = Path(__file__).parent.parent / "tools" / "proof-site.py"


def run_cli(*args, cwd=None):
    """Run proof-site.py and return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(TOOL_PATH)] + list(args),
        capture_output=True, text=True, cwd=cwd,
    )


@pytest.fixture
def site_dir(tmp_path):
    """Create a minimal site structure."""
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    return tmp_path / "site"


@pytest.fixture
def source_proof(tmp_path):
    """Create a source directory with valid proof artifacts."""
    src = tmp_path / "my-proof"
    src.mkdir()
    (src / "proof.py").write_text(
        "import json\n"
        "print('running proof')\n"
        "summary = {\n"
        '    "claim_natural": "Water boils at 100C",\n'
        '    "verdict": "PROVED",\n'
        '    "fact_registry": {"A1": {"label": "boiling point"}},\n'
        '    "claim_formal": {"subject": "water", "property": "boiling_point"},\n'
        '    "key_results": {"boiling_point": 100},\n'
        '    "generator": {"name": "proof-engine", "version": "1.0.0",\n'
        '        "repo": "https://github.com/yaniv-golan/proof-engine",\n'
        '        "generated_at": "2026-03-30"},\n'
        "}\n"
        "print('=== PROOF SUMMARY (JSON) ===')\n"
        "print(json.dumps(summary))\n"
    )
    (src / "proof.md").write_text(
        "# Water Boils at 100C\n\n"
        "## Key Findings\n\n- Boils at 100C\n\n"
        "## Claim Interpretation\n\nStandard pressure.\n\n"
        "## Evidence Summary\n\n| ID | Fact |\n|---|---|\n| A1 | 100C |\n\n"
        "## Proof Logic\n\nThermodynamics.\n\n"
        "## Conclusion\n\n**Verdict: PROVED**\n"
    )
    (src / "proof_audit.md").write_text(
        "# Audit\n\n## Hardening Checklist\n\nAll pass.\n"
    )
    (src / "proof.json").write_text(json.dumps({
        "claim_natural": "Water boils at 100C",
        "verdict": "PROVED",
        "fact_registry": {"A1": {"label": "boiling point"}},
        "claim_formal": {"subject": "water", "property": "boiling_point"},
        "key_results": {"boiling_point": 100},
        "generator": {
            "name": "proof-engine", "version": "1.0.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": "2026-03-30",
        },
    }))
    (src / "proof_narrative.md").write_text(
        "# Proof Narrative: Water boils at 100C\n\n"
        "## Verdict\n\n**Verdict: PROVED**\n\n"
        "Yes — water boils at 100 degrees Celsius at standard atmospheric pressure. "
        "This is confirmed by thermodynamic computation and matches established constants.\n\n"
        "## What was claimed?\n\n"
        "Water boils at 100C at standard pressure. This is fundamental chemistry "
        "and matters because boiling point is a key reference in science and cooking. "
        "Getting this right underpins countless practical and theoretical applications.\n\n"
        "## What did we find?\n\n"
        "Thermodynamic computation confirms the boiling point at exactly 100 degrees Celsius "
        "at standard atmospheric pressure of 101.325 kilopascals. "
        "The result matches established physical constants from NIST reference data. "
        "Independent verification through the Clausius-Clapeyron equation agrees within tolerance. "
        "Cross-referencing against published chemistry reference tables showed exact agreement. "
        "The Antoine equation yields 99.97 degrees Celsius at standard pressure, "
        "confirming the result within rounding precision. "
        "Multiple independent thermodynamic databases were consulted and all concur. "
        "No contradictory evidence was found in any authoritative source. "
        "Adversarial checks for altitude effects and impurity impacts "
        "confirmed these only matter at non-standard conditions.\n\n"
        "## What should you keep in mind?\n\n"
        "This applies at standard atmospheric pressure only. "
        "At higher altitudes or different pressures the boiling point changes. "
        "Dissolved substances also raise the boiling point through colligative effects.\n\n"
        "## How was this verified?\n\n"
        "Verified through computation. "
        "See [the structured proof report](proof.md), "
        "[the full verification audit](proof_audit.md), "
        "or [re-run the proof yourself](proof.py).\n"
    )
    return src


def test_feature_creates_featured_json(site_dir):
    """feature should create featured.json if missing."""
    slug = "test-proof"
    (site_dir / "proofs" / slug).mkdir()
    (site_dir / "proofs" / slug / "proof.json").write_text('{"claim_natural":"test"}')
    result = run_cli("feature", slug, "--site-dir", str(site_dir))
    assert result.returncode == 0
    data = json.loads((site_dir / "proofs" / "featured.json").read_text())
    assert slug in data


def test_feature_idempotent(site_dir):
    """Featuring an already-featured proof should succeed."""
    slug = "test-proof"
    (site_dir / "proofs" / slug).mkdir()
    (site_dir / "proofs" / slug / "proof.json").write_text('{"claim_natural":"test"}')
    run_cli("feature", slug, "--site-dir", str(site_dir))
    result = run_cli("feature", slug, "--site-dir", str(site_dir))
    assert result.returncode == 0


def test_feature_nonexistent_proof(site_dir):
    """Featuring a non-existent proof should fail."""
    result = run_cli("feature", "no-such-proof", "--site-dir", str(site_dir))
    assert result.returncode != 0


def test_unfeature_removes_slug(site_dir):
    slug = "test-proof"
    (site_dir / "proofs" / slug).mkdir()
    (site_dir / "proofs" / slug / "proof.json").write_text('{"claim_natural":"test"}')
    run_cli("feature", slug, "--site-dir", str(site_dir))
    result = run_cli("unfeature", slug, "--site-dir", str(site_dir))
    assert result.returncode == 0
    data = json.loads((site_dir / "proofs" / "featured.json").read_text())
    assert slug not in data


def test_unfeature_not_featured(site_dir):
    """Unfeaturing a non-featured proof should fail."""
    result = run_cli("unfeature", "no-such", "--site-dir", str(site_dir))
    assert result.returncode != 0


# --- Publish integration tests ---

def test_publish_missing_artifacts(site_dir, tmp_path):
    """Publish should fail if required artifacts are missing."""
    src = tmp_path / "incomplete"
    src.mkdir()
    (src / "proof.py").write_text("# only proof.py")
    result = run_cli("publish", str(src), "--site-dir", str(site_dir))
    assert result.returncode != 0
    assert "Missing" in result.stderr


def test_publish_slug_collision_without_force(site_dir, source_proof):
    """Publish should fail on slug collision without --force."""
    slug = "water-boils-at-100c"
    target = site_dir / "proofs" / slug
    target.mkdir(parents=True)
    (target / "proof.json").write_text(json.dumps({
        "claim_natural": "Water boils at 100C"
    }))
    result = run_cli("publish", str(source_proof), "--slug", slug, "--site-dir", str(site_dir))
    assert result.returncode != 0
    assert "force" in result.stderr.lower() or "exists" in result.stderr.lower()


def test_publish_duplicate_claim_different_slug_refuses(site_dir, source_proof):
    """Duplicate claim under different slug should fail even with --force."""
    existing = site_dir / "proofs" / "old-slug"
    existing.mkdir(parents=True)
    (existing / "proof.json").write_text(json.dumps({
        "claim_natural": "Water boils at 100C"
    }))
    result = run_cli(
        "publish", str(source_proof),
        "--slug", "new-slug", "--force",
        "--site-dir", str(site_dir)
    )
    assert result.returncode != 0
    assert "old-slug" in result.stderr


def test_publish_bad_thumbnail(site_dir, source_proof):
    """Publish should fail if thumbnail is wrong size."""
    from PIL import Image
    img = Image.new("RGB", (500, 300), "red")
    img.save(source_proof / "thumbnail.png")
    result = run_cli("publish", str(source_proof), "--site-dir", str(site_dir))
    assert result.returncode != 0
    assert "240x240" in result.stderr


def test_publish_rejects_missing_narrative(source_proof, tmp_path):
    """proof-site.py publish must fail when proof_narrative.md is missing."""
    narrative = source_proof / "proof_narrative.md"
    if narrative.exists():
        narrative.unlink()
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "proofs").mkdir()
    result = subprocess.run(
        [sys.executable, str(TOOL_PATH), "publish",
         str(source_proof), "--site-dir", str(site_dir)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "proof_narrative.md" in result.stdout or "proof_narrative.md" in result.stderr


def test_mint_doi_help_mentions_sync_doi_deps(tmp_path):
    """Smoke test: the new CLI hint string is reachable without minting."""
    import re
    src = (Path(__file__).parent.parent / "tools" / "proof-site.py").read_text()
    assert re.search(r"sync-doi-deps --slug", src), (
        "mint-doi must end with a hint to run sync-doi-deps"
    )


def _write_proof_dir(proofs_dir, slug, meta=None, doi_json=None):
    """Helper: build a minimal published-proof shape under proofs_dir/slug/."""
    import yaml
    pdir = proofs_dir / slug
    pdir.mkdir(parents=True)
    (pdir / "proof.json").write_text("{}")
    if meta is not None:
        (pdir / "meta.yaml").write_text(yaml.dump(meta, sort_keys=False))
    if doi_json is not None:
        (pdir / "doi.json").write_text(json.dumps(doi_json))
    return pdir


def test_sync_doi_deps_appends_canonical_doi(tmp_path):
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "upstream", doi_json={
        "doi": "10.5281/zenodo.222",
        "concept_doi": "10.5281/zenodo.111",
    })
    _write_proof_dir(proofs, "downstream", meta={
        "tags": ["mathematics"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "upstream"}]},
        ],
    })

    result = run_cli("sync-doi-deps", "--slug", "upstream",
                     "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr

    import yaml
    meta = yaml.safe_load((proofs / "downstream" / "meta.yaml").read_text())
    types = sorted(i["type"] for i in meta["depends_on"][0]["identifiers"])
    assert types == ["doi", "slug"]
    doi_id = next(i for i in meta["depends_on"][0]["identifiers"]
                  if i["type"] == "doi")
    assert doi_id["value"] == "10.5281/zenodo.111"  # concept_doi wins


def test_sync_doi_deps_replaces_stale_doi(tmp_path):
    """An existing DOI that is neither the concept DOI nor the current version
    DOI is treated as stale and replaced."""
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "upstream", doi_json={
        "doi": "10.5281/zenodo.222",
        "concept_doi": "10.5281/zenodo.111",
    })
    _write_proof_dir(proofs, "downstream", meta={
        "tags": ["mathematics"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [
                 {"type": "slug", "value": "upstream"},
                 {"type": "doi", "value": "10.5281/zenodo.000"},
             ]},
        ],
    })

    result = run_cli("sync-doi-deps", "--slug", "upstream",
                     "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr

    import yaml
    meta = yaml.safe_load((proofs / "downstream" / "meta.yaml").read_text())
    dois = [i["value"] for i in meta["depends_on"][0]["identifiers"]
            if i["type"] == "doi"]
    assert dois == ["10.5281/zenodo.111"]


def test_sync_doi_deps_preserves_hand_pinned_version_doi(tmp_path):
    """A DOI matching the upstream's current version DOI is treated as a
    deliberate pin; sync leaves it alone."""
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "upstream", doi_json={
        "doi": "10.5281/zenodo.222",
        "concept_doi": "10.5281/zenodo.111",
    })
    _write_proof_dir(proofs, "downstream", meta={
        "tags": ["mathematics"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [
                 {"type": "slug", "value": "upstream"},
                 {"type": "doi", "value": "10.5281/zenodo.222"},
             ]},
        ],
    })

    result = run_cli("sync-doi-deps", "--slug", "upstream",
                     "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr

    import yaml
    meta = yaml.safe_load((proofs / "downstream" / "meta.yaml").read_text())
    dois = [i["value"] for i in meta["depends_on"][0]["identifiers"]
            if i["type"] == "doi"]
    assert dois == ["10.5281/zenodo.222"]


def test_sync_doi_deps_dry_run_writes_nothing(tmp_path):
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "upstream", doi_json={
        "doi": "10.5281/zenodo.111",
        "concept_doi": "10.5281/zenodo.111",
    })
    _write_proof_dir(proofs, "downstream", meta={
        "tags": ["mathematics"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "upstream"}]},
        ],
    })
    before = (proofs / "downstream" / "meta.yaml").read_text()
    result = run_cli("sync-doi-deps", "--slug", "upstream", "--dry-run",
                     "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr
    after = (proofs / "downstream" / "meta.yaml").read_text()
    assert before == after


def test_sync_doi_deps_missing_doi_json_is_no_op(tmp_path):
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "upstream")
    _write_proof_dir(proofs, "downstream", meta={
        "tags": ["mathematics"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "upstream"}]},
        ],
    })
    result = run_cli("sync-doi-deps", "--slug", "upstream",
                     "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr


def test_show_deps_default_text_is_slug_only_prereq(tmp_path):
    """Default text view shows only slug entries with prerequisite relations."""
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "u")
    _write_proof_dir(proofs, "me", meta={
        "tags": ["t"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "u"}]},
            {"relation": "References",
             "identifiers": [{"type": "arxiv", "value": "2603.21852"}]},
        ],
    })
    result = run_cli("show-deps", "me", "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr
    assert "u" in result.stdout
    assert "2603.21852" not in result.stdout


def test_show_deps_include_external(tmp_path):
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "u")
    _write_proof_dir(proofs, "me", meta={
        "tags": ["t"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "u"}]},
            {"relation": "References",
             "identifiers": [{"type": "arxiv", "value": "2603.21852"}]},
        ],
    })
    result = run_cli("show-deps", "me", "--include-external",
                     "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr
    assert "u" in result.stdout
    assert "2603.21852" in result.stdout


def test_show_deps_json_always_includes_everything(tmp_path):
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "u")
    _write_proof_dir(proofs, "me", meta={
        "tags": ["t"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "u"}]},
            {"relation": "References",
             "identifiers": [{"type": "arxiv", "value": "2603.21852"}]},
        ],
    })
    result = run_cli("show-deps", "me", "--format", "json",
                     "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    types = {ident["type"] for entry in payload["direct"]
             for ident in entry["identifiers"]}
    assert types == {"slug", "arxiv"}


def test_show_deps_transitive_walks_prereq_slugs(tmp_path):
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "deep")
    _write_proof_dir(proofs, "u", meta={
        "tags": ["t"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "deep"}]},
        ],
    })
    _write_proof_dir(proofs, "me", meta={
        "tags": ["t"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "u"}]},
        ],
    })
    result = run_cli("show-deps", "me", "--transitive",
                     "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr
    assert "u" in result.stdout
    assert "deep" in result.stdout


def test_show_deps_reverse(tmp_path):
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "u")
    _write_proof_dir(proofs, "me", meta={
        "tags": ["t"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "u"}]},
        ],
    })
    result = run_cli("show-deps", "u", "--reverse",
                     "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr
    assert "me" in result.stdout


def test_show_deps_missing_slug_errors(tmp_path):
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    result = run_cli("show-deps", "ghost", "--site-dir", str(tmp_path / "site"))
    assert result.returncode != 0
    assert "ghost" in (result.stdout + result.stderr)


def test_audit_deps_passes_clean_site(tmp_path):
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "a")
    _write_proof_dir(proofs, "b", meta={
        "tags": ["t"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "a"}]},
        ],
    })
    result = run_cli("audit-deps", "--site-dir", str(tmp_path / "site"))
    assert result.returncode == 0, result.stderr


def test_audit_deps_fails_on_broken_state(tmp_path):
    proofs = tmp_path / "site" / "proofs"
    proofs.mkdir(parents=True)
    _write_proof_dir(proofs, "b", meta={
        "tags": ["t"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "ghost"}]},
        ],
    })
    result = run_cli("audit-deps", "--site-dir", str(tmp_path / "site"))
    assert result.returncode != 0
    assert "ghost" in (result.stdout + result.stderr)


def test_publish_rejects_unknown_dependency_slug(site_dir, source_proof):
    """publish must fail when depends_on slug points to a non-existent proof."""
    import yaml
    # Pad narrative past the 200-word minimum so we reach the cross-check stage.
    narrative = source_proof / "proof_narrative.md"
    narrative.write_text(
        narrative.read_text()
        + "\n## Additional Notes\n\n"
        + ("Padding sentence to satisfy minimum narrative length. " * 20)
        + "\n"
    )
    (source_proof / "meta.yaml").write_text(yaml.dump({
        "tags": ["test"],
        "depends_on": [
            {"relation": "IsDerivedFrom",
             "identifiers": [{"type": "slug", "value": "ghost-prereq"}]},
        ],
    }))
    result = run_cli("publish", str(source_proof), "--site-dir", str(site_dir))
    assert result.returncode != 0
    assert "ghost-prereq" in (result.stdout + result.stderr)
