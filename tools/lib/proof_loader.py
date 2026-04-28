import json
import re
import sys
from pathlib import Path
import yaml

from tools.lib.featured import load_featured_slugs
from tools.lib.narrative_validator import extract_verdict_declaration
from tools.lib.section_extractor import extract_sections, validate_required_sections
from tools.lib.tagger import llm_tag, canonicalize_tag
from tools.lib.verdict import normalize_verdict
from tools.lib.normalize import normalize_to_v3

# --- Section requirements loaded from shared schema ---
def _load_format_schema():
    schema_path = Path(__file__).resolve().parent.parent.parent / \
        "proof-engine" / "skills" / "proof-engine" / "proof_format_schema.json"
    return json.loads(schema_path.read_text())

_FORMAT_SCHEMA = _load_format_schema()
REQUIRED_NARRATIVE_SECTIONS = _FORMAT_SCHEMA["proof_narrative_md"]["required"]

REQUIRED_JSON_KEYS = ["fact_registry", "claim_formal", "claim_natural",
                      "verdict", "key_results", "generator"]

REQUIRED_GENERATOR_KEYS = ["name", "version", "repo", "generated_at"]

REQUIRED_CLAIM_FORMAL_KEYS = []  # claim_formal structure varies by proof type


# Default purpose for proofs that don't explicitly declare CLAIM_FORMAL.purpose.
# Path 3 of the deductive-theorem plan: artifacts now declare their
# value-proposition explicitly. This mapping lets the existing corpus continue
# to work unchanged — every proof gets a sensible default — while new proofs
# can override by setting `purpose` in CLAIM_FORMAL. See proof_types.py for
# the enumeration of valid purpose values.
_PURPOSE_DEFAULT_BY_CLAIM_TYPE = {
    "theorem": "methodology_demonstration",
    "open_problem": "methodology_demonstration",
}


def default_purpose_for_claim_type(claim_type, has_attribution=False):
    """Infer the artifact's purpose from claim_type when CLAIM_FORMAL.purpose
    is not set explicitly. Theorem and open_problem default to
    methodology_demonstration (especially when attribution is present, which
    confirms re-exposition status); all other claim types default to
    fact_verification. The fallback is fact_verification because the bulk of
    the corpus is empirical-claim verification, which is the engine's primary
    product surface."""
    if claim_type in _PURPOSE_DEFAULT_BY_CLAIM_TYPE:
        return _PURPOSE_DEFAULT_BY_CLAIM_TYPE[claim_type]
    return "fact_verification"


def resolve_purpose(claim_formal):
    """Return the artifact's purpose, preferring an explicit `purpose` field
    in claim_formal and falling back to default_purpose_for_claim_type."""
    explicit = claim_formal.get("purpose")
    if explicit:
        return explicit
    claim_type = claim_formal.get("claim_type", "")
    has_attribution = bool(claim_formal.get("attribution"))
    return default_purpose_for_claim_type(claim_type, has_attribution)


def extract_source_names(proof_data, max_sources=3):
    """Extract unique source names from v3 evidence map."""
    evidence = proof_data.get("evidence", {})
    seen = set()
    names = []
    for entry in evidence.values():
        if entry.get("type") == "empirical":
            name = entry.get("source", {}).get("name", "")
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

    # Validate required keys and determine format version
    original_format_version = proof_data.get("format_version", 1)
    format_version = original_format_version
    if format_version == 3:
        v3_required = ["claim_formal", "claim_natural", "evidence",
                       "verdict", "key_results", "generator"]
        for key in v3_required:
            if key not in proof_data:
                raise ValueError(f"{slug}: proof.json missing required key: {key}")
    else:
        for key in REQUIRED_JSON_KEYS:
            if key not in proof_data:
                raise ValueError(f"{slug}: proof.json missing required key: {key}")

        # Normalize v1/v2 to v3 in memory — single code path from here on.
        # The on-disk proof.json is NOT modified (migration is Task 6).
        proof_data = normalize_to_v3(proof_data)
        format_version = 3

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

    # Use the original format version (not the normalized one) for section validation,
    # since v1 proofs don't have the same required sections as v2+.
    # claim_type == "theorem" dispatches to the v2_theorem profile (paper-shaped
    # canonical theorem-proof sections); see proof_format_schema.json.
    claim_type = proof_data.get("claim_formal", {}).get("claim_type")
    profile = (
        "v2_theorem" if claim_type == "theorem"
        else ("v2" if original_format_version >= 2 else "v1")
    )
    required_md = _FORMAT_SCHEMA["proof_md"][profile]["required"]
    optional_md = _FORMAT_SCHEMA["proof_md"][profile].get("optional", [])
    required_audit = _FORMAT_SCHEMA["proof_audit_md"][profile]["required"]
    optional_audit = _FORMAT_SCHEMA["proof_audit_md"][profile].get("optional", [])

    missing = validate_required_sections(sections_md, required_md)
    if missing:
        raise ValueError(f"{slug}: proof.md missing required sections: {missing}. Found: {sorted(sections_md.keys())}")

    # Extract sections from proof_audit.md
    audit_md = (proof_dir / "proof_audit.md").read_text()
    sections_audit = extract_sections(audit_md)

    # Validate required audit sections
    missing_audit_req = validate_required_sections(sections_audit, required_audit)
    if missing_audit_req:
        raise ValueError(f"{slug}: proof_audit.md missing required sections: {missing_audit_req}. Found: {sorted(sections_audit.keys())}")

    # Warn about missing optional sections
    missing_audit = validate_required_sections(sections_audit, optional_audit)
    if missing_audit:
        print(f"WARNING: {slug}: proof_audit.md missing optional sections: {missing_audit}. Found: {sorted(sections_audit.keys())}",
              file=sys.stderr)

    # Conditional audit sections from schema
    for cond in _FORMAT_SCHEMA["proof_audit_md"].get("conditional", []):
        section_name = cond["section"]
        if profile in cond.get("applies_to", []):
            if section_name == "Type S (Search) Facts":
                has_search = any(
                    e.get("type") == "search"
                    for e in proof_data.get("evidence", {}).values()
                )
                if has_search and section_name not in sections_audit:
                    print(
                        f"WARNING: {slug}: proof_audit.md missing '{section_name}' section "
                        f"(expected for absence proofs with search_registry)",
                        file=sys.stderr,
                    )

    missing_md_opt = validate_required_sections(sections_md, optional_md)
    if missing_md_opt:
        print(f"WARNING: {slug}: proof.md missing optional sections: {missing_md_opt}. Found: {sorted(sections_md.keys())}",
              file=sys.stderr)

    # Extract sections from proof_narrative.md
    narrative_path = proof_dir / "proof_narrative.md"
    if not narrative_path.exists():
        raise ValueError(f"{slug}: missing required artifact: proof_narrative.md")
    narrative_md = narrative_path.read_text()
    sections_narrative = extract_sections(narrative_md)
    missing_narrative = validate_required_sections(sections_narrative, REQUIRED_NARRATIVE_SECTIONS)
    if missing_narrative:
        raise ValueError(f"{slug}: proof_narrative.md missing required sections: {missing_narrative}. Found: {sorted(sections_narrative.keys())}")

    # Parse verdict declaration and hook from narrative
    verdict_declaration_str, verdict_hook = extract_verdict_declaration(
        sections_narrative.get("Verdict", "")
    )

    # Tags: meta.yaml cache or generate via LLM and cache
    meta_path = proof_dir / "meta.yaml"
    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text()) or {}
        if "featured" in meta:
            raise ValueError(
                f"{slug}: meta.yaml contains deprecated 'featured' key — "
                f"featured status is now managed via site/proofs/featured.json"
            )
    else:
        meta = {}

    if meta.get("tags_manual") and "tags" not in meta:
        raise ValueError(
            f"{slug}: meta.yaml has tags_manual: true but no tags — "
            f"manual tagging requires explicit tags list"
        )

    if "tags" in meta:
        tags = [canonicalize_tag(t) for t in meta["tags"]]
    else:
        tags = llm_tag(proof_data["claim_natural"])
        meta["tags"] = tags
        meta_path.write_text(yaml.dump(meta, default_flow_style=False))

    # depends_on: parse + proof-local checks. Cross-proof checks run later
    # (proof-site.py publish, build-site.py validate_repo).
    from tools.lib.depends_on import parse_depends_on, check_local
    depends_on_entries, dep_errors = parse_depends_on(
        meta, source=str(meta_path),
    )
    dep_errors.extend(check_local(depends_on_entries, candidate_slug=slug))
    if dep_errors:
        raise ValueError(
            f"{slug}: meta.yaml depends_on invalid:\n  "
            + "\n  ".join(dep_errors)
        )

    # Citation/search counts — always v3 after normalization
    evidence = proof_data.get("evidence", {})
    citation_count = sum(1 for e in evidence.values() if e.get("type") == "empirical")
    search_count = sum(1 for e in evidence.values() if e.get("type") == "search")
    citation_count = citation_count if citation_count > 0 else None
    search_count = search_count if search_count > 0 else None

    return {
        "slug": slug,
        "proof_data": proof_data,
        "format_version": format_version,
        "purpose": resolve_purpose(proof_data.get("claim_formal", {})),
        "sections_md": sections_md,
        "sections_audit": sections_audit,
        "verdict": verdict,
        "tags": tags,
        "depends_on": depends_on_entries,
        "featured": False,
        "citation_count": citation_count,
        "search_count": search_count,
        "verdict_summary": extract_verdict_summary(
            sections_md, verdict["raw"]
        ),
        "source_names": extract_source_names(proof_data),
        "source_names_extra": max(0, len({e.get("source", {}).get("name") for e in proof_data.get("evidence", {}).values()
                                          if e.get("type") == "empirical" and e.get("source", {}).get("name")}) - 3),
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
