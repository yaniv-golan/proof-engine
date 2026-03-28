# Audit: Quantum entanglement enables the transmission of usable information faster than the speed of light when the distant parties pre-agree on a measurement basis.

- **Generated:** 2026-03-28
- **Reader summary:** [proof.md](proof.md)
- **Proof script:** [proof.py](proof.py)

## Claim Specification

| Field | Value |
|-------|-------|
| Subject | quantum entanglement with pre-agreed measurement basis |
| Property | number of independent authoritative sources confirming this is impossible |
| Operator | >= |
| Threshold | 3 |
| Proof direction | disprove |
| Operator note | This is a DISPROOF. The claim asserts entanglement enables FTL information transfer with a pre-agreed measurement basis. The no-communication theorem in quantum mechanics proves this is impossible: local measurement statistics are independent of the distant party's measurement choice, so no information can be encoded or decoded superluminally regardless of any pre-agreed protocol. We disprove the claim by finding >= 3 independent authoritative sources that confirm entanglement cannot transmit usable information FTL. The threshold of 3 reflects broad scientific consensus from independent institutions. |

*Source: proof.py JSON summary*

## Fact Registry

| ID | Key | Label |
|----|-----|-------|
| B1 | source_a | Wikipedia: No-communication theorem -- theorem statement |
| B2 | source_b | Caltech Science Exchange -- entanglement does not enable FTL communication |
| B3 | source_c | Wikipedia: Faster-than-light communication -- scientific consensus |
| B4 | source_d | QSNP (EU Quantum Flagship) -- debunking FTL entanglement myth |
| A1 | -- | Verified source count meeting disproof threshold |

*Source: proof.py JSON summary*

## Full Evidence Table

### Type A (Computed) Facts

| ID | Fact | Method | Result |
|----|------|--------|--------|
| A1 | Verified source count meeting disproof threshold | count(verified citations) = 4 | 4 |

*Source: proof.py JSON summary*

### Type B (Empirical) Facts

| ID | Fact | Source | URL | Quote | Status | Method | Credibility |
|----|------|--------|-----|-------|--------|--------|-------------|
| B1 | No-communication theorem statement | Wikipedia -- No-communication theorem | [link](https://en.wikipedia.org/wiki/No-communication_theorem) | "It asserts that during the measurement of an entangled quantum state, it is impossible for one observer to transmit information to another observer, regardless of their spatial separation." | verified | full_quote | Tier 3 (reference) |
| B2 | Entanglement does not enable FTL communication | Caltech Science Exchange | [link](https://scienceexchange.caltech.edu/topics/quantum-science-explained/entanglement) | "Experiments have shown that this is not true, nor can quantum physics be used to send faster-than-light communications." | verified | full_quote | Tier 4 (academic) |
| B3 | Scientific consensus on FTL communication | Wikipedia -- Faster-than-light communication | [link](https://en.wikipedia.org/wiki/Faster-than-light_communication) | "The current scientific consensus is that faster-than-light communication is not possible, and to date it has not been achieved in any experiment." | verified | full_quote | Tier 3 (reference) |
| B4 | Debunking FTL entanglement myth | QSNP (EU Quantum Flagship) | [link](https://qsnp.eu/debunking-quantum-myths-entanglement-allows-faster-than-light-communication/) | "The catch is that we are not actually sending any information." | verified | full_quote | Tier 2 (unknown) |

*Source: proof.py JSON summary*

## Citation Verification Details

**B1 — Wikipedia: No-communication theorem**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B2 — Caltech Science Exchange**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B3 — Wikipedia: Faster-than-light communication**
- Status: verified
- Method: full_quote
- Fetch mode: live

**B4 — QSNP (EU Quantum Flagship)**
- Status: verified
- Method: full_quote
- Fetch mode: live

*Source: proof.py JSON summary*

## Computation Traces

```
  Confirmed sources: 4 / 4
  verified source count vs disproof threshold: 4 >= 3 = True
```

*Source: proof.py inline output (execution trace)*

## Independent Source Agreement (Rule 6)

| Check | Sources Consulted | Sources Verified | Agreement |
|-------|-------------------|------------------|-----------|
| Multiple independent sources consulted | 4 | 4 | All verified |

**Sources:**
- source_a (Wikipedia No-communication theorem): verified
- source_b (Caltech Science Exchange): verified
- source_c (Wikipedia FTL communication): verified
- source_d (QSNP/EU Quantum Flagship): verified

**Independence note:** Sources are from 4 different institutions/publications: Wikipedia (community encyclopedia citing physics literature), Caltech (university research institution), Wikipedia FTL article (separate article with distinct references), and QSNP/EU Quantum Flagship (European research consortium). All trace to independent primary physics research and the mathematically proven no-communication theorem.

*Source: proof.py JSON summary*

## Adversarial Checks (Rule 5)

**Check 1: Peer-reviewed FTL demonstrations**
- Question: Is there any credible peer-reviewed physics paper demonstrating FTL information transfer via entanglement with pre-agreed measurement bases?
- Verification performed: Searched for: 'pre-agreed measurement basis entanglement superluminal signaling loophole scheme'. Reviewed results from arXiv, Physics Forums, Stanford Encyclopedia of Philosophy, and Wikipedia.
- Finding: No credible peer-reviewed source demonstrates FTL information transfer via entanglement. Proposed schemes (e.g., Gao Shan 2003) have been refuted. The no-communication theorem is mathematically proven under standard quantum mechanics. All search results confirm the impossibility.
- Breaks proof: No

**Check 2: Pre-agreed basis loopholes**
- Question: Does pre-agreeing on a measurement basis create any loophole in the no-communication theorem?
- Verification performed: Searched for: 'quantum entanglement FTL information transfer pre-agreed measurement basis impossibility'. Reviewed Physics Forums discussions and the arXiv paper 2001.08867.
- Finding: Pre-agreeing on a measurement basis does not create a loophole. The no-communication theorem proves that Bob's local measurement statistics are completely independent of Alice's measurement choice, regardless of any prior agreement. Each party sees random 50/50 outcomes locally; correlations only emerge when results are compared via a classical (light-speed-limited) channel.
- Breaks proof: No

**Check 3: Experimental demonstrations**
- Question: Has any experiment ever demonstrated superluminal information transfer using quantum entanglement?
- Verification performed: Searched for: 'quantum entanglement enables faster than light communication claim debunked physics'. Reviewed phys.org, Caltech, and QSNP articles.
- Finding: No experiment has ever demonstrated FTL information transfer. Wikipedia's Faster-than-light communication article states: 'The current scientific consensus is that faster-than-light communication is not possible, and to date it has not been achieved in any experiment.'
- Breaks proof: No

*Source: proof.py JSON summary*

## Source Credibility Assessment

| Fact ID | Domain | Type | Tier | Note |
|---------|--------|------|------|------|
| B1 | wikipedia.org | reference | 3 | Established reference source |
| B2 | caltech.edu | academic | 4 | Academic domain (.edu) |
| B3 | wikipedia.org | reference | 3 | Established reference source |
| B4 | qsnp.eu | unknown | 2 | Unclassified domain -- verify source authority manually |

Note: B4 (qsnp.eu) is tier 2 (unclassified). QSNP is the Quantum Secure Networks Partnership, part of the EU Quantum Flagship program -- a major European research consortium. The disproof does not depend solely on this source; 3 other sources from tier 3-4 institutions independently confirm the same conclusion.

*Source: proof.py JSON summary*

## Extraction Records

For this qualitative consensus proof, extractions record citation verification status per source rather than numeric values.

| Fact ID | Value (status) | Countable | Quote Snippet |
|---------|----------------|-----------|---------------|
| B1 | verified | Yes | "It asserts that during the measurement of an entangled quantum state, it is impo..." |
| B2 | verified | Yes | "Experiments have shown that this is not true, nor can quantum physics be used to..." |
| B3 | verified | Yes | "The current scientific consensus is that faster-than-light communication is not..." |
| B4 | verified | Yes | "The catch is that we are not actually sending any information." |

*Source: proof.py JSON summary*

## Hardening Checklist

- **Rule 1:** N/A -- qualitative consensus proof, no numeric value extraction
- **Rule 2:** Every citation URL fetched and quote checked via `verify_all_citations()`. All 4 quotes verified as full_quote match.
- **Rule 3:** N/A -- no date-dependent logic in this proof
- **Rule 4:** Claim interpretation explicit with operator rationale in `CLAIM_FORMAL["operator_note"]`. Disproof direction documented.
- **Rule 5:** 3 adversarial checks performed searching for sources supporting FTL communication via entanglement. No supporting evidence found.
- **Rule 6:** 4 independent sources from different institutions/publications consulted. All verified.
- **Rule 7:** N/A -- qualitative consensus proof, no constants or formulas
- **validate_proof.py result:** PASS with warnings (14/15 checks passed, 0 issues, 1 warning about else branch)

*Source: author analysis*

---
Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v0.10.0 on 2026-03-28.
