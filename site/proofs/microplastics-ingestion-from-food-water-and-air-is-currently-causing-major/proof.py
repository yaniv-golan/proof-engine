"""
Proof: Microplastics ingestion from food, water, and air is currently causing
       major declines in human fertility and hormone disruption.
Generated: 2026-03-31
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "Microplastics ingestion from food, water, and air is currently causing "
    "major declines in human fertility and hormone disruption."
)

CLAIM_FORMAL = {
    "subject": "Microplastics ingested via food, water, and air",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "Humans are currently exposed to and ingesting microplastics "
                        "via food, water, and air",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC1 requires at least 2 independent authoritative sources confirming "
                "that microplastic ingestion and inhalation from food, water, and air "
                "are documented in humans. This is the exposure pathway sub-claim and "
                "has the clearest evidence base."
            ),
        },
        {
            "id": "SC2",
            "property": "Microplastics exposure is causing or associated with hormone "
                        "(endocrine) disruption in humans",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC2 requires at least 2 independent peer-reviewed sources documenting "
                "endocrine/hormonal changes associated with microplastic or "
                "microplastic-associated chemical (EDC) exposure. "
                "'Causing' is interpreted broadly to include demonstrated associations "
                "with measurable hormonal changes and plausible mechanistic evidence, "
                "given that controlled human causation trials are ethically impossible. "
                "This is the more lenient interpretation — proof of strict population-level "
                "causation would require a higher threshold."
            ),
        },
        {
            "id": "SC3",
            "property": "Microplastics exposure is currently CAUSING MAJOR DECLINES "
                        "in human fertility (causal, population-level, not merely associative)",
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC3 uses threshold=3 because 'currently causing major declines' is a "
                "strong causal claim requiring: (a) demonstrated causation, not just "
                "association; (b) population-level magnitude ('major declines'); and "
                "(c) human-specific evidence (animal models alone are insufficient). "
                "The elevated threshold reflects the strength of the claim. "
                "Sources showing only correlation or animal-model fertility reduction "
                "count toward the evidence tally but do not establish the causal major-decline "
                "narrative on their own — the claim_holds flag for SC3 will be False if "
                "fewer than 3 qualifying sources are found."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "All three sub-claims must hold for the compound claim to be PROVED. "
        "If any SC fails, the verdict is PARTIALLY VERIFIED (if at least one holds) "
        "or UNDETERMINED (if none hold). "
        "SC1 documents the exposure pathway; SC2 documents the endocrine-disruption arm "
        "of the claim; SC3 documents the fertility-decline arm with causal attribution."
    ),
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    # SC1 — Exposure via food, water, air
    "B1": {"key": "sc1_source_a", "label": "SC1: PMC review — MPs ingested via food, inhaled via air"},
    "B2": {"key": "sc1_source_b", "label": "SC1: PMC endocrine review — three exposure routes confirmed"},
    # SC2 — Hormone disruption
    "B3": {"key": "sc2_source_a", "label": "SC2: Frontiers endocrinology review — reproductive hormone signalling changes"},
    "B4": {"key": "sc2_source_b", "label": "SC2: PMC endocrine disruptors review — gonadal susceptibility and EDC axis disruption"},
    # SC3 — Major fertility decline (causal)
    "B5": {"key": "sc3_source_a", "label": "SC3: Lancet eBioMedicine PMC — MPs associated with sperm dysfunction"},
    "B6": {"key": "sc3_source_b", "label": "SC3: Frontiers endocrinology — animal-model fertility reduction by MPs"},
    # Computed
    "A1": {"label": "SC1: verified source count", "method": None, "result": None},
    "A2": {"label": "SC2: verified source count", "method": None, "result": None},
    "A3": {"label": "SC3: verified source count", "method": None, "result": None},
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS
# ---------------------------------------------------------------------------
empirical_facts = {
    # SC1 — Exposure
    "sc1_source_a": {
        "quote": (
            "The main route of human exposure to MPs is through food ingestion, "
            "including seafood contaminated with microplastics. "
            "The second route of exposure is through the inhalation of air and dust "
            "containing MPs."
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9920460/",
        "source_name": (
            "Amobonye et al. (2023) 'Microplastics: A Real Global Threat for Environment "
            "and Food Safety' — PMC9920460"
        ),
    },
    "sc1_source_b": {
        "quote": (
            "Humans can be exposed to MNPs in three ways: ingestion, inhalation, "
            "and dermal contact"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12249724/",
        "source_name": (
            "Bures et al. (2025) 'Micro- and Nanoplastics as Disruptors of the "
            "Endocrine System' — PMC12249724"
        ),
    },
    # SC2 — Hormone disruption
    "sc2_source_a": {
        "quote": (
            "distinct changes in reproductive hormone signalling are observed, with "
            "reductions in the circulating concentrations of estradiol (E2) and "
            "anti-mullerian hormone (AMH), and increased concentrations of LH, "
            "follicle stimulating hormone (FSH) and testosterone"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10794604/",
        "source_name": (
            "Conley et al. (2024) 'Microplastics exposure: implications for human "
            "fertility, pregnancy and child health' — PMC10794604 (Frontiers Endocrinology)"
        ),
    },
    "sc2_source_b": {
        "quote": (
            "The gonads are particularly susceptible, with studies demonstrating "
            "oxidative stress, cellular apoptosis, and infertility due to MNP exposure"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12249724/",
        "source_name": (
            "Bures et al. (2025) 'Micro- and Nanoplastics as Disruptors of the "
            "Endocrine System' — PMC12249724"
        ),
    },
    # SC3 — Major fertility decline
    "sc3_source_a": {
        "quote": (
            "each additional type of microplastic exposure was associated with a "
            "significant decrease in total sperm number"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11663775/",
        "source_name": (
            "Li et al. (2024) 'Association of mixed exposure to microplastics with "
            "sperm dysfunction: a multi-site study in China' — PMC11663775 (Lancet eBioMedicine)"
        ),
    },
    "sc3_source_b": {
        "quote": (
            "MNP exposure in rodent models leads to reduced sperm quantity and quality "
            "in addition to reduced testicular androgen production and circulating levels "
            "of testosterone"
        ),
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10794604/",
        "source_name": (
            "Conley et al. (2024) 'Microplastics exposure: implications for human "
            "fertility, pregnancy and child health' — PMC10794604 (Frontiers Endocrinology)"
        ),
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
print("Verifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. COUNT VERIFIED SOURCES PER SUB-CLAIM
# ---------------------------------------------------------------------------
COUNTABLE_STATUSES = ("verified", "partial")

sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]
sc3_keys = [k for k in empirical_facts if k.startswith("sc3_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc3 = sum(1 for k in sc3_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)

print(f"  SC1 confirmed sources: {n_sc1} / {len(sc1_keys)}")
print(f"  SC2 confirmed sources: {n_sc2} / {len(sc2_keys)}")
print(f"  SC3 confirmed sources: {n_sc3} / {len(sc3_keys)}")

# ---------------------------------------------------------------------------
# 6. PER-SUB-CLAIM EVALUATION (Rule 7 — compare(), not hardcoded)
# ---------------------------------------------------------------------------
sc1_holds = compare(
    n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
    label="SC1: exposure via food/water/air confirmed by independent sources",
)
sc2_holds = compare(
    n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
    label="SC2: hormone disruption evidenced by independent sources",
)
sc3_holds = compare(
    n_sc3, ">=", CLAIM_FORMAL["sub_claims"][2]["threshold"],
    label="SC3: causal major fertility decline — verified sources vs threshold=3",
)

# ---------------------------------------------------------------------------
# 7. COMPOUND EVALUATION
# ---------------------------------------------------------------------------
n_holding = sum([sc1_holds, sc2_holds, sc3_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(
    n_holding, "==", n_total,
    label="compound: all sub-claims hold",
)

# ---------------------------------------------------------------------------
# 8. ADVERSARIAL CHECKS (Rule 5)
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "Does the scientific consensus support the claim that microplastics are "
            "definitively CAUSING (not just associated with) infertility in humans?"
        ),
        "verification_performed": (
            "Searched for 'microplastics fertility causation established evidence 2024' "
            "and 'microplastics infertility not proven criticism'. Found microplasticsinfo.org "
            "review synthesizing current evidence."
        ),
        "finding": (
            "The scientific consensus explicitly states causation is not established. "
            "microplasticsinfo.org: 'Current evidence does not demonstrate that microplastics "
            "are causing infertility in humans.' A systematic review (cited in the same source) "
            "found all 24 animal studies on MPs and fertility had significant methodological flaws "
            "including lack of appropriate controls, insufficient sample sizes, and incorrect "
            "statistical methods. Human cross-sectional studies show associations but cannot "
            "establish causation."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Are human sperm counts actually declining globally, or are trends more complex?"
        ),
        "verification_performed": (
            "Searched for 'human sperm count trends recent data 2024 2025 increase stable'. "
            "Found a recent large-scale study of 18,000+ semen samples."
        ),
        "finding": (
            "A recent study analyzing more than 18,000 semen samples from more than 15,000 men "
            "found sperm concentrations have INCREASED over the past 15 years, contradicting "
            "the 'major declines' narrative. Global trends are regionally heterogeneous. "
            "The Levine et al. (2022) meta-analysis did find declining trends over decades, "
            "but attributing this specifically to microplastics (versus other EDCs, lifestyle "
            "factors, heat, obesity) is not established. This substantially undermines SC3."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Do studies specifically on MPs in semen confirm reduced sperm counts, or "
            "are results mixed?"
        ),
        "verification_performed": (
            "Reviewed PMC12299061 (Toxics 2025, microplastics in semen study, n=45). "
            "Also reviewed PMC11663775 (Lancet eBioMedicine, n=113, multi-site China)."
        ),
        "finding": (
            "Results are mixed. PMC12299061: 'No significant association was found between "
            "MP exposure and sperm concentration or total sperm count.' Only PET MPs showed "
            "a marginal (p=0.056, not significant) association with progressive motility. "
            "PMC11663775 found association with total sperm number, but explicitly states "
            "'this study is a cross-sectional study, not supported by cohort data, and is "
            "only an association between microplastic exposure and sperm quality, but does "
            "not establish causation.' Both studies had small samples (45 and 113 participants "
            "respectively). Findings do not support 'major declines' at population scale."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Are the hormone-disruption effects attributed to microplastic particles "
            "themselves, or to the chemical additives (BPA, phthalates) that leach from them?"
        ),
        "verification_performed": (
            "Searched for 'microplastics vs plastic additives BPA phthalates hormone disruption "
            "attribution'. Reviewed multiple PMC sources on endocrine disruption mechanisms."
        ),
        "finding": (
            "Multiple reviews distinguish between MPs as particles vs. the EDCs (endocrine-"
            "disrupting chemicals) like BPA and phthalates that leach from them. The EDC effects "
            "of plastic additives are well-established; the particle effects of MPs themselves "
            "on hormones are less clear. PMC12249724 states 'MPs act through their EDCs to "
            "disrupt the feedback of the HPT and the HPG axes.' BPA/phthalates regulation "
            "is independent of microplastic ingestion per se, complicating the causal chain "
            "in the original claim which specifies 'microplastics ingestion' as the cause."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 9. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    if any_breaks:
        verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified SC1 citations) = {n_sc1}"
    FACT_REGISTRY["A1"]["result"] = str(n_sc1)
    FACT_REGISTRY["A2"]["method"] = f"count(verified SC2 citations) = {n_sc2}"
    FACT_REGISTRY["A2"]["result"] = str(n_sc2)
    FACT_REGISTRY["A3"]["method"] = f"count(verified SC3 citations) = {n_sc3}"
    FACT_REGISTRY["A3"]["result"] = str(n_sc3)

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
        "fact_registry": {fid: dict(info) for fid, info in FACT_REGISTRY.items()},
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": [
            {
                "description": "SC1: independent sources documenting exposure via food/water/air",
                "n_sources_consulted": len(sc1_keys),
                "n_sources_verified": n_sc1,
                "sources": {k: citation_results[k]["status"] for k in sc1_keys},
                "independence_note": (
                    "Two separate peer-reviewed papers: Amobonye et al. (food chain review, PMC9920460) "
                    "and Bures et al. (endocrine system review, PMC12249724) — different journals, "
                    "different author teams, different research scope."
                ),
            },
            {
                "description": "SC2: independent sources documenting hormonal disruption evidence",
                "n_sources_consulted": len(sc2_keys),
                "n_sources_verified": n_sc2,
                "sources": {k: citation_results[k]["status"] for k in sc2_keys},
                "independence_note": (
                    "Conley et al. (fertility/pregnancy review, PMC10794604) and "
                    "Bures et al. (endocrine system review, PMC12249724) — different journals, "
                    "different primary focus areas, independent literature synthesis."
                ),
            },
            {
                "description": "SC3: sources documenting fertility-related MP associations",
                "n_sources_consulted": len(sc3_keys),
                "n_sources_verified": n_sc3,
                "sources": {k: citation_results[k]["status"] for k in sc3_keys},
                "independence_note": (
                    "Li et al. (multi-site human sperm study, PMC11663775) and "
                    "Conley et al. (rodent model evidence, PMC10794604). "
                    "Note: sc3_source_b draws from the same paper as sc2_source_a (PMC10794604) "
                    "but cites a different finding (rodent sperm reduction vs. hormonal changes). "
                    "Even with both sources verified, n_sc3=2 < threshold=3, so SC3 does not hold."
                ),
            },
        ],
        "sub_claim_results": [
            {
                "id": "SC1",
                "n_confirming": n_sc1,
                "threshold": CLAIM_FORMAL["sub_claims"][0]["threshold"],
                "holds": sc1_holds,
            },
            {
                "id": "SC2",
                "n_confirming": n_sc2,
                "threshold": CLAIM_FORMAL["sub_claims"][1]["threshold"],
                "holds": sc2_holds,
            },
            {
                "id": "SC3",
                "n_confirming": n_sc3,
                "threshold": CLAIM_FORMAL["sub_claims"][2]["threshold"],
                "holds": sc3_holds,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_holds": sc1_holds,
            "sc2_holds": sc2_holds,
            "sc3_holds": sc3_holds,
            "n_holding": n_holding,
            "n_total": n_total,
            "claim_holds": claim_holds,
            "any_unverified": any_unverified,
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
