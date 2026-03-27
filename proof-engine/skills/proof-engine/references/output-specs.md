# Output Specifications

Read this at **Step 5** when writing proof.md and proof_audit.md.

## proof.md structure

The reader-facing report. A reader who never opens proof_audit.md should fully understand the verdict and its justification.

Title line: `# Proof: [claim text]`

Header block:
- Generated: [date]
- Verdict: [VERDICT]
- Audit trail: link to proof_audit.md and proof.py

Section "Key Findings": 3-4 bullet points with the decisive numbers that justify the verdict. This is the executive summary — a reader who stops here should understand the result. Source: JSON summary `verdict` and `key_results`.

Section "Claim Interpretation": CLAIM_FORMAL in prose. State the natural-language claim, the formal interpretation, the operator choice with rationale. Expand acronyms on first use (e.g., "greenhouse gases (GHGs)"). Source: JSON summary `claim_formal` and `claim_natural`.

Section "Evidence Summary": Table with columns ID, Fact, Verified. IDs and labels from JSON summary `fact_registry`.
- Type A facts: Verified = "Computed"
- Type B facts: Verified = "Yes", "No", or "Partial" with brief reason for No/Partial (e.g., "No (URL returned 403)"). Derive from JSON summary `citations[fact_id].status`.
- Each source is its own fact row — no aggregation

Section "Proof Logic": Narrative explanation of the reasoning chain. Every key number must reference its fact ID inline, e.g., "Human activities account for ~95.5% of observed warming (B1, B3)." When multiple facts establish the same claim, note the redundancy: "Israel was founded on May 14, 1948 (B1, B2 — independently sourced)." Sub-claims get their own sub-sections if the proof has multiple parts. Source: author analysis.

Section "Counter-Evidence Search": Results of adversarial checks — what counter-evidence was searched for and what was found. Use plain language, not "Rule 5". Source: JSON summary `adversarial_checks`.

Section "Conclusion": Restate verdict with the key numbers. Verdict-specific:
- PROVED/DISPROVED: If any citations are not fully verified, state which conclusions depend on them and whether those conclusions are independently supported by verified sources.
- PROVED (with unverified citations): Same as PROVED, but explicitly list the unverified citations and their impact.
- DISPROVED (with unverified citations): Same as DISPROVED, but explicitly list the unverified citations and note whether the disproof depends solely on verified sources.
- PARTIALLY VERIFIED: List which sub-claims were proved and which remain unverifiable, with reasons.
- UNDETERMINED: State what specific evidence would be needed to resolve the claim.
- If any cited source has credibility tier ≤ 2 (unclassified or flagged), add a note: "Note: [N] citation(s) come from unclassified or low-credibility sources. See Source Credibility Assessment in the audit trail."
Source: JSON summary `verdict`, `key_results`, `citations[].credibility`; impact analysis is author analysis.

## proof_audit.md structure

The verification-focused report. Contains everything a verifier needs to check the proof's machinery without running proof.py. For proofs with more than 10 citations, group evidence and citation details by sub-claim rather than listing all citations linearly.

Title line: `# Audit: [claim text]`

Header block:
- Generated: [date]
- Reader summary: link to proof.md
- Proof script: link to proof.py

Section "Claim Specification": CLAIM_FORMAL fields. Source: proof.py JSON summary `claim_formal`.

Section "Fact Registry": FACT_REGISTRY showing ID-to-key mapping. Source: proof.py JSON summary `fact_registry`.

Section "Full Evidence Table": Two sub-sections:

- "Type A (Computed) Facts" — table with columns: ID, Fact, Method, Result. All fields from JSON summary `fact_registry` entries where `method` and `result` are present. Source: proof.py JSON summary.
- "Type B (Empirical) Facts" — table with columns: ID, Fact, Source, URL, Quote, Status, Method, Credibility. One row per source. Source: proof.py JSON summary `citations` (which has normalized `status` and `method` fields — not free-form messages). The Credibility column shows "Tier N (type)" from `citations[fact_id].credibility`. For pure-math proofs, omit.

Section "Citation Verification Details": For each Type B citation, four fields — all from structured JSON fields, not parsed from prose:
- Status: verified / partial / not_found / fetch_failed. Source: JSON summary `citations[fact_id].status`.
- Method (only if verified or partial): full_quote / unicode_normalized / fragment / aggressive_normalization. Source: JSON summary `citations[fact_id].method` and `.coverage_pct`. Note: `coverage_pct` is null for full_quote and unicode_normalized methods — only populated for fragment matches. Partial (fragment match) is a degraded result — present it distinctly from full verification.
- Fetch mode: live / snapshot / wayback. Source: JSON summary `citations[fact_id].fetch_mode`. Indicates how the page was obtained.
- Impact (only if NOT verified): Which conclusions in proof.md depend on this citation, and whether they have independent support. Source: author analysis (label as such).
For pure-math proofs, omit this section.

Section "Computation Traces": The explain_calc() and compare() output from proof.py execution. Source: proof.py inline output (execution trace). Reproduce these lines verbatim — do not add annotations or labels that are not in the actual output. Use `compare(value, op, threshold, label="SC1: description")` to make traces self-documenting; the label appears in the printed output. For qualitative proofs without `explain_calc()` calls, the compare() output is the trace.

Section "Independent Source Agreement (Rule 6)": Cross-check details — which values were independently sourced, whether they agree, source-to-source comparisons. Source: proof.py JSON summary `cross_checks`. For pure-math proofs, omit.

Section "Adversarial Checks (Rule 5)": Full records with questions, searches performed, findings, and whether each breaks the proof. Source: proof.py JSON summary `adversarial_checks`.

Section "Source Credibility Assessment": Table with columns: Fact ID, Domain, Type, Tier, Note. Source: JSON summary `citations[fact_id].credibility`. If any source has tier ≤ 1 (flagged unreliable or satire), add a note explaining why it was cited and whether the claim depends solely on it. Tier scale: 5=government/intergovernmental, 4=academic/peer-reviewed, 3=major news or established reference, 2=unclassified, 1=flagged unreliable. For pure-math proofs, omit.

Section "Extraction Records": For each extracted value — fact ID, extracted value, whether value was found in quote. Source: JSON summary `extractions[fact_id]` (value, value_in_quote, quote_snippet). Plus: extraction method and normalization narrative. Source: author analysis (label as such). For pure-math proofs, omit.

For qualitative/consensus proofs (no numeric extraction), the `extractions` field records citation verification status per source instead of extracted values: `value` = verification status string, `value_in_quote` = whether the citation was countable (verified or partial), `quote_snippet` = first 80 chars of the quote.

Section "Hardening Checklist":
- Rule 1: Every empirical value parsed from quote text, not hand-typed
- Rule 2: Every citation URL fetched and quote checked
- Rule 3: System time used for date-dependent logic
- Rule 4: Claim interpretation explicit with operator rationale
- Rule 5: Adversarial checks searched for independent counter-evidence
- Rule 6: Cross-checks used independently sourced inputs
- Rule 7: Constants and formulas imported from computations.py, not hand-coded
- validate_proof.py result: [PASS/FAIL with details]

For pure-math proofs, mark Rules 1, 2, and 6 as "N/A — pure computation, no empirical facts."

## Consistency rules

- Every fact ID in proof.md must appear in the JSON summary's `fact_registry` and in proof_audit.md's evidence table
- Verification statuses in proof.md must be derivable from JSON summary `citations[].status` (normalized field, not parsed from message)
- The verdict and key numbers must be identical across proof.md, proof_audit.md, and the JSON summary
- All Type A facts in proof_audit.md must have method/result from JSON summary `fact_registry` entries
- All extraction records in proof_audit.md must have value/value_in_quote from JSON summary `extractions`
- Sections labeled "Source: proof.py JSON summary" or "Source: proof.py inline output" must be traceable to actual proof.py output
- Sections labeled "Source: author analysis" must be clearly marked as such in proof_audit.md

## Provenance labels

Use these exact formats as a trailing line in each section:

- `*Source: proof.py JSON summary*`
- `*Source: proof.py inline output (execution trace)*`
- `*Source: author analysis*`
