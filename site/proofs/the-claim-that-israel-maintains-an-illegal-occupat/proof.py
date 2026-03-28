"""
Proof: The claim that Israel maintains an illegal occupation of the entire West Bank is
contradicted by the Oslo Accords designating Area C as remaining under full Israeli civil
and security administration pending final-status negotiations.
Generated: 2026-03-27
"""
import json
from datetime import date
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from scripts.smart_extract import verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ============================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# ============================================================
CLAIM_NATURAL = (
    "The claim that Israel maintains an illegal occupation of the entire West Bank "
    "is contradicted by the Oslo Accords designating Area C as remaining under full "
    "Israeli civil and security administration pending final-status negotiations."
)

# This is a COMPOUND claim with two sub-claims that must both hold:
#
# SC1: The Oslo Accords (Oslo II, 1995) do designate Area C under full Israeli
#      civil and security administration pending final-status negotiations.
#      (A factual claim about treaty content — verifiable.)
#
# SC2: This designation "contradicts" the assertion that Israel illegally occupies
#      the ENTIRE West Bank. This further decomposes:
#
#   SC2a — the "entire" dimension:
#      Oslo shows Areas A and B are NOT under Israeli civil control, undermining
#      the "entire West Bank" characterization. This sub-dimension HOLDS.
#
#   SC2b — the "illegal" dimension:
#      Does the Oslo administrative designation contradict the claim that the
#      occupation is *illegal* under international law?
#      International law (Fourth Geneva Convention Art. 47) bars bilateral
#      agreements from derogating IHL protections, and the ICJ's 2024 Advisory
#      Opinion explicitly found the occupation unlawful regardless of Oslo.
#      This sub-dimension does NOT hold.
#
# Because SC2b fails, the overall claim is only PARTIALLY VERIFIED.

CLAIM_FORMAL = {
    "subject": "Oslo Accords / Area C designation",
    "sub_claims": [
        {
            "id": "SC1",
            "property": "Oslo II (1995) designates Area C under full Israeli civil and security administration pending final-status negotiations",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC1 requires at least 2 independent sources confirming the Area C designation. "
                "This is a factual claim about the text of the Interim Agreement and is "
                "non-controversial — confirmed by the treaty text itself and authoritative summaries."
            ),
        },
        {
            "id": "SC2a",
            "property": "Oslo shows the West Bank is NOT entirely under Israeli civil control (Areas A and B have Palestinian civil administration)",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC2a requires at least 2 sources confirming Areas A and B are under Palestinian "
                "civil administration, undercutting the 'entire West Bank' characterization. "
                "This is also non-controversial and established by the treaty text."
            ),
        },
        {
            "id": "SC2b",
            "property": "The Oslo designation contradicts the 'illegal' characterization under international law",
            "operator": ">=",
            "threshold": 2,
            "operator_note": (
                "SC2b would require sources showing Oslo's bilateral arrangements preclude an "
                "'illegal occupation' finding under international law. This sub-claim FAILS: "
                "the ICJ 2024 Advisory Opinion explicitly found the occupation unlawful and "
                "stated that Oslo accords cannot detract from Israel's obligations under "
                "international law. The Fourth Geneva Convention (Art. 47) bars bilateral "
                "agreements from derogating IHL protections."
            ),
        },
    ],
    "compound_operator": "AND",
    "operator_note": (
        "All three sub-claims must hold for the overall claim to be PROVED. "
        "SC1 and SC2a are verifiable and hold; SC2b fails. "
        "Result: PARTIALLY VERIFIED — the factual basis is correct (Area C designation exists "
        "and does differentiate from Areas A/B), but the 'illegal' dimension is not contradicted "
        "by Oslo, which is a bilateral administrative arrangement, not an international law adjudication."
    ),
}

# ============================================================
# 2. FACT REGISTRY
# ============================================================
FACT_REGISTRY = {
    # SC1: Area C designation
    "B1": {"key": "wiki_oslo_ii_areas", "label": "Wikipedia: Oslo II Accord — Area C 'full Israeli civil and security control'"},
    "B2": {"key": "area_c_wiki", "label": "Wikipedia: Area C — Oslo II definition 'gradually transferred to Palestinian jurisdiction'"},
    # SC2a: Areas A and B under Palestinian civil administration
    "B3": {"key": "wiki_area_a", "label": "Wikipedia: Oslo II Accord — Area A 'full civil and security control by the Palestinian Authority'"},
    "B4": {"key": "wiki_area_b", "label": "Wikipedia: Oslo II Accord — Area B 'Palestinian civil control and joint Israeli-Palestinian security control'"},
    # SC2b adversarial: ICJ on illegality and Oslo
    # (These go to adversarial_checks, not empirical_facts — they argue AGAINST the meta-claim)
    "A1": {"label": "SC1 confirmed: n_sources_sc1 >= 2", "method": None, "result": None},
    "A2": {"label": "SC2a confirmed: n_sources_sc2a >= 2", "method": None, "result": None},
    "A3": {"label": "SC2b fails: ICJ 2024 finds occupation unlawful regardless of Oslo", "method": None, "result": None},
}

# ============================================================
# 3. EMPIRICAL FACTS — supporting SC1 and SC2a
# (Adversarial sources documenting SC2b failure go in adversarial_checks)
# ============================================================
empirical_facts = {
    # SC1 sources: Area C under Israeli control
    "wiki_oslo_ii_areas": {
        "quote": (
            "Area C (full Israeli civil and security control): initially, circa 72\u201374% "
            "(first phase, 1995)"
        ),
        "url": "https://en.wikipedia.org/wiki/West_Bank_areas_in_the_Oslo_II_Accord",
        "source_name": "Wikipedia: West Bank areas in the Oslo II Accord",
    },
    "area_c_wiki": {
        "quote": (
            "areas of the West Bank outside Areas A and B, which, except for the issues "
            "that will be negotiated in the permanent status negotiations, will be gradually "
            "transferred to Palestinian jurisdiction in accordance with this Agreement"
        ),
        "url": "https://en.wikipedia.org/wiki/Area_C_(West_Bank)",
        "source_name": "Wikipedia: Area C (West Bank) — quoting Oslo II Accord definition",
    },
    # SC2a sources: Areas A and B under Palestinian civil administration
    "wiki_area_a": {
        "quote": (
            "full civil and security control by the Palestinian Authority"
        ),
        "url": "https://en.wikipedia.org/wiki/West_Bank_areas_in_the_Oslo_II_Accord",
        "source_name": "Wikipedia: West Bank areas in the Oslo II Accord — Area A designation",
    },
    "wiki_area_b": {
        "quote": (
            "Palestinian civil control and joint Israeli-Palestinian security control"
        ),
        "url": "https://en.wikipedia.org/wiki/West_Bank_areas_in_the_Oslo_II_Accord",
        "source_name": "Wikipedia: West Bank areas in the Oslo II Accord — Area B designation",
    },
}

# ============================================================
# 4. CITATION VERIFICATION (Rule 2)
# ============================================================
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ============================================================
# 5. KEYWORD EXTRACTION — verify key terms appear in each quote
# ============================================================

# SC1: confirm Area C is under Israeli control
sc1_confirmations = []
sc1_confirmations.append(
    verify_extraction("Israeli civil and security control", empirical_facts["wiki_oslo_ii_areas"]["quote"], "B1")
)
sc1_confirmations.append(
    verify_extraction("permanent status negotiations", empirical_facts["area_c_wiki"]["quote"], "B2")
)

# SC2a: confirm Areas A and B have Palestinian civil control
sc2a_confirmations = []
sc2a_confirmations.append(
    verify_extraction("Palestinian Authority", empirical_facts["wiki_area_a"]["quote"], "B3")
)
sc2a_confirmations.append(
    verify_extraction("Palestinian civil control", empirical_facts["wiki_area_b"]["quote"], "B4")
)

# ============================================================
# 6. SOURCE COUNTS AND SUB-CLAIM EVALUATION
# ============================================================
n_sc1 = sum(1 for c in sc1_confirmations if c)
n_sc2a = sum(1 for c in sc2a_confirmations if c)
# SC2b: fails by definition — see adversarial_checks below
n_sc2b = 0  # ICJ 2024 opinion directly contradicts this sub-claim

sc1_holds = compare(n_sc1, ">=", 2)    # Oslo designates Area C under Israeli control
sc2a_holds = compare(n_sc2a, ">=", 2)  # Oslo shows not "entire" West Bank under Israeli civil control
sc2b_holds = compare(n_sc2b, ">=", 2)  # Oslo contradicts "illegal" under int'l law → FALSE

# Count holding sub-claims (out of 3)
n_holding = sum([sc1_holds, sc2a_holds, sc2b_holds])
n_total = 3
claim_holds = compare(n_holding, "==", n_total)  # True only if ALL hold

# ============================================================
# 7. ADVERSARIAL CHECKS (Rule 5)
# ============================================================
adversarial_checks = [
    {
        "question": "Does the Oslo II Accord's designation of Area C contradict international legal characterizations of the occupation as illegal?",
        "verification_performed": (
            "Fetched ICJ Advisory Opinion summary (icj-cij.org/node/204176, July 19 2024). "
            "Searched for legal scholarship on Oslo Accords and occupation law. "
            "Reviewed opiniojuris.org article on Oslo Accords and ICC jurisdiction (2020). "
            "Reviewed Indiana University Law Review article on Oslo Accords and occupation. "
            "Reviewed Max Planck Institute analysis (mpil.de) on West Bank/Gaza legal status."
        ),
        "finding": (
            "The ICJ 2024 Advisory Opinion explicitly found: (1) 'Israel's continued presence "
            "in the Occupied Palestinian Territory is unlawful'; (2) 'the Oslo Accords do not "
            "permit Israel to annex parts of the Occupied Palestinian Territory in order to meet "
            "its security needs. Nor do they authorize Israel to maintain a permanent presence'; "
            "(3) such agreements 'cannot be understood to detract from Israel's obligations under "
            "the pertinent rules of international law applicable in the Occupied Palestinian Territory.' "
            "Fourth Geneva Convention Article 47 bars bilateral agreements from derogating "
            "international humanitarian law protections. The Oslo Accords govern administrative "
            "arrangements but do not adjudicate legality under international law. "
            "Therefore SC2b (Oslo contradicts 'illegal' characterization) fails."
        ),
        "breaks_proof": False,  # Does not break SC1 or SC2a; only confirms SC2b fails
    },
    {
        "question": "Does Israel's consent argument (Palestinians agreed via Oslo, so no occupation) have legal merit?",
        "verification_performed": (
            "Searched: 'Israel Oslo Accords estoppel no occupation argument international law'. "
            "Reviewed JCFA article 'Palestinian Compliance with the Oslo Accords: A Legal Overview'. "
            "Reviewed Opinio Juris analysis of ICC jurisdiction and Oslo."
        ),
        "finding": (
            "Israel argues that Palestinian consent via Oslo removes the 'occupation' characterization. "
            "This argument is rejected by the ICJ and mainstream international law scholarship: "
            "Article 47 of the Fourth Geneva Convention specifically states that protected persons "
            "cannot renounce rights regardless of any agreement. The ICJ 2004 Wall Advisory Opinion "
            "also found the West Bank remained occupied territory subject to international law. "
            "Israel's consent argument is a minority legal position not accepted by international tribunals."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does 'entire West Bank' terminology accurately describe the occupation given Oslo's zone divisions?",
        "verification_performed": (
            "Searched for UN, Palestinian Authority, and scholarly usage of 'entire West Bank occupation'. "
            "Reviewed Al Jazeera, Anera, and UN sources on Areas A, B, C. "
            "Checked whether critics of the occupation claim 'entire West Bank' or qualify by zone."
        ),
        "finding": (
            "International critics typically say 'occupied West Bank' (not 'entire') or acknowledge "
            "the Oslo zone divisions. The ICJ 2024 opinion refers to 'the Occupied Palestinian Territory' "
            "without implying uniform Israeli civil administration. Area A (18%) has full Palestinian "
            "civil and security control; Area B (22%) has Palestinian civil control. "
            "The 'entire West Bank under Israeli civil control' framing overstates the situation "
            "even under Oslo — SC2a therefore partially holds, but critics seldom use this exact framing."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the Area C designation be read as mutual agreement that legitimizes Israeli control, thereby undermining the 'illegal' label?",
        "verification_performed": (
            "Reviewed legal analysis of Oslo Accords as lex specialis vs. lex generalis. "
            "Fetched opiniojuris.org/2020/06/10 (Oslo Accords and ICC jurisdiction). "
            "Searched for academic articles on Oslo II and Fourth Geneva Convention applicability."
        ),
        "finding": (
            "International law scholars and the ICJ consistently hold that Oslo is not lex specialis "
            "overriding the Fourth Geneva Convention. Bilateral consent cannot waive occupation law "
            "protections. The PLO's agreement to interim arrangements does not transform the legal "
            "character of the occupation. This confirms SC2b fails — the Oslo designation does not "
            "constitute a contradiction of the 'illegal' characterization under international law."
        ),
        "breaks_proof": False,
    },
]

# ============================================================
# 8. VERDICT AND STRUCTURED OUTPUT
# ============================================================
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    # Compound verdict logic:
    # SC1 holds, SC2a holds, SC2b fails → mixed → PARTIALLY VERIFIED
    if not claim_holds and n_holding > 0:
        verdict = "PARTIALLY VERIFIED"
    elif claim_holds and not any_unverified:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds and n_holding == 0:
        verdict = "DISPROVED"
    else:
        verdict = "UNDETERMINED"

    FACT_REGISTRY["A1"]["method"] = f"sum(sc1_confirmations) = {n_sc1}"
    FACT_REGISTRY["A1"]["result"] = f"{n_sc1} / 2 sources confirm SC1 (Area C under Israeli control)"
    FACT_REGISTRY["A2"]["method"] = f"sum(sc2a_confirmations) = {n_sc2a}"
    FACT_REGISTRY["A2"]["result"] = f"{n_sc2a} / 2 sources confirm SC2a (Areas A, B under Palestinian civil control)"
    FACT_REGISTRY["A3"]["method"] = "adversarial_check: ICJ 2024 Advisory Opinion"
    FACT_REGISTRY["A3"]["result"] = (
        "SC2b fails: ICJ found occupation unlawful; Oslo cannot detract from international law obligations"
    )

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    sc1_extractions = {
        "B1": {
            "value": "Israeli civil and security control confirmed",
            "value_in_quote": sc1_confirmations[0],
            "quote_snippet": empirical_facts["wiki_oslo_ii_areas"]["quote"][:80],
        },
        "B2": {
            "value": "permanent status negotiations confirmed",
            "value_in_quote": sc1_confirmations[1],
            "quote_snippet": empirical_facts["area_c_wiki"]["quote"][:80],
        },
    }
    sc2a_extractions = {
        "B3": {
            "value": "Palestinian Authority civil control (Area A) confirmed",
            "value_in_quote": sc2a_confirmations[0],
            "quote_snippet": empirical_facts["wiki_area_a"]["quote"][:80],
        },
        "B4": {
            "value": "Palestinian civil control (Area B) confirmed",
            "value_in_quote": sc2a_confirmations[1],
            "quote_snippet": empirical_facts["wiki_area_b"]["quote"][:80],
        },
    }
    extractions = {**sc1_extractions, **sc2a_extractions}

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
                "description": "SC1: Area C under Israeli control — two independent Wikipedia sections (same article, different claims)",
                "n_sources": 2,
                "n_confirming": n_sc1,
                "agreement": n_sc1 >= 2,
            },
            {
                "description": "SC2a: Areas A and B under Palestinian civil control — Area A and Area B descriptions independently confirm",
                "n_sources": 2,
                "n_confirming": n_sc2a,
                "agreement": n_sc2a >= 2,
            },
            {
                "description": "SC2b: Oslo contradicts 'illegal' characterization — ICJ 2024 Advisory Opinion contradicts this sub-claim",
                "n_sources": 1,
                "n_confirming": 0,
                "agreement": False,
                "note": "SC2b fails: ICJ 2024 explicitly found occupation unlawful and stated Oslo cannot detract from international law obligations",
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "n_sc1_confirming": n_sc1,
            "n_sc2a_confirming": n_sc2a,
            "n_sc2b_confirming": n_sc2b,
            "sc1_holds": sc1_holds,
            "sc2a_holds": sc2a_holds,
            "sc2b_holds": sc2b_holds,
            "n_subclaims_holding": n_holding,
            "n_subclaims_total": n_total,
            "claim_holds": claim_holds,
        },
        "generator": {
            "name": "proof-engine",
            "version": "0.10.0",
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    print("\n=== PROOF SUMMARY (JSON) ===")
    print(json.dumps(summary, indent=2, default=str))
