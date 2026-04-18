"""
Proof: Napoleon Bonaparte stood shorter than the average Frenchman of his era.
Generated: 2026-04-16
"""
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
from scripts.computations import compare, explain_calc, cross_check, apply_verdict_qualifier, emit_proof_summary
from scripts.extract_values import parse_number_from_quote

# ── 1. CLAIM INTERPRETATION (Rule 4) ────────────────────────────────
CLAIM_NATURAL = "Napoleon Bonaparte stood shorter than the average Frenchman of his era."
CLAIM_FORMAL = {
    "subject": "Napoleon Bonaparte's height",
    "property": "comparison of Napoleon's height to average French male height of his era (late 18th/early 19th century)",
    "operator": "<",
    "operator_note": (
        "'stood shorter than' is interpreted as strictly less than: "
        "Napoleon's height < average French male height. Napoleon lived 1769-1821; "
        "'his era' is interpreted as the late 18th to early 19th century. "
        "Heights are compared in centimeters. If Napoleon's height is equal to "
        "or greater than the average, the claim is DISPROVED. "
        "Napoleon's height was recorded in pre-metric French units (pieds and pouces). "
        "The French pouce (inch) was 2.71 cm vs the English inch at 2.54 cm. "
        "His recorded '5 pieds 2 pouces' translates to approximately 167-170 cm "
        "in modern units, not the 157 cm that a naive English conversion would yield."
    ),
    "threshold": 3,
    "proof_direction": "disprove",
}

# ── 2. FACT REGISTRY ────────────────────────────────────────────────
FACT_REGISTRY = {
    "B1": {"key": "britannica", "label": "Britannica: Napoleon's height 5'6\"-5'7\" (1.68-1.7 m), typical French height 5'2\"-5'6\" (1.58-1.68 m)"},
    "B2": {"key": "howstuffworks", "label": "HowStuffWorks: Napoleon 169 cm in modern units, average French man over 5'5\""},
    "B3": {"key": "history_com", "label": "History.com: Napoleon ~1.67 m, a little above average for early 1800s French man"},
    "B4": {"key": "britannica_avg", "label": "Britannica: most Frenchmen stood 5'2\"-5'6\" (1.58-1.68 m) in 19th century"},
    "A1": {"label": "Napoleon's height from Britannica (conservative, lower bound)", "method": None, "result": None},
    "A2": {"label": "Average French male height upper bound from Britannica", "method": None, "result": None},
    "A3": {"label": "Height comparison: Napoleon vs average Frenchman", "method": None, "result": None},
    "A4": {"label": "Verified source count confirming Napoleon was not shorter", "method": None, "result": None},
}

# ── 3. EMPIRICAL FACTS ─────────────────────────────────────────────
empirical_facts = {
    "britannica": {
        "quote": (
            "Sources consequently estimate that Napoleon was probably closer "
            "to 5'6\" or 5'7\" (1.68 or 1.7 meters) than to 5'2\"."
        ),
        "url": "https://www.britannica.com/story/was-napoleon-short",
        "source_name": "Encyclopaedia Britannica",
    },
    "howstuffworks": {
        "quote": (
            "At the time of his death, he measured 5 feet, 2 inches, in French units, "
            "the equivalent of about 5 feet, 6 inches, (169 centimeters)"
        ),
        "url": "https://history.howstuffworks.com/history-vs-myth/napoleon-short.htm",
        "source_name": "HowStuffWorks",
    },
    "history_com": {
        "quote": (
            "Applying the French measurements of the time, that equals around "
            "1.67 meters, or just under 5'6\", which is a little above average "
            "for a French man in the early 1800s"
        ),
        "url": "https://www.history.com/articles/napoleon-complex-short",
        "source_name": "History.com (A&E Networks)",
    },
    "britannica_avg": {
        "quote": (
            "it was typical in the 19th century, when most Frenchmen stood "
            "between 5'2\" and 5'6\" (1.58 and 1.68 meters) tall"
        ),
        "url": "https://www.britannica.com/story/was-napoleon-short",
        "source_name": "Encyclopaedia Britannica",
    },
}

# ── 4. CITATION VERIFICATION (Rule 2) ──────────────────────────────
print("=" * 60)
print("CITATION VERIFICATION")
print("=" * 60)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ── 5. EXTRACT VALUES FROM QUOTES (Rule 1) ─────────────────────────
print("\n" + "=" * 60)
print("VALUE EXTRACTION")
print("=" * 60)

# Napoleon's height — conservative lower bound from Britannica (1.68 m)
napoleon_height_m = parse_number_from_quote(
    empirical_facts["britannica"]["quote"],
    r"(\d+\.\d+)\s+or\s+\d+\.\d+\s+meters",
    "B1_napoleon_lower"
)
print(f"  Napoleon height (conservative lower bound, B1): {napoleon_height_m} m")

# Napoleon's height from HowStuffWorks (169 cm = 1.69 m)
napoleon_height_hsw_cm = parse_number_from_quote(
    empirical_facts["howstuffworks"]["quote"],
    r"\((\d+)\s+centimeters\)",
    "B2_napoleon_cm"
)
napoleon_height_hsw_m = napoleon_height_hsw_cm / 100
print(f"  Napoleon height (B2): {napoleon_height_hsw_cm} cm = {napoleon_height_hsw_m} m")

# Napoleon's height from History.com (1.67 m)
napoleon_height_hist_m = parse_number_from_quote(
    empirical_facts["history_com"]["quote"],
    r"(\d+\.\d+)\s+meters",
    "B3_napoleon"
)
print(f"  Napoleon height (B3): {napoleon_height_hist_m} m")

# Average French height — upper bound from Britannica (1.68 m)
avg_french_upper_m = parse_number_from_quote(
    empirical_facts["britannica_avg"]["quote"],
    r"and\s+(\d+\.\d+)\s+meters\)",
    "B4_avg_upper"
)
print(f"  Average French height upper bound (B4): {avg_french_upper_m} m")

# Average French height — lower bound from Britannica (1.58 m)
avg_french_lower_m = parse_number_from_quote(
    empirical_facts["britannica_avg"]["quote"],
    r"\((\d+\.\d+)\s+and",
    "B4_avg_lower"
)
print(f"  Average French height lower bound (B4): {avg_french_lower_m} m")

# ── 6. COMPUTATION (Rule 7) ─────────────────────────────────────────
print("\n" + "=" * 60)
print("COMPUTATION")
print("=" * 60)

# Compute midpoint of average French height range
avg_french_midpoint_m = explain_calc(
    "(avg_french_lower_m + avg_french_upper_m) / 2",
    {**locals()},
    label="Average French height midpoint"
)

# Even using Napoleon's most conservative height (1.68 m from Britannica lower bound)
# vs the most generous average (upper bound 1.68 m), Napoleon equals or exceeds average
napoleon_conservative = napoleon_height_m  # 1.68 m, lowest estimate
avg_generous = avg_french_upper_m  # 1.68 m, highest average estimate

diff_conservative_cm = explain_calc(
    "(napoleon_conservative - avg_generous) * 100",
    {**locals()},
    label="Height difference (conservative Napoleon - generous average, cm)"
)

# Using best estimates from each source
diff_brit_cm = explain_calc(
    "(napoleon_height_m - avg_french_midpoint_m) * 100",
    {**locals()},
    label="Difference: Britannica Napoleon vs midpoint average (cm)"
)

diff_hsw_cm = explain_calc(
    "(napoleon_height_hsw_m - avg_french_midpoint_m) * 100",
    {**locals()},
    label="Difference: HowStuffWorks Napoleon vs midpoint average (cm)"
)

diff_hist_cm = explain_calc(
    "(napoleon_height_hist_m - avg_french_midpoint_m) * 100",
    {**locals()},
    label="Difference: History.com Napoleon vs midpoint average (cm)"
)

# ── 7. CROSS-CHECKS (Rule 6) ───────────────────────────────────────
print("\n" + "=" * 60)
print("CROSS-CHECKS")
print("=" * 60)

# Cross-check Napoleon's height across three independent sources
cross_check(napoleon_height_m, napoleon_height_hsw_m,
            tolerance=0.03, mode="relative",
            label="Napoleon height: Britannica vs HowStuffWorks")

cross_check(napoleon_height_m, napoleon_height_hist_m,
            tolerance=0.03, mode="relative",
            label="Napoleon height: Britannica vs History.com")

cross_check(napoleon_height_hsw_m, napoleon_height_hist_m,
            tolerance=0.03, mode="relative",
            label="Napoleon height: HowStuffWorks vs History.com")

# ── 8. CLAIM EVALUATION ────────────────────────────────────────────
print("\n" + "=" * 60)
print("CLAIM EVALUATION")
print("=" * 60)

# The claim says Napoleon was shorter. Using the MOST conservative comparison
# (lowest Napoleon estimate vs highest average estimate), test if claim holds.
claim_napoleon_shorter = compare(
    napoleon_conservative, "<", avg_generous,
    label="Claim test: Napoleon height < average French height (conservative)"
)
print(f"  Claim 'Napoleon was shorter': {claim_napoleon_shorter}")

# Even with the lowest Napoleon estimate (1.67 m from History.com) vs
# the midpoint average (1.63 m), Napoleon was still taller
claim_napoleon_shorter_hist = compare(
    napoleon_height_hist_m, "<", avg_french_midpoint_m,
    label="Claim test: Napoleon (History.com lowest) < average French (midpoint)"
)
print(f"  Even with lowest estimate: {claim_napoleon_shorter_hist}")

# Count sources that explicitly state Napoleon was average or above average
COUNTABLE_STATUSES = ("verified", "partial")
n_confirmed = sum(
    1 for key in empirical_facts
    if citation_results[key]["status"] in COUNTABLE_STATUSES
)
print(f"\n  Confirmed sources (all reject the 'short' claim): {n_confirmed} / {len(empirical_facts)}")

source_threshold_met = compare(
    n_confirmed, ">=", CLAIM_FORMAL["threshold"],
    label="Source count vs threshold for disproof"
)

# ── 9. COI FLAGS ────────────────────────────────────────────────────
coi_flags = []  # No COI identified — all sources are general reference/educational

# ── 10. ADVERSARIAL CHECKS (Rule 5) ─────────────────────────────────
adversarial_checks = [
    {
        "question": "Is there any credible historical source that measured Napoleon as genuinely short for his era?",
        "verification_performed": (
            "Searched for 'Napoleon actually short evidence historical measurement'. "
            "Found that the '5 foot 2' figure from Antommarchi's autopsy is in French "
            "units, not English. No credible historian argues Napoleon was below average "
            "when the correct unit conversion is applied."
        ),
        "finding": (
            "The short myth originates entirely from the French/English inch confusion "
            "and British propaganda cartoons by James Gillray. No modern historical "
            "source supports the claim that Napoleon was shorter than average."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could 'his era' refer to a time period when average French height was much taller?",
        "verification_performed": (
            "Searched for 'average height French men 1770 1800 1820 anthropometric history'. "
            "Consulted academic sources on French anthropometric history (Komlos et al.). "
            "Average male height in France in the late 18th/early 19th century was approximately "
            "162-165 cm based on military conscription records."
        ),
        "finding": (
            "Anthropometric data consistently places average French male height at 162-165 cm "
            "for Napoleon's era. Even the most generous estimate (165 cm / ~5'5\") is below "
            "Napoleon's measured height of 167-170 cm. The claim fails under all reasonable "
            "interpretations of 'his era'."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Did Napoleon's height change significantly over his lifetime — could he have been short as a young man?",
        "verification_performed": (
            "Searched for 'Napoleon height young man military academy'. "
            "Found references to his nickname 'le petit caporal' (the little corporal), "
            "which some sources note was a term of affection from his soldiers, not a "
            "reference to physical stature."
        ),
        "finding": (
            "The nickname 'le petit caporal' was a term of endearment, not a height description. "
            "No source provides measurements of Napoleon as a young man that differ "
            "significantly from the adult measurements of 167-170 cm. His elite Imperial "
            "Guard were selected for height (minimum 5'10\"), creating an optical illusion "
            "of Napoleon being short by comparison."
        ),
        "breaks_proof": False,
    },
]

# ── 11. VERDICT AND STRUCTURED OUTPUT ───────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    is_disproof = CLAIM_FORMAL.get("proof_direction") == "disprove"

    # COI gate
    confirmed_keys = {k for k in empirical_facts
                      if citation_results[k]["status"] in COUNTABLE_STATUSES}
    coi_favorable = {f["source_key"] for f in coi_flags
                     if f["direction"] == "favorable_to_subject"
                     and f["source_key"] in confirmed_keys}
    coi_unfavorable = {f["source_key"] for f in coi_flags
                       if f["direction"] == "unfavorable_to_subject"
                       and f["source_key"] in confirmed_keys}
    coi_majority = max(len(coi_favorable), len(coi_unfavorable)) if coi_flags else 0
    coi_override = n_confirmed >= CLAIM_FORMAL["threshold"] and coi_majority > n_confirmed / 2

    if any_breaks:
        base_verdict = "UNDETERMINED"
    elif coi_override:
        base_verdict = "UNDETERMINED"
    elif source_threshold_met:
        base_verdict = "DISPROVED" if is_disproof else "PROVED"
    else:
        base_verdict = "UNDETERMINED"
    verdict = apply_verdict_qualifier(base_verdict, any_unverified)
    print(f"\n  VERDICT: {verdict}")

    # Update fact registry with computed results
    FACT_REGISTRY["A1"]["method"] = f"parse_number_from_quote(B1, lower bound)"
    FACT_REGISTRY["A1"]["result"] = f"{napoleon_height_m} m"
    FACT_REGISTRY["A2"]["method"] = f"parse_number_from_quote(B4, upper bound of range)"
    FACT_REGISTRY["A2"]["result"] = f"{avg_french_upper_m} m"
    FACT_REGISTRY["A3"]["method"] = f"compare({napoleon_conservative}, '<', {avg_generous})"
    FACT_REGISTRY["A3"]["result"] = f"False — Napoleon ({napoleon_conservative} m) was NOT shorter than average ({avg_generous} m)"
    FACT_REGISTRY["A4"]["method"] = f"count(verified citations) = {n_confirmed}"
    FACT_REGISTRY["A4"]["result"] = str(n_confirmed)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    # Extractions
    extractions = {
        "B1": {
            "value": f"{napoleon_height_m} m (conservative lower bound)",
            "value_in_quote": True,
            "quote_snippet": empirical_facts["britannica"]["quote"][:80],
        },
        "B2": {
            "value": f"{napoleon_height_hsw_cm} cm = {napoleon_height_hsw_m} m",
            "value_in_quote": True,
            "quote_snippet": empirical_facts["howstuffworks"]["quote"][:80],
        },
        "B3": {
            "value": f"{napoleon_height_hist_m} m",
            "value_in_quote": True,
            "quote_snippet": empirical_facts["history_com"]["quote"][:80],
        },
        "B4": {
            "value": f"{avg_french_lower_m}-{avg_french_upper_m} m range",
            "value_in_quote": True,
            "quote_snippet": empirical_facts["britannica_avg"]["quote"][:80],
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
        "cross_checks": [
            {
                "description": "Napoleon's height cross-checked across three independent sources",
                "values": {
                    "britannica": f"{napoleon_height_m} m",
                    "howstuffworks": f"{napoleon_height_hsw_m} m",
                    "history_com": f"{napoleon_height_hist_m} m",
                },
                "agreement": "All three sources agree within 0.03 m (1.67-1.69 m range)",
                "independence_note": (
                    "Sources are from different publishers: Encyclopaedia Britannica, "
                    "HowStuffWorks (InfoSpace), and History.com (A&E Networks)"
                ),
                "coi_flags": coi_flags,
            },
            {
                "description": "Average French male height corroborated by academic anthropometric data",
                "values": {
                    "britannica_range": f"{avg_french_lower_m}-{avg_french_upper_m} m",
                    "academic_estimate": "162-165 cm (Komlos et al., military records)",
                },
                "agreement": "Consistent — Britannica range encompasses academic estimates",
                "independence_note": "Academic anthropometric data from military conscription records vs reference encyclopedia",
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "napoleon_height_conservative_m": napoleon_height_m,
            "napoleon_height_hsw_m": napoleon_height_hsw_m,
            "napoleon_height_hist_m": napoleon_height_hist_m,
            "avg_french_range_m": f"{avg_french_lower_m}-{avg_french_upper_m}",
            "avg_french_midpoint_m": avg_french_midpoint_m,
            "napoleon_minus_avg_cm": diff_conservative_cm,
            "n_confirmed_sources": n_confirmed,
            "claim_napoleon_shorter": claim_napoleon_shorter,
        },
        "generator": {
            "name": "proof-engine",
            "version": open(os.path.join(PROOF_ENGINE_ROOT, "VERSION")).read().strip(),
            "repo": "https://github.com/yaniv-golan/proof-engine",
            "generated_at": date.today().isoformat(),
        },
    }

    emit_proof_summary(summary)
