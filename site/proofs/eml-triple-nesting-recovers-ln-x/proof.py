"""
Proof: eml(1, eml(eml(1, x), 1)) = ln(x) for every real x > 0
Generated: 2026-04-16
"""
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date
from sympy import Symbol, exp, ln, simplify, E, log, assumptions, oo

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
    r"For every real \(x > 0\), the nested expression "
    r"\(\text{eml}(1, \text{eml}(\text{eml}(1, x), 1))\) equals the "
    r"natural logarithm \(\ln(x)\)."
)

CLAIM_FORMAL = {
    "subject": "Binary operator eml(a, b) = exp(a) - ln(b)",
    "property": "eml(1, eml(eml(1, x), 1)) = ln(x) for all real x > 0",
    "operator": "==",
    "operator_note": (
        "The claim asserts a symbolic identity for the triple nesting of eml. "
        "Working inside out: (1) eml(1, x) = exp(1) - ln(x) = e - ln(x). "
        "(2) eml(eml(1, x), 1) = exp(e - ln(x)) - ln(1) = exp(e)/x. "
        "(3) eml(1, exp(e)/x) = exp(1) - ln(exp(e)/x) = e - (e - ln(x)) "
        "= ln(x). The domain restriction x > 0 ensures ln(x) is real-valued. "
        "The proof verifies symbolically that the nested expression minus "
        "ln(x) simplifies to 0 for symbolic positive x."
    ),
    "threshold": True,
    "is_time_sensitive": False,
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {
        "label": "eml(1, x) = e - ln(x) (inner evaluation)",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "eml(eml(1, x), 1) = exp(e)/x (middle evaluation)",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "eml(1, eml(eml(1, x), 1)) - ln(x) = 0 (full identity)",
        "method": None,
        "result": None,
    },
    "A4": {
        "label": "Numerical spot-check at 6 positive real points",
        "method": None,
        "result": None,
    },
}

# ============================================================================
# 3. COMPUTATION — primary method: symbolic simplification
# ============================================================================

# Define eml as a Python function over SymPy expressions
def eml(a, b):
    return exp(a) - ln(b)


# Use a positive real symbol
x = Symbol("x", positive=True)

# A1: Verify eml(1, x) = e - ln(x)
inner = eml(1, x)
inner_expected = E - ln(x)
A1_residual = simplify(inner - inner_expected)
A1_verified = compare(
    A1_residual, "==", 0,
    label="A1: eml(1, x) - (e - ln(x)) = 0",
)

# A2: Verify eml(eml(1, x), 1) simplifies to exp(e)/x
middle = eml(inner, 1)
middle_expected = exp(E) / x
A2_residual = simplify(middle - middle_expected)
A2_verified = compare(
    A2_residual, "==", 0,
    label="A2: eml(eml(1, x), 1) - exp(e)/x = 0",
)

# A3: Verify the full nested expression equals ln(x)
outer = eml(1, middle)
full_residual = simplify(outer - ln(x))
A3_verified = compare(
    full_residual, "==", 0,
    label="A3: eml(1, eml(eml(1, x), 1)) - ln(x) = 0",
)

# ============================================================================
# 4. CROSS-CHECKS — numerical evaluation at specific points (Rule 6)
# ============================================================================

import math

test_points = [0.01, 0.5, 1.0, 2.0, math.e, 100.0]

numerical_results = []
for xv in test_points:
    # Compute eml(1, eml(eml(1, xv), 1)) numerically
    step1 = math.exp(1) - math.log(xv)         # eml(1, xv)
    step2 = math.exp(step1) - math.log(1)       # eml(step1, 1)
    step3 = math.exp(1) - math.log(step2)       # eml(1, step2)
    expected = math.log(xv)
    diff = abs(step3 - expected)
    numerical_results.append((xv, step3, expected, diff))
    print(f"  x = {xv:>8}  nested = {step3:>20.15f}  ln(x) = {expected:>20.15f}  |diff| = {diff:.2e}")

max_diff = max(d for _, _, _, d in numerical_results)
A4_verified = compare(
    max_diff < 1e-10, "==", True,
    label="A4: all numerical spot-checks agree within 1e-10",
)

# ============================================================================
# 5. ADVERSARIAL CHECKS (Rule 5)
# ============================================================================

adversarial_checks = [
    {
        "question": "Does the identity hold at the boundary x -> 0+?",
        "verification_performed": (
            "As x -> 0+, ln(x) -> -infinity. The inner expression eml(1, x) "
            "= e - ln(x) -> +infinity. Then eml(eml(1, x), 1) = exp(e - ln(x)) "
            "-> +infinity. Then eml(1, eml(...)) = e - ln(exp(e - ln(x))) "
            "= e - (e - ln(x)) = ln(x) -> -infinity. The algebraic identity "
            "holds for all x > 0 regardless of how large or small x is; "
            "the intermediate values may be extreme, but the cancellations "
            "are exact. The numerical test at x = 0.01 confirms this."
        ),
        "finding": (
            "The identity holds even as x -> 0+. The intermediate expressions "
            "diverge, but the final cancellation is algebraically exact."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does the identity hold at x -> +infinity?",
        "verification_performed": (
            "As x -> +infinity, ln(x) -> +infinity. eml(1, x) = e - ln(x) "
            "-> -infinity. eml(eml(1, x), 1) = exp(e - ln(x)) -> 0+. "
            "eml(1, exp(e - ln(x))) = e - ln(exp(e - ln(x))) = e - (e - ln(x)) "
            "= ln(x). Again the algebraic cancellation is exact. The numerical "
            "test at x = 100 confirms the identity holds for large x."
        ),
        "finding": (
            "The identity holds as x -> +infinity. Despite intermediate "
            "expressions approaching 0 or -infinity, the cancellation is exact."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is ln(exp(e - ln(x))) = e - ln(x) always valid for x > 0?",
        "verification_performed": (
            "For real y, ln(exp(y)) = y holds for all real y (the natural "
            "logarithm and exponential are inverse functions on the reals). "
            "Here y = e - ln(x), which is real for any x > 0. So "
            "ln(exp(e - ln(x))) = e - ln(x) without restriction. "
            "This step would fail for complex x where branch cuts matter, "
            "but the claim restricts to real x > 0."
        ),
        "finding": (
            "ln(exp(y)) = y holds for all real y. Since the claim restricts "
            "to x > 0 (making e - ln(x) real), no branch cut issue arises."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could numerical overflow in exp(e - ln(x)) cause false agreement?",
        "verification_performed": (
            "For small x (e.g., x = 0.01), e - ln(x) ≈ 2.718 + 4.605 ≈ 7.323, "
            "so exp(7.323) ≈ 1512 — well within float64 range. For very small x "
            "(e.g., x = 1e-300), e - ln(x) ≈ 694, and exp(694) ≈ 1e301 — still "
            "representable. Overflow would require x < exp(-exp(709)) which is "
            "below the smallest positive float. The symbolic proof does not "
            "depend on floating-point at all; the numerical cross-check is "
            "supplementary."
        ),
        "finding": (
            "No overflow risk for representable positive floats. The proof "
            "rests on exact symbolic algebra, not numerics."
        ),
        "breaks_proof": False,
    },
]

# ============================================================================
# 6. VERDICT AND STRUCTURED OUTPUT
# ============================================================================

if __name__ == "__main__":
    all_verified = A1_verified and A2_verified and A3_verified and A4_verified
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
        method=(
            "SymPy symbolic evaluation of eml(1, x) = exp(1) - ln(x) for "
            "positive symbol x; verify simplify(result - (E - ln(x))) = 0"
        ),
        result="Confirmed: eml(1, x) = e - ln(x)",
    )
    builder.add_computed_fact(
        "A2",
        label=FACT_REGISTRY["A2"]["label"],
        method=(
            "SymPy symbolic evaluation of eml(eml(1, x), 1) for positive "
            "symbol x; verify simplify(result - exp(E)/x) = 0"
        ),
        result="Confirmed: eml(eml(1, x), 1) = exp(e)/x",
        depends_on=["A1"],
    )
    builder.add_computed_fact(
        "A3",
        label=FACT_REGISTRY["A3"]["label"],
        method=(
            "SymPy symbolic evaluation of eml(1, eml(eml(1, x), 1)) for "
            "positive symbol x; verify simplify(result - ln(x)) = 0"
        ),
        result="Confirmed: full nested expression = ln(x), residual = 0",
        depends_on=["A1", "A2"],
    )
    builder.add_computed_fact(
        "A4",
        label=FACT_REGISTRY["A4"]["label"],
        method=(
            "Numerical evaluation of eml(1, eml(eml(1, x), 1)) - ln(x) at "
            "x = 0.01, 0.5, 1, 2, e, 100 using Python math; verify all < 1e-10"
        ),
        result=f"Confirmed: max |diff| = {max_diff:.2e}",
    )

    builder.add_cross_check(
        description=(
            "Symbolic (A3) vs numerical (A4): symbolic proves identity exactly "
            "for all x > 0; numerical confirms at 6 representative points "
            "spanning 4 orders of magnitude"
        ),
        fact_ids=["A3", "A4"],
        agreement=A3_verified and A4_verified,
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
        inner_evaluation_verified=A1_verified,
        middle_evaluation_verified=A2_verified,
        full_identity_verified=A3_verified,
        numerical_crosscheck_passed=A4_verified,
        claim_holds=claim_holds,
    )

    builder.emit()
