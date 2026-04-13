"""Generate RO-Crate 1.1 metadata for a proof."""

FILE_TYPES = {
    "proof.py": {"@type": "SoftwareSourceCode", "name": "Verification Script",
                 "description": "Re-runnable Python script that verifies the claim",
                 "programmingLanguage": "Python", "encodingFormat": "text/x-python"},
    "proof.json": {"@type": "Dataset", "name": "Proof Data",
                   "description": "Machine-readable proof evidence and verdict",
                   "encodingFormat": "application/json"},
    "proof.md": {"@type": "ScholarlyArticle", "name": "Proof Report",
                 "description": "Structured proof report with evidence and conclusion",
                 "encodingFormat": "text/markdown"},
    "proof_audit.md": {"@type": "ScholarlyArticle", "name": "Verification Audit Trail",
                       "description": "Full verification audit with citation details and computation traces",
                       "encodingFormat": "text/markdown"},
    "proof_narrative.md": {"@type": "Article", "name": "Narrative Summary",
                           "description": "Plain-language summary of the proof for general audiences",
                           "encodingFormat": "text/markdown"},
    "provenance.json": {"@type": "CreativeWork", "name": "W3C PROV Provenance",
                        "description": "W3C PROV-JSON provenance chain for the verification",
                        "encodingFormat": "application/json",
                        "conformsTo": {"@id": "http://www.w3.org/ns/prov"}},
    "proof.ipynb": {"@type": "ComputationalNotebook", "name": "Interactive Notebook",
                    "description": "Jupyter Notebook for interactive re-verification",
                    "encodingFormat": "application/x-ipynb+json", "programmingLanguage": "Python"},
}


def generate_ro_crate(proof_data: dict, slug: str, canonical_url: str,
                      available_files: list[str], doi: str | None = None,
                      concept_doi: str | None = None) -> dict:
    verdict = proof_data.get("verdict", {})
    verdict_str = verdict.get("value", "") if isinstance(verdict, dict) else verdict
    generator = proof_data.get("generator", {})
    claim = proof_data.get("claim_natural", "")

    graph = []

    # Metadata descriptor
    graph.append({"@id": "ro-crate-metadata.json", "@type": "CreativeWork",
                  "about": {"@id": "./"}, "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"}})

    # Root dataset
    parts = [{"@id": f} for f in available_files if f in FILE_TYPES]
    root = {"@id": "./", "@type": "Dataset", "name": f"Proof: {claim}",
            "description": f"Verification of: {claim}. Verdict: {verdict_str}.",
            "datePublished": generator.get("generated_at", ""),
            "license": {"@id": "https://opensource.org/licenses/MIT"},
            "url": canonical_url, "hasPart": parts,
            "creator": {"@id": "#proof-engine"},
            "conformsTo": {"@id": "https://yaniv-golan.github.io/proof-engine/proof-schema.json"}}
    if doi:
        root["identifier"] = f"https://doi.org/{doi}"
    if concept_doi and concept_doi != doi:
        root["sameAs"] = f"https://doi.org/{concept_doi}"
    graph.append(root)

    # File entries
    for filename in available_files:
        if filename in FILE_TYPES:
            graph.append({"@id": filename, **FILE_TYPES[filename]})

    # Creator
    graph.append({"@id": "#proof-engine", "@type": "SoftwareApplication",
                  "name": "Proof Engine", "version": generator.get("version", ""),
                  "url": generator.get("repo", "")})

    return {"@context": "https://w3id.org/ro/crate/1.1/context", "@graph": graph}
