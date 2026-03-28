"""
Proof: The assertion that no Arab state has ever recognized Israel is false because
Egypt signed a peace treaty in 1979, Jordan in 1994, and four additional states
joined the Abraham Accords by 2023.
Generated: 2026-03-27
"""
import json
import sys
from datetime import date

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.smart_extract import verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "The assertion that no Arab state has ever recognized Israel is false because "
    "Egypt signed a peace treaty in 1979, Jordan in 1994, and four additional states "
    "joined the Abraham Accords by 2023."
)
CLAIM_FORMAL = {
    "subject": "Assertion that no Arab state has ever recognized Israel",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "Egypt signed a peace treaty with Israel in 1979",
            "operator": ">=",
            "threshold": 1,
            "operator_note": (
                "SC1 holds if at least 1 authoritative source confirms Egypt signed a peace "
                "treaty with Israel in 1979. We require ≥ 1 confirming source; two independent "
                "sources (Wikipedia + US State Dept) are used for cross-check (Rule 6). "
                "One confirming source is sufficient because this is a matter of established "
                "historical record."
            ),
        },
        {
            "id": "SC2",
            "property": "Jordan signed a peace treaty with Israel in 1994",
            "operator": ">=",
            "threshold": 1,
            "operator_note": (
                "SC2 holds if at least 1 authoritative source confirms Jordan signed a peace "
                "treaty (the Wadi Araba Treaty) with Israel in 1994. Jordan was the second "
                "Arab country to formally recognize Israel after Egypt. Two independent sources "
                "are used: the treaty's own Wikipedia article and the Abraham Accords Wikipedia "
                "article (which cross-references Jordan 1994)."
            ),
        },
        {
            "id": "SC3",
            "property": "At least 4 Arab states joined the Abraham Accords by 2023",
            "operator": ">=",
            "threshold": 4,
            "operator_note": (
                "SC3 holds if at least 4 Arab states signed the Abraham Accords Declaration "
                "or a bilateral normalization agreement with Israel by 31 December 2023. "
                "'Joined' includes both bilateral agreements and signing the general Declaration, "
                "consistent with Wikipedia and Britannica definitions. The four states are: "
                "United Arab Emirates and Bahrain (bilateral, September 15 2020), Morocco "
                "(bilateral, December 2020), and Sudan (Declaration, January 6 2021). "
                "All four joined by January 2021, well before the 2023 cutoff."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "The meta-claim — that 'no Arab state has ever recognized Israel' is false — is proved "
        "by demonstrating ANY one of SC1, SC2, SC3 holds. The original claim asserts all three "
        "simultaneously, so we verify all three (AND). Even SC1 alone (Egypt 1979) constitutes "
        "a decisive counterexample to the 'no Arab state' assertion."
    ),
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {"key": "egypt_wiki",          "label": "Wikipedia: Egypt–Israel peace treaty signed 26 March 1979"},
    "B2": {"key": "egypt_state_dept",    "label": "US State Dept (history.state.gov): Egypt-Israel Peace Treaty signed March 26"},
    "B3": {"key": "jordan_wiki",         "label": "Wikipedia: Israel–Jordan peace treaty signed 26 October 1994"},
    "B4": {"key": "jordan_accords_xref", "label": "Wikipedia (Abraham Accords): UAE/Bahrain first Arab recognition since Jordan in 1994"},
    "B5": {"key": "accords_britannica",  "label": "Britannica: Abraham Accords — UAE, Bahrain, Morocco bilateral agreements 2020"},
    "B6": {"key": "accords_wiki_sudan",  "label": "Wikipedia (Abraham Accords): Sudan signed Declaration January 6, 2021"},
    "A1": {"label": "SC1 — Egypt treaty confirming-source count",       "method": None, "result": None},
    "A2": {"label": "SC2 — Jordan treaty confirming-source count",      "method": None, "result": None},
    "A3": {"label": "SC3 — Abraham Accords state count by 2023",        "method": None, "result": None},
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS (Rule 2)
# ---------------------------------------------------------------------------
empirical_facts = {
    "egypt_wiki": {
        "quote": (
            "The Egypt–Israel peace treaty was signed in Washington, D.C., United States, "
            "on 26 March 1979, following the 1978 Camp David Accords."
        ),
        "url": "https://en.wikipedia.org/wiki/Egypt%E2%80%93Israel_peace_treaty",
        "source_name": "Wikipedia: Egypt–Israel peace treaty",
    },
    "egypt_state_dept": {
        "quote": "the Egyptian-Israeli Peace Treaty was formally signed on March 26.",
        "url": "https://history.state.gov/milestones/1977-1980/camp-david",
        "source_name": "U.S. Department of State, Office of the Historian: Camp David Accords",
    },
    "jordan_wiki": {
        "quote": (
            "The signing ceremony took place at the southern border crossing of Arabah on "
            "26 October 1994. Jordan was the second Arab country, after Egypt, to sign a "
            "peace accord with Israel."
        ),
        "url": "https://en.wikipedia.org/wiki/Israel%E2%80%93Jordan_peace_treaty",
        "source_name": "Wikipedia: Israel–Jordan peace treaty",
    },
    "jordan_accords_xref": {
        "quote": (
            "The UAE and Bahrain became the first Arab countries to formally recognize "
            "Israel since Jordan in 1994."
        ),
        "url": "https://en.wikipedia.org/wiki/Abraham_Accords",
        "source_name": "Wikipedia: Abraham Accords (Jordan 1994 cross-reference)",
    },
    "accords_britannica": {
        "quote": (
            "The accords, all of which were signed in the latter half of 2020, consist of "
            "a general declaration alongside individual bilateral agreements between Israel "
            "and each of the following countries: United Arab Emirates, Bahrain, Morocco."
        ),
        "url": "https://www.britannica.com/topic/Abraham-Accords",
        "source_name": "Encyclopaedia Britannica: Abraham Accords",
    },
    "accords_wiki_sudan": {
        "quote": (
            'On January 6, 2021, the government of Sudan signed the "Abraham Accords '
            'Declaration" in Khartoum.'
        ),
        "url": "https://en.wikipedia.org/wiki/Abraham_Accords",
        "source_name": "Wikipedia: Abraham Accords (Sudan signing)",
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
print("Verifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. KEYWORD EXTRACTION (Rule 1)
# Extract key tokens from quote text — never hand-typed separately.
# ---------------------------------------------------------------------------

# SC1: Egypt 1979
egypt_confirm_b1 = verify_extraction("1979", empirical_facts["egypt_wiki"]["quote"], "B1")
egypt_confirm_b2 = verify_extraction("March 26", empirical_facts["egypt_state_dept"]["quote"], "B2")
n_egypt = sum(1 for c in [egypt_confirm_b1, egypt_confirm_b2] if c)
print(f"SC1 Egypt confirmations: {n_egypt}/2")

# SC2: Jordan 1994
jordan_confirm_b3 = verify_extraction("1994", empirical_facts["jordan_wiki"]["quote"], "B3")
jordan_confirm_b4 = verify_extraction("Jordan in 1994", empirical_facts["jordan_accords_xref"]["quote"], "B4")
n_jordan = sum(1 for c in [jordan_confirm_b3, jordan_confirm_b4] if c)
print(f"SC2 Jordan confirmations: {n_jordan}/2")

# SC3: Abraham Accords — 4 states by 2023
# UAE, Bahrain, Morocco from B5 (Britannica); Sudan from B6 (Wikipedia)
uae_confirm     = verify_extraction("United Arab Emirates", empirical_facts["accords_britannica"]["quote"], "B5_uae")
bahrain_confirm = verify_extraction("Bahrain",              empirical_facts["accords_britannica"]["quote"], "B5_bah")
morocco_confirm = verify_extraction("Morocco",              empirical_facts["accords_britannica"]["quote"], "B5_mor")
sudan_confirm   = verify_extraction("Abraham Accords Declaration", empirical_facts["accords_wiki_sudan"]["quote"], "B6_sud")

accords_confirmations = [uae_confirm, bahrain_confirm, morocco_confirm, sudan_confirm]
n_accords_states = sum(1 for c in accords_confirmations if c)
print(f"SC3 Abraham Accords states confirmed: {n_accords_states}/4")

# ---------------------------------------------------------------------------
# 6. RULE 3 — System time (proof is historical; current date for audit record)
# ---------------------------------------------------------------------------
PROOF_GENERATION_DATE = date(2026, 3, 27)
today = date.today()
if today == PROOF_GENERATION_DATE:
    date_note = "System date matches proof generation date."
else:
    date_note = f"Proof generated for {PROOF_GENERATION_DATE}; running on {today}."
print(f"Date check: {date_note}")

# ---------------------------------------------------------------------------
# 7. SUB-CLAIM EVALUATION (Rule 7 — use compare(), never hardcode booleans)
# ---------------------------------------------------------------------------
sc1_holds = compare(n_egypt,          CLAIM_FORMAL["sub_claims"][0]["operator"],
                                      CLAIM_FORMAL["sub_claims"][0]["threshold"])
sc2_holds = compare(n_jordan,         CLAIM_FORMAL["sub_claims"][1]["operator"],
                                      CLAIM_FORMAL["sub_claims"][1]["threshold"])
sc3_holds = compare(n_accords_states, CLAIM_FORMAL["sub_claims"][2]["operator"],
                                      CLAIM_FORMAL["sub_claims"][2]["threshold"])

print(f"SC1 (Egypt 1979) holds: {sc1_holds}")
print(f"SC2 (Jordan 1994) holds: {sc2_holds}")
print(f"SC3 (≥4 Abraham Accords states by 2023) holds: {sc3_holds}")

# Compound: all three must hold (AND)
n_holding = sum([sc1_holds, sc2_holds, sc3_holds])
n_total = 3
claim_holds = compare(n_holding, "==", n_total)

# ---------------------------------------------------------------------------
# 8. CROSS-CHECKS (Rule 6)
# ---------------------------------------------------------------------------
cross_checks = [
    {
        "description": "SC1 Egypt 1979: Wikipedia (B1) vs US State Dept (B2) — independent sources confirm same event",
        "values_compared": [
            "B1: 'signed ... on 26 March 1979'",
            "B2: 'Peace Treaty was formally signed on March 26'",
        ],
        "agreement": egypt_confirm_b1 and egypt_confirm_b2,
    },
    {
        "description": "SC2 Jordan 1994: Wikipedia treaty page (B3) vs Wikipedia Abraham Accords (B4) — different pages confirm Jordan 1994",
        "values_compared": [
            "B3: 'signed ... on 26 October 1994'",
            "B4: 'formally recognize Israel since Jordan in 1994'",
        ],
        "agreement": jordan_confirm_b3 and jordan_confirm_b4,
    },
    {
        "description": "SC3 Abraham Accords states: Britannica (B5, three bilateral states) + Wikipedia (B6, Sudan Declaration) — independent sources",
        "values_compared": [
            f"B5 (Britannica): UAE={uae_confirm}, Bahrain={bahrain_confirm}, Morocco={morocco_confirm}",
            f"B6 (Wikipedia Sudan): Sudan Declaration={sudan_confirm}",
        ],
        "agreement": n_accords_states == 4,
    },
]

# ---------------------------------------------------------------------------
# 9. ADVERSARIAL CHECKS (Rule 5)
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": "Was the Egypt-Israel peace treaty revoked or suspended after Sadat's assassination in 1981?",
        "verification_performed": (
            "Searched for 'Egypt Israel peace treaty revoked annulled suspended after Sadat assassination'. "
            "Reviewed Wikipedia Egypt–Israel peace treaty article and news sources."
        ),
        "finding": (
            "The peace treaty remained continuously in force after Sadat's assassination. "
            "President Mubarak maintained the treaty throughout his 30-year reign. Egypt "
            "recalled its ambassador temporarily (1982-1988 over Lebanon, 2000-2005 over "
            "the Second Intifada), but the treaty was never annulled. SC1 is not undermined."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does 'normalization' in the Abraham Accords constitute formal diplomatic recognition of Israel, or is it merely economic/security cooperation?",
        "verification_performed": (
            "Searched for 'Abraham Accords normalization not recognition argument critics 2020'. "
            "Reviewed Foreign Affairs, Middle East Institute, and Wikipedia Abraham Accords articles."
        ),
        "finding": (
            "Critics argue the Accords bypassed Palestinian concerns and the 2002 Arab Peace "
            "Initiative, but do not dispute that the agreements establish full diplomatic relations. "
            "Wikipedia's Abraham Accords article explicitly states UAE and Bahrain 'formally recognize "
            "Israel' — the same language used for Egypt (1979) and Jordan (1994). SC3 stands."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Should Sudan be excluded from the Abraham Accords count given its bilateral agreement remains unratified?",
        "verification_performed": (
            "Reviewed Britannica Abraham Accords (which notes Sudan signed only the general declaration) "
            "and Wikipedia Abraham Accords (which confirms Sudan signed the Declaration on January 6, 2021). "
            "Checked whether excluding Sudan breaks SC3."
        ),
        "finding": (
            "Sudan signed the Abraham Accords Declaration on January 6, 2021, which constitutes "
            "joining the Accords even without a bilateral agreement. However, even excluding Sudan, "
            "three Abraham Accords states (UAE, Bahrain, Morocco) plus Egypt and Jordan give five "
            "Arab states that formally recognized Israel, still decisively disproving the 'no Arab "
            "state' assertion. SC3 as stated (≥4) requires Sudan to hold — but the meta-claim is "
            "still proved by SC1+SC2 alone if SC3 fails."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 10. VERDICT AND STRUCTURED OUTPUT
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
    elif not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"sum([egypt_confirm_b1, egypt_confirm_b2]) = {n_egypt}"
    FACT_REGISTRY["A1"]["result"] = str(n_egypt)
    FACT_REGISTRY["A2"]["method"] = f"sum([jordan_confirm_b3, jordan_confirm_b4]) = {n_jordan}"
    FACT_REGISTRY["A2"]["result"] = str(n_jordan)
    FACT_REGISTRY["A3"]["method"] = f"sum([uae, bahrain, morocco, sudan confirmations]) = {n_accords_states}"
    FACT_REGISTRY["A3"]["result"] = str(n_accords_states)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1": {
            "value": "1979",
            "value_in_quote": egypt_confirm_b1,
            "quote_snippet": empirical_facts["egypt_wiki"]["quote"][:80],
        },
        "B2": {
            "value": "March 26",
            "value_in_quote": egypt_confirm_b2,
            "quote_snippet": empirical_facts["egypt_state_dept"]["quote"][:80],
        },
        "B3": {
            "value": "1994",
            "value_in_quote": jordan_confirm_b3,
            "quote_snippet": empirical_facts["jordan_wiki"]["quote"][:80],
        },
        "B4": {
            "value": "Jordan in 1994",
            "value_in_quote": jordan_confirm_b4,
            "quote_snippet": empirical_facts["jordan_accords_xref"]["quote"][:80],
        },
        "B5_uae": {
            "value": "United Arab Emirates",
            "value_in_quote": uae_confirm,
            "quote_snippet": empirical_facts["accords_britannica"]["quote"][:80],
        },
        "B5_bah": {
            "value": "Bahrain",
            "value_in_quote": bahrain_confirm,
            "quote_snippet": empirical_facts["accords_britannica"]["quote"][:80],
        },
        "B5_mor": {
            "value": "Morocco",
            "value_in_quote": morocco_confirm,
            "quote_snippet": empirical_facts["accords_britannica"]["quote"][:80],
        },
        "B6_sud": {
            "value": "Abraham Accords Declaration",
            "value_in_quote": sudan_confirm,
            "quote_snippet": empirical_facts["accords_wiki_sudan"]["quote"][:80],
        },
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
        "cross_checks": cross_checks,
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_egypt_1979": {"n_confirming": n_egypt, "holds": sc1_holds},
            "sc2_jordan_1994": {"n_confirming": n_jordan, "holds": sc2_holds},
            "sc3_accords_states": {"n_confirming": n_accords_states, "holds": sc3_holds},
            "n_sub_claims_holding": n_holding,
            "n_sub_claims_total": n_total,
            "claim_holds": claim_holds,
        },
        "date_note": date_note,
        "generator": {
            "name": "proof-engine",
            "version": "0.10.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
