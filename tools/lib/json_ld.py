import json
from tools.lib.verdict import normalize_verdict
from tools.lib.latex_utils import strip_latex

REPO_URL = "https://github.com/yaniv-golan/proof-engine"


def generate_claim_review(
    proof_data: dict,
    canonical_url: str,
    doi: str | None = None,
    concept_doi: str | None = None,
    proof_py_url: str | None = None,
    proof_json_url: str | None = None,
    provenance_url: str | None = None,
) -> str:
    verdict_info = normalize_verdict(proof_data["verdict"])

    claim_review = {
        "@context": "https://schema.org",
        "@type": "ClaimReview",
        "claimReviewed": strip_latex(proof_data["claim_natural"]),
        "reviewRating": {
            "@type": "Rating",
            "ratingValue": verdict_info["rating"],
            "bestRating": 5,
            "worstRating": 1,
            "alternateName": verdict_info["raw"],
        },
        "author": {
            "@type": "Organization",
            "name": "Proof Engine",
            "url": REPO_URL,
        },
        "datePublished": proof_data["generator"]["generated_at"],
        "url": canonical_url,
    }

    if doi:
        claim_review["identifier"] = doi
        same_as = [f"https://doi.org/{doi}"]
        if concept_doi and concept_doi != doi:
            same_as.append(f"https://doi.org/{concept_doi}")
        claim_review["sameAs"] = same_as

    if proof_py_url:
        claim_review["isBasedOn"] = {
            "@type": "SoftwareSourceCode",
            "url": proof_py_url,
            "programmingLanguage": "Python",
            "name": "proof.py",
        }

    if proof_json_url:
        claim_review["mainEntity"] = {
            "@type": "Dataset",
            "url": proof_json_url,
            "name": "proof.json",
            "description": (
                f"Machine-readable proof data for the claim: "
                f"\"{strip_latex(proof_data['claim_natural'])}\". "
                f"Verdict: {verdict_info['raw']}."
            ),
            "encodingFormat": "application/json",
            "creator": {
                "@type": "Organization",
                "name": "Proof Engine",
                "url": REPO_URL,
            },
            "license": "https://opensource.org/licenses/MIT",
        }

    if provenance_url:
        claim_review["about"] = {
            "@type": "CreativeWork",
            "url": provenance_url,
            "name": "provenance.json",
            "encodingFormat": "application/json",
        }

    return json.dumps(claim_review, indent=2)
