"""
Proof: Sunscreen is more dangerous due to chemical absorption and vitamin D blocking
       than moderate sun exposure.
Generated: 2026-03-31
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        if os.path.isdir(os.path.join(_d, "proof-engine", "skills", "proof-engine", "scripts")):
            PROOF_ENGINE_ROOT = os.path.join(_d, "proof-engine", "skills", "proof-engine")
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError("PROOF_ENGINE_ROOT not set and skill dir not found via walk-up from proof.py")
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ── Rule 3: Anchor to system time ──────────────────────────────────────────────
PROOF_GENERATION_DATE = date(2026, 3, 31)
actual = date.today()
if actual == PROOF_GENERATION_DATE:
    today = PROOF_GENERATION_DATE
    date_note = "System date matches proof generation date"
else:
    today = actual
    date_note = f"Proof generated for {PROOF_GENERATION_DATE}, running on {actual}"
print(f"  Date: {today} ({date_note})")

# ── Rule 4: Explicit claim interpretation ──────────────────────────────────────
CLAIM_NATURAL = (
    "Sunscreen is more dangerous due to chemical absorption and vitamin D blocking "
    "than moderate sun exposure."
)
CLAIM_FORMAL = {
    "subject": "Chemical sunscreen",
    "property": "comparative harm vs. moderate sun exposure",
    "operator": ">=",
    "operator_note": (
        "The claim asserts sunscreen is MORE dangerous than moderate sun exposure, "
        "citing two mechanisms: (1) systemic absorption of chemical UV filters and "
        "(2) reduction of vitamin D synthesis. Interpreted as: the combined harm of "
        "sunscreen use >= the harm of moderate unprotected sun exposure. "
        "We DISPROVE this by gathering authoritative sources showing: "
        "(a) chemical absorption is documented but no human harm has been demonstrated; "
        "(b) real-world vitamin D reduction from sunscreen is minimal — population "
        "studies show no significant difference in vitamin D levels between sunscreen "
        "users and non-users with equivalent outdoor exposure; "
        "(c) UV radiation is the dominant cause of skin cancer (~86-90% of cases); and "
        "(d) sunscreen use reduces melanoma risk by ~50% and squamous cell carcinoma "
        "by ~40%. Threshold: 3 or more independently verified authoritative sources "
        "must reject the claim's conclusion for a DISPROVED verdict."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# ── Fact Registry ──────────────────────────────────────────────────────────────
FACT_REGISTRY = {
    "B1": {
        "key": "source_aad",
        "label": "American Academy of Dermatology: absorbed ingredients not proven harmful",
    },
    "B2": {
        "key": "source_mdanderson",
        "label": "MD Anderson Cancer Center: no medical evidence sunscreen causes cancer; UV does",
    },
    "B3": {
        "key": "source_pmc_cmaj",
        "label": "PMC/CMAJ 2020: high-quality evidence sunscreen reduces melanoma and nonmelanoma cancer",
    },
    "B4": {
        "key": "source_pmc_vitd",
        "label": "PMC 2022 expert panel: sunscreen does not limit vitamin D production in real-world use",
    },
    "B5": {
        "key": "source_skincancer",
        "label": "Skin Cancer Foundation: ~90% of nonmelanoma skin cancers associated with UV exposure",
    },
    "A1": {
        "label": "Verified disproof source count",
        "method": None,
        "result": None,
    },
}

# ── Empirical Facts — sources that REJECT the claim (confirm it is false) ─────
# (Rule 5: adversarial sources supporting the claim go in adversarial_checks only)
empirical_facts = {
    "source_aad": {
        "quote": (
            "Just because an ingredient is absorbed into the bloodstream does not mean "
            "that it is harmful or unsafe."
        ),
        "url": "https://www.aad.org/media/stats-sunscreen",
        "source_name": "American Academy of Dermatology — Sunscreen FAQs",
    },
    "source_mdanderson": {
        "quote": (
            "There is no medical evidence that sunscreen causes cancer. However, there is "
            "a lot of evidence that UV rays from the sun and tanning beds do."
        ),
        "url": "https://www.mdanderson.org/cancerwise/sunscreen-myths-debunked.h00-159697545.html",
        "source_name": "MD Anderson Cancer Center — Sunscreen Myths Debunked",
    },
    "source_pmc_cmaj": {
        "quote": (
            "High-quality evidence has shown that sunscreen reduces the risk of developing "
            "both melanoma and nonmelanoma skin cancer."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7759112/",
        "source_name": "PMC / CMAJ — Efficacy and Safety of Sunscreen (2020)",
    },
    "source_pmc_vitd": {
        "quote": (
            "Sunscreens can be effective in preventing erythema from solar exposure without "
            "limiting the benefits with respect to vitamin D production."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9002342/",
        "source_name": "PMC — Sunscreen and Vitamin D Expert Panel (2022)",
    },
    "source_skincancer": {
        "quote": (
            "About 90 percent of nonmelanoma skin cancers are associated with exposure to "
            "ultraviolet (UV) radiation from the sun."
        ),
        "url": "https://www.skincancer.org/skin-cancer-information/skin-cancer-facts/",
        "source_name": "Skin Cancer Foundation — Skin Cancer Facts & Statistics",
    },
}

# ── Rule 2: Citation verification ─────────────────────────────────────────────
print("\nVerifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ── Count sources with verified citations ─────────────────────────────────────
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# ── Rule 7: Use compare() — never hardcode claim_holds ────────────────────────
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified disproof sources vs threshold",
)

# ── Rule 5: Adversarial checks — search for evidence SUPPORTING the claim ─────
adversarial_checks = [
    {
        "question": (
            "Does the FDA's own research confirm that sunscreen chemicals are absorbed, "
            "potentially supporting the danger claim?"
        ),
        "verification_performed": (
            "Searched for 'FDA sunscreen chemical absorption oxybenzone bloodstream JAMA 2019 2020'. "
            "Found two FDA-sponsored JAMA studies (2019 and 2020) confirming that oxybenzone and "
            "other ingredients are absorbed into the bloodstream at concentrations exceeding the "
            "FDA threshold of 0.5 ng/mL. Oxybenzone reached up to 258.1 ng/mL and remained "
            "detectable for up to 21 days. However, both study authors explicitly stated: "
            "'These findings do not indicate that individuals should refrain from the use of "
            "sunscreen.' The FDA called for more research but did not conclude harm."
        ),
        "finding": (
            "FDA studies confirm absorption is real (oxybenzone up to 258 ng/mL, persisting "
            "21 days), but the studies' own authors explicitly state this does not mean sunscreen "
            "should be avoided. Absorption documented; harm from that absorption: not demonstrated."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there evidence that oxybenzone or other absorbed chemicals disrupt hormones "
            "or cause cancer in humans at realistic exposure levels?"
        ),
        "verification_performed": (
            "Searched for 'oxybenzone endocrine disruptor humans evidence cancer realistic exposure'. "
            "Harvard Health and NYP/Weill Cornell both report that studies showing hormone disruption "
            "used concentrations equivalent to approximately 277 years of daily sunscreen application. "
            "Human volunteer studies confirmed no biologically significant alterations in reproductive "
            "hormones at real-world exposure levels. Oxybenzone has been in use since 1978 with no "
            "demonstrated human carcinogenicity."
        ),
        "finding": (
            "Animal-model endocrine effects require ~277 years of equivalent daily human use. "
            "Human studies show no biologically significant reproductive hormone changes. "
            "No human carcinogenicity has been demonstrated after decades of use."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does sunscreen use lead to clinically significant vitamin D deficiency "
            "in real-world populations?"
        ),
        "verification_performed": (
            "Searched for 'sunscreen vitamin D deficiency real world population studies clinical'. "
            "PMC 2022 expert panel found that population studies of outdoor individuals (vacationers) "
            "showed vitamin D levels 'did not seem to differ between those applying sunscreen and "
            "those who did not, with exposure time and body surface area exposed being equivalent.' "
            "Real-world sunscreen application is typically incomplete; shorter UVB wavelengths that "
            "drive vitamin D synthesis are also attenuated by the ozone layer, partially compensating. "
            "The Skin Cancer Foundation recommends dietary sources and supplements as the safe route "
            "to vitamin D rather than UV exposure."
        ),
        "finding": (
            "Real-world population studies show no significant difference in vitamin D levels between "
            "sunscreen users and non-users given equivalent outdoor exposure time. Laboratory-controlled "
            "reductions do not translate to clinically meaningful deficiency in practice. "
            "Dietary supplementation is the recommended and safe vitamin D source."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Are there peer-reviewed studies directly concluding that sunscreen is more dangerous "
            "than moderate unprotected sun exposure on a net-harm basis?"
        ),
        "verification_performed": (
            "Searched for 'sunscreen more dangerous sun exposure net harm peer reviewed evidence'. "
            "Harvard Health explains that studies where sunscreen users appeared to have higher cancer "
            "rates reflect behavioral confounding: people who use more sunscreen tend to spend more time "
            "in the sun, reversing the causal arrow. MD Anderson, AAD, and the Skin Cancer Foundation "
            "all explicitly reject the conclusion that sunscreen causes net harm exceeding sun exposure. "
            "No peer-reviewed study was found concluding sunscreen use causes greater net harm than "
            "moderate unprotected sun exposure."
        ),
        "finding": (
            "No peer-reviewed studies support this conclusion. The observed correlation is reversed "
            "causation: higher-sunscreen users get more sun, not cancer from sunscreen. All major "
            "medical institutions — AAD, MD Anderson, Skin Cancer Foundation, CDC — explicitly "
            "reject the claim."
        ),
        "breaks_proof": False,
    },
]

# ── Verdict and structured output ─────────────────────────────────────────────
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

    FACT_REGISTRY["A1"]["method"] = (
        f"count(verified disproof citations) = {n_confirmed}"
    )
    FACT_REGISTRY["A1"]["result"] = str(n_confirmed)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # For qualitative proofs: extractions record citation verification status
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
                "description": "Multiple independent authoritative institutions consulted",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources span distinct institution types: professional medical association "
                    "(AAD), major cancer research and treatment center (MD Anderson), "
                    "peer-reviewed academic literature (PMC/CMAJ 2020), international expert "
                    "consensus panel (PMC 2022), and an independent cancer prevention foundation "
                    "(Skin Cancer Foundation). All five are institutionally independent with no "
                    "shared authorship."
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
