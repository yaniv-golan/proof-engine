# Proof: A man on TikTok has solved the Riemann Hypothesis after one week of work.

- **Generated:** 2026-03-28
- **Verdict:** DISPROVED (with unverified citations)
- **Audit trail:** [proof_audit.md](proof_audit.md) · [proof.py](proof.py)

---

## Key Findings

- The Riemann Hypothesis is still officially **unsolved** as of 2026, confirmed by two independently verified sources (B1, B2).
- Wikipedia's Riemann Hypothesis article states: *"According to a 2026 survey, there is overwhelming numerical evidence for the hypothesis, but no proof is known."* (B1 — verified)
- Wikipedia's Millennium Prize Problems article confirms the RH is among *"six Millennium Prize Problems [that] remain unsolved, despite a large number of unsatisfactory proofs by both amateur and professional mathematicians."* (B2 — verified)
- The Clay Mathematics Institute has not awarded its $1 million prize for a solution — the authoritative signal that no accepted proof exists.

---

## Claim Interpretation

**Natural language:** A man on TikTok has solved the Riemann Hypothesis after one week of work.

**Formal interpretation:** The claim asserts the Riemann Hypothesis (RH) has been "solved" — meaning a mathematically valid proof exists and has been accepted by the community. The claim contains three sub-claims:

- **SC1:** The solver is a man on TikTok
- **SC2:** The work took approximately one week
- **SC3:** The solution is mathematically valid

**SC3 is decisive.** If SC3 is false, the whole claim is false regardless of SC1 or SC2. "Solved" means the proof has been accepted by the mathematical community. The Clay Mathematics Institute (CMI) administers a $1 million Millennium Prize for a correct solution; if this prize has not been awarded, the hypothesis is not solved. This proof focuses on disproving SC3.

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Wikipedia: Riemann Hypothesis — 2026 survey confirms no proof is known | Yes |
| B2 | Wikipedia: Millennium Prize Problems — RH listed among six remaining unsolved problems | Yes |
| B3 | Clay Mathematics Institute — official Millennium Prize page for Riemann Hypothesis | Partial (aggressive normalization; claymath.org unclassified by credibility system — verify manually) |
| A1 | Logical conclusion: if RH is unsolved per authoritative sources, no TikTok claim can constitute a valid solution | Computed: False — rh_is_solved=False, claim requires True. Two independent sources (B1, B2) confirm no proof is known. |

> Note: 1 citation (B3) comes from an unclassified-domain source (claymath.org). See Source Credibility Assessment in the audit trail. The disproof does not depend on B3 — it is independently established by B1 and B2.

---

## Proof Logic

The proof is a disproof by authoritative evidence. The decisive question is whether the Riemann Hypothesis has been validly solved (SC3).

Two independent, verified sources establish that it has not:

1. **B1** — Wikipedia's dedicated Riemann Hypothesis article explicitly states that as of a 2026 survey, *"no proof is known."* Wikipedia articles on major mathematical problems are maintained by the mathematical community and reflect current consensus.

2. **B2** — Wikipedia's Millennium Prize Problems article independently confirms that the RH is among the *"six Millennium Prize Problems [that] remain unsolved."* This page separately tracks the status of all seven problems and explicitly distinguishes the one solved problem (Poincaré conjecture) from the six still unsolved.

These two sources have separate editorial histories on different pages and cannot both be wrong simultaneously about such a high-profile result.

**The Clay Institute connection (B3):** The CMI administers the $1 million prize. Its Millennium Prize page still lists the RH as a prize problem, confirmed via live fetch (partial match). If anyone — on TikTok or anywhere — had solved the RH, the prize process would have been triggered, generating extensive public record.

**Logical chain:**
(1) SC3 requires the RH to be validly solved → (2) Two independent sources confirm no proof is known as of 2026 → (3) SC3 = False → (4) The compound claim is False.

`compare(rh_is_solved=False, "==", True)` → **False**

---

## Counter-Evidence Search

Three adversarial checks were performed before writing this proof:

**1. Has any TikTok-based claimed solution been found credible by mathematicians?**
Searched for TikTok-originating Riemann Hypothesis claims and expert responses. Found many TikTok videos with titles claiming to solve the RH — consistent with the endemic pattern of amateur claimed proofs. Found a video by @blitzphd explicitly debunking one such claim: *"Dude didn't solve the Riemann hypothesis."* No credible mathematical evaluation of any TikTok-based claimed solution was found.

**2. Could a valid proof have been submitted too recently for community review?**
A 2026 status report (mathlumen.com) confirms *"In 2026, after 167 years, the Riemann Hypothesis remains open."* The mathematical community evaluates high-profile claimed proofs within days (e.g., Michael Atiyah's 2018 claimed proof was widely analyzed within 48 hours). No lag in the review process could explain a complete absence of any confirmed proof.

**3. Has any Millennium Prize Problem ever been solved via social media or in one week?**
The only solved Millennium problem (Poincaré conjecture) took Grigori Perelman years of peer-reviewed work. Wikipedia notes the remaining six problems resist "a large number of unsatisfactory proofs by both amateur and professional mathematicians." No Millennium Prize Problem has ever been solved through social media.

None of these checks produce counter-evidence that breaks the disproof.

---

## Conclusion

**Verdict: DISPROVED (with unverified citations)**

Two independently verified authoritative sources (B1, B2) establish that the Riemann Hypothesis remains unsolved as of 2026, with no accepted proof in existence. The claim that a man on TikTok "has solved" it — implying a valid, accepted mathematical proof — is therefore false.

The unverified citation (B3, Clay Institute) is from the official prize-administering body and was fetched live (partial match due to unicode normalization). The disproof is independently established by B1 and B2 alone and does not depend on B3.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
