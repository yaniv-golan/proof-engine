"""
Proof: The St. Petersburg paradox has a finite expected value that a rational person should be willing to pay.
Generated: 2026-03-28

Compound claim decomposition:
  SC1: The St. Petersburg game's expected monetary value E[X] is finite.
       → DISPROVED: E[X] = sum_{n>=1} (1/2)^n * 2^n = sum_{n>=1} 1 = infinity (diverges).

  SC2: A rational person should be willing to pay only a finite amount to play.
       → PROVED: Under Bernoulli's (1738) logarithmic utility, E[ln(2^N)] = 2*ln(2)
         (finite), and the certainty equivalent = exp(2*ln(2)) = $4.

Overall verdict: DISPROVED.
The premise "has a finite expected value" is mathematically false — EV is infinite.
The correct resolution (SC2) is finite expected *utility*, not finite expected *value*.
"""
import json
import math
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get(
    "PROOF_ENGINE_ROOT",
    "/Users/yaniv/Documents/code/proof-engine/proof-engine/skills/proof-engine",
)
sys.path.insert(0, PROOF_ENGINE_ROOT)
from datetime import date

from scripts.verify_citations import verify_all_citations, build_citation_detail
from scripts.computations import compare, explain_calc

# ── 1. CLAIM INTERPRETATION (Rule 4) ──────────────────────────────────────────
CLAIM_NATURAL = (
    "The St. Petersburg paradox has a finite expected value that a rational "
    "person should be willing to pay."
)

CLAIM_FORMAL = {
    "subject": "St. Petersburg game",
    "property": "expected monetary value (SC1) and rational certainty equivalent (SC2)",
    "operator": "AND",
    "operator_note": (
        "The claim makes two assertions: "
        "(SC1) the expected monetary value E[X] is finite, AND "
        "(SC2) a rational person should pay only a finite amount. "
        "SC1 requires the series sum_{n>=1} (1/2^n)*2^n to converge to a finite number. "
        "SC2 requires decision theory (expected utility) to yield a finite certainty equivalent. "
        "The overall claim is DISPROVED because SC1 is false: the EV series diverges to infinity. "
        "SC2 is true — under Bernoulli's (1738) log utility, the certainty equivalent = $4 "
        "(initial wealth assumed zero) — but this does not save the compound claim because "
        "the correct resolution involves expected *utility*, not expected *value*."
    ),
}

# ── 2. FACT REGISTRY ──────────────────────────────────────────────────────────
FACT_REGISTRY = {
    "A1": {
        "label": "SC1: EV term (1/2)^n * 2^n = 1 for every n; series = sum of infinitely many 1s",
        "method": None, "result": None,
    },
    "A2": {
        "label": "SC1 cross-check: partial sums grow as N (unbounded), confirming divergence",
        "method": None, "result": None,
    },
    "A3": {
        "label": "SC2: E[ln(2^N)] = ln(2) * sum(n*(1/2)^n) = ln(2)*2 = 2*ln(2) (finite)",
        "method": None, "result": None,
    },
    "A4": {
        "label": "SC2 cross-check: generating function confirms sum(n*(1/2)^n) = 2",
        "method": None, "result": None,
    },
    "B1": {"key": "source_wiki",
           "label": "Wikipedia: St. Petersburg paradox — game rules and infinite expected value"},
    "B2": {"key": "source_sep",
           "label": "Stanford Encyclopedia of Philosophy — Bernoulli utility resolution"},
}

# ── 3. EMPIRICAL FACTS ────────────────────────────────────────────────────────
empirical_facts = {
    "source_wiki": {
        "quote": "The expected payoff of the lottery game is infinite",
        "url": "https://en.wikipedia.org/wiki/St._Petersburg_paradox",
        "source_name": "Wikipedia: St. Petersburg paradox",
    },
    "source_sep": {
        "quote": "the logarithm of the monetary amount, which entails that improbable but large monetary prizes will contribute less to the expected utility of the game than more probable but smaller monetary amounts",
        "url": "https://plato.stanford.edu/entries/paradox-stpetersburg/",
        "source_name": "Stanford Encyclopedia of Philosophy: St. Petersburg Paradox",
    },
}

# ── 4. CITATION VERIFICATION (Rule 2) ─────────────────────────────────────────
citation_results = verify_all_citations(empirical_facts, wayback_fallback=True)

# ── 5. SC1: EV Series Diverges ────────────────────────────────────────────────
# Game rules: flip fair coin until heads. Payout = 2^n if heads first on flip n.
# P(heads on flip n) = (1/2)^n
# E[X] = sum_{n=1}^inf (1/2)^n * 2^n

# Algebraic simplification (primary method):
# Each term: (1/2)^n * 2^n = (1/2 * 2)^n = 1^n = 1
# Therefore E[X] = sum_{n=1}^inf 1 = infinity

# Verify numerically for n in [1..20] where floating-point is safe (2^20 = 1048576)
print("\n── SC1: Term verification (1/2)^n * 2^n for n = 1..20 ──")
ev_terms = [(0.5**n) * (2.0**n) for n in range(1, 21)]
all_terms_one = all(abs(t - 1.0) < 1e-10 for t in ev_terms)
print(f"First 5 terms: {ev_terms[:5]}")
print(f"All 20 terms equal 1.0: {all_terms_one}")
A1_result = compare(all_terms_one, "==", True,
                    label="SC1: Every term (1/2)^n * 2^n = 1.0 (verified n=1..20)")

# Spot-check with explain_calc for n=5:
print("\nSpot-check n=5:")
term_n5 = explain_calc("(0.5**5) * (2.0**5)", locals())

# Partial sums grow as N (cross-check, algebraic consequence):
print("\n── SC1 cross-check: Partial sums ──")
partial_sum_10 = sum(ev_terms[:10])   # sum of first 10 terms = 10
partial_sum_20 = sum(ev_terms[:20])   # sum of first 20 terms = 20

ps10 = explain_calc("partial_sum_10", locals())
ps20 = explain_calc("partial_sum_20", locals())
A2_result_10 = compare(abs(partial_sum_10 - 10.0), "<", 1e-9,
                       label="SC1 cross-check: 10-term partial sum = 10.0 (unbounded growth)")
A2_result_20 = compare(abs(partial_sum_20 - 20.0), "<", 1e-9,
                       label="SC1 cross-check: 20-term partial sum = 20.0 (N-term sum = N)")

# Check for convergence: if terms 11-20 still contribute ~10, the series doesn't converge
delta_10_to_20 = partial_sum_20 - partial_sum_10  # = 10.0 if each term = 1
# sc1_holds is True only if the series CONVERGES (terms 11-20 contribute < 0.001)
sc1_holds = compare(delta_10_to_20, "<", 0.001,
                    label="SC1: EV series converges? Terms 11-20 contribute <0.001? (False = diverges)")

# ── 6. SC2: Bernoulli Log Utility Gives Finite CE ─────────────────────────────
# Bernoulli (1738): a rational agent maximizes E[U(W)] where U(w) = ln(w).
# E[U] = E[ln(2^N)] = sum_{n=1}^inf (1/2)^n * ln(2^n)
#       = sum_{n=1}^inf (1/2)^n * n * ln(2)
#       = ln(2) * sum_{n=1}^inf n * (1/2)^n

# Primary: power series identity sum_{n=1}^inf n*x^n = x/(1-x)^2, at x = 1/2:
print("\n── SC2: Bernoulli expected utility ──")
x = 0.5
generating_fn = explain_calc("x / (1 - x)**2", locals())
# At x=0.5: (0.5)/(0.5)^2 = 0.5/0.25 = 2.0
A4_result = compare(abs(generating_fn - 2.0), "<", 1e-14,
                    label="SC2/A4: sum(n*(1/2)^n) = x/(1-x)^2 at x=0.5 = 2.0 (generating function)")

# Therefore E[U] = ln(2) * 2:
print("\nExpected utility computation:")
analytical_eu = explain_calc("math.log(2) * generating_fn", locals())
A3_result = compare(abs(analytical_eu - 2 * math.log(2)), "<", 1e-12,
                    label="SC2/A3: E[ln(2^N)] = ln(2) * 2 = 2*ln(2) ≈ 1.3863 (finite)")

# Certainty equivalent: w such that ln(w) = E[U] → w = exp(E[U])
print("\nCertainty equivalent:")
certainty_equivalent = explain_calc("math.exp(analytical_eu)", locals())
# CE = exp(2*ln(2)) = exp(ln(4)) = 4.0
A3_ce_result = compare(abs(certainty_equivalent - 4.0), "<", 1e-10,
                       label="SC2: Certainty equivalent = exp(2*ln(2)) = $4.00 (rational WTP, finite)")

# Cross-check: numerical convergence of partial sums to 2*ln(2)
print("\n── SC2 cross-check: numerical convergence ──")
eu_numerical = sum((0.5**n) * n * math.log(2) for n in range(1, 10001))
eu_diff = explain_calc("abs(eu_numerical - analytical_eu)", locals())
A3_converge = compare(eu_diff, "<", 1e-3,
                      label="SC2 cross-check: 10000-term numerical EU matches 2*ln(2) within 0.001")

sc2_holds = compare(certainty_equivalent, "<", 1e15,
                    label="SC2: Certainty equivalent is finite (< 1e15, i.e., a real finite dollar amount)")

# ── 7. ADVERSARIAL CHECKS (Rule 5) ────────────────────────────────────────────
adversarial_checks = [
    {
        "question": "Is there a mathematical framework where the standard St. Petersburg EV is finite?",
        "verification_performed": (
            "Searched 'St. Petersburg paradox finite expected value' and "
            "'St. Petersburg standard game EV convergent'. Found no credible source "
            "claiming the standard game (unlimited flips, payoff = 2^n) has finite EV. "
            "Bounded-payoff and finite-wealth-cap variants are different games."
        ),
        "finding": (
            "No peer-reviewed source claims standard St. Petersburg EV is finite. "
            "The divergence (EV = infinity) is mathematical consensus. "
            "Claim's premise 'finite expected value' is false for the standard game."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Could 'expected value' in the claim mean 'expected utility' or 'certainty equivalent'?",
        "verification_performed": (
            "Analyzed the claim language: 'finite expected value that a rational person "
            "should be willing to pay'. In standard probability/economics usage, "
            "'expected value' is a defined technical term = E[X] = sum p_i * x_i. "
            "Searched for alternative readings, found none in standard literature."
        ),
        "finding": (
            "Even under the most charitable reading — 'finite value that rational persons "
            "should pay' — the claim incorrectly calls it an 'expected value'. "
            "The correct term for the finite quantity is 'certainty equivalent' (= $4 under "
            "log utility) or 'expected utility' (= 2*ln(2)). The claim's terminology is wrong."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Does Menger's (1934) super-St.-Petersburg paradox undermine SC2?",
        "verification_performed": (
            "Searched 'Menger 1934 super St. Petersburg paradox log utility unbounded'. "
            "Found Menger showed that for any unbounded utility function U, a game with "
            "payoff exp(2^n) produces infinite E[U]. Log utility is not a general solution."
        ),
        "finding": (
            "Menger's result does NOT break SC2. SC2 only claims that the STANDARD "
            "St. Petersburg game (payoff = 2^n) has a finite certainty equivalent ($4) "
            "under log utility. This holds. Menger's game has a different payoff structure "
            "and is a separate paradox. SC2 is limited to the standard game."
        ),
        "breaks_proof": False,
    },
    {
        "question": "Is log utility the only framework giving finite willingness to pay for the standard game?",
        "verification_performed": (
            "Searched 'St. Petersburg paradox CRRA utility solution' and "
            "'risk aversion St. Petersburg finite certainty equivalent'. Found that any "
            "utility function with relative risk aversion coefficient gamma > 0 gives "
            "a finite CE for the standard game. Log utility (gamma=1) is Bernoulli's original."
        ),
        "finding": (
            "Log utility is not unique — any risk-averse utility (CRRA with gamma > 0) "
            "gives a finite CE for the standard game. This STRENGTHENS SC2: the conclusion "
            "(finite rational willingness to pay) is robust across multiple frameworks. "
            "Only the precise dollar amount ($4) is specific to Bernoulli's log utility "
            "with zero initial wealth."
        ),
        "breaks_proof": False,
    },
]

# ── 8. VERDICT AND STRUCTURED OUTPUT ──────────────────────────────────────────
if __name__ == "__main__":
    any_unverified = any(
        cr["status"] != "verified" for cr in citation_results.values()
    )

    # SC1 is the primary claim (finite expected value). It is false.
    # SC2 is true but uses a different framework (expected utility, not expected value).
    # Overall: DISPROVED because SC1 fails.
    # Compound claim (SC1 AND SC2): both must hold; since SC1 is false, compound is false.
    overall_claim_holds = compare(int(sc1_holds) + int(sc2_holds), "==", 2,
                                  label="Overall: compound claim holds only if SC1=True AND SC2=True")

    if not overall_claim_holds and not any_unverified:
        verdict = "DISPROVED"
    elif not overall_claim_holds and any_unverified:
        verdict = "DISPROVED (with unverified citations)"
    else:
        verdict = "PROVED"  # unreachable given sc1_holds = False

    FACT_REGISTRY["A1"]["method"] = "algebraic: (1/2)^n * 2^n = 1^n = 1 for all n >= 1"
    FACT_REGISTRY["A1"]["result"] = f"All terms = 1.0 (verified n=1..20); series = sum of infinity 1s"
    FACT_REGISTRY["A2"]["method"] = "partial sum: sum_{k=1}^{N} 1 = N (unbounded)"
    FACT_REGISTRY["A2"]["result"] = f"10-term sum={partial_sum_10:.1f}, 20-term sum={partial_sum_20:.1f} (grows as N)"
    FACT_REGISTRY["A3"]["method"] = "E[ln(2^N)] = ln(2) * sum(n*(1/2)^n) = ln(2) * 2 = 2*ln(2)"
    FACT_REGISTRY["A3"]["result"] = f"E[U] = {analytical_eu:.6f} = 2*ln(2); CE = exp(E[U]) = ${certainty_equivalent:.6f}"
    FACT_REGISTRY["A4"]["method"] = "generating function: sum(n*x^n) = x/(1-x)^2 at x=1/2"
    FACT_REGISTRY["A4"]["result"] = f"sum(n*(1/2)^n) = {generating_fn:.1f} (confirms = 2)"

    citation_detail = build_citation_detail(FACT_REGISTRY, citation_results, empirical_facts)

    summary = {
        "fact_registry": {fid: {k: v for k, v in info.items()} for fid, info in FACT_REGISTRY.items()},
        "claim_formal": CLAIM_FORMAL,
        "claim_natural": CLAIM_NATURAL,
        "citations": citation_detail,
        "cross_checks": [
            {
                "description": "SC1: partial sum check — N-term sum = N (confirms unbounded growth)",
                "values_compared": [str(partial_sum_10), "10.0", str(partial_sum_20), "20.0"],
                "agreement": abs(partial_sum_10 - 10.0) < 1e-9 and abs(partial_sum_20 - 20.0) < 1e-9,
            },
            {
                "description": "SC2: numerical convergence of 10000-term partial sum to analytical 2*ln(2)",
                "values_compared": [f"{eu_numerical:.8f}", f"{2*math.log(2):.8f}"],
                "agreement": abs(eu_numerical - 2 * math.log(2)) < 1e-3,
            },
        ],
        "adversarial_checks": adversarial_checks,
        "verdict": verdict,
        "key_results": {
            "sc1_ev_diverges": True,
            "sc1_ev_is_finite": sc1_holds,
            "sc1_description": "EV = sum(1, 1, 1, ...) = infinity",
            "sc2_expected_utility": round(analytical_eu, 6),
            "sc2_certainty_equivalent_dollars": round(certainty_equivalent, 6),
            "sc2_rational_wtp_is_finite": sc2_holds,
            "overall_claim_holds": overall_claim_holds,
            "note": (
                "SC1 is DISPROVED (EV is infinite). SC2 is PROVED ($4 rational WTP "
                "under Bernoulli log utility). The claim's framing is wrong: "
                "the resolution is via expected *utility*, not expected *value*."
            ),
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
