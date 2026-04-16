"""
Proof: eml(x, 1) = exp(x) for every complex number x
Generated: 2026-04-16
"""
import os
import sys

PROOF_ENGINE_ROOT = "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine"
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date
from sympy import Symbol, exp, ln, simplify, I, pi, Rational, zoo, oo

from scripts.computations import compare
from scripts.proof_summary import ProofSummaryBuilder

# ============================================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# ============================================================================

CLAIM_NATURAL = (
    r"The binary operator defined by \(\text{eml}(a, b) = \exp(a) - \ln(b)\) "
    r"satisfies \(\text{eml}(x, 1) = \exp(x)\) for every complex number x."
)

CLAIM_FORMAL = {
    "subject": "Binary operator eml(a, b) = exp(a) - ln(b)",
    "property": "eml(x, 1) = exp(x) for all complex x",
    "operator": "==",
    "operator_note": (
        "The claim follows from ln(1) = 0, which holds in the principal branch "
        "of the complex logarithm. Substituting b = 1: eml(x, 1) = exp(x) - ln(1) "
        "= exp(x) - 0 = exp(x). This is an algebraic identity, not a limit or "
        "approximation. The proof verifies symbolically that "
        "exp(x) - ln(1) - exp(x) simplifies to 0 for symbolic x."
    ),
    "threshold": True,
    "is_time_sensitive": False,
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {
        "label": "ln(1) = 0 (symbolic verification)",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "eml(x, 1) - exp(x) = 0 (symbolic simplification)",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "Numerical spot-check at 5 complex points",
        "method": None,
        "result": None,
    },
}

# ============================================================================
# 3. COMPUTATION — primary method: symbolic simplification
# ============================================================================

x = Symbol("x")

# A1: Verify ln(1) = 0 symbolically
ln_1 = ln(1)
A1_verified = compare(
    ln_1, "==", 0,
    label="A1: ln(1) = 0",
)

# A2: Verify eml(x, 1) - exp(x) simplifies to 0 for symbolic x
eml_x_1 = exp(x) - ln(1)
residual = simplify(eml_x_1 - exp(x))
A2_verified = compare(
    residual, "==", 0,
    label="A2: simplify(eml(x,1) - exp(x)) = 0",
)

# ============================================================================
# 4. CROSS-CHECKS — numerical evaluation at specific complex points (Rule 6)
# ============================================================================

import cmath

test_points = [
    0,                   # zero
    1,                   # positive real
    -3,                  # negative real
    1j * cmath.pi,       # purely imaginary (i*pi)
    2 + 3j,              # general complex
]

numerical_results = []
for z in test_points:
    eml_val = cmath.exp(z) - cmath.log(1)
    exp_val = cmath.exp(z)
    diff = abs(eml_val - exp_val)
    numerical_results.append((z, diff))
    print(f"  x = {z:>12}  |eml(x,1) - exp(x)| = {diff:.2e}")

all_numerical = all(d < 1e-15 for _, d in numerical_results)
A3_verified = compare(
    all_numerical, "==", True,
    label="A3: numerical spot-checks at 5 complex points all < 1e-15",
)

# ============================================================================
# 5. ADVERSARIAL CHECKS (Rule 5)
# ============================================================================

adversarial_checks = [
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
        "question": "Is the operator well-defined for all complex x?",
        "verification_performed": (
            "eml(x, 1) = exp(x) - ln(1). The exponential function exp(x) "
            "is entire (defined for all complex x). ln(1) = 0 is a constant. "
            "The subtraction of a constant from an entire function is entire. "
            "The only concern would be if b = 0 (since ln(0) is undefined), "
            "but the claim fixes b = 1."
        ),
        "finding": (
            "eml(x, 1) is well-defined for every complex x. The operator "
            "eml(a, b) has a singularity at b = 0, but the claim only "
            "evaluates at b = 1."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could numerical precision mask a nonzero residual?",
        "verification_performed": (
            "The symbolic computation uses SymPy's exact symbolic engine, "
            "not floating-point arithmetic. simplify(exp(x) - ln(1) - exp(x)) "
            "returns exactly 0, not an approximation. The numerical cross-check "
            "is supplementary — the proof rests on the symbolic result."
        ),
        "finding": (
            "The symbolic residual is exactly 0 — no numerical precision "
            "issue can affect it. Numerical cross-checks confirm agreement "
            "to machine epsilon."
        ),
        "breaks_proof": False,
    },
]

# ============================================================================
# 6. VERDICT AND STRUCTURED OUTPUT
# ============================================================================

if __name__ == "__main__":
    all_verified = A1_verified and A2_verified and A3_verified
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
        method="SymPy symbolic evaluation of ln(1); verify equals 0",
        result="Confirmed: ln(1) = 0",
    )
    builder.add_computed_fact(
        "A2",
        label=FACT_REGISTRY["A2"]["label"],
        method=(
            "SymPy symbolic simplification of exp(x) - ln(1) - exp(x); "
            "verify result is identically 0 for symbolic x"
        ),
        result="Confirmed: residual = 0",
        depends_on=["A1"],
    )
    builder.add_computed_fact(
        "A3",
        label=FACT_REGISTRY["A3"]["label"],
        method=(
            "Numerical evaluation of |eml(x,1) - exp(x)| at x = 0, 1, -3, "
            "i*pi, 2+3i using Python cmath; verify all < 1e-15"
        ),
        result=f"Confirmed: max residual = {max(d for _, d in numerical_results):.2e}",
    )

    builder.add_cross_check(
        description=(
            "Symbolic (A2) vs numerical (A3): symbolic proves identity exactly; "
            "numerical confirms at 5 representative complex points"
        ),
        fact_ids=["A2", "A3"],
        agreement=A2_verified and A3_verified,
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
        ln_1_equals_zero=A1_verified,
        symbolic_residual_zero=A2_verified,
        numerical_crosscheck_passed=A3_verified,
        claim_holds=claim_holds,
    )

    builder.emit()
