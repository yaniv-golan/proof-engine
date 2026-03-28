# Audit: AI-generated code has fewer security vulnerabilities than typical human-written code

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

---

## Claim Specification

| Field | Value |
|-------|-------|
| subject | AI-generated code |
| property | security vulnerability rate relative to typical human-written code |
| operator | `>=` (counting verified sources that reject the claim) |
| operator_note | The claim asserts AI code has FEWER vulnerabilities than human code. We disprove this using proof_direction='disprove': we collect at least 3 independent peer-reviewed studies whose findings REJECT the claim (showing AI code has MORE or EQUAL vulnerabilities). The operator '>=' counts verified sources against threshold=3. A source counts if its quote was found on the page (status verified or partial). 'Fewer' is interpreted strictly: the claim is false if credible independent research consistently finds AI code is not safer. We use the conservative threshold of 3 independent studies from different research groups and venues. |
| threshold | 3 |
| proof_direction | disprove |

---

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | pearce_2022 | Pearce et al. 2022 (IEEE S&P): Copilot generated ~40% vulnerable programs across 89 security-sensitive scenarios |
| B2 | perry_2023 | Perry et al. 2023 (ACM CCS): AI-assisted participants wrote significantly less secure code than unassisted participants |
| B3 | cotroneo_2025 | Cotroneo et al. 2025 (IEEE ISSRE): Large-scale study (500k+ samples) finds AI-generated code contains more high-risk security vulnerabilities than human code |
| A1 | _(computed)_ | Count of independently verified sources rejecting the claim |

---

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Count of independently verified sources rejecting the claim | count(verified citations) = 3 | 3 |

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | Pearce et al. 2022 (IEEE S&P): ~40% vulnerable | Pearce et al. 2022, 'Asleep at the Keyboard?', IEEE S&P 2022 | https://arxiv.org/abs/2108.09293 | "In total, we produce 89 different scenarios for Copilot to complete, producing 1,689 programs. Of these, we found approximately 40% to be vulnerable." | verified | full_quote | Tier 4 (academic) |
| B2 | Perry et al. 2023 (ACM CCS): significantly less secure | Perry et al. 2023, 'Do Users Write More Insecure Code with AI Assistants?', ACM CCS 2023 | https://arxiv.org/html/2211.03622v3 | "participants who had access to an AI assistant wrote significantly less secure code than those without access to an assistant" | verified | full_quote | Tier 4 (academic) |
| B3 | Cotroneo et al. 2025 (IEEE ISSRE): more high-risk vulnerabilities | Cotroneo et al. 2025, 'Human-Written vs. AI-Generated Code: A Large-Scale Study', IEEE ISSRE 2025 | https://arxiv.org/abs/2508.21634 | "AI-generated code also contains more high-risk security vulnerabilities" | verified | full_quote | Tier 4 (academic) |

---

## Citation Verification Details

### B1 — Pearce et al. 2022 (pearce_2022)

- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live
- **Coverage:** N/A (full-quote match, no fragment scoring)

### B2 — Perry et al. 2023 (perry_2023)

- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live
- **Coverage:** N/A (full-quote match, no fragment scoring)

### B3 — Cotroneo et al. 2025 (cotroneo_2025)

- **Status:** verified
- **Method:** full_quote
- **Fetch mode:** live
- **Coverage:** N/A (full-quote match, no fragment scoring)

---

## Computation Traces

```
  [✓] pearce_2022: Full quote verified for pearce_2022 (source: tier 4/academic)
  [✓] perry_2023: Full quote verified for perry_2023 (source: tier 4/academic)
  [✓] cotroneo_2025: Full quote verified for cotroneo_2025 (source: tier 4/academic)
  Confirmed sources: 3 / 3
  verified source count vs threshold: 3 >= 3 = True
```

---

## Independent Source Agreement (Rule 6)

| Description | Sources Consulted | Sources Verified | Agreement |
|-------------|-------------------|------------------|-----------|
| Three independent studies from different research groups and venues consulted, all finding AI code is NOT more secure than human code | 3 | 3 | All three independently confirm AI code has more vulnerabilities |

**Independence note:** Sources from three different research groups: (1) NYU — Pearce et al. 2022, IEEE S&P; (2) Stanford/UCSD/UIUC — Perry et al. 2023, ACM CCS; (3) University of Naples — Cotroneo et al. 2025, IEEE ISSRE. Different methodologies: security-targeted prompts (B1), user study with diverse tasks (B2), large-scale general sampling (B3). Time span 2022-2025 covers multiple generations of AI coding tools.

**Source status:** pearce_2022: verified | perry_2023: verified | cotroneo_2025: verified

---

## Adversarial Checks (Rule 5)

### Check 1

**Question:** Does any peer-reviewed study find AI-generated code has FEWER security vulnerabilities than human-written code, contradicting this disproof?

**Verification performed:** Searched 'AI generated code fewer security vulnerabilities than human peer-reviewed', 'Copilot code more secure than human developer', and reviewed Sandoval et al. 2023 (USENIX Security) 'Lost at C: A User Study on the Security Implications of LLM Code Assistants'. Sandoval et al. found that AI-assisted C programmers produced critical security bugs at a rate no greater than ~10% more than controls in a narrow low-level C pointer/array task. Some metrics showed the assisted group had fewer bugs.

**Finding:** Sandoval et al. 2023 found limited/neutral security impact in one narrow scenario (low-level C). This does NOT show AI code has categorically fewer vulnerabilities — it shows one specific task where the difference was small. No study was found claiming AI-generated code is generally more secure than human-written code across broad domains. The Sandoval finding does not break the disproof.

**Breaks proof:** No

---

### Check 2

**Question:** Do Perry et al. and Pearce et al. study different things (AI-assisted humans vs. pure AI-generated code), making the comparison inconsistent?

**Verification performed:** Reviewed the scope of all three sources. Pearce et al. generates code directly from GitHub Copilot (100% AI-generated). Cotroneo et al. generates code from ChatGPT, DeepSeek-Coder, and Qwen-Coder without human editing (100% AI-generated). Perry et al. studies human developers who USE an AI assistant — they write the final code but with AI suggestions. The claim uses the broad phrase 'AI-generated code', which in practice encompasses both scenarios.

**Finding:** Two of three sources (B1 Pearce, B3 Cotroneo) study purely AI-generated code. B2 Perry et al. studies AI-assisted coding — still directly relevant to the claim as stated, since developers widely use AI assistants to generate code. The mixed scope does not undermine the disproof: even in the broader AI-assisted interpretation of the claim, the evidence shows more vulnerabilities, not fewer.

**Breaks proof:** No

---

### Check 3

**Question:** Are Pearce et al.'s results biased by cherry-picked security-sensitive prompts not representative of typical code generation?

**Verification performed:** Reviewed methodology: Pearce et al. explicitly targeted CWE Top-25 vulnerability scenarios, which could inflate vulnerability rates. However, Cotroneo et al. 2025 used over 500,000 general-purpose Python and Java code samples — not adversarially selected for security sensitivity — and still found AI code had more high-risk security vulnerabilities. Searched for 'Copilot code representative sample security' to check for rebuttal papers; found none contradicting the general trend.

**Finding:** Pearce et al.'s focused-prompt methodology is a legitimate limitation for that study alone. However, Cotroneo et al.'s large-scale general study independently confirms the finding on 500k+ samples without security-focused prompting. The convergence of findings across different methodologies (targeted security prompts vs. general-purpose coding) strengthens the disproof.

**Breaks proof:** No

---

## Source Credibility Assessment

All three sources are hosted on arxiv.org (Tier 4, academic). The papers were published at the following peer-reviewed venues:
- B1: IEEE Symposium on Security and Privacy (IEEE S&P) 2022 — top-tier security venue
- B2: ACM Conference on Computer and Communications Security (CCS) 2023 — top-tier security venue
- B3: IEEE International Symposium on Software Reliability Engineering (ISSRE) 2025 — top-tier software engineering venue

No sources were from unclassified or low-credibility domains.

---

*Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.*
