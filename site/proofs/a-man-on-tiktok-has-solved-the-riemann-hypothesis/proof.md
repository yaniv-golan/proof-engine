# Proof: A man on TikTok has solved the Riemann Hypothesis after one week of work.

- **Generated:** 2026-04-07
- **Verdict:** DISPROVED
- **Audit trail:** [proof_audit.md](proof_audit.md) · [proof.py](proof.py)

---

## Key Findings

- The Riemann Hypothesis is still officially **unsolved** as of 2026, confirmed by three independently verified sources (B1, B2, B3).
- Wikipedia's Riemann Hypothesis article states: *"According to a 2026 survey, there is overwhelming numerical evidence for the hypothesis, but no proof is known."* (B1 — verified)
- Wikipedia's Millennium Prize Problems article confirms the RH is among *"six Millennium Prize Problems [that] remain unsolved."* (B2 — verified)
- The Clay Mathematics Institute designates the problem as *"Unsolved"* on its official Millennium Prize page (B3 — verified).

---

## Claim Interpretation

**Natural language:** A man on TikTok has solved the Riemann Hypothesis after one week of work.

**Formal interpretation:** The claim asserts the Riemann Hypothesis (RH) has been "solved" — meaning a mathematically valid proof exists and has been accepted by the community. The claim contains three sub-claims:

- **SC1:** The solver is a man on TikTok
- **SC2:** The work took approximately one week
- **SC3:** The solution is mathematically valid

**SC3 is decisive.** If SC3 is false, the whole claim is false regardless of SC1 or SC2. "Solved" means the proof has been accepted by the mathematical community. The Clay Mathematics Institute (CMI) administers a $1 million Millennium Prize for a correct solution; if this prize has not been awarded, the hypothesis is not solved. This proof focuses on disproving SC3.

**Formalization scope:** "Solved" is operationalized as "accepted by the mathematical community," which does not logically exclude the bare possibility of a valid proof that has not yet been recognized. However, the claim's public framing ("a man on TikTok") implies public knowledge and community awareness, making this operationalization appropriate for the claim as stated.

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Wikipedia: Riemann Hypothesis — 2026 survey confirms no proof is known | Yes |
| B2 | Wikipedia: Millennium Prize Problems — RH listed among six remaining unsolved problems | Yes |
| B3 | Clay Mathematics Institute — official problem status: Unsolved | Yes |
| A1 | Logical conclusion: if RH is unsolved per authoritative sources, no TikTok claim can constitute a valid solution | Computed: False — 3 of 3 sources confirm RH unsolved, so rh_is_solved=False. Claim requires True. |

---

## Proof Logic

The proof is a disproof by authoritative evidence. The decisive question is whether the Riemann Hypothesis has been validly solved (SC3).

The `rh_is_solved` value is **derived from citation verification results**, not hardcoded. Three sources are checked: if at least two are confirmed as verified, the evidence establishes the RH is unsolved. All three verified successfully, yielding `n_sources_confirming_unsolved = 3`.

1. **B1** — Wikipedia's dedicated Riemann Hypothesis article explicitly states that as of a 2026 survey, *"no proof is known."* Wikipedia articles on major mathematical problems are maintained by the mathematical community and reflect current consensus.

2. **B2** — Wikipedia's Millennium Prize Problems article independently confirms that the RH is among the *"six Millennium Prize Problems [that] remain unsolved."* This page separately tracks the status of all seven problems.

3. **B3** — The Clay Mathematics Institute's official Millennium Prize page designates the Riemann Hypothesis as *"Unsolved."* The CMI is the authoritative prize administrator.

**Logical chain:**
(1) SC3 requires the RH to be validly solved → (2) Three independent sources confirm no proof is known as of 2026 → (3) `compare(n_sources_confirming_unsolved=3, "<", 2)` → False → rh_is_solved=False → (4) `compare(rh_is_solved=False, "==", True)` → False → claim is False.

---

## Counter-Evidence Search

Three adversarial checks were performed before writing this proof:

**1. Has any TikTok-based claimed solution been found credible by mathematicians?**
Searched for TikTok-originating Riemann Hypothesis claims and expert responses. Found many TikTok videos claiming to solve the RH. Found a video by @blitzphd explicitly debunking one such claim. No credible mathematical evaluation of any TikTok-based claimed solution was found.

**2. Could a valid proof have been submitted too recently for community review?**
A 2026 status report confirms the Riemann Hypothesis remains open. The mathematical community evaluates high-profile claimed proofs within days (e.g., Michael Atiyah's 2018 claimed proof was widely analyzed within 48 hours). No lag in the review process could explain a complete absence of any confirmed proof.

**3. Has any Millennium Prize Problem ever been solved via social media or in one week?**
The only solved Millennium problem (Poincare conjecture) took Grigori Perelman years of peer-reviewed work. No Millennium Prize Problem has ever been solved through social media.

None of these checks produce counter-evidence that breaks the disproof.

---

## Conclusion

**Verdict: DISPROVED**

Three independently verified authoritative sources (B1, B2, B3) establish that the Riemann Hypothesis remains unsolved as of 2026, with no accepted proof in existence. The claim that a man on TikTok "has solved" it — implying a valid, accepted mathematical proof — is therefore false.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.8.0 on 2026-04-07.*
