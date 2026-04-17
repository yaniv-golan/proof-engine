"""
Proof: Automation Nash Equilibrium vs Cooperative Optimum — Over-Automation Gap
Generated: 2026-04-15
"""
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date
from sympy import Symbol, Rational, diff, solve, simplify

from scripts.computations import compare, explain_calc
from scripts.proof_summary import ProofSummaryBuilder

# ============================================================================
# 1. CLAIM INTERPRETATION (Rule 4)
# ============================================================================

CLAIM_NATURAL = 'Consider a sector with \\(N \\geq 2\\) symmetric firms, each endowed with L task-positions. Each firm i chooses an automation rate \\(\\alpha_i\\) in [0,1], paying wage w per human-staffed task and cost c per automated task, with integration friction cost \\((k/2) \\cdot L \\cdot \\alpha_i^2\\) where \\(k > 0\\). Aggregate sectoral demand is \\(D = A + \\lambda \\cdot w \\cdot L \\cdot [N - (1-\\eta) \\sum_j \\alpha_j]\\), where \\(A > 0\\) is exogenous demand, \\(\\lambda \\in (0,1]\\) is workers\' marginal propensity to consume from wages, and \\(\\eta \\in [0,1)\\) is the fraction of displaced wage income recovered through reemployment. Each firm\'s revenue is \\(D/N\\) (equal market shares). Define \\(s = w - c > 0\\) and \\(\\ell = \\lambda(1-\\eta)w > 0\\). Each firm i maximizes \\(\\pi_i = D/N - wL(1-\\alpha_i) - cL\\alpha_i - (k/2)L\\alpha_i^2\\). The Nash equilibrium automation rate is \\(\\alpha^{NE} = (s - \\ell/N)/k\\). The cooperative optimum is \\(\\alpha^{CO} = (s - \\ell)/k\\). The difference \\(\\alpha^{NE} - \\alpha^{CO} = \\ell \\cdot (1 - 1/N)/k\\) is strictly positive.'

CLAIM_FORMAL = {
    "subject": "Symmetric N-firm automation game with demand externality",
    "property": "All three equilibrium results hold",
    "operator": "==",
    "operator_note": (
        "The claim asserts three algebraic identities derived from first-order "
        "conditions of the given model: (1) the symmetric Nash equilibrium rate "
        "alpha^NE = (s - ell/N)/k, (2) the cooperative (joint) optimum "
        "alpha^CO = (s - ell)/k, and (3) the gap alpha^NE - alpha^CO = "
        "ell*(1 - 1/N)/k > 0. These are interior solutions from unconstrained "
        "FOCs; the claim implicitly assumes parameters place the optima in "
        "(0,1). Strict positivity of the gap follows from ell > 0 and N >= 2."
    ),
    "threshold": True,
    "is_time_sensitive": False,
}

# ============================================================================
# 2. FACT REGISTRY
# ============================================================================

FACT_REGISTRY = {
    "A1": {
        "label": "Nash equilibrium rate alpha^NE = (s - ell/N)/k via FOC",
        "method": None,
        "result": None,
    },
    "A2": {
        "label": "Cooperative optimum alpha^CO = (s - ell)/k via joint FOC",
        "method": None,
        "result": None,
    },
    "A3": {
        "label": "Gap alpha^NE - alpha^CO = ell*(1 - 1/N)/k > 0",
        "method": None,
        "result": None,
    },
}

# ============================================================================
# 3. PRIMARY METHOD: Symbolic derivation with SymPy
# ============================================================================

print("=" * 70)
print("PRIMARY METHOD: Symbolic derivation via SymPy")
print("=" * 70)

# Model parameters (positive symbols matching the model assumptions)
N_s = Symbol("N", positive=True, integer=True)
L_s = Symbol("L", positive=True)
w_s = Symbol("w", positive=True)
c_s = Symbol("c", positive=True)
k_s = Symbol("k", positive=True)
A_s = Symbol("A", positive=True)
lam_s = Symbol("lambda", positive=True)
eta_s = Symbol("eta", nonnegative=True)

# Decision variables
ai_s = Symbol("alpha_i")      # firm i's automation rate
ar_s = Symbol("alpha_r")      # rivals' common rate
aco_s = Symbol("alpha_co")    # cooperative rate

# --- A1: Nash Equilibrium ---
print("\n--- A1: Nash Equilibrium (FOC for firm i) ---\n")

# Demand when (N-1) rivals play ar_s and firm i plays ai_s
D_NE = A_s + lam_s * w_s * L_s * (
    N_s - (1 - eta_s) * ((N_s - 1) * ar_s + ai_s)
)

# Firm i's profit
pi_i = (
    D_NE / N_s
    - w_s * L_s * (1 - ai_s)
    - c_s * L_s * ai_s
    - Rational(1, 2) * k_s * L_s * ai_s**2
)

# First-order condition
foc_i = diff(pi_i, ai_s)
print(f"FOC (dpi_i/dalpha_i): {foc_i}")

# Solve for alpha_i
ai_solutions = solve(foc_i, ai_s)
assert len(ai_solutions) == 1, f"Expected unique FOC solution, got {ai_solutions}"
ai_star = ai_solutions[0]
print(f"alpha_i* = {ai_star}")

# Note: ai_star does not depend on ar_s — this is a dominant strategy.
# At symmetric NE, all firms play this rate.

# Claimed NE in original parameters: (w - c - lambda*(1-eta)*w/N) / k
claimed_NE = (w_s - c_s - lam_s * (1 - eta_s) * w_s / N_s) / k_s

A1_residual = simplify(ai_star - claimed_NE)
print(f"alpha_i* - claimed_NE = {A1_residual}")
A1_verified = A1_residual == 0
print(f"A1 verified (symbolic): {A1_verified}")
assert A1_verified, f"A1 failed: residual = {A1_residual}"

# --- A2: Cooperative Optimum ---
print("\n--- A2: Cooperative Optimum (joint optimization) ---\n")

# Total profit at symmetric profile (all firms play aco_s)
D_CO = A_s + lam_s * w_s * L_s * (N_s - (1 - eta_s) * N_s * aco_s)

Pi_total = (
    D_CO
    - N_s * w_s * L_s * (1 - aco_s)
    - N_s * c_s * L_s * aco_s
    - Rational(1, 2) * k_s * L_s * N_s * aco_s**2
)

foc_co = diff(Pi_total, aco_s)
print(f"FOC (dPi/dalpha_co): {foc_co}")

aco_solutions = solve(foc_co, aco_s)
assert len(aco_solutions) == 1, f"Expected unique FOC solution, got {aco_solutions}"
aco_star = aco_solutions[0]
print(f"alpha_co* = {aco_star}")

# Claimed CO: (w - c - lambda*(1-eta)*w) / k
claimed_CO = (w_s - c_s - lam_s * (1 - eta_s) * w_s) / k_s

A2_residual = simplify(aco_star - claimed_CO)
print(f"alpha_co* - claimed_CO = {A2_residual}")
A2_verified = A2_residual == 0
print(f"A2 verified (symbolic): {A2_verified}")
assert A2_verified, f"A2 failed: residual = {A2_residual}"

# --- A3: Gap and strict positivity ---
print("\n--- A3: Gap computation and positivity ---\n")

gap_sym = simplify(ai_star - aco_star)
print(f"Gap (symbolic): {gap_sym}")

# Claimed gap: lambda*(1-eta)*w*(1 - 1/N)/k
claimed_gap = lam_s * (1 - eta_s) * w_s * (1 - 1 / N_s) / k_s

A3_residual = simplify(gap_sym - claimed_gap)
print(f"Gap - claimed_gap = {A3_residual}")
A3_verified = A3_residual == 0
print(f"A3 gap formula verified: {A3_verified}")
assert A3_verified, f"A3 failed: residual = {A3_residual}"

# Positivity: all factors are positive under the model assumptions
print(
    "Positivity: ell = lambda*(1-eta)*w > 0 (product of positive terms); "
    "(1 - 1/N) >= 1/2 > 0 for N >= 2; k > 0. "
    "Gap = ell*(1-1/N)/k is strictly positive."
)

all_primary = A1_verified and A2_verified and A3_verified
print(f"\nAll primary (symbolic) checks pass: {all_primary}")

# ============================================================================
# 4. CROSS-CHECK: Numerical spot-check (Rule 6)
# ============================================================================

print("\n" + "=" * 70)
print("CROSS-CHECK: Numerical verification at specific parameter values")
print("=" * 70)

# Parameters chosen so interior solutions lie in (0, 1)
N_v, L_v, w_v, c_v = 5, 100, 1.0, 0.5
k_v, A_v, lam_v, eta_v = 1.0, 1000.0, 0.5, 0.4

print(
    f"\nParameters: N={N_v}, L={L_v}, w={w_v}, c={c_v}, "
    f"k={k_v}, A={A_v}, lambda={lam_v}, eta={eta_v}"
)

s_v = explain_calc(
    "w_v - c_v", {"w_v": w_v, "c_v": c_v}, label="s = w - c"
)

ell_v = explain_calc(
    "lam_v * (1 - eta_v) * w_v",
    {"lam_v": lam_v, "eta_v": eta_v, "w_v": w_v},
    label="ell = lambda*(1-eta)*w",
)

alpha_NE_num = explain_calc(
    "(s_v - ell_v / N_v) / k_v",
    {"s_v": s_v, "ell_v": ell_v, "N_v": N_v, "k_v": k_v},
    label="alpha^NE = (s - ell/N)/k",
)

alpha_CO_num = explain_calc(
    "(s_v - ell_v) / k_v",
    {"s_v": s_v, "ell_v": ell_v, "k_v": k_v},
    label="alpha^CO = (s - ell)/k",
)

gap_num = explain_calc(
    "ell_v * (1 - 1 / N_v) / k_v",
    {"ell_v": ell_v, "N_v": N_v, "k_v": k_v},
    label="gap = ell*(1-1/N)/k",
)

# Verify NE by checking individual FOC residual
foc_at_NE = explain_calc(
    "-lam_v * (1 - eta_v) * w_v * L_v / N_v "
    "+ (w_v - c_v) * L_v "
    "- k_v * L_v * alpha_NE_num",
    {
        "lam_v": lam_v, "eta_v": eta_v, "w_v": w_v, "L_v": L_v,
        "N_v": N_v, "c_v": c_v, "k_v": k_v, "alpha_NE_num": alpha_NE_num,
    },
    label="Individual FOC at alpha^NE (should be 0)",
)
NE_foc_ok = compare(abs(foc_at_NE), "<", 1e-10, label="NE FOC residual near zero")

# Verify CO by checking joint FOC residual
foc_at_CO = explain_calc(
    "N_v * L_v * (s_v - ell_v - k_v * alpha_CO_num)",
    {
        "N_v": N_v, "L_v": L_v, "s_v": s_v, "ell_v": ell_v,
        "k_v": k_v, "alpha_CO_num": alpha_CO_num,
    },
    label="Joint FOC at alpha^CO (should be 0)",
)
CO_foc_ok = compare(abs(foc_at_CO), "<", 1e-10, label="CO FOC residual near zero")

# Verify gap matches direct subtraction
gap_direct = alpha_NE_num - alpha_CO_num
gap_match = compare(
    abs(gap_direct - gap_num), "<", 1e-12,
    label="Gap formula matches direct subtraction",
)
gap_positive = compare(gap_num, ">", 0, label="Gap is strictly positive")

all_numerical = NE_foc_ok and CO_foc_ok and gap_match and gap_positive
print(f"\nAll numerical cross-checks pass: {all_numerical}")
assert all_numerical, "Numerical cross-check failed"

# Second-order conditions (symbolic confirmation)
print("\n--- Second-order conditions (symbolic) ---")
soc_ind = diff(pi_i, ai_s, 2)
soc_ind_val = simplify(soc_ind + k_s * L_s)
soc_ind_ok = soc_ind_val == 0
print(f"d^2 pi_i / d alpha_i^2 = -kL: {soc_ind_ok} (residual: {soc_ind_val})")

soc_co = diff(Pi_total, aco_s, 2)
soc_co_val = simplify(soc_co + N_s * k_s * L_s)
soc_co_ok = soc_co_val == 0
print(f"d^2 Pi / d alpha^2 = -NkL: {soc_co_ok} (residual: {soc_co_val})")

# ============================================================================
# 5. ADVERSARIAL CHECKS (Rule 5)
# ============================================================================

adversarial_checks = [
    {
        "question": "Does the FOC yield a maximum (not minimum or saddle)?",
        "verification_performed": (
            "Computed second-order conditions symbolically with SymPy. "
            "d^2 pi_i / d alpha_i^2 = -kL < 0 (k > 0, L > 0): strict concavity. "
            "d^2 Pi / d alpha^2 = -NkL < 0: joint problem also strictly concave. "
            "Both SOCs confirmed computationally."
        ),
        "finding": (
            "SOC confirmed: both individual and joint profit are strictly "
            "concave, so FOC solutions are global maxima."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is the symmetric Nash equilibrium unique?",
        "verification_performed": (
            "Examined the best-response function. The FOC solution alpha_i* = "
            "(s - ell/N)/k does not depend on rivals' strategies, making it a "
            "dominant strategy. Strict concavity ensures uniqueness of each "
            "firm's best response."
        ),
        "finding": (
            "The NE is unique: alpha_i* is a dominant strategy, independent of "
            "rivals' choices. No asymmetric equilibria exist."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could the interior solutions lie outside [0,1]?",
        "verification_performed": (
            "Checked parameter conditions for interiority. alpha^NE in (0,1) "
            "requires ell/N < s < k + ell/N. alpha^CO in (0,1) requires "
            "ell < s < k + ell. The claim derives unconstrained FOC solutions; "
            "interiority is a parameter assumption noted in operator_note."
        ),
        "finding": (
            "Formulas are correct as interior FOC solutions. Whether they "
            "fall in [0,1] depends on parameter magnitudes, which is an "
            "implicit assumption of the claim."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Can aggregate demand D become negative?",
        "verification_performed": (
            "At maximum automation (all alpha_j = 1): "
            "D = A + lambda*w*L*N*eta >= A > 0. "
            "D is linear and decreasing in each alpha_j, so it is minimized "
            "at full automation. Since D > 0 even there, D > 0 always."
        ),
        "finding": "D >= A > 0 for all feasible profiles. Model is well-specified.",
        "breaks_proof": False,
    },
]

# ============================================================================
# 6. VERDICT AND STRUCTURED OUTPUT
# ============================================================================

if __name__ == "__main__":
    all_checks = all_primary and all_numerical and soc_ind_ok and soc_co_ok
    claim_holds = compare(
        all_checks, "==", CLAIM_FORMAL["threshold"],
        label="All three sub-claims verified (symbolic + numerical)",
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
            "SymPy symbolic differentiation of pi_i w.r.t. alpha_i; "
            "solve FOC; verify result equals (w-c-lambda(1-eta)w/N)/k"
        ),
        result="Confirmed: residual = 0",
    )
    builder.add_computed_fact(
        "A2",
        label=FACT_REGISTRY["A2"]["label"],
        method=(
            "SymPy symbolic differentiation of total profit Pi w.r.t. alpha "
            "at symmetric profile; solve FOC; verify result equals "
            "(w-c-lambda(1-eta)w)/k"
        ),
        result="Confirmed: residual = 0",
    )
    builder.add_computed_fact(
        "A3",
        label=FACT_REGISTRY["A3"]["label"],
        method=(
            "SymPy symbolic subtraction alpha^NE - alpha^CO; verify equals "
            "lambda(1-eta)w(1-1/N)/k; positivity from parameter assumptions"
        ),
        result="Confirmed: gap formula correct, strictly positive for N >= 2",
        depends_on=["A1", "A2"],
    )

    builder.add_cross_check(
        description=(
            "Numerical spot-check at N=5, w=1, c=0.5, k=1, "
            "lambda=0.5, eta=0.4 (s=0.5, ell=0.3)"
        ),
        fact_ids=["A1", "A2", "A3"],
        agreement=all_numerical,
        values_compared=[
            f"NE FOC residual = {foc_at_NE:.2e}",
            f"CO FOC residual = {foc_at_CO:.2e}",
            f"Gap direct = {gap_direct}, gap formula = {gap_num}",
        ],
    )
    builder.add_cross_check(
        description=(
            "Second-order conditions verified symbolically "
            "(strict concavity of individual and joint profit)"
        ),
        fact_ids=["A1", "A2"],
        agreement=soc_ind_ok and soc_co_ok,
        values_compared=[
            f"d^2 pi_i/dalpha_i^2 = -kL: {soc_ind_ok}",
            f"d^2 Pi/dalpha^2 = -NkL: {soc_co_ok}",
        ],
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
        A1_NE_verified=A1_verified,
        A2_CO_verified=A2_verified,
        A3_gap_verified=A3_verified,
        numerical_crosscheck_passed=all_numerical,
        SOC_verified=soc_ind_ok and soc_co_ok,
    )

    builder.emit()
