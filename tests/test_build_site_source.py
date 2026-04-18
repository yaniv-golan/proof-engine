import json
import shutil
import subprocess
from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent


def _build_fixture_site(tmp_path, keep_slugs):
    """Copy site/ to tmp, trim to `keep_slugs` only, and rewrite
    featured.json to reference only kept slugs so the build-site loader
    doesn't fail on dangling refs (tools/lib/featured.py raises
    ValueError for featured entries without a loadable proof dir)."""
    src_site = REPO / "site"
    fixture_site = tmp_path / "site"
    shutil.copytree(src_site, fixture_site)

    proofs_dir = fixture_site / "proofs"
    keep_set = set(keep_slugs)
    for d in proofs_dir.iterdir():
        if d.is_dir() and d.name not in keep_set:
            shutil.rmtree(d)

    featured_path = proofs_dir / "featured.json"
    if featured_path.exists():
        original = json.loads(featured_path.read_text())
        filtered = [s for s in original if s in keep_set]
        featured_path.write_text(json.dumps(filtered, indent=2) + "\n")

    return fixture_site


def _run_build(fixture_site, out_dir, timeout=120, commit_sha=None):
    cmd = ["python", "tools/build-site.py",
           "--site-dir", str(fixture_site), "--output-dir", str(out_dir),
           "--base-url", "/proof-engine/", "--site-url", "https://example.test",
           "--design-md", "docs/DESIGN.md",
           "--hardening-rules-md",
           "proof-engine/skills/proof-engine/references/hardening-rules.md"]
    if commit_sha is not None:
        cmd += ["--commit-sha", commit_sha]
    return subprocess.run(
        cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout,
    )


def test_proof_page_includes_inline_source_minted(tmp_path):
    """Minted proof: source section present AND 'deposited to Zenodo'
    intro + 'view on Zenodo' action are both rendered.

    Regression guard for the template-context wiring bug where
    `proof_py_html` was attached to `augmented` (built after render)
    instead of `proof` (what the template sees)."""
    keep = "us-dollar-purchasing-power"  # minted (has doi.json)
    if not (REPO / "site" / "proofs" / keep / "doi.json").is_file():
        pytest.skip(f"fixture slug {keep} not minted — no doi.json")

    fixture_site = _build_fixture_site(tmp_path, [keep])
    out = tmp_path / "_site"
    result = _run_build(fixture_site, out, timeout=60)
    assert result.returncode == 0, result.stderr

    html = (out / "proofs" / keep / "index.html").read_text()
    assert 'class="proof-source-section"' in html, "inline source section missing"
    assert 'class="highlight"' in html, "Pygments highlighting missing"
    assert "View proof source" in html, "section label missing"
    # Minted-only copy / action:
    assert "deposited to Zenodo" in html, "minted intro copy missing"
    assert "view on Zenodo" in html, "Zenodo action link missing"
    assert "doi.org/10." in html, "DOI link missing from source section"


def test_proof_page_includes_inline_source_unminted(tmp_path):
    """Un-minted proof: source section still present, but provenance copy
    degrades to the working-copy variant and the Zenodo action is absent.

    Guards against publishing false 'deposited to Zenodo' claims on the
    ~30 un-minted proofs currently in site/proofs/."""
    unminted = None
    for d in sorted((REPO / "site" / "proofs").iterdir()):
        if d.is_dir() and (d / "proof.py").is_file() \
           and not (d / "doi.json").is_file():
            unminted = d.name
            break
    if unminted is None:
        pytest.skip("no un-minted proofs in site/proofs/")

    fixture_site = _build_fixture_site(tmp_path, [unminted])
    out = tmp_path / "_site"
    result = _run_build(fixture_site, out, timeout=60)
    assert result.returncode == 0, result.stderr

    html = (out / "proofs" / unminted / "index.html").read_text()
    assert 'class="proof-source-section"' in html, "inline source section missing"
    assert 'class="highlight"' in html, "Pygments highlighting missing"
    # Un-minted must NOT claim Zenodo deposit:
    assert "deposited to Zenodo" not in html, \
        f"un-minted proof {unminted} falsely claims Zenodo deposit"
    assert "view on Zenodo" not in html, \
        f"un-minted proof {unminted} shows Zenodo action link"
    # Should show the fallback intro:
    assert "working copy from this repository" in html, \
        "un-minted fallback intro copy missing"


def test_unminted_proof_has_slug_mode_binder_url(tmp_path):
    """Un-minted proof: the rendered page must include a slug-mode Binder URL
    pinned to the passed commit SHA, plus a human-readable provenance hint
    showing the short SHA. Guards the end-to-end wiring from
    build-site.py `--commit-sha` → citation.py `commit_sha` → proof.html
    template → rendered HTML."""
    unminted = None
    for d in sorted((REPO / "site" / "proofs").iterdir()):
        if d.is_dir() and (d / "proof.py").is_file() \
           and not (d / "doi.json").is_file():
            unminted = d.name
            break
    if unminted is None:
        pytest.skip("no un-minted proofs in site/proofs/")

    fake_sha = "deadbeef" + ("0" * 32)  # 40-hex, validates against ^[0-9a-f]{40}$
    fixture_site = _build_fixture_site(tmp_path, [unminted])
    out = tmp_path / "_site"
    result = _run_build(fixture_site, out, timeout=60, commit_sha=fake_sha)
    assert result.returncode == 0, result.stderr

    html = (out / "proofs" / unminted / "index.html").read_text()
    # Binder URL carries both slug and ref as the inner (URL-encoded)
    # query of the mybinder.org `?urlpath=lab/tree/launcher.ipynb?slug=X&ref=Y`
    # trick — so `?slug=` renders in the HTML as `%3Fslug%3D` and `&` as `%26`.
    expected_fragment = f"%3Fslug%3D{unminted}%26ref%3D{fake_sha}"
    assert expected_fragment in html, \
        f"slug-mode Binder URL fragment {expected_fragment!r} not found in rendered HTML"
    # And the provenance hint:
    assert "GitHub commit <code>deadbee</code>" in html, \
        "short-SHA provenance copy missing from rendered HTML"


@pytest.mark.slow  # full-site build; run in CI, skip in fast local iterations
def test_doi_index_generated(tmp_path):
    """`doi-index.json` at site root maps DOI → slug for the launcher."""
    fixture_site = tmp_path / "site"
    shutil.copytree(REPO / "site", fixture_site)
    out = tmp_path / "_site"
    result = _run_build(fixture_site, out, timeout=300)
    assert result.returncode == 0, result.stderr

    index = json.loads((out / "doi-index.json").read_text())
    assert len(index) > 0, "doi-index.json is empty"
    for doi, slug in index.items():
        assert doi.startswith("10."), f"bad DOI format: {doi!r}"
        assert (out / "proofs" / slug / "index.html").exists(), \
            f"slug {slug} not built"
