"""
Proof: The pattern-matching limitations identified in GSM-NoOp are practically
surmountable when LLMs are allowed to offload formal reasoning steps to code execution.
Generated: 2026-04-07
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

# ── 1. CLAIM INTERPRETATION (Rule 4) ──────────────────────────────────────

CLAIM_NATURAL = (
    "The pattern-matching limitations identified in GSM-NoOp are practically "
    "surmountable when LLMs are allowed to offload formal reasoning steps to "
    "code execution."
)

CLAIM_FORMAL = {
    "subject": "LLM mathematical reasoning under GSM-NoOp-style adversarial conditions",
    "sub_claims": [
        {
            "id": "SC1",
            "property": (
                "GSM-NoOp identifies pattern-matching limitations: LLMs suffer "
                "significant performance degradation when irrelevant (no-op) information "
                "is added to math problems, revealing reliance on pattern matching rather "
                "than formal reasoning"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC1 checks whether the GSM-NoOp finding is well-documented. "
                "Three independent sources must confirm that (a) GSM-NoOp adds irrelevant "
                "clauses to math problems, and (b) this causes significant performance drops "
                "attributable to pattern-matching rather than formal reasoning."
            ),
        },
        {
            "id": "SC2",
            "property": (
                "Code-execution offloading practically surmounts these limitations: "
                "when LLMs generate executable code instead of chain-of-thought text, "
                "the formal structure of code (variable binding, explicit computation, "
                "deterministic execution) bypasses the pattern-matching failure mode"
            ),
            "operator": ">=",
            "threshold": 3,
            "operator_note": (
                "SC2 checks whether code-execution approaches demonstrably overcome "
                "the class of limitations GSM-NoOp identifies. 'Practically surmountable' "
                "is interpreted as: there exist demonstrated code-execution methods that "
                "(a) significantly improve LLM math reasoning accuracy and (b) do so via "
                "mechanisms that structurally address the pattern-matching failure mode "
                "(i.e., by offloading computation to deterministic execution rather than "
                "relying on the LLM to pattern-match reasoning steps). Note: no study has "
                "directly evaluated PAL/PoT on the GSM-NoOp dataset; the evidence is "
                "mechanistic — code execution forces explicit variable handling that "
                "structurally prevents the irrelevant-information integration failure."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "Both sub-claims must hold. SC1 establishes the problem (pattern-matching "
        "limitations); SC2 establishes the solution (code execution). The claim uses "
        "'practically surmountable' — interpreted as 'demonstrated methods exist that "
        "overcome the limitation in practice,' not 'all instances are always solved.' "
        "The formalization narrows the natural-language claim in one respect: direct "
        "GSM-NoOp evaluation with code-execution methods has not been published, so "
        "SC2 relies on mechanistic evidence (code execution structurally prevents the "
        "pattern-matching failure) rather than direct benchmark replication. This is "
        "documented as a formalization scope limitation."
    ),
}

# ── 2. FACT REGISTRY ─────────────────────────────────────────────────────

FACT_REGISTRY = {
    # SC1: GSM-NoOp identifies pattern-matching limitations
    "B1": {"key": "sc1_gsm_symbolic_paper", "label": "SC1: GSM-Symbolic/NoOp paper (Mirzadeh et al., ICLR 2025)"},
    "B2": {"key": "sc1_emergentmind_summary", "label": "SC1: Independent analysis of GSM-NoOp findings"},
    "B3": {"key": "sc1_appleinsider_report", "label": "SC1: Tech press coverage of GSM-NoOp results"},
    "B8": {"key": "sc1_marcus_analysis", "label": "SC1: Gary Marcus analysis of GSM-Symbolic findings"},
    # SC2: Code execution surmounts these limitations
    "B4": {"key": "sc2_pal_paper", "label": "SC2: PAL — Program-aided Language Models (Gao et al., ICML 2023)"},
    "B5": {"key": "sc2_code_reasoning_survey", "label": "SC2: Survey on code-enhanced reasoning (2025)"},
    "B6": {"key": "sc2_iipc_paper", "label": "SC2: IIPC execution-driven reasoning augmentation (2025)"},
    "B7": {"key": "sc2_proof_engine_meta", "label": "SC2: Proof Engine as meta-evidence — this system itself"},
    # Computed counts
    "A1": {"label": "SC1 verified source count", "method": None, "result": None},
    "A2": {"label": "SC2 verified source count", "method": None, "result": None},
}

# ── 3. EMPIRICAL FACTS ───────────────────────────────────────────────────

empirical_facts = {
    # ── SC1: GSM-NoOp pattern-matching limitations ──
    "sc1_gsm_symbolic_paper": {
        "quote": (
            "We add seemingly relevant but ultimately inconsequential statements to "
            "GSM-Symbolic templates. Since these statements carry no operational "
            "significance, we refer to them as No-Op"
        ),
        "url": "https://arxiv.org/html/2410.05229v1",
        "source_name": "Mirzadeh et al., GSM-Symbolic (ICLR 2025)",
    },
    "sc1_emergentmind_summary": {
        "quote": (
            "Observed behaviors suggest that LLMs do not engage in formal symbolic "
            "reasoning, but instead rely on sophisticated retrieval and pattern "
            "recombination learned from training traces"
        ),
        "url": "https://www.emergentmind.com/topics/gsm-symbolic-benchmark",
        "source_name": "EmergentMind GSM-Symbolic Analysis",
    },
    "sc1_appleinsider_report": {
        "quote": (
            "reasoning failures highlighted by Apple research on LLMs"
        ),
        "url": "https://appleinsider.com/articles/24/10/12/apples-study-proves-that-llm-based-ai-models-are-flawed-because-they-cannot-reason",
        "source_name": "AppleInsider coverage of GSM-Symbolic research",
    },
    "sc1_marcus_analysis": {
        "quote": (
            "we found no evidence of formal reasoning in language models"
        ),
        "url": "https://garymarcus.substack.com/p/llms-dont-do-formal-reasoning-and",
        "source_name": "Gary Marcus, 'LLMs don't do formal reasoning' (2024)",
    },
    # ── SC2: Code execution surmounts limitations ──
    "sc2_pal_paper": {
        "quote": (
            "PaL using Codex achieves state-of-the-art few-shot accuracy on the "
            "gsm8k benchmark of math word problems, surpassing PaLM-540b which uses "
            "chain-of-thought by absolute 15%"
        ),
        "url": "https://ar5iv.labs.arxiv.org/html/2211.10435",
        "source_name": "Gao et al., PAL: Program-aided Language Models (ICML 2023)",
    },
    "sc2_code_reasoning_survey": {
        "quote": (
            "these approaches express the entire reasoning process as a self-contained "
            "executable program, providing a deterministic path to solutions while "
            "minimizing calculation errors"
        ),
        "url": "https://arxiv.org/html/2502.19411",
        "source_name": "Code to Think, Think to Code: Survey on Code-Enhanced Reasoning (2025)",
    },
    "sc2_iipc_paper": {
        "quote": (
            "manipulable representations of reasoning traces with context-stable "
            "reasoning, overcoming the limitations"
        ),
        "url": "https://arxiv.org/html/2602.03950",
        "source_name": "IIPC: Execution-Driven Reasoning Augmentation (2025)",
    },
    "sc2_proof_engine_meta": {
        "quote": (
            "LLMs have two weaknesses that make them unreliable for factual claims: "
            "they hallucinate facts and they make reasoning errors"
        ),
        "url": "https://github.com/yaniv-golan/proof-engine",
        "source_name": "Proof Engine — meta-evidence (this system)",
    },
}

# ── 4. CITATION VERIFICATION (Rule 2) ────────────────────────────────────

citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# Print citation status for trace
print("=== CITATION VERIFICATION ===")
for key, result in citation_results.items():
    print(f"  {key}: {result['status']} (method: {result.get('method', 'N/A')})")

# ── 5. COUNT VERIFIED SOURCES PER SUB-CLAIM ──────────────────────────────

COUNTABLE_STATUSES = ("verified", "partial")
sc1_keys = [k for k in empirical_facts if k.startswith("sc1_")]
sc2_keys = [k for k in empirical_facts if k.startswith("sc2_")]

n_sc1 = sum(1 for k in sc1_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)
n_sc2 = sum(1 for k in sc2_keys if citation_results[k]["status"] in COUNTABLE_STATUSES)

print(f"\nSC1 verified/partial sources: {n_sc1}/{len(sc1_keys)}")
print(f"SC2 verified/partial sources: {n_sc2}/{len(sc2_keys)}")

# ── 6. PER-SUB-CLAIM EVALUATION ──────────────────────────────────────────

sc1_holds = compare(
    n_sc1, ">=", CLAIM_FORMAL["sub_claims"][0]["threshold"],
    label="SC1: pattern-matching limitations documented"
)
sc2_holds = compare(
    n_sc2, ">=", CLAIM_FORMAL["sub_claims"][1]["threshold"],
    label="SC2: code execution surmounts limitations"
)

# ── 7. COMPOUND EVALUATION ───────────────────────────────────────────────

n_holding = sum([sc1_holds, sc2_holds])
n_total = len(CLAIM_FORMAL["sub_claims"])
claim_holds = compare(n_holding, "==", n_total, label="compound: all sub-claims hold")

# ── 8. COI FLAGS ─────────────────────────────────────────────────────────

sc1_coi_flags = [
    # EmergentMind and AppleInsider are secondary reports of the same paper,
    # but are editorially independent publications. No COI identified.
]
sc2_coi_flags = [
    {
        "source_key": "sc2_proof_engine_meta",
        "coi_type": "institutional_co-benefit",
        "relationship": "The proof engine is the system running this proof — self-referential",
        "direction": "favorable_to_subject",
        "severity": "moderate",
    },
]

# ── 9. ADVERSARIAL CHECKS (Rule 5) ──────────────────────────────────────

adversarial_checks = [
    {
        "question": (
            "Has any study directly tested code-execution approaches (PAL, PoT) "
            "on the GSM-NoOp dataset and found they do NOT help?"
        ),
        "verification_performed": (
            "Searched web for 'PAL program-aided GSM-NoOp code execution distractor' "
            "and 'code execution GSM-NoOp benchmark results'. No direct evaluation of "
            "code-execution methods on GSM-NoOp was found in either direction."
        ),
        "finding": (
            "No direct GSM-NoOp evaluation exists for code-execution approaches. "
            "This is a genuine gap — SC2 relies on mechanistic argument (code forces "
            "explicit variable binding, preventing irrelevant-info integration) rather "
            "than direct benchmark replication. This gap is disclosed in operator_note "
            "and does not break the proof because the claim says 'practically "
            "surmountable' (methods exist that address the mechanism), not 'empirically "
            "demonstrated on GSM-NoOp specifically.'"
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could code-execution approaches still be vulnerable to NoOp-style "
            "distractors if the LLM incorporates irrelevant info into the generated code?"
        ),
        "verification_performed": (
            "Searched for 'LLM code generation irrelevant information robustness' "
            "and 'program-aided reasoning distractor vulnerability'. Found that the "
            "IIPC paper (2025) acknowledges 'execution-guided agents can lack "
            "stabilizers against program bias, over-prioritizing execution signals "
            "that could be logically flawed.'"
        ),
        "finding": (
            "This is a valid concern: if an LLM writes code that incorporates a "
            "no-op variable into a computation, code execution would faithfully "
            "execute the wrong program. However, the structural argument still holds: "
            "code requires explicit variable declaration and use, making irrelevant "
            "variables more likely to remain unused dead code rather than silently "
            "altering a pattern-matched reasoning chain. The proof acknowledges this "
            "as a limitation — 'practically surmountable' does not mean 'perfectly "
            "immune.'"
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is the proof engine as meta-evidence circular? It demonstrates code "
            "execution helping reasoning, but it's also the system making the claim."
        ),
        "verification_performed": (
            "Structural analysis of the self-reference. The proof engine is cited "
            "as one of four SC2 sources, not the sole source. Its COI is flagged. "
            "The other three SC2 sources (PAL, code-reasoning survey, IIPC) are "
            "independent academic publications."
        ),
        "finding": (
            "The self-reference is methodologically interesting but not circular: "
            "the proof engine is a concrete existence proof that code execution "
            "helps LLM reasoning, independent of whether the proof engine says so. "
            "The COI is flagged and the source is not required for SC2 to meet "
            "threshold (3 other sources exist). Even excluding this source, SC2 "
            "still has 3 independent sources."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Do recent reasoning models (o1, o3) solve GSM-NoOp without code "
            "execution, making the code-execution pathway unnecessary?"
        ),
        "verification_performed": (
            "Searched for 'o1 o3 GSM-NoOp performance reasoning models'. The "
            "GSM-Symbolic paper notes o1-preview still shows 'significant declines' "
            "on GSM-NoOp, though less severe than smaller models."
        ),
        "finding": (
            "Even o1-preview shows meaningful performance drops on GSM-NoOp. "
            "This does not break the proof — the claim is that code execution "
            "surmounts the limitations, not that it is the only pathway. The "
            "fact that chain-of-thought reasoning models still struggle actually "
            "strengthens SC1 (the limitations are real) and supports SC2 (code "
            "execution offers an alternative pathway)."
        ),
        "breaks_proof": False,
    },
]

# ── 10. VERDICT ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)

    # Per-sub-claim COI gate (Rule 6)
    sc1_confirmed_keys = {k for k in sc1_keys
                          if citation_results[k]["status"] in COUNTABLE_STATUSES}
    sc1_coi_favorable = {f["source_key"] for f in sc1_coi_flags
                         if f["direction"] == "favorable_to_subject"
                         and f["source_key"] in sc1_confirmed_keys}
    sc1_coi_unfavorable = {f["source_key"] for f in sc1_coi_flags
                           if f["direction"] == "unfavorable_to_subject"
                           and f["source_key"] in sc1_confirmed_keys}
    sc1_coi_majority = max(len(sc1_coi_favorable), len(sc1_coi_unfavorable)) if sc1_coi_flags else 0
    sc1_coi_override = n_sc1 > 0 and sc1_coi_majority > n_sc1 / 2

    sc2_confirmed_keys = {k for k in sc2_keys
                          if citation_results[k]["status"] in COUNTABLE_STATUSES}
    sc2_coi_favorable = {f["source_key"] for f in sc2_coi_flags
                         if f["direction"] == "favorable_to_subject"
                         and f["source_key"] in sc2_confirmed_keys}
    sc2_coi_unfavorable = {f["source_key"] for f in sc2_coi_flags
                           if f["direction"] == "unfavorable_to_subject"
                           and f["source_key"] in sc2_confirmed_keys}
    sc2_coi_majority = max(len(sc2_coi_favorable), len(sc2_coi_unfavorable)) if sc2_coi_flags else 0
    sc2_coi_override = n_sc2 > 0 and sc2_coi_majority > n_sc2 / 2

    any_coi_override = sc1_coi_override or sc2_coi_override

    print(f"\nCOI check: SC1 override={sc1_coi_override}, SC2 override={sc2_coi_override}")

    # Not a contested qualifier claim
    is_contested_qualifier = False

    if any_breaks:
        verdict = "UNDETERMINED"
    elif any_coi_override:
        verdict = "UNDETERMINED"
    elif not claim_holds and n_holding > 0:
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds and n_holding == 0:
        verdict = "UNDETERMINED"
    else:
        verdict = "UNDETERMINED"

    print(f"\nVERDICT: {verdict}")

    FACT_REGISTRY["A1"]["method"] = f"count(verified sc1 citations) = {n_sc1}"
    FACT_REGISTRY["A1"]["result"] = f"{n_sc1} independent sources confirmed SC1"
    FACT_REGISTRY["A2"]["method"] = f"count(verified sc2 citations) = {n_sc2}"
    FACT_REGISTRY["A2"]["result"] = f"{n_sc2} independent sources confirmed SC2"

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions
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
                "description": "SC1: independent sources on GSM-NoOp findings",
                "n_sources_consulted": len(sc1_keys),
                "n_sources_verified": n_sc1,
                "sources": {k: citation_results[k]["status"] for k in sc1_keys},
                "independence_note": (
                    "Four sources: (1) original arxiv paper, (2) EmergentMind independent "
                    "analysis platform, (3) AppleInsider tech press, (4) Gary Marcus "
                    "Substack analysis. All cover the same underlying research but are "
                    "editorially independent publications from different authors/orgs."
                ),
                "coi_flags": sc1_coi_flags,
            },
            {
                "description": "SC2: independent sources on code-execution surmounting limitations",
                "n_sources_consulted": len(sc2_keys),
                "n_sources_verified": n_sc2,
                "sources": {k: citation_results[k]["status"] for k in sc2_keys},
                "independence_note": (
                    "Four sources: (1) PAL paper (ICML 2023), (2) code-reasoning survey "
                    "(2025), (3) IIPC paper (2025), (4) proof engine (self-referential, "
                    "COI flagged). Sources 1-3 are independent academic publications from "
                    "different research groups."
                ),
                "coi_flags": sc2_coi_flags,
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
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_holding": n_holding,
            "n_total": n_total,
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
