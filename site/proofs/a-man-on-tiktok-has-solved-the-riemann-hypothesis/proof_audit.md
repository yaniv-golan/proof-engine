# Audit: A man on TikTok has solved the Riemann Hypothesis after one week of work.

- **Generated:** 2026-04-07
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
| operator_note | The claim asserts the Riemann Hypothesis has been 'solved'. For this to be true, a correct proof must exist and have been accepted by the mathematical community. The Clay Mathematics Institute (CMI) administers a $1 million Millennium Prize for a correct solution; non-award of this prize is treated as authoritative evidence the hypothesis remains unsolved. The claim has three sub-claims: (SC1) the solver is a man on TikTok; (SC2) the work took ~1 week; (SC3) the solution is mathematically valid. SC3 is decisive — if SC3 is false, the whole claim is false regardless of SC1/SC2. This proof focuses on disproving SC3 via authoritative independent sources. Formalization scope: 'solved' is operationalized as 'accepted by the mathematical community,' which does not logically exclude the bare possibility of a valid proof that has not yet been recognized. However, the claim's public framing ('a man on TikTok') implies public knowledge and community awareness, making this operationalization appropriate for the claim as stated. |

*Source: proof.py JSON summary*

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_wikipedia_rh | Wikipedia: Riemann Hypothesis — 2026 survey confirms no proof is known |
| B2 | source_wikipedia_mpp | Wikipedia: Millennium Prize Problems — RH listed among six remaining unsolved problems |
| B3 | source_clay | Clay Mathematics Institute — official problem status: Unsolved |
| A1 | *(computed)* | Logical conclusion: if RH is unsolved per authoritative sources, no TikTok claim can constitute a valid solution |

*Source: proof.py JSON summary*

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Logical conclusion: RH unsolved per authoritative sources, TikTok claim invalid | compare(n_sources_confirming_unsolved, '<', 2) => rh_is_solved; compare(rh_is_solved, '==', True) | False — 3 of 3 sources confirm RH unsolved, so rh_is_solved=False. Claim requires True. |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Wikipedia: Riemann Hypothesis — 2026 survey confirms no proof is known | Wikipedia: Riemann Hypothesis | https://en.wikipedia.org/wiki/Riemann_hypothesis | "According to a 2026 survey, there is overwhelming numerical evidence for the hypothesis, but no proof is known." | verified | full_quote | Tier 3 (reference) |
| B2 | Wikipedia: Millennium Prize Problems — RH listed among six remaining unsolved problems | Wikipedia: Millennium Prize Problems | https://en.wikipedia.org/wiki/Millennium_Prize_Problems | "The other six Millennium Prize Problems remain unsolved, despite a large number of unsatisfactory proofs by both amateur and professional mathematicians." | verified | full_quote | Tier 3 (reference) |
| B3 | Clay Mathematics Institute — official problem status: Unsolved | Clay Mathematics Institute: Riemann Hypothesis (Millennium Prize) | https://www.claymath.org/millennium/riemann-hypothesis/ | "Unsolved" | verified | full_quote | Tier 2 (unknown) |

*Source: proof.py JSON summary*

---

## Citation Verification Details

**B1 — Wikipedia: Riemann Hypothesis**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: 100% (full quote match)
- Impact: Primary disproof source. Directly establishes that no proof of the Riemann Hypothesis is known as of a 2026 survey.

**B2 — Wikipedia: Millennium Prize Problems**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: 100% (full quote match)
- Impact: Independent confirmation. Separately confirms the RH is among the six remaining unsolved Millennium Prize Problems.

**B3 — Clay Mathematics Institute**
- Status: **verified**
- Method: full_quote
- Fetch mode: live
- Coverage: 100% (full quote match)
- Impact: Authoritative institutional confirmation. The Clay Mathematics Institute is the body that administers the $1 million Millennium Prize for the Riemann Hypothesis; its official designation of "Unsolved" is the most authoritative single signal available.

All three citations were fully verified. No "with unverified citations" qualifier applies.

**Source Credibility Assessment:**
- B1 (wikipedia.org): Tier 3 — established reference source
- B2 (wikipedia.org): Tier 3 — established reference source
- B3 (claymath.org): Tier 2 — unclassified domain. Note: The Clay Mathematics Institute is the authoritative body administering the Millennium Prize Problems; the Tier 2 classification reflects an unclassified domain in the credibility database, not a genuine concern about the source's authority.

*Source: proof.py JSON summary; credibility note is author analysis*

---

## Computation Traces

```
Verifying citations...
  [✓] source_wikipedia_rh: Full quote verified (source: tier 3/reference)
  [✓] source_wikipedia_mpp: Full quote verified (source: tier 3/reference)
  [✓] source_clay: Full quote verified (source: tier 2/unknown)
  Confirmed sources: 3 / 3
  n_sources_confirming_unsolved = 3
  compare(3, '<', 2) = False => rh_is_solved = False
  compare(rh_is_solved=False, '==', True) = False => claim_holds = False
  SC3: Riemann Hypothesis is validly solved: False == True = False
```

*Source: proof.py inline output (execution trace)*

---

## Independent Source Agreement (Rule 6)

| Cross-check | Values Compared | Agreement |
|-------------|-----------------|-----------|
| B1 (Wikipedia RH article), B2 (Wikipedia MPP article), and B3 (Clay Mathematics Institute) independently confirm the Riemann Hypothesis is unsolved as of 2026. | B1: verified, B2: verified, B3: verified | True |

**Independence rationale:** B1 is Wikipedia's article specifically about the Riemann Hypothesis (maintained by mathematicians and editors focused on number theory). B2 is Wikipedia's article about the Millennium Prize Problems as a collection (maintained by editors tracking prize status broadly). B3 is the Clay Mathematics Institute's official Millennium Prize page, maintained by the prize-administering body itself. These are three independently authored and maintained sources. All three confirming the RH is unsolved provides cross-source validation that none has stale or erroneous status information.

*Source: proof.py JSON summary; independence rationale is author analysis*

---

## Adversarial Checks (Rule 5)

**Check 1: Has any TikTok-based claimed solution been evaluated as credible by mathematicians?**
- Question: Has any TikTok-based claimed solution been evaluated as credible by mathematicians?
- Verification performed: Searched 'Riemann Hypothesis TikTok viral claim debunked mathematician response 2024 2025'. Found TikTok discovery pages showing many users claiming to solve RH. Found a video by @blitzphd explicitly debunking one such claim: 'Dude didn't solve the Riemann hypothesis'. Found no credible mathematical evaluation of any TikTok-originating claimed solution.
- Finding: No TikTok-based claimed solution has been verified or accepted by the mathematical community.
- Breaks proof: No

**Check 2: Could a valid proof have been very recently submitted and not yet reviewed by the Clay Institute or wider community?**
- Question: Could a valid proof have been very recently submitted and not yet reviewed by the Clay Institute or wider community?
- Verification performed: Searched 'Riemann Hypothesis solved 2025 2026 Clay Mathematics Institute status'. Found a 2026 status report stating: 'In 2026, after 167 years, the Riemann Hypothesis remains open.' No pending proof evaluation found.
- Finding: The mathematical community responds rapidly to claimed proofs of famous problems. The Clay Institute's 2026 Millennium Prize page still designates RH as 'Unsolved'. No lag in review could explain the complete absence of any accepted or actively-evaluated proof.
- Breaks proof: No

**Check 3: Has any Millennium Prize Problem ever been solved through social media or by an amateur working alone for one week?**
- Question: Has any Millennium Prize Problem ever been solved through social media or by an amateur working alone for one week?
- Verification performed: Reviewed history of solved Millennium Prize Problems. The only solved problem, the Poincare conjecture, was proved by Grigori Perelman over several years through peer-reviewed academic papers — not social media.
- Finding: No Millennium Prize Problem has ever been solved through social media or by informal one-week effort.
- Breaks proof: No

*Source: proof.py JSON summary*

---

## Hardening Checklist

| Rule | Status | Notes |
|------|--------|-------|
| Rule 1: Every empirical value parsed from quote text, not hand-typed | N/A — qualitative proof; no numeric values extracted from quotes | Disproof is based on citation verification status, not numeric extraction |
| Rule 2: Every citation URL fetched and quote checked | PASS | All 3 citations verified via live fetch (B1: full_quote, B2: full_quote, B3: full_quote) |
| Rule 3: System time used for date-dependent logic | N/A — no time-dependent computation | Proof generates date via `date.today()` for the generator block only |
| Rule 4: Claim interpretation explicit with operator rationale | PASS | CLAIM_FORMAL includes operator_note explaining sub-claims (SC1/SC2/SC3), decisive sub-claim identification, formalization scope, and operationalization rationale |
| Rule 5: Adversarial checks searched for independent counter-evidence | PASS | Three adversarial checks covering TikTok claim credibility, review lag possibility, and historical precedent |
| Rule 6: Cross-checks used independently sourced inputs | PASS | Three independently authored and maintained sources (two Wikipedia pages with separate editorial histories, plus Clay Mathematics Institute) all verified |
| Rule 7: Constants and formulas imported from computations.py, not hand-coded | PASS | `compare()` imported from `scripts/computations.py`; no hard-coded constants |

*Source: author analysis based on proof.py structure and execution results*

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v1.8.0 on 2026-04-07.*
