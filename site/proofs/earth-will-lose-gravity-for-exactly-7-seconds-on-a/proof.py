"""
Proof: Earth will lose gravity for exactly 7 seconds on August 12, 2026, causing 40 million deaths.
Generated: 2026-03-28

Proof strategy: DISPROOF via qualitative consensus.
The claim is a compound assertion (SC1 AND SC2):
  SC1: Earth will experience a zero-gravity event on 2026-08-12
  SC2: This event will cause 40 million deaths
SC1 is physically impossible per Newton's law of gravitation and is a documented internet hoax.
SC2 is contingent on SC1 and falls with it.
Three independent authoritative sources confirming the impossibility of SC1 establish DISPROVED.
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare

# ---------------------------------------------------------------------------
# 1. CLAIM INTERPRETATION (Rule 4)
# ---------------------------------------------------------------------------
CLAIM_NATURAL = (
    "Earth will lose gravity for exactly 7 seconds on August 12, 2026, "
    "causing 40 million deaths."
)
CLAIM_FORMAL = {
    "subject": "Earth's gravitational field on 2026-08-12",
    "property": "count of authoritative sources confirming this event is physically impossible",
    "operator": ">=",
    "operator_note": (
        "The claim is a compound assertion: "
        "SC1 (Earth undergoes a 7-second zero-gravity event on 2026-08-12) AND "
        "SC2 (this causes 40 million deaths). "
        "SC1 is disproved if 3 or more authoritative sources independently confirm it is "
        "physically impossible. SC2 is contingent on SC1 — if SC1 is impossible, SC2 "
        "cannot occur. Gravity is produced by mass via Newton's law F = Gm1*m2/r^2; "
        "it cannot 'switch off' while Earth's mass exists. "
        "NASA — the institution the hoax falsely invokes — has explicitly denied this claim."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
    "sub_claims": [
        {
            "id": "SC1",
            "description": "Earth will experience a zero-gravity event on 2026-08-12",
            "disproof_method": "3 authoritative sources confirm physical impossibility",
        },
        {
            "id": "SC2",
            "description": "The alleged event causes 40 million deaths",
            "disproof_method": "Contingent on SC1; falls with SC1 disproof",
        },
    ],
}

# ---------------------------------------------------------------------------
# 2. FACT REGISTRY
# ---------------------------------------------------------------------------
FACT_REGISTRY = {
    "B1": {
        "key": "source_bgr",
        "label": "BGR: NASA spokesperson explicitly denies Earth will lose gravity on 2026-08-12",
    },
    "B2": {
        "key": "source_dailygalaxy",
        "label": "Daily Galaxy: Full NASA statement — only way to lose gravity is to lose mass",
    },
    "B3": {
        "key": "source_nasa_spaceplace",
        "label": "NASA Space Place: Authoritative physics — gravity comes from mass",
    },
    "A1": {
        "label": "Verified source count for SC1 disproof",
        "method": None,
        "result": None,
    },
}

# ---------------------------------------------------------------------------
# 3. EMPIRICAL FACTS — sources that REJECT the claim (support disproof)
#    Adversarial sources (those that could support the claim) go in
#    adversarial_checks only, NOT here.
# ---------------------------------------------------------------------------
empirical_facts = {
    "source_bgr": {
        "quote": (
            "The Earth will not lose gravity on Aug. 12, 2026. "
            "Earth's gravity, or total gravitational force, is determined by its mass."
        ),
        "url": "https://www.bgr.com/2081398/nasa-conspiracy-theory-earth-lose-gravity-august-2026-explained/",
        "source_name": "BGR (citing NASA spokesperson confirmation)",
    },
    "source_dailygalaxy": {
        "quote": (
            "The Earth will not lose gravity on Aug. 12, 2026. "
            "Earth's gravity, or total gravitational force, is determined by its mass. "
            "The only way for the Earth to lose gravity would be for the Earth system, "
            "the combined mass of its core, mantle, crust, ocean, terrestrial water, "
            "and atmosphere, to lose mass."
        ),
        "url": "https://dailygalaxy.com/2026/01/earth-lose-gravity-for-7-seconds-2026-nasa/",
        "source_name": "Daily Galaxy (citing NASA statement on the hoax)",
    },
    "source_nasa_spaceplace": {
        "quote": (
            "Earth's gravity comes from all its mass. "
            "All its mass makes a combined gravitational pull on all the mass in your body."
        ),
        "url": "https://spaceplace.nasa.gov/what-is-gravity/en/",
        "source_name": "NASA Space Place (NASA official educational resource on gravity)",
    },
}

# ---------------------------------------------------------------------------
# 4. CITATION VERIFICATION (Rule 2)
# ---------------------------------------------------------------------------
print("Verifying citations...")
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ---------------------------------------------------------------------------
# 5. COUNT SOURCES WITH VERIFIED CITATIONS
# ---------------------------------------------------------------------------
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"  Confirmed sources: {n_confirmed} / {len(empirical_facts)}")

# ---------------------------------------------------------------------------
# 6. CLAIM EVALUATION (Rule 7 — use compare(), never hardcode)
# ---------------------------------------------------------------------------
claim_holds = compare(
    n_confirmed,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="verified sources rejecting the gravity-loss claim",
)

# ---------------------------------------------------------------------------
# 7. ADVERSARIAL CHECKS (Rule 5) — performed before writing this proof
# ---------------------------------------------------------------------------
adversarial_checks = [
    {
        "question": (
            "Is there a real NASA document called 'Project Anchor' predicting a "
            "7-second gravitational anomaly on 2026-08-12?"
        ),
        "verification_performed": (
            "Searched 'NASA Project Anchor gravity 2026' across Google, Bing, DuckDuckGo, "
            "and Yahoo. Reviewed Snopes investigation (which conducted the same multi-engine "
            "search). Also searched NASA.gov directly."
        ),
        "finding": (
            "No credible evidence for 'Project Anchor' exists. The claim originated as an "
            "anonymous social media post circulated in November 2024. NASA's spokesperson "
            "confirmed no such document or project exists. Snopes rated the claim False."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could any known astronomical event on August 12, 2026 affect Earth's gravity?"
        ),
        "verification_performed": (
            "Searched astronomical calendars for events on 2026-08-12. "
            "NASA confirms a total solar eclipse is visible from parts of Europe and the "
            "Arctic on that date."
        ),
        "finding": (
            "A total solar eclipse does occur on 2026-08-12. However, NASA states 'A total "
            "solar eclipse has no unusual impact on Earth's gravity.' Solar and lunar tidal "
            "forces are well-studied and cause < 0.01% variation in local gravity — "
            "not a total loss. This known event may be the seed of the hoax but does not "
            "support the claim."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could gravitational waves cause Earth to temporarily 'lose gravity'?"
        ),
        "verification_performed": (
            "Searched LIGO/Virgo documentation on gravitational wave effects at Earth's surface. "
            "Reviewed physics literature on gravitational wave strain magnitude."
        ),
        "finding": (
            "Gravitational waves (ripples in spacetime from, e.g., black hole mergers) produce "
            "strain of order 10^-21 — one part per sextillion — utterly imperceptible. "
            "They do not modify Earth's surface gravitational acceleration; they cannot cause "
            "a 'loss' of gravity. No credible source supports this mechanism for the alleged event."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Is there any peer-reviewed scientific paper or credible forecast of a temporary "
            "gravity-cessation event on Earth in 2026?"
        ),
        "verification_performed": (
            "Searched NASA ADS, arXiv, Google Scholar, and general web search for "
            "'Earth gravity cessation 2026', 'temporary gravity loss Earth mechanism', "
            "'zero gravity Earth event 2026'. Searched for any credible scientific claim "
            "supporting the 40 million death figure."
        ),
        "finding": (
            "Zero peer-reviewed papers or credible forecasts found. All results are news "
            "articles and fact-checks debunking the hoax. No scientific institution has "
            "predicted, modeled, or warned of such an event. The 40 million death figure "
            "appears in no scientific literature."
        ),
        "breaks_proof": False,
    },
]

# ---------------------------------------------------------------------------
# 8. VERDICT AND STRUCTURED OUTPUT
# ---------------------------------------------------------------------------
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
    FACT_REGISTRY["A1"]["result"] = str(n_confirmed)

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
                "description": (
                    "Three independent publications all reject the gravity-loss claim. "
                    "B1 and B2 both cite the same NASA spokesperson statement (same upstream "
                    "authority, independently published). B3 (NASA Space Place) is an independent "
                    "NASA educational resource establishing the underlying physics: gravity is "
                    "produced by mass and cannot 'switch off.'"
                ),
                "n_sources_consulted": len(empirical_facts),
                "n_sources_verified": n_confirmed,
                "sources": {k: citation_results[k]["status"] for k in empirical_facts},
                "independence_note": (
                    "B1 and B2 independently published the same NASA statement (same upstream "
                    "authority). B3 is an independent NASA educational resource. This is "
                    "'independently published (same upstream authority)' — weaker than "
                    "independent measurements, but sufficient for disproving a hoax claim "
                    "given the underlying physics is unambiguous."
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
            "sc1_disproved": claim_holds,
            "sc2_disproved": claim_holds,  # SC2 contingent on SC1
            "proof_direction": "disprove",
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
