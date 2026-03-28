"""
Proof: Local Cepheid-variable measurements of the Hubble constant exceed
72 km s⁻¹ Mpc⁻¹ while the 2018 Planck CMB inference yields a value below
68 km s⁻¹ Mpc⁻¹.
Generated: 2026-03-28
"""
import json
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

# --- STRUCTURAL IMPORTS ---
from scripts.smart_extract import verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.extract_values import parse_number_from_quote
from scripts.computations import compare, explain_calc, cross_check

# ============================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# ============================================================
CLAIM_NATURAL = (
    "Local Cepheid-variable measurements of the Hubble constant exceed "
    "72 km s⁻¹ Mpc⁻¹ while the 2018 Planck CMB inference yields a value "
    "below 68 km s⁻¹ Mpc⁻¹."
)

CLAIM_FORMAL = {
    "subject": "Hubble constant (H₀) as measured by two independent methods",
    "property": "central reported values of H₀ from (a) the SH0ES Cepheid-calibrated "
                "distance ladder and (b) the Planck 2018 CMB ΛCDM inference",
    "operator": "SC1: > 72 AND SC2: < 68",
    "operator_note": (
        "The claim is a conjunction of two sub-claims. "
        "SC1: The SH0ES Cepheid-variable measurement of H₀ strictly exceeds 72 km/s/Mpc. "
        "SC2: The Planck 2018 CMB-inferred H₀ under base-ΛCDM is strictly less than 68 km/s/Mpc. "
        "'Local Cepheid-variable measurements' is interpreted as the most comprehensive "
        "Cepheid-based determination, i.e. the SH0ES team result (Riess et al. 2022), "
        "which is the definitive Cepheid distance-ladder measurement. "
        "'2018 Planck CMB inference' refers to the Planck Collaboration 2018 result "
        "(published 2020 in A&A) under base-ΛCDM. "
        "Both thresholds refer to central (best-fit) values, not uncertainty bounds."
    ),
    "threshold_sc1": 72,
    "threshold_sc2": 68,
}

# ============================================================
# 2. FACT REGISTRY
# ============================================================
FACT_REGISTRY = {
    "B1": {"key": "shoes_arxiv", "label": "SH0ES H₀ measurement (Riess et al. 2022, arXiv)"},
    "B2": {"key": "shoes_iop", "label": "SH0ES H₀ measurement (Riess et al. 2022, IOPscience)"},
    "B3": {"key": "planck_arxiv", "label": "Planck 2018 H₀ inference (Planck Collaboration, arXiv)"},
    "B4": {"key": "planck_esa", "label": "Planck 2018 H₀ inference (ESA Science Portal)"},
    "A1": {"label": "SC1: SH0ES H₀ > 72 km/s/Mpc", "method": None, "result": None},
    "A2": {"label": "SC2: Planck H₀ < 68 km/s/Mpc", "method": None, "result": None},
    "A3": {"label": "Cross-check: SH0ES values agree across sources", "method": None, "result": None},
    "A4": {"label": "Cross-check: Planck values agree across sources", "method": None, "result": None},
}

# ============================================================
# 3. EMPIRICAL FACTS
# ============================================================
empirical_facts = {
    "shoes_arxiv": {
        "quote": (
            "Our baseline result from the Cepheid-SN sample is "
            "H0=73.04+-1.04 km/s/Mpc, which includes systematics "
            "and lies near the median of all analysis variants."
        ),
        "url": "https://arxiv.org/abs/2112.04510",
        "source_name": "Riess et al. 2022 (arXiv:2112.04510)",
        "snapshot": (
            "We report observations from HST of Cepheids in the hosts of 42 SNe Ia "
            "used to calibrate the Hubble constant (H0). These include all suitable "
            "SNe Ia in the last 40 years at z<0.01, measured with >1000 orbits, more "
            "than doubling the sample whose size limits the precision of H0. "
            "Our baseline result from the Cepheid-SN sample is H0=73.04+-1.04 "
            "km/s/Mpc, which includes systematics and lies near the median of all "
            "analysis variants. We demonstrate consistency with measures from HST of "
            "the TRGB between SN hosts and NGC 4258 with Cepheids and together these "
            "yield 72.53+-0.99. Including high-z SN Ia we find H0=73.30+-1.04 with "
            "q0=-0.51+-0.024. We find a 5-sigma difference with H0 predicted by "
            "Planck+LCDM, with no indication this arises from measurement errors or "
            "analysis variations considered to date."
        ),
    },
    "shoes_iop": {
        "quote": (
            "Our baseline result from the Cepheid–SN Ia sample is "
            "H 0 = 73.04 ± 1.04 km s−1 Mpc−1, which includes systematic "
            "uncertainties and lies near the median of all analysis variants."
        ),
        "url": "https://iopscience.iop.org/article/10.3847/2041-8213/ac5c5b",
        "source_name": "Riess et al. 2022 (ApJL 934 L7, IOPscience)",
        "snapshot": (
            "Our baseline result from the Cepheid–SN Ia sample is "
            "H 0 = 73.04 ± 1.04 km s−1 Mpc−1, which includes systematic "
            "uncertainties and lies near the median of all analysis variants. "
            "We demonstrate consistency with measures from HST of the TRGB between "
            "SN hosts and NGC 4258 with Cepheids and together these yield "
            "72.53 ± 0.99 km s−1 Mpc−1."
        ),
    },
    "planck_arxiv": {
        "quote": (
            "Assuming the base-LCDM cosmology, the inferred late-Universe "
            "parameters are: Hubble constant H0 = (67.4+-0.5) km/s/Mpc"
        ),
        "url": "https://arxiv.org/abs/1807.06209",
        "source_name": "Planck Collaboration 2018 (arXiv:1807.06209)",
        "snapshot": (
            "Assuming the base-LCDM cosmology, the inferred (flat) late-Universe "
            "parameters are: Hubble constant H0 = (67.4+-0.5) km/s/Mpc; matter "
            "density parameter Omegam = 0.315+-0.007; and matter fluctuation "
            "amplitude sigma8 = 0.811+-0.006."
        ),
    },
    "planck_esa": {
        "quote": (
            "When applied to Planck data, this method gives a lower value "
            "of 67.4 km/s/Mpc, with a tiny uncertainty of less than a percent."
        ),
        "url": "https://sci.esa.int/web/planck/-/60504-measurements-of-the-hubble-constant",
        "source_name": "ESA Planck Science Portal",
    },
}

# ============================================================
# 4. CITATION VERIFICATION (Rule 2)
# ============================================================
print("=" * 60)
print("CITATION VERIFICATION")
print("=" * 60)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)
for key, res in citation_results.items():
    print(f"  {key}: {res['status']} (method: {res.get('method', 'N/A')})")

# ============================================================
# 5. VALUE EXTRACTION (Rule 1)
# ============================================================
print("\n" + "=" * 60)
print("VALUE EXTRACTION")
print("=" * 60)

# SH0ES H₀ from arXiv quote
h0_shoes_arxiv = parse_number_from_quote(
    empirical_facts["shoes_arxiv"]["quote"],
    r"H0[=\s]*([\d.]+)",
    "B1_h0"
)
h0_shoes_arxiv_in_quote = verify_extraction(
    h0_shoes_arxiv, empirical_facts["shoes_arxiv"]["quote"], "B1"
)

# SH0ES H₀ from IOPscience quote
h0_shoes_iop = parse_number_from_quote(
    empirical_facts["shoes_iop"]["quote"],
    r"H\s*0\s*=\s*([\d.]+)",
    "B2_h0"
)
h0_shoes_iop_in_quote = verify_extraction(
    h0_shoes_iop, empirical_facts["shoes_iop"]["quote"], "B2"
)

# Planck H₀ from arXiv quote
h0_planck_arxiv = parse_number_from_quote(
    empirical_facts["planck_arxiv"]["quote"],
    r"H0\s*=\s*\(?([\d.]+)",
    "B3_h0"
)
h0_planck_arxiv_in_quote = verify_extraction(
    h0_planck_arxiv, empirical_facts["planck_arxiv"]["quote"], "B3"
)

# Planck H₀ from ESA quote
h0_planck_esa = parse_number_from_quote(
    empirical_facts["planck_esa"]["quote"],
    r"([\d.]+)\s*km/s/Mpc",
    "B4_h0"
)
h0_planck_esa_in_quote = verify_extraction(
    h0_planck_esa, empirical_facts["planck_esa"]["quote"], "B4"
)

print(f"  SH0ES (arXiv):  H₀ = {h0_shoes_arxiv} km/s/Mpc")
print(f"  SH0ES (IOP):    H₀ = {h0_shoes_iop} km/s/Mpc")
print(f"  Planck (arXiv): H₀ = {h0_planck_arxiv} km/s/Mpc")
print(f"  Planck (ESA):   H₀ = {h0_planck_esa} km/s/Mpc")

# ============================================================
# 6. CROSS-CHECKS (Rule 6)
# ============================================================
print("\n" + "=" * 60)
print("CROSS-CHECKS")
print("=" * 60)

# SH0ES sources must agree
shoes_agree = cross_check(
    h0_shoes_arxiv, h0_shoes_iop,
    tolerance=0.01, mode="absolute",
    label="SH0ES H₀: arXiv vs IOPscience"
)

# Planck sources must agree
planck_agree = cross_check(
    h0_planck_arxiv, h0_planck_esa,
    tolerance=0.01, mode="absolute",
    label="Planck H₀: arXiv vs ESA"
)

FACT_REGISTRY["A3"]["method"] = "cross_check(h0_shoes_arxiv, h0_shoes_iop, tolerance=0.01)"
FACT_REGISTRY["A3"]["result"] = f"Agreement: {shoes_agree} ({h0_shoes_arxiv} vs {h0_shoes_iop})"
FACT_REGISTRY["A4"]["method"] = "cross_check(h0_planck_arxiv, h0_planck_esa, tolerance=0.01)"
FACT_REGISTRY["A4"]["result"] = f"Agreement: {planck_agree} ({h0_planck_arxiv} vs {h0_planck_esa})"

# ============================================================
# 7. CLAIM EVALUATION (Rule 7)
# ============================================================
print("\n" + "=" * 60)
print("CLAIM EVALUATION")
print("=" * 60)

# SC1: SH0ES Cepheid H₀ > 72
sc1_holds = compare(
    h0_shoes_arxiv, ">", CLAIM_FORMAL["threshold_sc1"],
    label="SC1: SH0ES Cepheid H₀ > 72"
)

# SC2: Planck 2018 H₀ < 68
sc2_holds = compare(
    h0_planck_arxiv, "<", CLAIM_FORMAL["threshold_sc2"],
    label="SC2: Planck 2018 H₀ < 68"
)

# Compute the tension magnitude for context
tension = explain_calc(
    "h0_shoes_arxiv - h0_planck_arxiv",
    {**locals()},
    label="H₀ tension (SH0ES − Planck)"
)

claim_holds = sc1_holds and sc2_holds

FACT_REGISTRY["A1"]["method"] = f"compare({h0_shoes_arxiv}, '>', 72)"
FACT_REGISTRY["A1"]["result"] = str(sc1_holds)
FACT_REGISTRY["A2"]["method"] = f"compare({h0_planck_arxiv}, '<', 68)"
FACT_REGISTRY["A2"]["result"] = str(sc2_holds)

# ============================================================
# 8. ADVERSARIAL CHECKS (Rule 5)
# ============================================================
adversarial_checks = [
    {
        "question": (
            "Are there Cepheid-based H₀ measurements that yield a value "
            "at or below 72 km/s/Mpc?"
        ),
        "verification_performed": (
            "Searched for 'Cepheid Hubble constant below 72 km/s/Mpc alternative'. "
            "Found that Freedman et al. (2019, 2021) use the TRGB method (Tip of the "
            "Red Giant Branch), NOT Cepheids, and obtain H₀ ≈ 69.8 km/s/Mpc. "
            "However, the CCHP team's own Cepheid measurement yields 72.04 km/s/Mpc, "
            "still exceeding 72. The SH0ES Cepheid measurement (73.04) is the most "
            "comprehensive Cepheid-based determination. No Cepheid-specific measurement "
            "from a major survey yields H₀ ≤ 72."
        ),
        "finding": (
            "Lower H₀ values (~69.8) use TRGB, not Cepheids. "
            "All major Cepheid-calibrated measurements exceed 72. "
            "Does not break the proof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Could alternative analyses of Planck 2018 CMB data yield "
            "H₀ ≥ 68 km/s/Mpc?"
        ),
        "verification_performed": (
            "Searched for 'Planck CMB Hubble constant above 68 alternative analysis'. "
            "The Planck 2018 base-ΛCDM result is H₀ = 67.4 ± 0.5. Even at the "
            "upper 1σ bound (67.9), it remains below 68. Extended models (e.g., "
            "with extra relativistic species Neff) can shift H₀ upward, but the "
            "claim specifically references the 2018 Planck inference, which uses "
            "base-ΛCDM. Other CMB experiments (ACT, SPT) combined with WMAP give "
            "67.6-68.2 km/s/Mpc, but those are not the '2018 Planck' result."
        ),
        "finding": (
            "The 2018 Planck base-ΛCDM value is firmly 67.4 ± 0.5. "
            "No standard analysis of Planck 2018 data yields H₀ ≥ 68 under base-ΛCDM. "
            "Does not break the proof."
        ),
        "breaks_proof": False,
    },
    {
        "question": (
            "Has the SH0ES result been superseded or revised downward "
            "by newer measurements?"
        ),
        "verification_performed": (
            "Searched for 'JWST Cepheid Hubble constant SH0ES confirmation'. "
            "JWST observations (2023-2024) independently surveyed >1000 Cepheid "
            "variables and confirmed the HST-based SH0ES value. The JWST Cepheid "
            "measurement is consistent with ~73 km/s/Mpc. The Hubble tension persists."
        ),
        "finding": (
            "JWST confirmed the SH0ES Cepheid-based H₀ value. "
            "No downward revision. Does not break the proof."
        ),
        "breaks_proof": False,
    },
]

# ============================================================
# 9. VERDICT AND STRUCTURED OUTPUT
# ============================================================
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )
    any_breaks = any(ac["breaks_proof"] for ac in adversarial_checks)

    if claim_holds and not any_unverified and not any_breaks:
        verdict = "PROVED"
    elif claim_holds and any_unverified:
        verdict = "PROVED (with unverified citations)"
    elif not claim_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not claim_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    else:
        verdict = "UNDETERMINED"

    print(f"\n{'=' * 60}")
    print(f"VERDICT: {verdict}")
    print(f"{'=' * 60}")

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1": {
            "value": str(h0_shoes_arxiv),
            "value_in_quote": h0_shoes_arxiv_in_quote,
            "quote_snippet": empirical_facts["shoes_arxiv"]["quote"][:80],
        },
        "B2": {
            "value": str(h0_shoes_iop),
            "value_in_quote": h0_shoes_iop_in_quote,
            "quote_snippet": empirical_facts["shoes_iop"]["quote"][:80],
        },
        "B3": {
            "value": str(h0_planck_arxiv),
            "value_in_quote": h0_planck_arxiv_in_quote,
            "quote_snippet": empirical_facts["planck_arxiv"]["quote"][:80],
        },
        "B4": {
            "value": str(h0_planck_esa),
            "value_in_quote": h0_planck_esa_in_quote,
            "quote_snippet": empirical_facts["planck_esa"]["quote"][:80],
        },
    }

    cross_checks_list = [
        {
            "description": "SH0ES H₀ agreement across arXiv and IOPscience",
            "values_compared": [str(h0_shoes_arxiv), str(h0_shoes_iop)],
            "agreement": shoes_agree,
        },
        {
            "description": "Planck H₀ agreement across arXiv and ESA portal",
            "values_compared": [str(h0_planck_arxiv), str(h0_planck_esa)],
            "agreement": planck_agree,
        },
    ]

    summary = {
        "claim_natural": CLAIM_NATURAL,
        "claim_formal": CLAIM_FORMAL,
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": cross_checks_list,
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "h0_shoes": h0_shoes_arxiv,
            "h0_planck": h0_planck_arxiv,
            "sc1_threshold": CLAIM_FORMAL["threshold_sc1"],
            "sc2_threshold": CLAIM_FORMAL["threshold_sc2"],
            "sc1_holds": sc1_holds,
            "sc2_holds": sc2_holds,
            "claim_holds": claim_holds,
            "tension_magnitude": float(tension),
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
