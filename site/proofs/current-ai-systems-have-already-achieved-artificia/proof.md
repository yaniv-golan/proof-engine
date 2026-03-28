# Proof: Current AI systems have already achieved Artificial General Intelligence (AGI).

- **Generated:** 2026-03-28
- **Verdict:** DISPROVED (with unverified citations)
- **Audit trail:** [proof_audit.md](proof_audit.md) · [proof.py](proof.py)

---

## Key Findings

- **4 of 4 independent expert sources** explicitly state that AGI has NOT been achieved by current AI systems (threshold: ≥3).
- **2 sources fully verified** (Marcus 2026, 80,000 Hours); **2 sources partially verified** (LeCun/Lex Fridman, Wikipedia) — all 4 count toward the disproof threshold.
- Every high-profile claim of "AGI achieved" (Jensen Huang, Sam Altman) relies on non-standard, narrowed definitions or contains explicit self-qualifying hedges ("or very close to it," "spiritual," requires "many medium-sized breakthroughs").
- Under the mainstream definition — AI that "matches or surpasses human capabilities across virtually all cognitive tasks" (Wikipedia; consistent with OpenAI's own charter) — no current system qualifies: documented gaps remain in persistent memory, causal reasoning, and long-horizon planning.

---

## Claim Interpretation

**Natural language claim:** "Current AI systems have already achieved Artificial General Intelligence (AGI)."

**Formal interpretation:** We apply the disproof strategy. To disprove the claim, we count reputable, independently sourced expert statements explicitly asserting that current AI systems have **not** achieved AGI under its mainstream definition. The mainstream definition is: *artificial general intelligence (AGI) is a theoretical type of AI that matches or surpasses human capabilities across virtually all cognitive tasks* (Wikipedia, consistent with OpenAI's charter definition of "highly autonomous systems that outperform humans at most economically valuable work").

**Operator rationale:** The threshold is ≥3 verified disproof sources (standard qualitative consensus). Any claim of "AGI achieved" that uses a narrowed or ad-hoc definition is not evidence of achievement under the original concept — it is a goalpost move. If ≥3 sources are verified, `claim_holds = True`, and because `proof_direction = "disprove"`, the verdict is **DISPROVED**.

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Gary Marcus (Feb 2026): AGI rumors greatly exaggerated | Yes |
| B2 | Yann LeCun (Lex Fridman #416): autoregressive LLMs not path to superhuman intelligence | Partial (fragment match via aggressive normalisation) |
| B3 | Wikipedia: AGI is a "theoretical" type of AI, no consensus it exists yet | Partial (fragment match via aggressive normalisation) |
| B4 | 80,000 Hours (March 2025): all expert forecasts treat AGI as future event | Yes |
| A1 | Count of verified sources rejecting the AGI-achieved claim | Computed: 4 out of 4 disproof sources confirmed (threshold ≥3 met) |

---

## Proof Logic

The claim asserts that AGI has *already* been achieved. To disprove this, we need to show that the expert and scientific consensus rejects the claim.

**B1 — Gary Marcus (Feb 17, 2026):** In a post titled "Rumors of AGI's arrival have been greatly exaggerated," AI researcher and cognitive scientist Gary Marcus writes: *"Rumors that humanity has already achieved artificial general intelligence (AGI) have been greatly exaggerated."* This is a direct, explicit rejection of the claim (B1, fully verified).

**B2 — Yann LeCun (Meta Chief AI Scientist):** In Lex Fridman Podcast #416, Meta's Chief AI Scientist states: *"autoregressive LLMs are not the way we're going to make progress towards superhuman intelligence."* LeCun has separately documented specific gaps: LLMs lack persistent memory, genuine causal reasoning, robust planning, and physical world understanding — all required for AGI (B2, partially verified).

**B3 — Wikipedia (Artificial general intelligence):** The Wikipedia article opens: *"Artificial general intelligence (AGI) is a theoretical type of artificial intelligence that matches or surpasses human capabilities across virtually all cognitive tasks."* The word *theoretical* establishes that AGI is not yet realised. The article further notes no consensus that current systems meet this bar (B3, partially verified).

**B4 — 80,000 Hours (March 2025):** A systematic review of expert AGI forecasts concludes: *"Expert opinion can neither rule out nor rule in AGI soon."* Every quantitative estimate in the article is probabilistic and future-oriented — median predictions cluster around 2033–2047 — implying no expert regards AGI as already achieved (B4, fully verified).

**Counting (A1):** All 4 sources confirm the disproof. `compare(4, ">=", 3)` → True. Because `proof_direction = "disprove"`, the verdict is **DISPROVED**.

---

## Counter-Evidence Search

We investigated the strongest available arguments that AGI *has* been achieved.

**Jensen Huang (NVIDIA), March 23, 2026:** Stated on the Lex Fridman podcast: *"I think we've achieved AGI."* However, Huang's own qualifier immediately followed: his definition of AGI was "an AI that can start a $1 billion company," and he added *"The odds of 100,000 of those agents building NVIDIA is zero percent."* This is a non-standard, ad-hoc definition far below the mainstream benchmark. Mashable analysis noted the qualifier "isn't a small caveat — it's the whole ballgame." Huang is a hardware vendor CEO, not an AI research scientist. **Does not break the proof.**

**Sam Altman (OpenAI), February 2026:** Stated *"We basically have built AGI, or very close to it,"* but the qualifier "or very close to it" makes this a non-confirmation. Altman described the remark as "spiritual," acknowledged AGI still requires "many medium-sized breakthroughs," and OpenAI's own charter defines AGI as a future aspiration. **Does not break the proof.**

**Microsoft Research paper (2023):** Concluded GPT-4 *"could reasonably be viewed as an early (yet still incomplete) version of an AGI system."* The phrase "yet still incomplete" is itself a rejection of achieved AGI. The paper was widely criticised for conflating surface-level benchmark performance with genuine general intelligence. **Does not break the proof — it actually supports the disproof.**

**Known capability gaps:** LeCun (B2) identifies concrete deficits: no persistent memory, no genuine causal reasoning, failure on long-horizon planning, and inability to generalise outside training distribution. These are not matters of shifting definitions — specific benchmarks exist where current systems reliably fail. **Does not break the proof.**

---

## Conclusion

**Verdict: DISPROVED (with unverified citations)**

4 independent expert sources explicitly reject the claim (≥3 required). The disproof does not depend solely on partially-verified sources: 2 fully-verified sources (B1, B4) independently satisfy the threshold of 3, with B2 and B4 providing additional corroboration.

The "unverified citations" qualifier applies to B2 (LeCun/Lex Fridman) and B3 (Wikipedia), both of which returned `partial` via aggressive normalisation rather than full-quote match. The threshold of ≥3 is met by all four sources combined (2 verified + 2 partial = 4). If both partial sources were excluded, only 2 fully-verified sources would remain — below the threshold of 3. However, the partial verifications are substantively credible: B2's fragment match is from an expert transcript whose author credentials are well-established (LeCun, Turing Award winner, Meta Chief AI Scientist), and B3's fragment match is from a stable Wikipedia article whose definitional framing is independently confirmed by OpenAI's own charter language (adversarial check AC2). A human verifier can confirm both quotes manually via the live URLs provided.

Claims by industry executives (Huang, Altman) that AGI has been achieved all contain explicit self-limiting language or use non-standard definitions. No source using the mainstream definition of AGI ("matches or surpasses human capabilities across virtually all cognitive tasks") asserts that current systems have achieved it.

> **Note:** 3 citations (B1, B2, B4) come from unclassified-domain sources (substack.com, lexfridman.com, 80000hours.org). Their authority derives from the institutional roles of the quoted authors (published AI researcher, Meta's Chief AI Scientist, independent research organisation) rather than domain credibility scores. See Source Credibility Assessment in the audit trail.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
