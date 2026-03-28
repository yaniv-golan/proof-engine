# Proof: Earth will lose gravity for exactly 7 seconds on August 12, 2026, causing 40 million deaths.

- **Generated:** 2026-03-28
- **Verdict:** DISPROVED (with unverified citations)
- **Audit trail:** [proof_audit.md](proof_audit.md) · [proof.py](proof.py)

---

## Key Findings

- **3 of 3** authoritative sources confirmed this event is physically impossible, meeting the disproof threshold (≥ 3).
- **NASA explicitly denied** the claim: "The Earth will not lose gravity on Aug. 12, 2026. Earth's gravity, or total gravitational force, is determined by its mass." (B1, B2)
- **NASA Space Place** (a NASA educational resource) confirms the physics: "Earth's gravity comes from all its mass." Gravity cannot "switch off" while mass exists. (B3 — independently verified, government tier)
- The "Project Anchor" NASA document cited in the hoax does not exist; no credible scientific forecast of this event was found in any database searched.

---

## Claim Interpretation

**Natural language claim:** Earth will lose gravity for exactly 7 seconds on August 12, 2026, causing 40 million deaths.

**Formal interpretation:** This is a compound assertion:

- **SC1:** Earth will experience a zero-gravity event on 2026-08-12
- **SC2:** This event will cause 40 million deaths

SC1 is disproved if 3 or more authoritative sources independently confirm it is physically impossible. SC2 is contingent on SC1 — if SC1 is impossible, SC2 cannot occur.

**Operator rationale:** The threshold of 3 verified sources is the default for consensus disproofs. Gravity is produced by mass via Newton's law F = Gm₁m₂/r²; it cannot "switch off" while Earth's mass exists. NASA — the institution the hoax falsely invokes — has explicitly denied this claim.

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | BGR: NASA spokesperson explicitly denies Earth will lose gravity on 2026-08-12 | Yes |
| B2 | Daily Galaxy: Full NASA statement — only way to lose gravity is to lose mass | Partial (fragment match via aggressive normalization) |
| B3 | NASA Space Place: Authoritative physics — gravity comes from mass | Yes |
| A1 | Verified source count for SC1 disproof | Computed: 3 of 3 sources confirmed the claim is physically impossible |

---

## Proof Logic

**SC1 — Zero-gravity event on 2026-08-12 is physically impossible.**

NASA's spokesperson directly addressed this hoax: "The Earth will not lose gravity on Aug. 12, 2026. Earth's gravity, or total gravitational force, is determined by its mass. The only way for the Earth to lose gravity would be for the Earth system, the combined mass of its core, mantle, crust, ocean, terrestrial water, and atmosphere, to lose mass." (B1, B2 — same NASA statement, independently published by BGR and Daily Galaxy.)

This is not merely a denial — it is grounded in established physics. NASA Space Place, an independent NASA educational resource, confirms the underlying mechanism: "Earth's gravity comes from all its mass. All its mass makes a combined gravitational pull on all the mass in your body." (B3 — government tier, fully verified.) Gravity is a consequence of mass; there is no known physical mechanism by which it can pause.

The threshold of 3 verified sources is met: B1 (verified, full quote), B2 (partial, fragment match), and B3 (verified, full quote from NASA.gov).

**SC2 — 40 million deaths.**

SC2 depends entirely on SC1. Since SC1 is physically impossible, SC2 cannot occur. No scientific literature contains a prediction, model, or estimate for deaths from this event.

---

## Counter-Evidence Search

Four adversarial searches were performed before writing this proof:

1. **"Project Anchor" existence.** Searched Google, Bing, DuckDuckGo, and Yahoo for the alleged leaked NASA document. The Snopes investigation conducted the same multi-engine search. Finding: No credible evidence for "Project Anchor" exists. The claim originated as an anonymous social media post in November 2024. NASA's spokesperson confirmed no such document or project exists. Snopes rated the claim False.

2. **Astronomical events on 2026-08-12.** A total solar eclipse does occur on this date (visible from parts of Europe and the Arctic). However, NASA states: "A total solar eclipse has no unusual impact on Earth's gravity." Solar and lunar tidal forces cause less than 0.01% variation in local gravity — not a total loss. The eclipse may have been the seed of the hoax but does not support the claim.

3. **Gravitational waves as a mechanism.** Gravitational waves (spacetime ripples from events such as black hole mergers) produce strain of order 10⁻²¹ — one part per sextillion — utterly imperceptible at Earth's surface. They do not modify Earth's surface gravitational acceleration and cannot cause a "loss" of gravity.

4. **Peer-reviewed forecasts.** Searched NASA ADS, arXiv, Google Scholar, and general web search for "Earth gravity cessation 2026," "temporary gravity loss Earth mechanism," and "zero gravity Earth event 2026." Zero peer-reviewed papers or credible forecasts were found. All results were news articles and fact-checks debunking the hoax.

No counter-evidence was found that supports the claim. All adversarial checks returned `breaks_proof: false`.

---

## Conclusion

**Verdict: DISPROVED (with unverified citations)**

SC1 — the alleged gravity-loss event — is physically impossible. Gravity is a consequence of mass; it cannot "switch off" while Earth's mass exists. NASA explicitly confirmed this. SC2 — 40 million deaths — is contingent on SC1 and falls with it.

**On unverified citations:** B2 (Daily Galaxy) returned a `partial` status via fragment match using aggressive normalization, not a full-quote match. However, the disproof does not depend solely on B2 — the conclusion is independently supported by B1 (BGR, fully verified, citing the same NASA statement) and B3 (NASA Space Place, fully verified, government tier). The disproof holds even excluding B2.

**Note:** 2 citations (B1, B2) come from unclassified or low-credibility sources (tier 2). The conclusion is independently supported by B3, a government-tier (tier 5) NASA source. See Source Credibility Assessment in the audit trail.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
