"""
Proof: eml(1, 1) = e
Generated: 2026-04-16
"""
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date
from sympy import Symbol, exp, ln, simplify, E, Rational

from scripts.computations import compare
from scripts.proof_summary import ProofSummaryBuilder

# ============================================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# ============================================================================

CLAIM_NATURAL = (
    r"The binary operator eml is defined by the expression "
    r"\(\text{eml}(a, b) = \exp(a) - \ln(b)\) "
    r"(where exp is the exponential function and ln is the principal branch "
    r"of the natural logarithm). "
    r"The expression \(\text{eml}(1, 1)\) equals the base of the natural "
    r"logarithm \(e\)."
)

CLAIM_FORMAL = {
    "subject": "Binary operator eml(a, b) = exp(a) - ln(b)",
    "property": "eml(1, 1) = e",
    "operator": "==",
    "operator_note": (
        "Substituting a = 1, b = 1: eml(1, 1) = exp(1) - ln(1). "
        "exp(1) = e by definition of the exponential function. "
        "ln(1) = 0 (principal branch of the complex logarithm: "
        "Log(1) = ln|1| + i*Arg(1) = 0 + 0 = 0). "
        "Therefore eml(1, 1) = e - 0 = e. This is an exact algebraic "
        "identity, not a numerical approximation."
    ),
    "threshold": True,
    "is_time_sensitive": False,
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {
        "label": "exp(1) = e (symbolic verification)",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "ln(1) = 0 (symbolic verification)",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "eml(1, 1) - e = 0 (symbolic simplification)",
        "method": None,
        "result": None,
    },
}

# ============================================================================
# 3. COMPUTATION — primary method: symbolic evaluation
# ============================================================================

# A1: Verify exp(1) = e symbolically
exp_1 = exp(1)
A1_verified = compare(
    simplify(exp_1 - E), "==", 0,
    label="A1: exp(1) - e = 0",
)

# A2: Verify ln(1) = 0 symbolically
ln_1 = ln(1)
A2_verified = compare(
    ln_1, "==", 0,
    label="A2: ln(1) = 0",
)

# A3: Verify eml(1, 1) - e = 0 symbolically
eml_1_1 = exp(1) - ln(1)
residual = simplify(eml_1_1 - E)
A3_verified = compare(
    residual, "==", 0,
    label="A3: simplify(eml(1,1) - e) = 0",
)

# ============================================================================
# 4. CROSS-CHECKS — numerical evaluation (Rule 6)
# ============================================================================

import math
import cmath

eml_numerical = cmath.exp(1) - cmath.log(1)
e_numerical = math.e
numerical_diff = abs(eml_numerical.real - e_numerical)
print(f"  Numerical: eml(1,1) = {eml_numerical.real:.15f}")
print(f"  Numerical: e        = {e_numerical:.15f}")
print(f"  |eml(1,1) - e|      = {numerical_diff:.2e}")

numerical_crosscheck = compare(
    numerical_diff < 1e-15, "==", True,
    label="Numerical cross-check: |eml(1,1) - e| < 1e-15",
)

# ============================================================================
# 5. ADVERSARIAL CHECKS (Rule 5)
# ============================================================================

adversarial_checks = [
    {
        "question": "Is exp(1) exactly e, or just an approximation?",
        "verification_performed": (
            "The exponential function exp is defined such that exp(1) = e "
            "by definition. In SymPy, exp(1) returns the symbolic constant E "
            "(Euler's number), not a floating-point approximation. The "
            "identity exp(1) = e is definitional, not computed."
        ),
        "finding": (
            "exp(1) = e is exact and definitional. No approximation is involved."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does ln(1) = 0 hold for the complex logarithm?",
        "verification_performed": (
            "The principal branch of the complex logarithm is defined as "
            "Log(z) = ln|z| + i*Arg(z) where Arg is the principal argument "
            "in (-pi, pi]. For z = 1: |1| = 1, Arg(1) = 0, so "
            "Log(1) = ln(1) + i*0 = 0. This holds regardless of branch "
            "cut conventions since z = 1 is on the positive real axis."
        ),
        "finding": (
            "ln(1) = 0 holds universally for the principal branch of the "
            "complex logarithm. No branch ambiguity at z = 1."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could SymPy's simplify() fail to reduce a nonzero expression to zero?",
        "verification_performed": (
            "For the expression exp(1) - ln(1) - E, SymPy evaluates exp(1) "
            "to E and ln(1) to 0 before simplify() is even called. The "
            "expression becomes E - 0 - E = 0, which is trivial constant "
            "arithmetic. There is no symbolic variable or complex cancellation "
            "involved. Additionally, the numerical cross-check confirms the "
            "result independently."
        ),
        "finding": (
            "The simplification is trivial constant folding (E - 0 - E = 0). "
            "No risk of simplify() missing a cancellation."
        ),
        "breaks_proof": False,
    },
]

# ============================================================================
# 6. VERDICT AND STRUCTURED OUTPUT
# ============================================================================

if __name__ == "__main__":
    all_verified = A1_verified and A2_verified and A3_verified and numerical_crosscheck
    claim_holds = compare(
        all_verified, "==", CLAIM_FORMAL["threshold"],
        label="All facts verified (symbolic + numerical)",
    )

    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    if any_breaks:
        verdict = "UNDETERMINED"
    else:
        verdict = "PROVED" if claim_holds else "DISPROVED"

    print(f"\nVERDICT: {verdict}")

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    builder.add_computed_fact(
        "A1",
        label=FACT_REGISTRY["A1"]["label"],
        method="SymPy symbolic evaluation: simplify(exp(1) - E); verify equals 0",
        result="Confirmed: exp(1) = e",
    )
    builder.add_computed_fact(
        "A2",
        label=FACT_REGISTRY["A2"]["label"],
        method="SymPy symbolic evaluation of ln(1); verify equals 0",
        result="Confirmed: ln(1) = 0",
    )
    builder.add_computed_fact(
        "A3",
        label=FACT_REGISTRY["A3"]["label"],
        method=(
            "SymPy symbolic simplification of exp(1) - ln(1) - E; "
            "verify result is 0"
        ),
        result="Confirmed: residual = 0",
        depends_on=["A1", "A2"],
    )

    builder.add_cross_check(
        description=(
            "Symbolic (A3) vs numerical: symbolic proves identity exactly; "
            "numerical confirms via Python math.e and cmath.exp/cmath.log"
        ),
        fact_ids=["A3"],
        agreement=A3_verified and numerical_crosscheck,
    )

    for ac in adversarial_checks:
        builder.add_adversarial_check(
            question=ac["question"],
            verification_performed=ac["verification_performed"],
            finding=ac["finding"],
            breaks_proof=ac["breaks_proof"],
        )

    builder.set_verdict(verdict)
    builder.set_key_results(
        exp_1_equals_e=A1_verified,
        ln_1_equals_zero=A2_verified,
        symbolic_residual_zero=A3_verified,
        numerical_crosscheck_passed=numerical_crosscheck,
        claim_holds=claim_holds,
    )

    builder.emit()
