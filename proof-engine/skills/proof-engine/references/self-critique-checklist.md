# Self-Critique Checklist

Read this at **Step 7** before presenting results.

**Must-check** items are structural — if these fail, the proof is broken. **Verify** items are quality checks.

## Must-check (structural correctness)

- [ ] validate_proof.py passes
- [ ] proof.py includes FACT_REGISTRY with IDs for all facts
- [ ] proof.py `__main__` emits `=== PROOF SUMMARY (JSON) ===` block
- [ ] JSON summary contains required keys: fact_registry (with method/result for A-types), claim_formal, adversarial_checks, verdict, key_results
- [ ] JSON summary contains `generator` block with `name`, `version`, `repo`, `generated_at`
- [ ] For empirical proofs: JSON summary also contains citations (with normalized status/method/coverage_pct/credibility), extractions, cross_checks
- [ ] For pure-math proofs: omit citations and extractions keys entirely. Use [template-pure-math.md](template-pure-math.md).
- [ ] FACT_REGISTRY keys in JSON match IDs used in both report documents
- [ ] Every fact ID in proof.md appears in JSON summary fact_registry and proof_audit.md evidence table
- [ ] All three files are consistent with each other
- [ ] For empirical proofs: `verify_all_citations()` returns "verified" for all citations. If any return "partial" or "not_found", the quote is likely paraphrased — fetch the raw page and replace with verbatim text before proceeding

## Verify (quality and completeness)

- [ ] All `quote` fields are verbatim substrings of the source page, not paraphrases (spot-check: does the first word match? are parenthetical insertions preserved?)
- [ ] PDF citations include `snapshot` with extracted text for re-run reproducibility
- [ ] All 9 hardening rules checked in proof_audit.md hardening checklist
- [ ] proof.md has executive summary with key numbers directly under verdict
- [ ] proof.md verification statuses derivable from JSON summary `evidence[fact_id].verification.status` (not from message strings)
- [ ] proof.md conclusion addresses unverified/partially verified citations with impact analysis (if any)
- [ ] proof.md conclusion notes low-credibility sources if any cited source has tier ≤ 2
- [ ] proof_audit.md sections labeled with provenance (proof.py JSON summary / proof.py inline output / author analysis)
- [ ] proof_audit.md includes Computation Traces reproduced from inline output
- [ ] proof_audit.md presents "Partially verified" citations distinctly from "Verified"
- [ ] proof_audit.md includes Source Credibility Assessment table (for empirical proofs)
- [ ] proof.md and proof_audit.md end with generator footer line
- [ ] Each adversarial check that found counter-evidence and has `breaks_proof: False` includes an explicit rebuttal in `finding`. Reproducibility/null-result checks are exempt.
- [ ] If claim uses causal language ("causes," "leads to," "promotes," "damages," "prevents"): decomposed into association + causation sub-claims via compound template; verdict is PARTIALLY VERIFIED if only associational evidence found
- [ ] If `threshold < 3`: operator_note documents domain scarcity search, sources meet domain-appropriate quality bar, and no majority COI among threshold sources (COI check only applies when verified count meets threshold)
- [ ] For comparative/superlative claims: if the cited source flags overlapping uncertainty in the compared values, `uncertainty_override = True` is set and verdict is UNDETERMINED
- [ ] If proof has `empirical_facts`: COI assessed for all citation sources. `coi_flags` populated in `cross_checks` (empty list if no COI identified). For source-counting proofs: majority COI check applied before verdict, but only when verified count meets the sub-claim threshold.
- [ ] Formalization fidelity: CLAIM_FORMAL captures all elements of the natural-language claim, or operator_note documents what was narrowed/excluded/proxied
- [ ] **proof.py reads as finished textbook code, not as a reasoning transcript.** Open every helper and constructive-example function in proof.py. Do any comments contain: verification arithmetic ("5-3 = 2; P(...) = ..."), retracted false starts ("Hmm — this gives the same P", "let's redo"), reasoning words ("Wait", "Actually", "Mismatch", "Check:"), or working-through-the-math passages longer than ~3 lines? If yes, replace the comment with a one-paragraph docstring and at most one short comment for non-obvious WHY. Visible reasoning traces signal "demo," not "citation target." This applies especially to deductive-theorem proofs (`claim_type: "theorem"`), where the deductive argument is the verdict and the code is supporting infrastructure that should not look provisional. See [template-deductive-theorem.md](template-deductive-theorem.md) §"Code style for proof.py: textbook, not scratchwork" for bad/good examples.
