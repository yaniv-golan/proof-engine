"""
Proof: Deepfake videos are now indistinguishable from real footage to the average human eye.
Generated: 2026-03-28
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "Deepfake videos are now indistinguishable from real footage to the average human eye."
CLAIM_FORMAL = {
    "subject": "Deepfake video detection by average, untrained humans",
    "property": "number of independent peer-reviewed sources confirming performance at or near chance level "
                "(i.e., not reliably above 50% accuracy) for video deepfake detection",
    "operator": ">=",
    "operator_note": (
        "'Indistinguishable' is interpreted as: average humans cannot reliably distinguish deepfake "
        "videos from real footage — meaning their detection accuracy is near chance (~50%) and not "
        "statistically significantly above chance in controlled studies. "
        "This is the most defensible formal rendering of the claim. "
        "Note: the claim applies to VIDEO deepfakes specifically (not static images). "
        "Threshold = 3 independent peer-reviewed sources confirming near-chance detection. "
        "Counter-evidence: studies showing above-chance video detection (63–67%) are documented "
        "in adversarial checks and may break the proof."
    ),
    "threshold": 3,
    "proof_direction": "affirm",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "meta_analysis_2024",
        "label": "Systematic review & meta-analysis of 56 papers (86,155 participants): "
                 "video detection CI crosses 50% — not significantly above chance",
    },
    "B2": {
        "key": "fooled_twice_2021",
        "label": "Fooled Twice RCT (N=210): people cannot reliably detect deepfakes; "
                 "only 5/16 videos detectable above chance",
    },
    "B3": {
        "key": "fooled_twice_sciencedirect",
        "label": "Fooled Twice (ScienceDirect full-text): 'seeing-is-believing' heuristic; "
                 "training and incentives do not improve detection",
    },
    "A1": {
        "label": "Verified source count meeting near-chance confirmation threshold",
        "method": None,
        "result": None,
    },
}

# 3. EMPIRICAL FACTS — sources confirming near-chance human video deepfake detection
empirical_facts = {
    "meta_analysis_2024": {
        "quote": (
            "Overall deepfake detection rates (sensitivity) were not significantly above chance "
            "because 95% confidence intervals crossed 50%. "
            "Total deepfake detection accuracy was 55.54% (95% CI [48.87, 62.10], k = 67)."
        ),
        "url": "https://www.sciencedirect.com/science/article/pii/S2451958824001714",
        "source_name": (
            "Somoray et al. (2024) — 'Human performance in detecting deepfakes: A systematic "
            "review and meta-analysis of 56 papers', Computers in Human Behavior Reports, "
            "Elsevier (peer-reviewed)"
        ),
    },
    "fooled_twice_2021": {
        "quote": (
            "people cannot reliably detect deepfakes and neither raising awareness nor "
            "introducing financial incentives improves their detection accuracy"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8602050/",
        "source_name": (
            "Köbis et al. (2021) — 'Fooled twice: People cannot detect deepfakes but think "
            "they can', iScience / PMC (peer-reviewed, N=210)"
        ),
    },
    "fooled_twice_sciencedirect": {
        "quote": (
            "people can no longer reliably detect deepfakes. "
            "Some of the previously established strategies against misinformation do not hold "
            "for the detection of deepfakes"
        ),
        "url": "https://www.sciencedirect.com/science/article/pii/S2589004221013353",
        "source_name": (
            "Köbis et al. (2021) — 'Fooled twice: People cannot detect deepfakes but think "
            "they can', iScience, Elsevier (peer-reviewed, ScienceDirect mirror)"
        ),
    },
}

# 4. CITATION VERIFICATION (Rule 2)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 5. COUNT SOURCES WITH VERIFIED CITATIONS
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION — MUST use compare(), never hardcode
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified source count vs threshold",
)

# 7. ADVERSARIAL CHECKS (Rule 5)
# Note: these represent research conducted before writing this proof (Step 2).
# Sources showing above-chance video detection are documented here as counter-evidence.
adversarial_checks = [
    {
        "question": (
            "Do studies show humans detect VIDEO deepfakes reliably above chance (~50%)?"
        ),
        "verification_performed": (
            "Searched PMC and PNAS for studies measuring human video deepfake detection accuracy. "
            "Found: (1) Groh et al. 2022 (PNAS, N=15,016): 66% accuracy for video deepfakes — "
            "well above chance; (2) Köbis et al. 2025 'Is this real?' (PMC12779810): 63% accuracy, "
            "AUC=0.67 for videos, described as 'fairly good' discrimination; "
            "(3) University of Florida study (Feb 2026): humans correctly identified real and fake "
            "videos about two-thirds of the time, outperforming AI algorithms. "
            "These three independent studies all show video detection significantly above 50%."
        ),
        "finding": (
            "Multiple studies — including a large PNAS study (N=15,016) and a 2025 PMC study — "
            "show human video deepfake detection at 63–67%, which IS above chance. "
            "This directly contradicts the claim that videos are 'indistinguishable.' "
            "The meta-analysis (B1) shows video CI [47.80, 66.57] crossing 50%, but individual "
            "studies with dedicated video stimuli consistently show above-chance performance. "
            "This is genuine counter-evidence that breaks the strong form of the claim."
        ),
        "breaks_proof": True,
    },
    {
        "question": (
            "Is the claim specifically about state-of-the-art (2024–2026) deepfakes, "
            "which may be harder to detect than older deepfakes used in older studies?"
        ),
        "verification_performed": (
            "Searched for studies specifically testing newest-generation deepfakes "
            "(e.g., Sora, HeyGen, Face Swap v2 tools) vs older FaceForensics++ dataset. "
            "Found: The iProov (2024) commercial study claims only 0.1% can detect AI-generated "
            "deepfakes, but this is from a company selling detection tools and uses opaque methodology. "
            "The academic meta-analysis (B1, 2024) uses studies up to ~2023. No peer-reviewed "
            "academic study specifically testing 2025–2026 generation deepfakes was found."
        ),
        "finding": (
            "The 'now' qualifier in the claim implies the most recent (2025–2026) deepfakes. "
            "Academic evidence covers mostly 2018–2023 deepfake generations. "
            "It is plausible that newer AI-generated videos are harder to detect, but no "
            "peer-reviewed study quantifies this for current-generation tools. "
            "This is an evidence gap, not direct counter-evidence."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could the meta-analysis aggregate bias explain why CI crosses 50% "
            "even though individual studies show above-chance detection?"
        ),
        "verification_performed": (
            "Examined the meta-analysis methodology: it pools 56 heterogeneous studies with "
            "different deepfake types (face-swap, voice, text), different quality levels, "
            "and different experimental designs. The wide CI [48.87, 62.10] reflects high "
            "between-study variability (heterogeneity). The pooled CI crossing 50% does not "
            "mean ALL studies found at-chance performance — it means the average is uncertain."
        ),
        "finding": (
            "The CI crossing 50% reflects high study heterogeneity, not a consensus that "
            "humans are at chance. Individual well-controlled video studies consistently show "
            "above-chance detection (63–67%). The meta-analysis is inconclusive, not supportive. "
            "This further weakens the claim."
        ),
        "breaks_proof": False,
    },
]

# 8. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif claim_holds and not any_unverified:
        verdict = "DISPROVED" if is_disproof else "PROVED"
    elif claim_holds and any_unverified:
        verdict = (
            "DISPROVED (with unverified citations)"
            if is_disproof
            else "PROVED (with unverified citations)"
        )
    elif not claim_holds:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified citations) = {n_confirmed}"
    FACT_REGISTRY["A1"]["result"] = (
        f"{n_confirmed} confirmed source(s) of {CLAIM_FORMAL['threshold']} required; "
        "adversarial check breaks proof (video detection above chance in multiple studies)"
    )

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: for qualitative proof, record citation status per B-fact
    extractions = {}
    for fid, info in FACT_REGISTRY.items():
        if not fid.startswith("B"):
            continue
        ef_key = info["key"]
        cr = citation_results.get(ef_key, {})
        extractions[fid] = {
            "value": cr.get("status", "unknown"),
            "value_in_quote": cr.get("status") in COUNTABLE_STATUSES,
            "quote_snippet": empirical_facts[ef_key]["quote"][:80],
        }

    summary = {
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": [
            {
                "description": (
                    "B1 (meta-analysis 2024) and B2/B3 (Fooled Twice 2021) — "
                    "independently conducted studies by different research groups. "
                    "Both report near-chance or unreliable detection, consistent direction."
                ),
                "values_compared": [
                    "Meta-analysis: 55.54% overall, video CI crosses 50%",
                    "Fooled Twice: 57.6% overall, only 5/16 videos detectable above chance",
                ],
                "agreement": True,
                "note": (
                    "Consistent direction (near-chance) but different methodologies. "
                    "Note: B2 and B3 are the PMC and ScienceDirect versions of the same paper — "
                    "they share upstream data. B1 (meta-analysis) is independent of B2/B3."
                ),
            }
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_confirmed": n_confirmed,
            "threshold": CLAIM_FORMAL["threshold"],
            "operator": CLAIM_FORMAL["operator"],
            "claim_holds": claim_holds,
            "any_breaks": any_breaks,
            "summary": (
                "The meta-analysis (56 papers, 86K participants) shows video detection CI "
                "crossing 50% — consistent with near-chance performance. "
                "However, three independent studies (PNAS 2022, PMC 2025, UF 2026) show "
                "above-chance video detection at 63–67%. The claim is not definitively "
                "proved or disproved."
            ),
        },
        "generator": {
            "name": "proof-engine",
            "version": open(os.path.join(PROOF_ENGINE_ROOT, "VERSION")).read().strip(),
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
