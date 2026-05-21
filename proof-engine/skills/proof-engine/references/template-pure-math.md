# Pure-Math Proof Template

> You are reading one template. See [proof-templates.md](proof-templates.md) for the full index and selection guidance.

For claims that are entirely mathematical (no empirical sources, no URLs, no citations).

## Runtime dependencies for re-runners

The Binder launcher image (where re-runners execute your `proof.py`) ships only `sympy`, `requests`, `python-dateutil`, and `Pillow` on top of the standard library. If your proof needs `numpy` or `scipy`, the Binder run will crash on `import` — re-runners can't `pip install` mid-notebook on Binder.

Prefer in this order:

1. **`sympy`** for algebra, calculus, polynomials, exact rational/integer arithmetic, symbolic linear algebra. Already in the image, deterministic, exact.
2. **Standard library** (`math`, `decimal`, `fractions`, `itertools`) for elementary numerics. Always available.
3. **`numpy`/`scipy`** only if `sympy` genuinely cannot do the job (large dense linear algebra, FFT, ODE integration). When you must, document the dep at the top of `proof.py` so a maintainer can decide whether to grow the Binder image vs. rewrite the proof:

   ```python
   # RUNTIME DEPENDENCY: requires numpy + scipy. Not in the default Binder
   # launcher image (proof-engine-binder/requirements.txt) — re-running on
   # Binder needs an image bump or proof rewrite to use sympy.
   import numpy as np
   from scipy import optimize
   ```

```python
"""
Proof: [claim text]
Generated: [date]
"""
import os
import sys

_SKILL_EXCLUDED_DIRS = {".git", ".venv", "venv", ".tox", ".worktrees",
                        ".cache", ".idea", ".vscode", "node_modules",
                        "__pycache__", "site-packages", "dist", "build"}

def _is_valid_skill_root(p):
    return (os.path.isfile(os.path.join(p, "scripts", "verify_citations.py"))
            and os.path.isfile(os.path.join(p, "SKILL.md")))

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        for _cand in (
            os.path.join(_d, "proof-engine", "skills", "proof-engine"),
            os.path.join(_d, "skills", "proof-engine"),
        ):
            if _is_valid_skill_root(_cand):
                PROOF_ENGINE_ROOT = _cand
                break
        if PROOF_ENGINE_ROOT:
            break
        try:
            for _sib in os.listdir(_d):
                if _sib in _SKILL_EXCLUDED_DIRS:
                    continue
                _sib_path = os.path.join(_d, _sib)
                if not os.path.isdir(_sib_path):
                    continue
                for _cand in (
                    os.path.join(_sib_path, "skills", "proof-engine"),
                    os.path.join(_sib_path, "proof-engine", "skills", "proof-engine"),
                ):
                    if _is_valid_skill_root(_cand):
                        PROOF_ENGINE_ROOT = _cand
                        break
                if PROOF_ENGINE_ROOT:
                    break
                if _sib.startswith("."):
                    try:
                        for _sub in os.listdir(_sib_path):
                            if _sub in _SKILL_EXCLUDED_DIRS:
                                continue
                            _cand = os.path.join(_sib_path, _sub, "skills", "proof-engine")
                            if _is_valid_skill_root(_cand):
                                PROOF_ENGINE_ROOT = _cand
                                break
                    except OSError:
                        pass
                    if PROOF_ENGINE_ROOT:
                        break
        except OSError:
            pass
        if PROOF_ENGINE_ROOT:
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError(
            "PROOF_ENGINE_ROOT not set and skill dir not found via walk-up "
            f"or sibling search from {os.path.dirname(os.path.abspath(__file__))}. "
            "Set the env var explicitly: "
            "export PROOF_ENGINE_ROOT=/path/to/skills/proof-engine"
        )
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.computations import compare, explain_calc
from scripts.proof_summary import ProofSummaryBuilder

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = "..."
CLAIM_FORMAL = {
    "subject": "...",
    "property": "...",
    "operator": "==",
    "operator_note": "...",
    "threshold": ...,
}

# 2. FACT REGISTRY — A-types only for pure math
FACT_REGISTRY = {
    "A1": {"label": "...", "method": None, "result": None},
    "A2": {"label": "...", "method": None, "result": None},
}

# 3. COMPUTATION — primary method
primary_result = ...

# 4. CROSS-CHECKS — mathematically independent methods (Rule 6)
crosscheck_result = ...
assert primary_result == crosscheck_result, (
    f"Cross-check failed: primary={primary_result}, crosscheck={crosscheck_result}"
)

# 5. ADVERSARIAL CHECKS (Rule 5)
adversarial_checks = [
    {
        "question": "...",
        "verification_performed": "...",
        "finding": "...",  # If counter-evidence found AND breaks_proof=False: MUST include explicit rebuttal (Rule 5)
        "breaks_proof": False,  # If True, verdict forced to UNDETERMINED
    },
]

# 6. VERDICT AND STRUCTURED OUTPUT
if __name__ == "__main__":
    claim_holds = compare(primary_result, CLAIM_FORMAL["operator"], CLAIM_FORMAL["threshold"])
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    # Pure-math: no citations, so no unverified-citation variants needed
    if any_breaks:
        verdict = "UNDETERMINED"
    else:
        verdict = "PROVED" if claim_holds else "DISPROVED"

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    builder.add_computed_fact("A1", label="...", method="...", result=primary_result)
    builder.add_computed_fact("A2", label="...", method="...", result=crosscheck_result)

    builder.add_cross_check(
        description="...",
        fact_ids=["A1", "A2"],
        values_compared=[str(primary_result), str(crosscheck_result)],
        agreement=primary_result == crosscheck_result,
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
        primary_result=primary_result,
        threshold=CLAIM_FORMAL["threshold"],
        operator=CLAIM_FORMAL["operator"],
        claim_holds=claim_holds,
    )
    # write_json_path lands proof.json next to proof.py regardless of CWD
    builder.emit(write_json_path=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "proof.json"))
```

**Note on `proof.json`.** `builder.emit(write_json_path=...)` writes `proof.json` as a real file alongside `proof.py` AND prints the JSON to stdout (preceded by the marker line `=== PROOF SUMMARY (JSON) ===`). The publish toolchain (`tools/proof-site.py publish`) and the site-build loader capture from stdout; downstream consumers can use either source. Inline path computation in the template anchors the output next to `proof.py` regardless of the caller's CWD. To suppress the file write (e.g., for a one-off inspection that shouldn't leave an artifact), call `builder.emit()` without `write_json_path`.

Key differences from the empirical template:
- No `empirical_facts`, `verify_all_citations`, `extract_values`, or `smart_extract` imports
- No `citations` or `extractions` keys in the JSON summary (omitted, not empty)
- Cross-checks use mathematically independent methods instead of independent sources
- `explain_calc()` is optional — use for scalar expressions; for aggregations over lists, use descriptive `print()` instead

### Adaptation: Open Problems (Unproved Conjectures)

For claims about conjectures that have no known proof or disproof (e.g., "The Goldbach conjecture holds for every even integer greater than 2"):

1. **CLAIM_FORMAL:** Set `operator` to `"=="`, `threshold` to `0` (zero counterexamples expected), and add `"claim_type": "open_problem"` and `"operator_note"` explaining that this is an unresolved conjecture — computational verification provides evidence but not proof.
2. **Computation:** Verify the conjecture computationally up to a large bound (e.g., 10^6). Record the bound explicitly.
3. **Cross-check:** Use a second independent computational method (different algorithm, library, or approach) to verify the same bound.
4. **Adversarial checks:** Search for known counterexample attempts, the current verified bound in the literature, and any conditional results.
5. **Verdict:** Always `UNDETERMINED`. Do NOT use `claim_holds` to drive the verdict — the computational check confirms "no counterexamples found up to N" which is not the same as proving the universal claim. The `operator_note` must state this explicitly.
6. **JSON summary:** Include `"verified_up_to"` in `key_results` documenting the computational bound, and `"counterexamples_found": 0`.

```python
# Example CLAIM_FORMAL for open problems
CLAIM_FORMAL = {
    "subject": "Goldbach conjecture",
    "property": "counterexamples in range [4, 10^6]",
    "operator": "==",
    "threshold": 0,
    "claim_type": "open_problem",
    "operator_note": (
        "Universal conjecture — computational verification up to a finite bound "
        "provides evidence but cannot prove the claim. Verdict is always UNDETERMINED."
    ),
}

# Example verdict logic for open problems
# NOTE: Uses if/else to satisfy check_verdict_branches() in validate_proof.py.
# Both branches produce UNDETERMINED — the conditional documents *why*.
if __name__ == "__main__":
    no_counterexamples = compare(n_counterexamples, "==", 0,
                                  label="no counterexamples in [4, 10^6]")
    if no_counterexamples:
        verdict = "UNDETERMINED"  # verified up to bound, but finite check ≠ proof
    else:
        verdict = "UNDETERMINED"  # counterexample found — but for open problems,
                                  # a counterexample would actually be DISPROVED;
                                  # adjust if your conjecture admits this
```

### Adaptation: Proof-by-Contradiction / Infinite Descent

For proofs that establish truth via logical contradiction rather than direct computation:

1. **Split into verifiable sub-steps:** Decompose the logical argument into steps that CAN be verified computationally. For infinite descent: (a) verify the descent produces a strictly smaller solution for small cases, (b) verify the base case, (c) verify modular constraints.
2. **Each sub-step is a separate A-type fact** with its own `explain_calc()` or `compare()` call.
3. **Cross-check:** Use an independent method (e.g., exhaustive search up to a bound confirming no solutions exist).
4. **Limitations:** Document in `operator_note` that the logical chain (parametrization, factorization, descent step) is presented as prose and not machine-verified. The computational checks verify necessary conditions, not the full argument.
5. **Verdict:** Use PROVED only if the computational verification is sufficient (e.g., exhaustive search for a finite domain). For infinite domains where the proof relies on unverified logical steps, prefer `UNDETERMINED` with documentation of what was verified computationally vs. what relies on the logical argument.

```python
# Example: cross-check via exhaustive search
exhaustive_solutions = [
    (x, y, z) for x in range(1, bound)
    for y in range(x, bound) for z in range(y, bound)
    if x**4 + y**4 == z**4
]
A2_result = compare(len(exhaustive_solutions), "==", 0,
                    label="exhaustive search confirms no solutions")
```

### Adaptation: Theorem-shaped claims (boolean, no numeric threshold)

For structural theorems where the claim is inherently boolean ("X implies Y", "property Z is preserved under operation W", existence/uniqueness), use `prove_holds()` instead of `compare(x, "==", True)`. This is a **readability** improvement over the numeric idiom — both produce the same verdict, but `prove_holds()` makes the audit output read as a theorem rather than a pretend-numeric comparison.

1. **Imports:** add `prove_holds` to the `from scripts.computations import ...` line. If the proof has no numeric comparisons, `compare` can be dropped from that import.
2. **CLAIM_FORMAL:** omit `threshold` entirely (or set to `None`), set `operator` to `"holds"`, and add `"claim_type": "theorem"` as documentation (no runtime effect — it signals intent to human readers).
3. **`operator_note`:** explain what "holds" means in the logical domain — which propositions are being asserted, over what quantifier domain, and what the verification strategy is. Do NOT write tautologies like *"'True' means the conditions are satisfied."*
4. **Cross-checks (Rule 6):** numeric cross-checks don't apply. Choose one of:
   - **Symbolic re-derivation** — derive the same implication by an independent route (e.g., sympy manipulation vs. hand-coded algebra).
   - **Exhaustive small-case verification** — confirm the theorem on a documented battery of specific instances. Suitable for finite domains or finite projections.
   - **Structural decomposition** — if the theorem is `A and B`, verify `A` and `B` by independent methods.
   - If no mechanical cross-check is feasible, set the verdict to `UNDETERMINED` and document the gap in `operator_note`. A theorem without a mechanical second check should not claim `PROVED`.
5. **Verdict:** assign `claim_holds = prove_holds(all_conditions_met, label="…")`. Compose `all_conditions_met` from A-type fact results using `and` — do NOT hardcode it to `True`.

```python
from scripts.computations import prove_holds, explain_calc  # drop `compare` if unused

CLAIM_FORMAL = {
    "subject": "composition of convex functions",
    "property": "preserves convexity under monotonic outer function",
    "operator": "holds",
    "claim_type": "theorem",  # documentation only — no runtime effect
    "operator_note": (
        "Asserts: for f convex and g convex-and-nondecreasing, g ∘ f is convex "
        "on the intersection of their domains. Verified by (A1) applying the "
        "composition rule from Boyd & Vandenberghe §3.2.4 and (A2) exhaustive "
        "check on a 50-point grid of parameterized (f, g) pairs covering the "
        "relevant monotonicity regimes. 'holds' = both verifications succeed."
    ),
    # No 'threshold' key: theorem claims are inherently boolean.
}

# Verdict
all_conditions_met = A1_result and A2_result
claim_holds = prove_holds(all_conditions_met, label="composition theorem holds")
```

**Note on `prove_holds()`:** coerces via `bool()` so numpy/sympy booleans (`np.bool_`, `BooleanTrue`) work correctly. Raises `TypeError` on `None` — an uninitialized FACT_REGISTRY entry silently becoming `False` would make missing evidence look like a disproof. Truthy non-bool values (non-empty strings, nonzero ints) coerce to `True` via `bool()` rather than erroring — compose `claim_holds` inputs from real booleans (A-type `result` values, comparison outputs) so the audit output reads cleanly.
