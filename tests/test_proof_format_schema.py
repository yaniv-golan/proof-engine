# tests/test_proof_format_schema.py
import json
import re
from pathlib import Path

SCHEMA_PATH = Path("proof-engine/skills/proof-engine/proof_format_schema.json")


def test_schema_file_exists():
    assert SCHEMA_PATH.exists(), f"Schema file missing: {SCHEMA_PATH}"


def test_schema_has_both_profiles():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert "proof_md" in schema
    assert "proof_audit_md" in schema
    assert "proof_narrative_md" in schema
    for version in ("v1", "v2", "v2_theorem"):
        assert version in schema["proof_md"], f"proof_md missing {version} profile"
        assert "required" in schema["proof_md"][version]
        assert version in schema["proof_audit_md"], f"proof_audit_md missing {version} profile"


def test_v2_theorem_profile_shape():
    """The v2_theorem profile has the canonical theorem-proof section list."""
    schema = json.loads(SCHEMA_PATH.read_text())
    md_required = schema["proof_md"]["v2_theorem"]["required"]
    # Canonical theorem-proof sections (title-cased per section_extractor._normalize_heading)
    expected_required = {
        "Theorem Statement",
        "Proof",
        "Corollaries",
        "Scope",
        "Relation To Prior Work",
        "What Could Challenge This Verdict?",
        "Conclusion",
    }
    assert set(md_required) == expected_required, (
        f"v2_theorem required mismatch: {set(md_required) ^ expected_required}"
    )
    # No Evidence Summary in theorem proofs (citation/computation tables move to audit)
    assert "Evidence Summary" not in md_required
    assert "Proof Logic" not in md_required  # replaced by "Proof"

    audit = schema["proof_audit_md"]["v2_theorem"]
    # Implementation Regression Checks is required for theorem proofs — locks in
    # the structure that consolidates sampling/regression detail away from proof.md.
    assert audit["required"] == ["Implementation Regression Checks"]
    assert "Implementation Regression Checks" not in audit["optional"]


def test_schema_has_conditional_sections():
    schema = json.loads(SCHEMA_PATH.read_text())
    conditional = schema["proof_audit_md"].get("conditional", [])
    section_names = [c["section"] for c in conditional]
    assert "Type S (Search) Facts" in section_names


def test_proof_loader_has_no_hardcoded_section_lists():
    """Verify proof_loader no longer has hardcoded section list constants."""
    loader_code = Path("tools/lib/proof_loader.py").read_text()
    assert "REQUIRED_PROOF_MD_SECTIONS_V1" not in loader_code, \
        "proof_loader.py still has hardcoded V1 section list constant"
    assert "REQUIRED_PROOF_MD_SECTIONS_V2" not in loader_code, \
        "proof_loader.py still has hardcoded V2 section list constant"
    assert "OPTIONAL_MD_SECTIONS_V1" not in loader_code
    assert "OPTIONAL_AUDIT_SECTIONS_V1" not in loader_code


def test_proof_loader_references_schema():
    """Verify proof_loader reads from the schema file."""
    loader_code = Path("tools/lib/proof_loader.py").read_text()
    assert "proof_format_schema.json" in loader_code


def test_template_headings_exist_in_schema():
    """Every heading name referenced in proof.html exists in the schema."""
    schema = json.loads(SCHEMA_PATH.read_text())

    all_schema_headings = set()
    for profile in ("v1", "v2", "v2_theorem"):
        for artifact in ("proof_md", "proof_audit_md"):
            if profile in schema.get(artifact, {}):
                all_schema_headings.update(schema[artifact][profile].get("required", []))
                all_schema_headings.update(schema[artifact][profile].get("optional", []))
        for cond in schema.get("proof_audit_md", {}).get("conditional", []):
            all_schema_headings.add(cond["section"])
    for heading, info in schema.get("template_fallbacks", {}).items():
        if heading != "_comment":
            all_schema_headings.add(heading)
            if "v1_alias" in info:
                all_schema_headings.add(info["v1_alias"])
    all_schema_headings.update(schema["proof_narrative_md"]["required"])

    template_path = Path("site/templates/proof.html")
    template_code = template_path.read_text()
    get_pattern = re.compile(r'\.get\("([^"]+)"\)')
    template_headings = set(get_pattern.findall(template_code))
    heading_refs = {h for h in template_headings if " " in h or h[0].isupper()}

    missing = heading_refs - all_schema_headings
    assert not missing, (
        f"Template references heading(s) not in schema: {sorted(missing)}. "
        f"Add them to proof_format_schema.json."
    )
