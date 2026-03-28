# Proof: UN Resolution 181 Allocated 56% of Mandatory Palestine to the Proposed Jewish State While Jews Were Less Than 33% of the Population

- Generated: 2026-03-27
- Verdict: **PROVED (with unverified citations)**
- Audit trail: [proof_audit.md](proof_audit.md) | [proof.py](proof.py)

---

## Key Findings

- **SC1 — Land allocation**: Resolution 181 allocated **56.47%** of Mandatory Palestine (15,264 km²) to the proposed Jewish state, meeting the claimed "56 percent" threshold (SC1 holds: 56.47 ≥ 56.0)
- **SC2 — Population**: Jewish population constituted **32.96%** of Mandatory Palestine's total population per 1946 British Mandate estimates, which is less than 33% (SC2 holds: 32.96 < 33.0)
- **Both sub-claims are independently supported by verified citations** (Wikipedia's Partition Plan article confirms both the 56.47% figure and the 608,225 / 1,845,559 population data)
- **Important caveat**: The claim refers to a "1947 British census" — no such census existed. The last formal British census of Palestine was 1931. The population figures used here are 1946 British Mandate estimates, which are the figures cited in all authoritative historical sources as the demographic context for Resolution 181.

---

## Claim Interpretation

**Natural-language claim**: "The UN Partition Plan Resolution 181 allocated 56 percent of Mandatory Palestine to the proposed Jewish state while Jews constituted less than 33 percent of the population according to the 1947 British census."

This is a compound claim (SC1 AND SC2):

**SC1 — Land allocation**: The percentage of Mandatory Palestine territory allocated to the proposed Jewish state under UN General Assembly Resolution 181 (November 29, 1947) was at least 56%. Interpreted as operator `>=` with threshold `56.0`. The actual figure (56.47%) rounds to 56%, making `>=` the correct operator. The claim would be FALSE only if the Jewish state received strictly less than 56% of total territory.

**SC2 — Population percentage**: The Jewish population of Mandatory Palestine constituted strictly less than 33% of the total population circa 1947. Interpreted as operator `<` with threshold `33.0`. TERMINOLOGY CAVEAT: The claim attributes this figure to a "1947 British census," but no census was conducted in 1947 — the last formal British census of Palestine was 1931. SC2 is evaluated using 1946 British Mandate estimates (608,225 Jews / 1,845,559 total = 32.96%), which are the figures used by UNSCOP and cited in all authoritative historical sources as the demographic context for Resolution 181.

*Source: author analysis*

---

## Evidence Summary

| ID | Fact | Verified |
|----|------|----------|
| B1 | Britannica: Jewish state = 15,264 km² (56.47%) under Resolution 181 | No (URL returned content without the exact quote — likely JavaScript-rendered or behind paywall) |
| B2 | Wikipedia (Partition Plan): Jewish state territory and percentage (independent source) | Yes |
| B3 | Wikipedia (Partition Plan): 1946 population total 1,845,559; Jewish 608,225 | Yes |
| B4 | Wikipedia (Demographic history of Palestine): 1946 Jewish population 608,225 | No (exact phrasing not found on live page) |
| A1 | SC1 — Jewish state land allocation percentage (from B1/B2) | Computed |
| A2 | SC2 — Jewish population percentage computed from raw counts (B3) | Computed |
| A3 | Cross-check: land percentage B1 vs B2 agreement | Computed |
| A4 | Cross-check: Jewish population count B3 vs B4 agreement | Computed |

*Source: proof.py JSON summary*

---

## Proof Logic

### SC1: Land Allocation

Resolution 181, adopted by the UN General Assembly on November 29, 1947, divided Mandatory Palestine into a proposed Jewish state, an Arab state, and an international zone (Jerusalem). Britannica states the Jewish state received 15,264 km², or 56.47% of the Mandate's territory (B1). Wikipedia's article on the Partition Plan independently confirms both figures — 15,264 km² and 56.47% — with data values verified directly on the live page (B2). The two sources agree exactly (cross-check: 56.47 vs 56.47, tolerance 0.01 — AGREE). Since 56.47 ≥ 56.0, **SC1 holds** (A1).

### SC2: Population Percentage

The 1946 British Mandate population estimates — the figures UNSCOP used in its August 1947 report and which all historical sources cite as the demographic context for Resolution 181 — record 608,225 Jews out of a total population of 1,845,559 (B3, verified on Wikipedia's Partition Plan article). Computing the Jewish percentage: 608,225 / 1,845,559 × 100 = **32.96%** (A2). Since 32.96 < 33.0, **SC2 holds**.

The Jewish population count of 608,225 is independently confirmed by Wikipedia's Demographic History of Palestine article (B4), though the exact quote phrasing was not found on the live page. The cross-check of raw counts confirms agreement (608,225 vs 608,225, tolerance 0 — AGREE, A4).

### Compound Result

Both sub-claims hold (2/2). The compound claim is **PROVED (with unverified citations)**.

*Source: author analysis*

---

## Counter-Evidence Search

**Does the 56% figure change if desert areas are excluded?** Alternative analyses distinguish "cultivated land" from total land area (Jewish-owned land was ~7% at the time, a separate figure). However, Resolution 181's territorial allocation refers to total land area including the Negev desert. All authoritative sources consistently cite 56.47% for the total territorial allocation. No credible source disputes this figure. *(Does not break proof)*

**Was Jewish population share at or above 33% by November 1947 due to post-WWII immigration?** Post-WWII Jewish immigration ("aliyah bet") brought significant numbers to Palestine in 1946-1947. UNSCOP used the 1946 estimates (32.96%) in its report preceding Resolution 181. Some 1947-specific estimates suggest ~630,000 Jews by late 1947, which with a total of ~1,900,000 would give ~33.2% — slightly above 33%. The claim's SC2 is therefore borderline: supported by the official figures used in the historical record, but conceivably not by some 1947-specific estimates. Most scholarly sources cite "approximately 31-33%" or "32%." *(Does not break proof, but borderline nature is acknowledged)*

**Does any authoritative source place Jewish population at ≥ 33%?** Most sources round 32.96% to "33%" or "approximately one-third." This rounding does not imply the figure was ≥ 33%; it reflects imprecision in summaries. No source credibly places Jews at significantly above 33% before November 1947. *(Does not break proof)*

**Was there actually a "1947 British census"?** No. The last formal British census of Palestine was 1931. The claim's attribution to a "1947 British census" is factually inaccurate. Population data for 1946-1947 are estimates derived from the 1931 census updated with immigration records and the Village Statistics 1945 survey. This inaccuracy does not invalidate the population percentage (32.96% < 33% is correct on the available data), but it should be noted. *(Does not break proof — the underlying number is correct even though the attribution is wrong)*

*Source: author analysis*

---

## Conclusion

**Verdict: PROVED (with unverified citations)**

Both sub-claims hold on verified data:
- **SC1**: Resolution 181 allocated **56.47%** of Mandatory Palestine to the proposed Jewish state — confirmed by Wikipedia (B2, verified) and independently by Britannica (B1, unverified)
- **SC2**: Jewish population constituted **32.96%** — strictly less than 33% — per 1946 British Mandate estimates confirmed by Wikipedia (B3, verified)

**Impact of unverified citations**: B1 (Britannica) and B4 (Wikipedia Demographic History) could not be verified by automated fetch. However, **neither conclusion depends solely on an unverified citation**:
- SC1 is independently established by B2 (Wikipedia Partition Plan, verified)
- SC2 is independently established by B3 (Wikipedia Partition Plan, verified)

The unverified citations (B1, B4) are corroborating rather than load-bearing.

**Factual correction**: The claim refers to a "1947 British census" which did not exist. The last formal British census of Palestine was 1931. The population figures cited are 1946 British Mandate estimates — the official data used by UNSCOP and all historical authorities in the context of Resolution 181.

All cited sources are Tier 3 (established reference). No Tier ≤ 2 sources were used.
