import json
import pytest

from tools.lib.ro_crate import generate_ro_crate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_proof_data():
    return {"format_version": 3, "claim_natural": "Test",
            "verdict": {"value": "PROVED", "qualified": False},
            "generator": {"name": "proof-engine", "version": "1.0.0",
                          "repo": "https://github.com/yaniv-golan/proof-engine",
                          "generated_at": "2026-04-13"}}


ALL_FILES = ["proof.py", "proof.json", "proof.md", "proof_audit.md",
             "proof_narrative.md", "provenance.json", "proof.ipynb"]

CANONICAL_URL = "https://example.com/proofs/test/"


def _generate(proof_data=None, files=None, doi=None, concept_doi=None):
    return generate_ro_crate(
        proof_data=proof_data or _minimal_proof_data(),
        slug="test", canonical_url=CANONICAL_URL,
        available_files=files or ALL_FILES,
        doi=doi, concept_doi=concept_doi,
    )


def _graph_index(crate):
    return {item["@id"]: item for item in crate["@graph"]}


# ---------------------------------------------------------------------------
# Existing structural tests
# ---------------------------------------------------------------------------

def test_ro_crate_basic_structure():
    result = _generate()
    assert result["@context"] == "https://w3id.org/ro/crate/1.1/context"
    graph = _graph_index(result)
    assert "./" in graph
    root = graph["./"]
    assert root["@type"] == "Dataset"
    assert "proof.py" in [p["@id"] for p in root["hasPart"]]


def test_ro_crate_proof_py_typed():
    result = _generate(files=["proof.py", "proof.json"])
    graph = _graph_index(result)
    assert graph["proof.py"]["@type"] == "SoftwareSourceCode"
    assert graph["proof.json"]["@type"] == "Dataset"


def test_ro_crate_includes_doi():
    result = _generate(files=["proof.py"], doi="10.5281/zenodo.12345")
    graph = _graph_index(result)
    root = graph["./"]
    assert root.get("identifier") == "https://doi.org/10.5281/zenodo.12345"


def test_ro_crate_only_includes_existing_files():
    result = _generate(files=["proof.py", "proof.json"])
    graph = _graph_index(result)
    assert "provenance.json" not in graph


# ---------------------------------------------------------------------------
# RO-Crate 1.1 spec-conformance tests (validated via the `rocrate` library)
# ---------------------------------------------------------------------------

pytest.importorskip("rocrate", reason="rocrate library not installed")

from rocrate.rocrate import ROCrate


def _to_ro_crate(proof_data=None, files=None, doi=None):
    """Generate RO-Crate JSON and load it via the rocrate library."""
    import tempfile, os, shutil
    crate_json = _generate(proof_data=proof_data, files=files, doi=doi)

    tmpdir = tempfile.mkdtemp()
    try:
        # Write ro-crate-metadata.json
        meta_path = os.path.join(tmpdir, "ro-crate-metadata.json")
        with open(meta_path, "w") as f:
            json.dump(crate_json, f)

        # Create stub files so the crate loader doesn't complain
        for filename in (files or ALL_FILES):
            fpath = os.path.join(tmpdir, filename)
            with open(fpath, "w") as f:
                f.write("")

        crate = ROCrate(tmpdir)
    finally:
        shutil.rmtree(tmpdir)
    return crate, crate_json


def test_spec_loads_as_valid_crate():
    """RO-Crate metadata must load without errors via the rocrate library."""
    crate, _ = _to_ro_crate()
    assert crate is not None


def test_spec_context_is_ro_crate_1_1():
    """@context must be the RO-Crate 1.1 context URL."""
    crate_json = _generate()
    assert crate_json["@context"] == "https://w3id.org/ro/crate/1.1/context"


def test_spec_metadata_descriptor():
    """Must have a metadata descriptor (ro-crate-metadata.json) with correct conformsTo."""
    crate_json = _generate()
    graph = _graph_index(crate_json)
    descriptor = graph.get("ro-crate-metadata.json")
    assert descriptor is not None, "Missing metadata descriptor"
    assert descriptor["@type"] == "CreativeWork"
    assert descriptor["about"] == {"@id": "./"}
    assert descriptor["conformsTo"] == {"@id": "https://w3id.org/ro/crate/1.1"}


def test_spec_root_dataset():
    """Root dataset (./) must be typed as Dataset."""
    crate, _ = _to_ro_crate()
    root = crate.root_dataset
    assert root is not None, "No root dataset found"
    assert "Dataset" in (root.type if isinstance(root.type, list) else [root.type])


def test_spec_root_has_name_and_description():
    """Root dataset must have name and description per RO-Crate 1.1 SHOULD."""
    crate, _ = _to_ro_crate()
    root = crate.root_dataset
    assert root.get("name"), "Root dataset missing name"
    assert root.get("description"), "Root dataset missing description"


def test_spec_root_has_date_published():
    """Root dataset must have datePublished."""
    crate, _ = _to_ro_crate()
    root = crate.root_dataset
    assert root.get("datePublished"), "Root dataset missing datePublished"


def test_spec_root_has_license():
    """Root dataset must have a license."""
    crate, _ = _to_ro_crate()
    root = crate.root_dataset
    # rocrate library stores references as dicts or entities
    license_val = root.get("license")
    assert license_val is not None, "Root dataset missing license"


def test_spec_all_parts_described():
    """Every hasPart entry in the root dataset must have its own @graph entry."""
    crate_json = _generate()
    graph = _graph_index(crate_json)
    root = graph["./"]
    for part_ref in root["hasPart"]:
        part_id = part_ref["@id"]
        assert part_id in graph, f"hasPart '{part_id}' not described in @graph"


def test_spec_all_graph_entries_have_id_and_type():
    """Every @graph entry must have @id and @type."""
    crate_json = _generate()
    for item in crate_json["@graph"]:
        assert "@id" in item, f"Graph entry missing @id: {item}"
        assert "@type" in item, f"Graph entry {item['@id']} missing @type"


def test_spec_file_types_correct():
    """File entries must have the expected RO-Crate types."""
    expected = {
        "proof.py": "SoftwareSourceCode",
        "proof.json": "Dataset",
        "proof.md": "ScholarlyArticle",
        "proof_audit.md": "ScholarlyArticle",
        "proof_narrative.md": "Article",
        "provenance.json": "CreativeWork",
        "proof.ipynb": "ComputationalNotebook",
    }
    crate_json = _generate()
    graph = _graph_index(crate_json)
    for filename, expected_type in expected.items():
        assert graph[filename]["@type"] == expected_type, (
            f"{filename}: expected {expected_type}, got {graph[filename]['@type']}"
        )


def test_spec_files_have_encoding_format():
    """All file entries should have encodingFormat for interoperability."""
    crate_json = _generate()
    graph = _graph_index(crate_json)
    for filename in ALL_FILES:
        entry = graph.get(filename)
        assert entry is not None, f"Missing entry for {filename}"
        assert "encodingFormat" in entry, f"{filename} missing encodingFormat"


def test_spec_creator_is_software_application():
    """Creator must be a SoftwareApplication with name and version."""
    crate, _ = _to_ro_crate()
    root = crate.root_dataset
    # Access creator — rocrate may return entity or dict
    creator_ref = root.get("creator")
    assert creator_ref is not None, "Root dataset missing creator"

    crate_json = _generate()
    graph = _graph_index(crate_json)
    creator = graph.get("#proof-engine")
    assert creator is not None, "Creator entity not in graph"
    assert creator["@type"] == "SoftwareApplication"
    assert creator.get("name"), "Creator missing name"
    assert creator.get("version"), "Creator missing version"


def test_spec_provenance_conforms_to_w3c_prov():
    """provenance.json entry must declare conformsTo W3C PROV."""
    crate_json = _generate()
    graph = _graph_index(crate_json)
    prov_entry = graph.get("provenance.json")
    assert prov_entry is not None
    assert prov_entry.get("conformsTo") == {"@id": "http://www.w3.org/ns/prov"}


def test_spec_doi_as_identifier():
    """When DOI is provided, root dataset must include it as identifier."""
    crate, raw = _to_ro_crate(doi="10.5281/zenodo.99999")
    root = crate.root_dataset
    # Check the raw JSON since rocrate may normalize the value
    graph = _graph_index(raw)
    assert graph["./"]["identifier"] == "https://doi.org/10.5281/zenodo.99999"


def test_spec_concept_doi_as_same_as():
    """When concept_doi differs from doi, root dataset must include sameAs."""
    crate_json = generate_ro_crate(
        proof_data=_minimal_proof_data(), slug="test",
        canonical_url=CANONICAL_URL, available_files=["proof.py"],
        doi="10.5281/zenodo.12345", concept_doi="10.5281/zenodo.00001",
    )
    graph = _graph_index(crate_json)
    assert graph["./"].get("sameAs") == "https://doi.org/10.5281/zenodo.00001"
