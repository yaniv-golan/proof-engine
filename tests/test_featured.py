import json
import pytest
from pathlib import Path
from tools.lib.featured import load_featured_slugs, save_featured_slugs, validate_featured


def test_load_featured_slugs_returns_set(tmp_path):
    proofs_dir = tmp_path / "proofs"
    proofs_dir.mkdir()
    (proofs_dir / "slug-a").mkdir()
    (proofs_dir / "slug-a" / "proof.json").write_text("{}")
    (proofs_dir / "slug-b").mkdir()
    (proofs_dir / "slug-b" / "proof.json").write_text("{}")
    featured_path = proofs_dir / "featured.json"
    featured_path.write_text(json.dumps(["slug-a", "slug-b"]))
    result = load_featured_slugs(proofs_dir)
    assert result == {"slug-a", "slug-b"}


def test_load_featured_slugs_missing_file_returns_empty(tmp_path):
    proofs_dir = tmp_path / "proofs"
    proofs_dir.mkdir()
    result = load_featured_slugs(proofs_dir)
    assert result == set()


def test_load_featured_slugs_dangling_ref_raises(tmp_path):
    proofs_dir = tmp_path / "proofs"
    proofs_dir.mkdir()
    (proofs_dir / "slug-a").mkdir()
    (proofs_dir / "slug-a" / "proof.json").write_text("{}")
    featured_path = proofs_dir / "featured.json"
    featured_path.write_text(json.dumps(["slug-a", "slug-nonexistent"]))
    with pytest.raises(ValueError, match="slug-nonexistent"):
        load_featured_slugs(proofs_dir)


def test_load_featured_slugs_dir_without_proof_json_raises(tmp_path):
    proofs_dir = tmp_path / "proofs"
    proofs_dir.mkdir()
    (proofs_dir / "slug-a").mkdir()  # no proof.json
    featured_path = proofs_dir / "featured.json"
    featured_path.write_text(json.dumps(["slug-a"]))
    with pytest.raises(ValueError, match="non-loadable"):
        load_featured_slugs(proofs_dir)


def test_load_featured_slugs_duplicate_raises(tmp_path):
    proofs_dir = tmp_path / "proofs"
    proofs_dir.mkdir()
    (proofs_dir / "slug-a").mkdir()
    (proofs_dir / "slug-a" / "proof.json").write_text("{}")
    featured_path = proofs_dir / "featured.json"
    featured_path.write_text(json.dumps(["slug-a", "slug-a"]))
    with pytest.raises(ValueError, match="duplicate"):
        load_featured_slugs(proofs_dir)


def test_load_featured_slugs_invalid_json_raises(tmp_path):
    proofs_dir = tmp_path / "proofs"
    proofs_dir.mkdir()
    featured_path = proofs_dir / "featured.json"
    featured_path.write_text("not json")
    with pytest.raises(ValueError):
        load_featured_slugs(proofs_dir)


def test_load_featured_slugs_not_array_raises(tmp_path):
    proofs_dir = tmp_path / "proofs"
    proofs_dir.mkdir()
    featured_path = proofs_dir / "featured.json"
    featured_path.write_text(json.dumps({"slug": True}))
    with pytest.raises(ValueError, match="array"):
        load_featured_slugs(proofs_dir)


def test_save_featured_slugs_writes_sorted(tmp_path):
    proofs_dir = tmp_path / "proofs"
    proofs_dir.mkdir()
    (proofs_dir / "zebra").mkdir()
    (proofs_dir / "zebra" / "proof.json").write_text("{}")
    (proofs_dir / "alpha").mkdir()
    (proofs_dir / "alpha" / "proof.json").write_text("{}")
    save_featured_slugs(proofs_dir, {"zebra", "alpha"})
    data = json.loads((proofs_dir / "featured.json").read_text())
    assert data == ["alpha", "zebra"]


def test_save_featured_slugs_dangling_raises(tmp_path):
    proofs_dir = tmp_path / "proofs"
    proofs_dir.mkdir()
    with pytest.raises(ValueError, match="non-loadable"):
        save_featured_slugs(proofs_dir, {"no-such-proof"})


def test_save_featured_slugs_empty_set(tmp_path):
    proofs_dir = tmp_path / "proofs"
    proofs_dir.mkdir()
    save_featured_slugs(proofs_dir, set())
    data = json.loads((proofs_dir / "featured.json").read_text())
    assert data == []
