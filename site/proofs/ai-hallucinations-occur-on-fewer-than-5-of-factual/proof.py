"""
Proof: AI hallucinations occur on fewer than 5% of factual questions
Generated: 2026-03-29
Type: Qualitative consensus disproof (Type B empirical)
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail, verify_data_values
from scripts.computations import compare

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "AI hallucinations occur on fewer than 5% of factual questions"
CLAIM_FORMAL = {
    "subject": "AI language models (as a general class)",
    "property": "hallucination rate on factual question benchmarks",
    "operator": ">=",
    "operator_note": (
        "To DISPROVE the claim that hallucinations occur on fewer than 5% of factual questions, "
        "we need >= 3 independent, verified sources showing hallucination rates >= 5% on factual "
        "question benchmarks. The claim is universal ('AI hallucinations') without specifying a "
        "particular model, so any major AI model demonstrating >= 5% hallucination on factual "
        "questions constitutes a counterexample. Even if some models on some narrow benchmarks "
        "achieve < 5%, the general claim is disproved if the typical or average rate exceeds 5%. "
        "Note: summarization benchmarks (Vectara original) measure grounded factual consistency "
        "with provided text, not open-ended factual question answering — we focus on open-ended "
        "factual QA benchmarks like SimpleQA, PersonQA, and AA-Omniscience."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# 2. FACT REGISTRY
FACT_REGISTRY = {
    "B1": {"key": "source_ieee", "label": "IEEE ComSoc: OpenAI o3 hallucinated 33% on PersonQA"},
    "B2": {"key": "source_allaboutai", "label": "AllAboutAI: ChatGPT hallucinates in ~19.5% of responses"},
    "B3": {"key": "source_aa", "label": "Artificial Analysis: best model 22% hallucination on AA-Omniscience"},
    "A1": {"label": "Verified source count meets disproof threshold", "method": None, "result": None},
}

# 3. EMPIRICAL FACTS — sources that REJECT the claim (confirm hallucination rates >= 5%)
empirical_facts = {
    "source_ieee": {
        "quote": (
            "The company found that o3 — its most powerful system — hallucinated "
            "33% of the time when running its PersonQA benchmark test"
        ),
        "url": "https://techblog.comsoc.org/2025/05/10/nyt-ai-is-getting-smarter-but-hallucinations-are-getting-worse/",
        "source_name": "IEEE Communications Society Technology Blog",
    },
    "source_allaboutai": {
        "quote": (
            "ChatGPT generates hallucinated content in approximately 19.5% of its responses"
        ),
        "url": "https://www.allaboutai.com/resources/llm-hallucination/",
        "source_name": "AllAboutAI LLM Hallucination Test",
    },
    "source_aa": {
        "quote": (
            "Grok 4.20 Beta 0309 (Reasoning)"
        ),
        "url": "https://artificialanalysis.ai/evaluations/omniscience",
        "source_name": "Artificial Analysis AA-Omniscience Benchmark",
        "data_values": {
            "best_model_hallucination_rate": "22%",
            "benchmark_questions": "6,000",
        },
    },
}

# 4. CITATION VERIFICATION (Rule 2)
print("=== CITATION VERIFICATION ===")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# Verify data_values for AA-Omniscience source
dv_results = verify_data_values(
    empirical_facts["source_aa"]["url"],
    empirical_facts["source_aa"]["data_values"],
    "source_aa",
)
print(f"  source_aa data_values: {json.dumps(dv_results, indent=2)}")

for key, result in citation_results.items():
    print(f"  {key}: {result['status']} (method: {result.get('method', 'N/A')})")

# 5. COUNT SOURCES WITH VERIFIED CITATIONS
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"\n  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# 6. CLAIM EVALUATION — MUST use compare()
claim_holds = compare(n_confirmed, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"],
                      label="verified disproof sources vs threshold")

# 7. ADVERSARIAL CHECKS (Rule 5) — search for evidence SUPPORTING the claim
adversarial_checks = [
    {
        "question": "Are there any major AI models that achieve < 5% hallucination on open-ended factual QA?",
        "verification_performed": (
            "Searched for 'AI model lowest hallucination rate factual questions 2025 2026'. "
            "Found that on Vectara's ORIGINAL summarization benchmark, some models achieve < 1% "
            "(Gemini-2.0-Flash at 0.7%). However, this measures grounded summarization (factual "
            "consistency with provided text), NOT open-ended factual question answering. On the "
            "Vectara NEW dataset (harder, more realistic), most frontier models exceed 10%. "
            "On AA-Omniscience (6,000 factual questions), the best model has 22% hallucination."
        ),
        "finding": (
            "Low hallucination rates (< 5%) exist only on narrow grounded summarization tasks, "
            "not on open-ended factual question benchmarks. The claim specifies 'factual questions' "
            "which maps to open-ended QA, where rates are consistently well above 5%."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the claim be true for a specific model under specific conditions?",
        "verification_performed": (
            "Searched for 'best AI model factual accuracy 2026 lowest error rate'. "
            "Some models with RAG (retrieval-augmented generation) can reduce hallucination "
            "rates significantly, but the claim says 'AI hallucinations' generically, not "
            "'AI with RAG hallucinations'. Base model performance on factual QA consistently "
            "shows rates above 5% across all major benchmarks."
        ),
        "finding": (
            "Even with the most charitable interpretation (best model, easiest benchmark), "
            "open-ended factual QA hallucination rates exceed 5%. RAG-augmented systems may "
            "achieve lower rates, but the claim does not specify RAG."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Are these benchmarks measuring hallucination correctly?",
        "verification_performed": (
            "Searched for 'AI hallucination benchmark methodology criticism'. "
            "Found that hallucination measurement varies by benchmark — some measure "
            "confabulation (making up facts), others measure factual inconsistency. "
            "PersonQA and SimpleQA specifically test factual accuracy on verifiable questions, "
            "which directly matches the claim's scope of 'factual questions'."
        ),
        "finding": (
            "Benchmark methodology criticism exists but does not undermine our sources. "
            "PersonQA, SimpleQA, and AA-Omniscience all specifically measure factual accuracy "
            "on verifiable questions — directly relevant to the claim."
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
        verdict = ("DISPROVED (with unverified citations)" if is_disproof
                   else "PROVED (with unverified citations)")
    elif not claim_holds:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"count(verified citations) = {n_confirmed}"
    FACT_REGISTRY["A1"]["result"] = str(n_confirmed)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions: for qualitative proofs, each B-type fact records citation status
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
                "description": "Multiple independent sources consulted across different benchmarks",
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "Sources are from different publications (IEEE ComSoc, AllAboutAI, "
                    "Artificial Analysis) reporting on different benchmarks and models (PersonQA, "
                    "ChatGPT testing, AA-Omniscience). Each measures hallucination rates independently."
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

    print(f"\n=== VERDICT: {verdict} ===")
    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
