import json
import sys
from pathlib import Path
import yaml

from tools.lib.section_extractor import extract_sections, validate_required_sections
from tools.lib.tagger import auto_tag, canonicalize_tag
from tools.lib.verdict import normalize_verdict

REQUIRED_PROOF_MD_SECTIONS = [
    "Key Findings",
    "Claim Interpretation",
    "Evidence Summary",
    "Proof Logic",
    "Conclusion",
]

REQUIRED_JSON_KEYS = ["fact_registry", "claim_formal", "claim_natural",
                      "verdict", "key_results", "generator"]

REQUIRED_GENERATOR_KEYS = ["name", "version", "repo", "generated_at"]

REQUIRED_CLAIM_FORMAL_KEYS = []  # claim_formal structure varies by proof type

OPTIONAL_AUDIT_SECTIONS = [
    "Citation Verification Details", "Computation Traces",
    "Independent Source Agreement", "Adversarial Checks",
    "Hardening Checklist", "Source Credibility Assessment",
    "Extraction Records",
]

OPTIONAL_MD_SECTIONS = ["Counter-Evidence Search"]


def load_proof(proof_dir: Path) -> dict:
    proof_dir = Path(proof_dir)
    slug = proof_dir.name

    # Load proof.json
    proof_json_path = proof_dir / "proof.json"
    proof_data = json.loads(proof_json_path.read_text())

    # Validate required keys
    for key in REQUIRED_JSON_KEYS:
        if key not in proof_data:
            raise ValueError(f"{slug}: proof.json missing required key: {key}")

    generator = proof_data["generator"]
    for key in REQUIRED_GENERATOR_KEYS:
        if key not in generator:
            raise ValueError(f"{slug}: proof.json generator missing key: {key}")

    claim_formal = proof_data["claim_formal"]
    for key in REQUIRED_CLAIM_FORMAL_KEYS:
        if key not in claim_formal:
            raise ValueError(f"{slug}: proof.json claim_formal missing key: {key}")

    # Normalize verdict
    verdict = normalize_verdict(proof_data["verdict"])

    # Extract sections from proof.md
    proof_md = (proof_dir / "proof.md").read_text()
    sections_md = extract_sections(proof_md)
    missing = validate_required_sections(sections_md, REQUIRED_PROOF_MD_SECTIONS)
    if missing:
        raise ValueError(f"{slug}: proof.md missing required sections: {missing}")

    # Extract sections from proof_audit.md
    audit_md = (proof_dir / "proof_audit.md").read_text()
    sections_audit = extract_sections(audit_md)

    # Warn about missing optional sections
    missing_audit = validate_required_sections(sections_audit, OPTIONAL_AUDIT_SECTIONS)
    if missing_audit:
        print(f"WARNING: {slug}: proof_audit.md missing optional sections: {missing_audit}",
              file=sys.stderr)

    missing_md_opt = validate_required_sections(sections_md, OPTIONAL_MD_SECTIONS)
    if missing_md_opt:
        print(f"WARNING: {slug}: proof.md missing optional sections: {missing_md_opt}",
              file=sys.stderr)

    # Tags: meta.yaml override or auto-tag
    meta_path = proof_dir / "meta.yaml"
    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text()) or {}
        if "tags" in meta:
            tags = [canonicalize_tag(t) for t in meta["tags"]]
        else:
            tags = auto_tag(proof_data["claim_natural"])
        featured = meta.get("featured", False)
    else:
        tags = auto_tag(proof_data["claim_natural"])
        featured = False

    # Citation count
    citations = proof_data.get("citations")
    citation_count = len(citations) if citations is not None else None

    return {
        "slug": slug,
        "proof_data": proof_data,
        "sections_md": sections_md,
        "sections_audit": sections_audit,
        "verdict": verdict,
        "tags": tags,
        "featured": featured,
        "citation_count": citation_count,
        "date": generator["generated_at"],
        "proof_engine_version": generator["version"],
    }


def load_all_proofs(proofs_dir: Path) -> list[dict]:
    proofs_dir = Path(proofs_dir)
    proofs = []
    for slug_dir in sorted(proofs_dir.iterdir()):
        if slug_dir.is_dir() and (slug_dir / "proof.json").exists():
            proofs.append(load_proof(slug_dir))
    return proofs
