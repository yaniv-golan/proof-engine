# Citation-Audit Template (Type R — Reference Audit)

> You are reading one template. See [proof-templates.md](proof-templates.md) for the full index and selection guidance.

For claims that assert specific bibliographic citations exist with claimed attributes — e.g., "Smith et al. (2023) in *Nature* showed X" — and where the operative question is "do those references actually exist as claimed?" Hallucinated citations are a top LLM failure mode; this template wires `verify_citation_record` and the `compare_metadata` verdict taxonomy into a formal proof structure.

**When to use:**
- Claim takes the form: "Paper X by author Y in journal Z (year W) reports finding F"
- Paper X has a structured identifier (DOI, PMID, arXiv ID, Handle) you can resolve
- You want to verify both that the paper exists AND that the bibliographic metadata matches

**Not for:** Claims that depend on quote-on-page verification of paper *contents*. For those, use the qualitative or compound templates — `verify_citation()` handles the quote-on-page check.

**Verdict taxonomy** (from `compare_metadata`):
- `genuine` — identifier resolves and every checked field matches → citation is real and correctly attributed
- `metadata_chimera` — identifier resolves but at least one of journal/year/DOI doesn't match the claim → real paper, forged bibliography
- `title_chimera` — identifier resolves to a paper with a clearly different title → wrong paper for the identifier
- `partial_match` — ambiguous (title in 0.50–0.85 similarity band) — needs manual review
- `unresolvable` — identifier doesn't resolve to any record → fabricated identifier OR record removed
- `fetch_failed` — registry lookup couldn't complete — re-run with network or a snapshot

```python
"""
Proof: [audit claim text, e.g., "All references in passage P resolve to genuine
publications matching the claimed bibliographic metadata"]
Generated: [date]
"""
import os
import sys

_SKILL_EXCLUDED_DIRS = {".git", ".venv", "venv", ".tox", ".worktrees",
                        ".cache", ".idea", ".vscode", "node_modules",
                        "__pycache__", "site-packages", "dist", "build"}

def _is_valid_skill_root(p):
    return (os.path.isfile(os.path.join(p, "scripts", "verify_citations.py"))
            and os.path.isfile(os.path.join(p, "SKILL.md")))

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        for _cand in (
            os.path.join(_d, "proof-engine", "skills", "proof-engine"),
            os.path.join(_d, "skills", "proof-engine"),
        ):
            if _is_valid_skill_root(_cand):
                PROOF_ENGINE_ROOT = _cand
                break
        if PROOF_ENGINE_ROOT:
            break
        try:
            for _sib in os.listdir(_d):
                if _sib in _SKILL_EXCLUDED_DIRS:
                    continue
                _sib_path = os.path.join(_d, _sib)
                if not os.path.isdir(_sib_path):
                    continue
                for _cand in (
                    os.path.join(_sib_path, "skills", "proof-engine"),
                    os.path.join(_sib_path, "proof-engine", "skills", "proof-engine"),
                ):
                    if _is_valid_skill_root(_cand):
                        PROOF_ENGINE_ROOT = _cand
                        break
                if PROOF_ENGINE_ROOT:
                    break
                if _sib.startswith("."):
                    try:
                        for _sub in os.listdir(_sib_path):
                            if _sub in _SKILL_EXCLUDED_DIRS:
                                continue
                            _cand = os.path.join(_sib_path, _sub, "skills", "proof-engine")
                            if _is_valid_skill_root(_cand):
                                PROOF_ENGINE_ROOT = _cand
                                break
                    except OSError:
                        pass
                    if PROOF_ENGINE_ROOT:
                        break
        except OSError:
            pass
        if PROOF_ENGINE_ROOT:
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError(
            "PROOF_ENGINE_ROOT not set and skill dir not found via walk-up "
            f"or sibling search from {os.path.dirname(os.path.abspath(__file__))}. "
            "Set the env var explicitly: "
            "export PROOF_ENGINE_ROOT=/path/to/skills/proof-engine"
        )
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date

from proof_citations import verify_citation_record
from scripts.computations import compare, apply_verdict_qualifier
from scripts.proof_summary import ProofSummaryBuilder

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "[Reproduce the claim text exactly.]"
CLAIM_FORMAL = {
    "subject": "the cited references in [source passage / paragraph]",
    "claim_type": "citation_audit",
    "property": "every cited reference resolves to a genuine record with matching bibliographic metadata",
    "operator": "==",
    "threshold": "all_genuine",
    "operator_note": (
        "PROVED if every reference returns verdict 'genuine'. "
        "DISPROVED if any reference returns 'metadata_chimera', 'title_chimera', "
        "or 'unresolvable' (fabrication detected). "
        "UNDETERMINED if any reference returns 'partial_match' or 'fetch_failed' "
        "and no fabrication is detected — needs manual review."
    ),
    "proof_direction": "disprove",  # set to "disprove" if claim asserts fabrication
}

# 2. CITED REFERENCES — one entry per citation appearing in the source passage.
# Each `identifier` is a (type, value) tuple or a "type:value" string.
# `expected` carries the claimed bibliographic attributes — these are what
# `verify_citation_record` compares the resolved record against.
cited_references = {
    "R1": {
        "identifier": ("pmid", "12345678"),
        "expected": {
            "title": "...",
            "journal": "...",
            "year": 2023,
            "doi": "10.1234/example",
            # Optional: "authors": ["Smith J", "Doe A"]
        },
        "context": "Cited in passage paragraph 1 as 'Smith et al. (2023) in Nature'.",
    },
    "R2": {
        "identifier": ("doi", "10.1038/s41586-022-12345-6"),
        "expected": {
            "title": "...",
            "journal": "Nature",
            "year": 2022,
        },
        "context": "Cited in passage paragraph 2 as supporting evidence for ...",
    },
    # Add one entry per reference being audited.
}

# 3. RUN THE AUDIT
audit_results = {}
for ref_id, ref in cited_references.items():
    print(f"Auditing {ref_id}: {ref['identifier']}")
    result = verify_citation_record(ref["identifier"], ref["expected"])
    audit_results[ref_id] = result
    print(f"  Verdict: {result['verdict']} — {result['message']}")

# 4. CLASSIFY RESULTS
GENUINE = "genuine"
FABRICATION_VERDICTS = ("metadata_chimera", "title_chimera", "unresolvable")
NEEDS_REVIEW_VERDICTS = ("partial_match", "fetch_failed")

n_genuine = sum(1 for r in audit_results.values() if r["verdict"] == GENUINE)
n_fabricated = sum(1 for r in audit_results.values() if r["verdict"] in FABRICATION_VERDICTS)
n_needs_review = sum(1 for r in audit_results.values() if r["verdict"] in NEEDS_REVIEW_VERDICTS)
n_total = len(cited_references)

print(f"\nAudit summary: {n_genuine}/{n_total} genuine, "
      f"{n_fabricated}/{n_total} fabricated, {n_needs_review}/{n_total} need review")

# 5. CLAIM EVALUATION
# A1: count of genuine references — claim holds iff every reference is genuine
# AND no references need manual review
all_genuine = compare(n_genuine, "==", n_total, label="all references resolve and match")
any_fabricated = compare(n_fabricated, ">", 0, label="any reference shows fabrication")
any_needs_review = compare(n_needs_review, ">", 0, label="any reference needs manual review")

# 6. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "Could a 'genuine' verdict mask a forged identifier that happens to resolve to a real paper?",
        "verification_performed": (
            "compare_metadata checks title (≥0.85 similarity) PLUS at least one of "
            "journal/year/DOI. A forged identifier resolving to the wrong paper would "
            "trip the title check (becomes 'title_chimera') or fail field matches "
            "(becomes 'metadata_chimera')."
        ),
        "finding": "Verdict taxonomy distinguishes these cases; 'genuine' is robust to identifier-only forgery.",
        "breaks_proof": False,
    },
    {
        "question": "Could a transient registry outage cause a 'fetch_failed' verdict that masks fabrication?",
        "verification_performed": (
            "Re-ran each fetch_failed reference at least once after delay. If the "
            "result persists, treat as UNDETERMINED rather than PROVED/DISPROVED."
        ),
        "finding": "[Document re-run results here. If still fetch_failed, mark UNDETERMINED.]",
        "breaks_proof": False,
    },
]

# 7. VERDICT
if __name__ == "__main__":
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif any_needs_review and not any_fabricated:
        base_verdict = "UNDETERMINED"
    elif any_fabricated:
        # Fabrication detected
        base_verdict = "PROVED" if is_disproof else "DISPROVED"
    elif all_genuine:
        # No fabrication, no review needed
        base_verdict = "DISPROVED" if is_disproof else "PROVED"
    else:
        base_verdict = "UNDETERMINED"

    verdict = apply_verdict_qualifier(base_verdict, any_unverified=False)

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    # Emit one Type R fact per reference
    for ref_id, ref in cited_references.items():
        result = audit_results[ref_id]
        identifier_str = (f"{ref['identifier'][0]}:{ref['identifier'][1]}"
                          if isinstance(ref['identifier'], tuple) else ref['identifier'])
        # Reuse add_empirical_fact shape — Type R is a structured-metadata audit,
        # which is a specialization of empirical citation verification.
        builder.add_empirical_fact(
            ref_id,
            label=f"Audit of {identifier_str}",
            source_name=ref.get("expected", {}).get("journal", "unknown"),
            source_url=f"https://doi.org/{ref['expected']['doi']}" if ref.get("expected", {}).get("doi") else "",
            source_quote=ref.get("context", ""),
            sub_claim=None,
        )
        builder.set_verification(
            ref_id,
            status=("verified" if result["verdict"] == GENUINE
                    else "not_found" if result["verdict"] in FABRICATION_VERDICTS
                    else "partial"),
            method="citation_record_audit",
            coverage_pct=None,
            fetch_mode="registry",
            credibility={"source_type": "registry_lookup",
                         "verdict": result["verdict"],
                         "mismatches": result.get("mismatches", [])},
        )

    builder.add_computed_fact(
        "A1",
        label="Genuine reference count",
        method=f"count(verdict == 'genuine') = {n_genuine}",
        result=n_genuine,
        depends_on=list(cited_references.keys()),
    )

    for ac in adversarial_checks:
        builder.add_adversarial_check(
            question=ac["question"],
            verification_performed=ac["verification_performed"],
            finding=ac["finding"],
            breaks_proof=ac["breaks_proof"],
        )

    builder.set_verdict(base_verdict, any_unverified=False)
    builder.set_key_results(
        n_genuine=n_genuine,
        n_fabricated=n_fabricated,
        n_needs_review=n_needs_review,
        n_total=n_total,
    )
    builder.emit()
```

**Key design points:**

- **Verdict taxonomy is authoritative.** The four `compare_metadata` outcomes (`genuine` / `metadata_chimera` / `title_chimera` / `partial_match`) are what the proof rests on — don't reinvent them. The taxonomy specifically catches "real DOI, forged journal" (`metadata_chimera`) and "DOI resolves to a different paper" (`title_chimera`) — the LLM-fabrication failure modes that quote-on-page checks can't see.
- **`expected` minimum keys.** At minimum populate `title`, `journal`, `year`. DOI is strongly recommended when available. Empty `expected` returns `verdict: "no_expected"` which is useful for harvesting metadata but doesn't prove anything about the citation's correctness.
- **Re-run `fetch_failed`.** Registry endpoints (PubMed E-utilities, Crossref, DataCite) occasionally throttle. Always re-run fetch_failed before treating as UNDETERMINED. If still failing after retry, the proof's verdict is genuinely UNDETERMINED — not PROVED or DISPROVED.
- **proof_direction.** Set `proof_direction: "disprove"` when the claim being audited is "these citations are fabricated" — then `any_fabricated → PROVED` (you've proved the fabrication). Default direction is `prove` (you're vouching for the citations being genuine).
- **CLI alternative.** For one-off audits without a formal proof, use the bundled CLI: `proof-citations verify-records --input refs.json --pretty`. The JSON input has the same shape as `cited_references` here. The proof template wraps that workflow with verdict logic, adversarial checks, and structured output for downstream consumers.

**Adversarial check checklist (Rule 5):**
- Identifier-only forgery: addressed by title check in `compare_metadata`.
- Transient registry outage: re-run fetch_failed entries.
- Partial-match ambiguity: 0.50–0.85 title similarity → manual review, never auto-PROVED.
- Wrong identifier type for source: e.g., claiming a DOI but providing an arXiv ID. The `identify()` helper normalizes URL forms.

**Validator interactions:**
- Rule 6 (cross-checks): not directly applicable — a citation audit is a per-reference structured check, not a multi-source consensus. The validator accepts `claim_type: "citation_audit"` and skips the source-count warning.
- Rule 1 (no hand-typed values): each `expected` field comes from the source passage being audited. Quote the passage verbatim in `cited_references[*]["context"]` so reviewers can compare.

**See also:** [environment-and-sources.md](environment-and-sources.md) for E-utilities usage notes; [hardening-rules.md](hardening-rules.md) Rule 2 for the broader citation-verification family this template specializes.
