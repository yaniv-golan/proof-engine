# Audit: Automation Nash Equilibrium vs Cooperative Optimum

- **Generated:** 2026-04-15
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Interpretation

The claim specifies a complete game-theoretic model with N symmetric firms choosing automation rates. Each firm's profit depends on a shared demand pool that shrinks as automation displaces wage workers, creating a negative externality. The claim asserts three specific algebraic formulas: the Nash equilibrium rate, the cooperative optimum rate, and their difference.

The formal interpretation treats these as interior first-order condition solutions from the unconstrained optimization problem. The claim implicitly assumes parameters place the optima in (0,1); this is noted in the operator_note but not separately verified (it depends on parameter magnitudes, not the algebra).

**Formalization scope:** The formal interpretation is a faithful 1:1 mapping of the natural-language claim. The model, objective functions, and equilibrium concepts are fully specified in the claim itself. The only interpretive choice is treating the formulas as unconstrained FOC solutions, which is the standard interpretation for interior optima in game theory.

*Source: proof.py JSON summary*

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | Symmetric N-firm automation game with demand externality |
| Property | All three equilibrium results hold |
| Operator | == |
| Threshold | True |
| Operator Note | The claim asserts three algebraic identities derived from first-order conditions of the given model: (1) the symmetric Nash equilibrium rate alpha^NE = (s - ell/N)/k, (2) the cooperative (joint) optimum alpha^CO = (s - ell)/k, and (3) the gap alpha^NE - alpha^CO = ell*(1 - 1/N)/k > 0. These are interior solutions from unconstrained FOCs; the claim implicitly assumes parameters place the optima in (0,1). Strict positivity of the gap follows from ell > 0 and N >= 2. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Label | Key |
|----|-------|-----|
| A1 | Nash equilibrium rate alpha^NE = (s - ell/N)/k via FOC | (computed) |
| A2 | Cooperative optimum alpha^CO = (s - ell)/k via joint FOC | (computed) |
| A3 | Gap alpha^NE - alpha^CO = ell*(1 - 1/N)/k > 0 | (computed) |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Nash equilibrium rate alpha^NE = (s - ell/N)/k via FOC | SymPy symbolic differentiation of pi_i w.r.t. alpha_i; solve FOC; verify result equals (w-c-lambda(1-eta)w/N)/k | Confirmed: residual = 0 |
| A2 | Cooperative optimum alpha^CO = (s - ell)/k via joint FOC | SymPy symbolic differentiation of total profit Pi w.r.t. alpha at symmetric profile; solve FOC; verify result equals (w-c-lambda(1-eta)w)/k | Confirmed: residual = 0 |
| A3 | Gap alpha^NE - alpha^CO = ell*(1 - 1/N)/k > 0 | SymPy symbolic subtraction alpha^NE - alpha^CO; verify equals lambda(1-eta)w(1-1/N)/k; positivity from parameter assumptions | Confirmed: gap formula correct, strictly positive for N >= 2 |

*Source: proof.py JSON summary*

## Computation Traces

```
======================================================================
PRIMARY METHOD: Symbolic derivation via SymPy
======================================================================

--- A1: Nash Equilibrium (FOC for firm i) ---

FOC (dpi_i/dalpha_i): -L*alpha_i*k - L*c + L*w + L*lambda*w*(eta - 1)/N
alpha_i* = (N*(-c + w) + lambda*w*(eta - 1))/(N*k)
alpha_i* - claimed_NE = 0
A1 verified (symbolic): True

--- A2: Cooperative Optimum (joint optimization) ---

FOC (dPi/dalpha_co): -L*N*alpha_co*k - L*N*c - L*N*lambda*w*(1 - eta) + L*N*w
alpha_co* = (-c + eta*lambda*w - lambda*w + w)/k
alpha_co* - claimed_CO = 0
A2 verified (symbolic): True

--- A3: Gap computation and positivity ---

Gap (symbolic): lambda*w*(-N*eta + N + eta - 1)/(N*k)
Gap - claimed_gap = 0
A3 gap formula verified: True

======================================================================
CROSS-CHECK: Numerical verification at specific parameter values
======================================================================

  s = w - c: w_v - c_v = 1.0 - 0.5 = 0.5000
  ell = lambda*(1-eta)*w: lam_v * (1 - eta_v) * w_v = 0.5 * (1 - 0.4) * 1.0 = 0.3000
  alpha^NE = (s - ell/N)/k: (s_v - ell_v / N_v) / k_v = (0.5 - 0.3 / 5) / 1.0 = 0.4400
  alpha^CO = (s - ell)/k: (s_v - ell_v) / k_v = (0.5 - 0.3) / 1.0 = 0.2000
  gap = ell*(1-1/N)/k: ell_v * (1 - 1 / N_v) / k_v = 0.3 * (1 - 1 / 5) / 1.0 = 0.2400
  Individual FOC at alpha^NE (should be 0): ... = 0.0000
  NE FOC residual near zero: 0.0 < 1e-10 = True
  Joint FOC at alpha^CO (should be 0): ... = 0.0000
  CO FOC residual near zero: 0.0 < 1e-10 = True
  Gap formula matches direct subtraction: 0.0 < 1e-12 = True
  Gap is strictly positive: 0.24 > 0 = True

--- Second-order conditions (symbolic) ---
d^2 pi_i / d alpha_i^2 = -kL: True (residual: 0)
d^2 Pi / d alpha^2 = -NkL: True (residual: 0)
  All three sub-claims verified (symbolic + numerical): True == True = True
```

*Source: proof.py inline output (execution trace)*

## Adversarial Checks (Rule 5)

### Check 1: Does the FOC yield a maximum?

- **Question:** Does the FOC yield a maximum (not minimum or saddle)?
- **Verification performed:** Computed second-order conditions symbolically with SymPy. d^2 pi_i / d alpha_i^2 = -kL < 0 (k > 0, L > 0): strict concavity. d^2 Pi / d alpha^2 = -NkL < 0: joint problem also strictly concave. Both SOCs confirmed computationally.
- **Finding:** SOC confirmed: both individual and joint profit are strictly concave, so FOC solutions are global maxima.
- **Breaks proof:** No

### Check 2: Is the symmetric Nash equilibrium unique?

- **Question:** Is the symmetric Nash equilibrium unique?
- **Verification performed:** Examined the best-response function. The FOC solution alpha_i* = (s - ell/N)/k does not depend on rivals' strategies, making it a dominant strategy. Strict concavity ensures uniqueness of each firm's best response.
- **Finding:** The NE is unique: alpha_i* is a dominant strategy, independent of rivals' choices. No asymmetric equilibria exist.
- **Breaks proof:** No

### Check 3: Could interior solutions lie outside [0,1]?

- **Question:** Could the interior solutions lie outside [0,1]?
- **Verification performed:** Checked parameter conditions for interiority. alpha^NE in (0,1) requires ell/N < s < k + ell/N. alpha^CO in (0,1) requires ell < s < k + ell. The claim derives unconstrained FOC solutions; interiority is a parameter assumption noted in operator_note.
- **Finding:** Formulas are correct as interior FOC solutions. Whether they fall in [0,1] depends on parameter magnitudes, which is an implicit assumption of the claim.
- **Breaks proof:** No

### Check 4: Can aggregate demand become negative?

- **Question:** Can aggregate demand D become negative?
- **Verification performed:** At maximum automation (all alpha_j = 1): D = A + lambda*w*L*N*eta >= A > 0. D is linear and decreasing in each alpha_j, so it is minimized at full automation. Since D > 0 even there, D > 0 always.
- **Finding:** D >= A > 0 for all feasible profiles. Model is well-specified.
- **Breaks proof:** No

*Source: proof.py JSON summary*

## Quality Checks

- **Rule 1:** N/A -- pure computation, no empirical facts
- **Rule 2:** N/A -- pure computation, no empirical facts
- **Rule 3:** N/A -- proof is not time-sensitive; date.today() used only in generator metadata
- **Rule 4:** CLAIM_FORMAL with operator_note present; documents interior-solution assumption
- **Rule 5:** 4 adversarial checks: SOC verification, uniqueness, boundary feasibility, demand well-specification
- **Rule 6:** N/A -- pure computation, no empirical facts. Cross-check uses mathematically independent method (numerical spot-check vs. symbolic algebra)
- **Rule 7:** All computations via SymPy (symbolic) and explain_calc/compare (numerical); no hard-coded constants
- **validate_proof.py result:** PASS (15/16 checks passed, 0 issues, 1 warning about is_time_sensitive declaration -- resolved)

*Source: author analysis*

---

Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.16.0 on 2026-04-15.
