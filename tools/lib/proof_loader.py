import json
import re
import sys
from pathlib import Path
import yaml

from tools.lib.featured import load_featured_slugs
from tools.lib.narrative_validator import extract_verdict_declaration, REQUIRED_NARRATIVE_SECTIONS
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



def extract_source_names(proof_data, max_sources=3):
    """Extract unique source names from citations, up to max_sources."""
    citations = proof_data.get("citations")
    if not citations:
        return []
    seen = set()
    names = []
    for cit in citations.values():
        name = cit.get("source_name", "")
        if name and name not in seen:
            seen.add(name)
            names.append(name)
    return names[:max_sources]


_VERDICT_PREFIX_RE = re.compile(
    r"^\*\*[A-Z ]+(?:\(.*?\))?\.\*\*\s*"
)


def extract_verdict_summary(
    sections_md: dict[str, str],
    verdict_raw: str,
) -> str:
    """Extract a one-sentence verdict summary from the Conclusion section."""
    conclusion = sections_md.get("Conclusion", "")
    if not conclusion:
        return f"{verdict_raw} \u2014 see full proof for details."

    text = _VERDICT_PREFIX_RE.sub("", conclusion).strip()
    if not text:
        return f"{verdict_raw} \u2014 see full proof for details."

    first_dot = text.find(". ")
    if first_dot != -1:
        return text[: first_dot + 1]
    if text.endswith("."):
        return text.rstrip().rstrip(".") + "."
    return text.split("\n")[0].strip()


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

    # Absence proofs: check for Type S (Search) Facts section
    if proof_data.get("search_registry") is not None:
        if "Type S (Search) Facts" not in sections_audit:
            print(f"WARNING: {slug}: proof_audit.md missing 'Type S (Search) Facts' section "
                  "(expected for absence proofs with search_registry)",
                  file=sys.stderr)

    missing_md_opt = validate_required_sections(sections_md, OPTIONAL_MD_SECTIONS)
    if missing_md_opt:
        print(f"WARNING: {slug}: proof.md missing optional sections: {missing_md_opt}",
              file=sys.stderr)

    # Extract sections from proof_narrative.md
    narrative_path = proof_dir / "proof_narrative.md"
    if not narrative_path.exists():
        raise ValueError(f"{slug}: missing required artifact: proof_narrative.md")
    narrative_md = narrative_path.read_text()
    sections_narrative = extract_sections(narrative_md)
    missing_narrative = validate_required_sections(sections_narrative, REQUIRED_NARRATIVE_SECTIONS)
    if missing_narrative:
        raise ValueError(f"{slug}: proof_narrative.md missing required sections: {missing_narrative}")

    # Parse verdict declaration and hook from narrative
    verdict_declaration_str, verdict_hook = extract_verdict_declaration(
        sections_narrative.get("Verdict", "")
    )

    # Tags: meta.yaml override or auto-tag
    meta_path = proof_dir / "meta.yaml"
    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text()) or {}
        if "featured" in meta:
            raise ValueError(
                f"{slug}: meta.yaml contains deprecated 'featured' key — "
                f"featured status is now managed via site/proofs/featured.json"
            )
        if "tags" in meta:
            tags = [canonicalize_tag(t) for t in meta["tags"]]
        else:
            tags = auto_tag(proof_data["claim_natural"])
    else:
        tags = auto_tag(proof_data["claim_natural"])

    # Citation count
    citations = proof_data.get("citations")
    citation_count = len(citations) if citations is not None else None

    # Search count (absence proofs)
    search_registry = proof_data.get("search_registry")
    search_count = len(search_registry) if search_registry is not None else None

    return {
        "slug": slug,
        "proof_data": proof_data,
        "sections_md": sections_md,
        "sections_audit": sections_audit,
        "verdict": verdict,
        "tags": tags,
        "featured": False,
        "citation_count": citation_count,
        "search_count": search_count,
        "verdict_summary": extract_verdict_summary(
            sections_md, verdict["raw"]
        ),
        "source_names": extract_source_names(proof_data),
        "source_names_extra": max(0, len({c.get("source_name") for c in proof_data.get("citations", {}).values() if c.get("source_name")}) - 3),
        "date": generator["generated_at"],
        "proof_engine_version": generator["version"],
        "sections_narrative": sections_narrative,
        "verdict_declaration": verdict_declaration_str or "",
        "verdict_hook": verdict_hook,
    }


def load_all_proofs(proofs_dir: Path) -> list[dict]:
    proofs_dir = Path(proofs_dir)
    featured_slugs = load_featured_slugs(proofs_dir)
    proofs = []
    for slug_dir in sorted(proofs_dir.iterdir()):
        # Skip dot-prefixed dirs (staging, backups) and non-proof dirs
        if slug_dir.name.startswith("."):
            continue
        if slug_dir.is_dir() and (slug_dir / "proof.json").exists():
            proof = load_proof(slug_dir)
            proof["featured"] = slug_dir.name in featured_slugs
            proofs.append(proof)
    return proofs
