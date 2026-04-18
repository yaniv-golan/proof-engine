"""
Proof: Lectins in nightshades like tomatoes and potatoes and grains cause widespread inflammation and leaky gut.
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

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    "Lectins in nightshades like tomatoes and potatoes and grains cause "
    "widespread inflammation and leaky gut."
)

CLAIM_FORMAL = {
    "subject": "Dietary lectins from nightshades (tomatoes, potatoes) and grains",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "Lectins are present in nightshades (tomatoes, potatoes) and grains",
            "proof_direction": "affirm",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC1 tests the premise: do nightshades and grains contain lectins? "
                "Affirm direction: 2+ authoritative sources confirm lectin presence. "
                "Threshold of 2 is appropriate because lectin presence in these foods is "
                "scientifically undisputed — a higher threshold would not add meaningful "
                "verification for an established biochemical fact."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "Dietary lectins from normally consumed nightshades and grains cause "
                "widespread inflammation and leaky gut in the general population"
            ),
            "proof_direction": "disprove",
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC2 tests the causative claim. Disprove direction: 3+ independent authoritative "
                "medical/scientific sources must explicitly state there is no strong human evidence "
                "for lectins in normal dietary contexts causing widespread inflammation or leaky gut. "
                "'Widespread' means affecting the general population eating normally prepared foods, "
                "not rare or high-dose exposures. Key distinction: raw or very high-dose lectins "
                "(e.g., raw kidney beans) can cause acute GI illness; this proof addresses the "
                "popular claim that cooked/normally consumed nightshades and grains drive systemic "
                "inflammation and intestinal permeability in the general population. "
                "Threshold of 3 from independent institutions is required for scientific disproof."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "The full claim asserts both that lectins exist in these foods (SC1) AND that they cause "
        "widespread inflammation and leaky gut (SC2). SC1 is affirmed if 2+ sources confirm lectin "
        "presence. SC2 is disproved if 3+ authoritative sources reject the causative claim. "
        "If SC1 holds but SC2 is disproved, the compound verdict is PARTIALLY VERIFIED: lectins "
        "are present (true) but the causal claim is contradicted by scientific evidence."
    ),
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {
        "key": "sc1_banner_health",
        "label": "SC1: Banner Health — lectins found in nightshades (tomatoes, potatoes) and grains",
    },
    "B2": {
        "key": "sc1_harvard",
        "label": "SC1: Harvard T.H. Chan Nutrition Source — lectins in grains and legumes",
    },
    "B3": {
        "key": "sc2_md_anderson",
        "label": "SC2: MD Anderson Cancer Center — no strong human evidence for lectin-induced inflammation",
    },
    "B4": {
        "key": "sc2_harvard",
        "label": "SC2: Harvard T.H. Chan Nutrition Source — very limited human research on dietary lectin health effects",
    },
    "B5": {
        "key": "sc2_cornell",
        "label": "SC2: Cornell Center for Nutrition Studies — lectin-hazard argument not supported",
    },
    "A1": {"label": "SC1 verified source count (lectin presence)", "method": None, "result": None},
    "A2": {"label": "SC2 verified refuting source count (causation rejected)", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — SC1 (affirm: sources confirming lectin presence in nightshades and grains)
sc1_empirical_facts = {
    "sc1_banner_health": {
        "quote": "Vegetables: Nightshades like tomatoes, potatoes and eggplants",
        "url": "https://www.bannerhealth.com/healthcareblog/teach-me/are-lectins-in-your-diet-bad-for-your-gut",
        "source_name": "Banner Health (major US health system)",
    },
    "sc1_harvard": {
        "quote": (
            "They are found in all plants, but raw legumes (beans, lentils, peas, soybeans, peanuts) "
            "and whole grains like wheat contain the highest amounts of lectins."
        ),
        "url": "https://nutritionsource.hsph.harvard.edu/anti-nutrients/lectins/",
        "source_name": "Harvard T.H. Chan School of Public Health — The Nutrition Source",
    },
}

# 4. EMPIRICAL FACTS — SC2 (disprove: sources REJECTING the widespread inflammation/leaky gut claim)
sc2_empirical_facts = {
    "sc2_md_anderson": {
        "quote": (
            "Aside from Celiac disease, which is specific to gluten, there is currently no strong "
            "evidence in human studies to support the claim that foods high in lectins consistently "
            "cause inflammation."
        ),
        "url": "https://www.mdanderson.org/cancerwise/should-you-eat-a-lectin-free-diet.h00-159695178.html",
        "source_name": "MD Anderson Cancer Center",
    },
    "sc2_harvard": {
        "quote": (
            "There is very limited research in humans on the amount of active lectins consumed "
            "in the diet and their long-term health effects."
        ),
        "url": "https://nutritionsource.hsph.harvard.edu/anti-nutrients/lectins/",
        "source_name": "Harvard T.H. Chan School of Public Health — The Nutrition Source",
    },
    "sc2_cornell": {
        "quote": "Dr. Gundry has not made a convincing argument that lectins as a class are hazardous.",
        "url": "https://nutritionstudies.org/the-plant-paradox-by-steven-grundy-md-commentary/",
        "source_name": "Cornell University Center for Nutrition Studies",
    },
}

# Combine all facts for verify_all_citations
empirical_facts = {**sc1_empirical_facts, **sc2_empirical_facts}

# 5. CITATION VERIFICATION (Rule 2)
print("Verifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# 6. COUNT SOURCES
COUNTABLE_STATUSES = ("verified", "partial")

n_sc1_confirmed = sum(
    1 for key in sc1_empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  SC1 confirmed sources: {n_sc1_confirmed} / {len(sc1_empirical_facts)}")

n_sc2_confirmed = sum(
    1 for key in sc2_empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  SC2 confirmed refuting sources: {n_sc2_confirmed} / {len(sc2_empirical_facts)}")

# 7. CLAIM EVALUATION — MUST use compare(), never hardcode
sc1_holds = compare(
    n_sc1_confirmed, ">=", 2,
    label="SC1: lectin presence — verified source count vs threshold"
)
sc2_disproved = compare(
    n_sc2_confirmed, ">=", 3,
    label="SC2: causation rejection — verified refuting source count vs threshold"
)

# 8. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": (
            "Do any peer-reviewed human clinical trials demonstrate that lectins in normally "
            "cooked nightshades or grains cause chronic inflammation?"
        ),
        "verification_performed": (
            "Searched for 'lectin inflammation human clinical trial cooked foods nightshades'. "
            "Reviewed the 1999 BMJ letter 'Do dietary lectins cause disease?' (Freed, PMC1115436), "
            "which raises theoretical human implications but acknowledges the evidence is 'suggestive' "
            "and based primarily on animal models and in-vitro studies, not human clinical trials."
        ),
        "finding": (
            "No human RCTs found demonstrating that normally consumed cooked nightshades or grains "
            "cause chronic inflammation via lectins. The animal-model and in-vitro evidence does not "
            "translate to confirmed causal disease from dietary lectins in ordinary preparation contexts."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Does Dr. Steven Gundry's 'Plant Paradox' provide clinical evidence for widespread "
            "lectin-caused leaky gut?"
        ),
        "verification_performed": (
            "Searched for 'Gundry Plant Paradox clinical evidence lectins leaky gut peer review'. "
            "Cornell Center for Nutrition Studies review found that Gundry's primary cited evidence "
            "is an unreviewed poster abstract. Banner Health notes that studies on gut lining "
            "disruption from lectins focus on animal models or isolated/uncooked lectins, not "
            "normally prepared foods."
        ),
        "finding": (
            "The Plant Paradox hypothesis rests on preliminary/anecdotal evidence, an unreviewed "
            "poster abstract, and animal/in-vitro studies. No large human RCTs support the widespread "
            "leaky gut claim from normally consumed, cooked foods."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Do populations with high lectin intake (legumes, whole grains, nightshades) show "
            "worse inflammatory or health outcomes?"
        ),
        "verification_performed": (
            "Searched for 'Blue Zones legume consumption longevity inflammation' and 'whole grain "
            "health outcomes epidemiology anti-inflammatory'. Cornell Nutrition Studies notes Blue "
            "Zones populations — known for exceptional longevity — consistently consume legumes "
            "(high in lectins). Multiple epidemiological studies link legume and whole grain "
            "consumption to reduced inflammation markers and better cardiovascular/metabolic outcomes."
        ),
        "finding": (
            "Epidemiological evidence directly contradicts the 'widespread harm' claim: populations "
            "with the highest lectin-food intake show better, not worse, health and longevity outcomes. "
            "This is strong counter-evidence to the widespread inflammation claim."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Can raw or improperly cooked lectins (e.g., raw kidney beans) cause acute illness, "
            "and does this validate the broader inflammation claim?"
        ),
        "verification_performed": (
            "Searched for 'raw kidney beans lectins toxicity phytohaemagglutinin food poisoning'. "
            "Well-established: raw kidney beans contain phytohaemagglutinin (PHA), which causes "
            "acute GI illness within hours. Cooking at boiling point for ≥10 minutes destroys PHA. "
            "This is distinct from the claim about chronic widespread inflammation from cooked foods."
        ),
        "finding": (
            "Raw/undercooked high-lectin foods CAN cause acute GI illness — this is toxicological "
            "fact. However, this is an acute effect of improperly prepared food, not evidence for "
            "chronic widespread inflammation or leaky gut from normally cooked dietary lectins. "
            "The claim's framing ('nightshades like tomatoes') does not specify raw consumption, "
            "so this acute mechanism does not support the broad claim."
        ),
        "breaks_proof": False,
    },
]

# 9. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    sc1_verdict = "PROVED" if sc1_holds else "UNDETERMINED"
    sc2_verdict = "DISPROVED" if sc2_disproved else "UNDETERMINED"

    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif sc1_holds and sc2_disproved:
        base = "PARTIALLY VERIFIED"
        verdict = (base + " (with unverified citations)") if any_unverified else base
    elif sc1_holds and not sc2_disproved:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(SC1 verified citations) >= 2"
    FACT_REGISTRY["A1"]["result"] = str(n_sc1_confirmed)
    FACT_REGISTRY["A2"]["method"] = f"count(SC2 verified refuting citations) >= 3"
    FACT_REGISTRY["A2"]["result"] = str(n_sc2_confirmed)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

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
                "description": "SC1: Multiple independent sources consulted for lectin presence",
                "n_sources_consulted": len(sc1_empirical_facts),
                "n_sources_verified": n_sc1_confirmed,
                "sources": {k: citation_results[k]["status"] for k in sc1_empirical_facts},
                "independence_note": (
                    "Sources from different institutions: Banner Health (health system) "
                    "and Harvard T.H. Chan School of Public Health (academic)"
                ),
            },
            {
                "description": "SC2: Multiple independent authoritative sources consulted for causation rejection",
                "n_sources_consulted": len(sc2_empirical_facts),
                "n_sources_verified": n_sc2_confirmed,
                "sources": {k: citation_results[k]["status"] for k in sc2_empirical_facts},
                "independence_note": (
                    "Sources from independent institutions: MD Anderson Cancer Center, "
                    "Harvard T.H. Chan School of Public Health, Cornell University Center "
                    "for Nutrition Studies"
                ),
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_confirmed_sources": n_sc1_confirmed,
            "sc1_threshold": 2,
            "sc1_holds": sc1_holds,
            "sc1_verdict": sc1_verdict,
            "sc2_confirmed_refuting_sources": n_sc2_confirmed,
            "sc2_threshold": 3,
            "sc2_disproved": sc2_disproved,
            "sc2_verdict": sc2_verdict,
            "claim_holds": sc1_holds and not sc2_disproved,
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
