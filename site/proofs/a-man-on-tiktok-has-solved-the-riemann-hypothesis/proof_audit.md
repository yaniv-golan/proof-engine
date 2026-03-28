# Audit: A man on TikTok has solved the Riemann Hypothesis after one week of work.

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| subject | Riemann Hypothesis — solved status |
| property | whether a valid proof has been accepted by the mathematical community |
| operator | == |
| threshold | True |
| claim_type | compound_empirical |
| operator_note | The claim asserts the Riemann Hypothesis has been 'solved'. For this to be true, a correct proof must exist and have been accepted by the mathematical community. The Clay Mathematics Institute (CMI) administers a $1 million Millennium Prize for a correct solution; non-award of this prize is treated as authoritative evidence the hypothesis remains unsolved. The claim has three sub-claims: (SC1) the solver is a man on TikTok; (SC2) the work took ~1 week; (SC3) the solution is mathematically valid. SC3 is decisive — if SC3 is false, the whole claim is false regardless of SC1/SC2. This proof focuses on disproving SC3 via authoritative independent sources. |

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_wikipedia_rh | Wikipedia: Riemann Hypothesis — 2026 survey confirms no proof is known |
| B2 | source_wikipedia_mpp | Wikipedia: Millennium Prize Problems — RH listed among six remaining unsolved problems |
| B3 | source_clay | Clay Mathematics Institute — official Millennium Prize page for Riemann Hypothesis |
| A1 | *(computed)* | Logical conclusion: if RH is unsolved per authoritative sources, no TikTok claim can constitute a valid solution |

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Logical conclusion: RH unsolved → TikTok claim invalid | compare(rh_is_solved, '==', True) | False — rh_is_solved=False, claim requires True. Two independent sources (B1, B2) confirm no proof is known. |

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Wikipedia: Riemann Hypothesis — 2026 survey confirms no proof is known | Wikipedia: Riemann Hypothesis | https://en.wikipedia.org/wiki/Riemann_hypothesis | "According to a 2026 survey, there is overwhelming numerical evidence for the hypothesis, but no proof is known." | verified | full_quote | Tier 3 (reference) |
| B2 | Wikipedia: Millennium Prize Problems — RH listed among six remaining unsolved problems | Wikipedia: Millennium Prize Problems | https://en.wikipedia.org/wiki/Millennium_Prize_Problems | "The other six Millennium Prize Problems remain unsolved, despite a large number of unsatisfactory proofs by both amateur and professional mathematicians." | verified | full_quote | Tier 3 (reference) |
| B3 | Clay Mathematics Institute — official Millennium Prize page for Riemann Hypothesis | Clay Mathematics Institute: Riemann Hypothesis (Millennium Prize) | https://www.claymath.org/millennium/riemann-hypothesis/ | "The Riemann hypothesis asserts that all the 'non-obvious' zeros of the zeta function are complex numbers with real part 1/2." | partial | aggressive_normalization | Tier 2 (unknown) |

---

## Citation Verification Details

**B1 — Wikipedia: Riemann Hypothesis**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: 100% (full quote match)

**B2 — Wikipedia: Millennium Prize Problems**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: 100% (full quote match)

**B3 — Clay Mathematics Institute**
- Status: **partial**
- Method: aggressive_normalization (fragment match, 6 words)
- Fetch mode: live
- Impact: B3 is not the primary disproof source. The disproof is independently established by B1 and B2 (both verified). B3's partial status is likely due to the Clay Institute page using Unicode curly quotes (ʻnon-obviousʼ) that differ from the authored straight quotes. The source authority of claymath.org as the prize-administering body is not in dispute.

**Source Credibility Assessment:**
- B1 (wikipedia.org): Tier 3 — established reference source
- B2 (wikipedia.org): Tier 3 — established reference source
- B3 (claymath.org): Tier 2 — unclassified domain. Note: The Clay Mathematics Institute is the authoritative body administering the Millennium Prize Problems; the Tier 2 classification reflects an unclassified domain in the credibility database, not a genuine concern about the source's authority.

---

## Computation Traces

```
SC3: Riemann Hypothesis is validly solved: False == True = False
```

*(from proof.py execution — verbatim output)*

---

## Independent Source Agreement (Rule 6)

| Cross-check | Values Compared | Agreement |
|-------------|-----------------|-----------|
| B1 (Wikipedia RH article) and B2 (Wikipedia MPP article) independently confirm the Riemann Hypothesis is unsolved as of 2026 — different pages, different editorial histories, same conclusion. | B1: verified, B2: verified | True |

**Independence rationale:** B1 is Wikipedia's article specifically about the Riemann Hypothesis (maintained by mathematicians and editors focused on number theory). B2 is Wikipedia's article about the Millennium Prize Problems as a collection (maintained by editors tracking prize status broadly). These are independently authored and edited pages. Both confirming the RH is unsolved provides cross-source validation that neither has a stale status.

---

## Adversarial Checks (Rule 5)

**Check 1: Has any TikTok-based claimed solution been evaluated as credible by mathematicians?**
- Question: Has any TikTok-based claimed solution been evaluated as credible by mathematicians?
- Verification performed: Searched 'Riemann Hypothesis TikTok viral claim debunked mathematician response 2024 2025'. Found TikTok discovery pages showing many users claiming to solve RH. Found a video by @blitzphd explicitly debunking one such claim: 'Dude didn't solve the Riemann hypothesis'. Found no credible mathematical evaluation of any TikTok-originating claimed solution.
- Finding: No TikTok-based claimed solution has been verified or accepted by the mathematical community. The pattern of amateur claimed proofs is consistent with Wikipedia's statement that 'a large number of unsatisfactory proofs by both amateur and professional mathematicians' have been submitted over the years.
- Breaks proof: No

**Check 2: Could a valid proof have been very recently submitted and not yet reviewed by the Clay Institute or wider community?**
- Question: Could a valid proof have been very recently submitted and not yet reviewed by the Clay Institute or wider community?
- Verification performed: Searched 'Riemann Hypothesis solved 2025 2026 Clay Mathematics Institute status'. Found a 2026 status report (mathlumen.com) stating: 'In 2026, after 167 years, the Riemann Hypothesis remains open.' Noted that high-profile claimed proofs (e.g., Michael Atiyah, 2018) are evaluated by the global mathematical community within days of submission. No pending proof evaluation found.
- Finding: The mathematical community responds rapidly to claimed proofs of famous problems. The Clay Institute's 2026 Millennium Prize page still lists RH as unsolved and the $1M prize is still available. No lag in review could explain the complete absence of any accepted or even actively-evaluated proof.
- Breaks proof: No

**Check 3: Has any Millennium Prize Problem ever been solved through social media or by an amateur working alone for one week?**
- Question: Has any Millennium Prize Problem ever been solved through social media or by an amateur working alone for one week?
- Verification performed: Reviewed history of solved Millennium Prize Problems. The only solved problem, the Poincare conjecture, was proved by Grigori Perelman over several years through peer-reviewed academic papers — not social media. Wikipedia MPP states the remaining six 'remain unsolved, despite a large number of unsatisfactory proofs by both amateur and professional mathematicians.'
- Finding: No Millennium Prize Problem has ever been solved through social media or by informal one-week effort. All serious claimed proofs have come through peer-reviewed academic channels. The claim's social-media origin and one-week timeframe are inconsistent with the depth of work the Riemann Hypothesis requires, though the decisive disproof is the Clay Institute's current 'unsolved' designation.
- Breaks proof: No

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
