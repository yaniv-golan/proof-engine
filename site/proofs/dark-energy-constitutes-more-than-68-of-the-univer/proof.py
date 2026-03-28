"""
Proof: Dark energy constitutes more than 68% of the universe's total energy density
       according to the Planck 2018 legacy release.
Generated: 2026-03-28
"""
import json
import os
import re
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

# --- STRUCTURAL IMPORTS ---
from scripts.smart_extract import verify_extraction
from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare, explain_calc, cross_check
from scripts.extract_values import parse_number_from_quote

# ============================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# ============================================================
CLAIM_NATURAL = (
    "Dark energy constitutes more than 68% of the universe's total energy density "
    "according to the Planck 2018 legacy release."
)
CLAIM_FORMAL = {
    "subject": "Dark energy fraction of the universe's total energy density",
    "property": "Omega_Lambda (dark energy density parameter) as reported by Planck 2018",
    "operator": ">",
    "operator_note": (
        "'More than 68%' is interpreted as Omega_Lambda > 0.68 (strictly greater). "
        "The claim references the Planck 2018 legacy release (Planck Collaboration VI, "
        "A&A 641, A6, 2020; arXiv:1807.06209). In the base-LCDM model with spatial "
        "flatness (Omega_total = 1), Omega_Lambda = 1 - Omega_m. The claim is about "
        "the best-fit central value, not the confidence interval."
    ),
    "threshold": 0.68,
}

# ============================================================
# 2. FACT REGISTRY
# ============================================================
FACT_REGISTRY = {
    "B1": {
        "key": "planck_paper",
        "label": "Planck 2018 paper: matter density Omega_m = 0.315 +/- 0.007",
    },
    "B2": {
        "key": "unlv_reference",
        "label": "UNLV cosmic parameters reference: Omega_Lambda = 0.6853(74) from Planck 2018",
    },
    "A1": {
        "label": "Derived Omega_Lambda from Omega_m via flat-LCDM relation",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "Cross-check: derived Omega_Lambda vs directly reported Omega_Lambda",
        "method": None,
        "result": None,
    },
}

# ============================================================
# 3. EMPIRICAL FACTS
# ============================================================
empirical_facts = {
    "planck_paper": {
        "quote": "matter density parameter Ωm=0.315±0.007",
        "url": "https://ar5iv.labs.arxiv.org/html/1807.06209",
        "source_name": "Planck Collaboration VI (2020), A&A 641, A6 — arXiv:1807.06209 (ar5iv HTML)",
    },
    "unlv_reference": {
        "quote": "Omega_Lambda           0.6853(74)               Assuming Omega = 1 (Planck 2018 p. 14)",
        "url": "https://www.physics.unlv.edu/~jeffery/astro/cosmol/cosmic_parameters.html",
        "source_name": "UNLV Cosmic Parameters Reference (sourced from Planck 2018)",
    },
}

# ============================================================
# 4. CITATION VERIFICATION (Rule 2)
# ============================================================
print("=" * 60)
print("CITATION VERIFICATION")
print("=" * 60)
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)
for key, result in citation_results.items():
    print(f"  {key}: {result['status']} (method: {result.get('method', 'N/A')})")

# ============================================================
# 5. VALUE EXTRACTION (Rule 1)
# ============================================================
print("\n" + "=" * 60)
print("VALUE EXTRACTION")
print("=" * 60)

# Source A: Extract Omega_m from Planck paper abstract
omega_m = parse_number_from_quote(
    empirical_facts["planck_paper"]["quote"],
    r'[Ωo]m\s*=\s*([\d.]+)',
    "B1_omega_m",
)
# Note: regex handles both Ωm=0.315 (ar5iv) and Omega_m = 0.315 formats
omega_m_in_quote = verify_extraction(
    omega_m, empirical_facts["planck_paper"]["quote"], "B1"
)
print(f"  Extracted Omega_m from B1: {omega_m}")

# Source B: Extract Omega_Lambda from UNLV reference
omega_lambda_direct = parse_number_from_quote(
    empirical_facts["unlv_reference"]["quote"],
    r'Omega_Lambda\s+([\d.]+)',
    "B2_omega_lambda",
)
omega_lambda_in_quote = verify_extraction(
    omega_lambda_direct, empirical_facts["unlv_reference"]["quote"], "B2"
)
print(f"  Extracted Omega_Lambda from B2: {omega_lambda_direct}")

# ============================================================
# 6. COMPUTATION (Rule 7)
# ============================================================
print("\n" + "=" * 60)
print("COMPUTATION")
print("=" * 60)

# Derive Omega_Lambda from Omega_m using flat-LCDM relation
omega_lambda_derived = explain_calc(
    "1 - omega_m",
    {"omega_m": omega_m},
    label="Omega_Lambda (derived from Omega_m, flat LCDM)",
)

# ============================================================
# 7. CROSS-CHECK (Rule 6)
# ============================================================
print("\n" + "=" * 60)
print("CROSS-CHECK")
print("=" * 60)

# Cross-check: derived value vs directly reported value
# Tolerance of 0.01 (relative) accounts for rounding in Omega_m
cross_check_ok = cross_check(
    float(omega_lambda_derived),
    omega_lambda_direct,
    tolerance=0.01,
    mode="relative",
    label="Omega_Lambda: derived from Omega_m vs direct report",
)
print(f"  Derived: {omega_lambda_derived}, Direct: {omega_lambda_direct}, Agreement: {cross_check_ok}")

# ============================================================
# 8. CLAIM EVALUATION
# ============================================================
print("\n" + "=" * 60)
print("CLAIM EVALUATION")
print("=" * 60)

# Use the directly reported value (more precise) for the final comparison
claim_holds = compare(
    omega_lambda_direct,
    CLAIM_FORMAL["operator"],
    CLAIM_FORMAL["threshold"],
    label="Omega_Lambda > 0.68",
)

# ============================================================
# 9. ADVERSARIAL CHECKS (Rule 5)
# ============================================================
adversarial_checks = [
    {
        "question": "Has the Planck 2018 value for Omega_Lambda been revised or retracted?",
        "verification_performed": (
            "Searched for 'Planck 2018 dark energy revised retracted correction erratum'. "
            "The Planck 2018 paper (arXiv:1807.06209) was published in A&A 641, A6 (2020) "
            "as the final legacy release. No errata revising the cosmological parameters "
            "have been issued."
        ),
        "finding": "No revision or retraction found. The 2018 release is the final Planck data release.",
        "breaks_proof": False,
    },
    {
        "question": "Could alternative cosmological models give Omega_Lambda < 0.68 from the same Planck data?",
        "verification_performed": (
            "Searched for 'Planck 2018 dark energy fraction alternative model lower than 68 percent'. "
            "Extended models (w0waCDM, curved models) can shift Omega_DE slightly, but the claim "
            "specifically references the base-LCDM results. In the base-LCDM model, Omega_Lambda "
            "is tightly constrained at 0.685 +/- 0.007."
        ),
        "finding": (
            "In the base-LCDM model (which the Planck 2018 release uses as its primary framework), "
            "Omega_Lambda = 0.6853 +/- 0.0074. Even at the lower 1-sigma bound (0.6779), the value "
            "remains below 0.68 only marginally. The central value is clearly > 0.68."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is the 68% threshold ambiguous — could it refer to a different quantity?",
        "verification_performed": (
            "Considered whether 'energy density' might refer to Omega_DE in a non-flat model, "
            "or to a different definition. In standard cosmology, 'dark energy fraction of total "
            "energy density' is Omega_Lambda = rho_Lambda / rho_critical, which equals 1 - Omega_m "
            "in a flat universe."
        ),
        "finding": (
            "The standard interpretation is unambiguous: Omega_Lambda is the dark energy fraction "
            "of the critical density, and equals the fraction of total energy density in a flat universe."
        ),
        "breaks_proof": False,
    },
]

# ============================================================
# 10. VERDICT AND STRUCTURED OUTPUT
# ============================================================
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    if claim_holds and not any_unverified:
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

    # Update fact registry with computed results
    FACT_REGISTRY["A1"]["method"] = "explain_calc('1 - omega_m')"
    FACT_REGISTRY["A1"]["result"] = str(float(omega_lambda_derived))

    FACT_REGISTRY["A2"]["method"] = "cross_check(derived, direct, tolerance=0.01, mode='relative')"
    FACT_REGISTRY["A2"]["result"] = str(cross_check_ok)

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    extractions = {
        "B1": {
            "value": str(omega_m),
            "value_in_quote": omega_m_in_quote,
            "quote_snippet": empirical_facts["planck_paper"]["quote"][:80],
        },
        "B2": {
            "value": str(omega_lambda_direct),
            "value_in_quote": omega_lambda_in_quote,
            "quote_snippet": empirical_facts["unlv_reference"]["quote"][:80],
        },
    }

    summary = {
        "claim_natural": CLAIM_NATURAL,
        "claim_formal": CLAIM_FORMAL,
        "fact_registry": {
            fid: {k: v for k, v in info.items()}
            for fid, info in FACT_REGISTRY.items()
        },
        "citations": citation_detail,
        "extractions": extractions,
        "cross_checks": [
            {
                "description": "Omega_Lambda derived from Omega_m (source A) vs directly reported (source B)",
                "values_compared": [str(float(omega_lambda_derived)), str(omega_lambda_direct)],
                "agreement": cross_check_ok,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "omega_lambda_direct": omega_lambda_direct,
            "omega_lambda_derived": float(omega_lambda_derived),
            "omega_m": omega_m,
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
