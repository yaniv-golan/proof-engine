# Output Specifications

Read this at **Step 5** when writing proof.md and proof_audit.md.

## Table of Contents

- [proof.md structure](#proofmd-structure)
- [proof_audit.md structure](#proof_auditmd-structure)
- [proof.json structure](#proofjson-structure)
- [proof_narrative.md structure](#proof_narrativemd-structure)
  - [Verdict](#verdict)
  - [What Was Claimed?](#what-was-claimed)
  - [What Did We Find?](#what-did-we-find)
  - [What Should You Keep In Mind?](#what-should-you-keep-in-mind)
  - [How Was This Verified?](#how-was-this-verified)
- [Consistency rules](#consistency-rules)
- [Provenance labels](#provenance-labels)
- [Machine-readable outputs](#machine-readable-outputs)

---

## proof.md structure

Section requirements are defined in `proof_format_schema.json` (single source of truth).
The skill produces format_version: 3 proofs via ProofSummaryBuilder. The section headings
below correspond to the v2 profile in the schema.

The reader-facing report. A reader who never opens proof_audit.md should fully understand the verdict and its justification.

Title line: `# Proof: [claim text]`

Header block:
- Generated: [date]
- Verdict: [VERDICT]
- Audit trail: link to proof_audit.md and proof.py

Section "Evidence Summary": Table with columns ID, Fact, Verified. IDs and labels from JSON summary `fact_registry`. Multi-source sub-entries (`{fact_id}_source_{N}`) inherit their label from the parent `fact_registry` entry, appending the source index.
- Type A facts: Verified = "Computed: [human-readable result]". The result should be meaningful to a non-technical reader — e.g., "Computed: 96.85%" or "Computed: True (all sub-claims hold)" or "Computed: 2 independent sources confirmed". Avoid bare numbers without context (not "Computed: 2" — say what 2 means).
- Type B facts: Verified = "Yes", "No", or "Partial" with brief reason for No/Partial (e.g., "No (URL returned 403)"). Derive from JSON summary `evidence[fact_id].verification.status` (v3). For multi-source facts, sub-entries are keyed `{fact_id}_source_{N}` — render one row per sub-entry.
- Note: "Verified: Yes" means the quote was found on the source page (citation presence). It does not mean the quote entails the claim's conclusion. If author reasoning connects a verified quote to the claim, the Proof Logic section must make this inference explicit.
- Type S facts (search): Verified = "Accessible (0 results)" for null accessible searches, "Known (blocked)" for known status, "Unreachable" for unreachable, "Reviewed: [brief note]" for result_count > 0. Note: "Accessible" means the search URL responded, not that the result count was machine-verified. Derive from JSON summary `evidence[S{n}].verification.status` (v3); the legacy `search_registry[key].verification.status` path was the v2 layout.
- Each source is its own fact row — no aggregation

Section "Proof Logic": Narrative explanation of the reasoning chain. Every key number must reference its fact ID inline, e.g., "Human activities account for ~95.5% of observed warming (B1, B3)." When multiple facts establish the same claim, note the redundancy: "Israel was founded on May 14, 1948 (B1, B2 — independently sourced)." Sub-claims get their own sub-sections if the proof has multiple parts. Source: author analysis.

Section "What could challenge this verdict?": Results of adversarial checks — what counter-evidence was searched for and what was found. Use plain language, not "Rule 5". Source: JSON summary `adversarial_checks`.

Section "Conclusion": Restate verdict with the key numbers. Verdict-specific:
- PROVED/DISPROVED: If any citations are not fully verified, state which conclusions depend on them and whether those conclusions are independently supported by verified sources.
- PROVED (with unverified citations): Same as PROVED, but explicitly list the unverified citations and their impact.
- DISPROVED (with unverified citations): Same as DISPROVED, but explicitly list the unverified citations and note whether the disproof depends solely on verified sources.
- PARTIALLY VERIFIED: List which sub-claims met threshold and which did not — state whether each failing SC lacked evidence or was contradicted, with reasons.
- UNDETERMINED: State what specific evidence would be needed to resolve the claim.
- SUPPORTED: State that the absence threshold was met (N databases searched, 0 results), list any non-accessible databases, and note that the result is reproducible via search URLs but not machine-verified. Emphasize that future research could change this verdict.
- SUPPORTED (with unverified citations): Same as SUPPORTED, but also list unverified corroborating citations and their impact.
- If any cited source has credibility tier ≤ 2 (unclassified or flagged), add a note immediately after the evidence table in the `Evidence Summary` section: "Note: [N] citation(s) come from unclassified or low-credibility sources. See Source Credibility Assessment in the audit trail." Do not place this note in the Conclusion section — it belongs adjacent to the table it annotates.
Source: JSON summary `verdict`, `key_results`, and credibility under each entry in `evidence` where `type=="empirical"` (`.verification.credibility`); impact analysis is author analysis.

Section "Generator": Footer line at the end of the document:
`---`
`Generated by [proof-engine](https://github.com/yaniv-golan/proof-engine) v[version] on [date].`
Source: JSON summary `generator`.

## proof_audit.md structure

The verification-focused report. Contains everything a verifier needs to check the proof's machinery without running proof.py. For proofs with more than 10 citations, group evidence and citation details by sub-claim rather than listing all citations linearly.

Title line: `# Audit: [claim text]`

Header block:
- Generated: [date]
- Reader summary: link to proof.md
- Proof script: link to proof.py

Section "Claim Interpretation": Formal claim specification in prose. State the natural-language claim, the formal interpretation, the operator choice with rationale. Expand acronyms on first use (e.g., "greenhouse gases (GHGs)"). Include a "Formalization scope" note stating which aspects of the natural-language claim are narrowed, excluded, or operationalized by proxy in the formal interpretation (e.g., "The natural-language claim refers to 'valid scientific practice'; the formal interpretation operationalizes this as 'endorsed by ≥3 independent authorities,' which does not capture methodological validity per se."). If the formalization is a faithful 1:1 mapping, state that explicitly. Source: JSON summary `claim_formal` and `claim_natural`.

Section "Claim Specification": Formal claim specification in readable table rows. Source: proof.py JSON summary `claim_formal`.

Section "Fact Registry": FACT_REGISTRY showing ID-to-key mapping. Source: proof.py JSON summary `fact_registry`. For Type A (computed) entries that have no `key` field, write `—` in the Key column.

Section "Full Evidence Table": Two sub-sections:

- "Type A (Computed) Facts" — table with columns: ID, Fact, Method, Result. All fields from JSON summary `fact_registry` entries where `method` and `result` are present. Source: proof.py JSON summary.
- "Type B (Empirical) Facts" — table with columns: ID, Fact, Source, URL, Quote, Status, Method, Credibility. One row per source. Source: proof.py JSON summary `evidence` (v3) where `type=="empirical"`; each entry has normalized `verification.status` and `verification.method` fields — not free-form messages. The Credibility column shows the plain-language type only (e.g., Government, Academic, Major news, Advocacy organization, Unclassified) from `evidence[fact_id].verification.credibility`. For pure-math proofs, omit. Multi-source facts produce `{fact_id}_source_{N}` keys; render each as its own row.
  For the `Quote` column: truncate to the first ~100 characters to keep the table readable, and replace any embedded double-quote characters (`"`) with single quotes or the HTML entities `&ldquo;`/`&rdquo;` (U+201C / U+201D) to avoid breaking Markdown table cell parsing.
- "Type S (Search) Facts" — table with columns: ID, Database, Search URL, Query Terms, Date Range, Result Count, Status, Credibility. One row per search. Source: JSON summary `fact_registry` (S-type entries) cross-referenced with `search_registry`. For absence proofs only; omit for other proof types.

Section "Citation Verification Details": For each Type B citation, four fields — all from structured JSON fields, not parsed from prose:
- Status: verified / partial / not_found / fetch_failed. Source: JSON summary `evidence[fact_id].verification.status`.
- Method (only if verified or partial): full_quote / unicode_normalized / fragment / aggressive_normalization. Source: JSON summary `evidence[fact_id].verification.method` and `.coverage_pct`. Note: `coverage_pct` is null for full_quote and unicode_normalized methods — only populated for fragment matches. Partial (fragment match) is a degraded result — present it distinctly from full verification.
- Fetch mode: live / snapshot / wayback. Source: JSON summary `evidence[fact_id].verification.fetch_mode`. Indicates how the page was obtained.
For multi-source facts, citation detail entries are keyed `{fact_id}_source_{N}` instead of `{fact_id}`. The same fields apply to each sub-entry.
- Rejection statement (disproof proofs only): The `rejection_statement` value from `proof.py` for this citation. Source: proof.py `empirical_facts[key].rejection_statement`. If absent, note that `validate_proof.py` warns.
- Verbatim status: Whether the quote is verbatim (`verbatim` field from `proof.py`, default: true). Source: proof.py `empirical_facts[key].verbatim`. If `verbatim: False`, note that evidentiary weight is reduced. If absent, quote is assumed verbatim.
- Time sensitivity (time-dependent proofs only): Whether the proof declared `is_time_sensitive: True` in `CLAIM_FORMAL` and whether `date.today()` is present. Source: proof.py `CLAIM_FORMAL.is_time_sensitive` + `date.today()` call site.
- Impact (only if NOT verified): Which conclusions in proof.md depend on this citation, and whether they have independent support. Source: author analysis (label as such).
For pure-math proofs, omit this section.

Section "Computation Traces": The explain_calc() and compare() output from proof.py execution. Source: proof.py inline output (execution trace). Reproduce these lines verbatim — do not add annotations or labels that are not in the actual output. Use `compare(value, op, threshold, label="SC1: description")` to make traces self-documenting; the label appears in the printed output. For qualitative proofs without `explain_calc()` calls, the compare() output is the trace.

Section "Independent Source Agreement (Rule 6)": Cross-check details — which values were independently sourced, whether they agree, source-to-source comparisons. Source: proof.py JSON summary `cross_checks`. For pure-math proofs, omit.

If any cross-check sources have a conflict of interest with the claim's subject, the `coi_flags` field documents each COI with type, relationship, direction, and severity. The audit doc's Rule 6 section must list identified COIs and assess whether a majority of threshold sources share COI on the same side. If the proof has `empirical_facts` and no `cross_checks` entry contains a `coi_flags` key, this is a gap — the self-critique checklist requires explicit COI assessment (even if the result is an empty list).

Section "Adversarial Checks (Rule 5)": Full records with questions, searches performed, findings, and whether each breaks the proof. Source: proof.py JSON summary `adversarial_checks`.

Section "Source Credibility Assessment": Table with columns: Fact ID, Domain, Type, Note. Source: JSON summary `evidence[fact_id].verification.credibility`. Use plain-language type only (Government, Academic, Major news, Advocacy organization, Unclassified). For multi-source facts, use `evidence[{fact_id}_source_{N}].verification.credibility` for each sub-source. If any source is flagged unreliable or satire, add a note explaining why it was cited and whether the claim depends solely on it. For pure-math proofs, omit.

Section "Source Data": For each extracted value — fact ID, extracted value, whether value was found in quote. Source: JSON summary `extractions[fact_id]` (value, value_in_quote, quote_snippet). Plus: extraction method and normalization narrative. Source: author analysis (label as such). For pure-math proofs, omit.

For qualitative/consensus proofs (no numeric extraction), the `extractions` field records citation verification status per source instead of extracted values: `value` = verification status string, `value_in_quote` = whether the citation was verified or partial, `quote_snippet` = first 80 chars of the quote.

Section "Quality Checks":
- Rule 1: Every empirical value parsed from quote text, not hand-typed
- Rule 2: Every citation URL fetched and quote checked
- Rule 3: System time used for date-dependent logic
- Rule 4: Claim interpretation explicit with operator rationale
- Rule 5: Adversarial checks searched for independent counter-evidence
- Rule 6: Cross-checks used independently sourced inputs
- Rule 7: Constants and formulas imported from computations.py, not hand-coded
- validate_proof.py result: [PASS/FAIL with details — reflect the **final** state of proof.py at the time of audit writing, not intermediate iteration history. Copy the validator's actual summary line verbatim as printed (e.g., "PASS — N/N checks, 0 warnings" — use whatever the script printed, not a hardcoded number). If earlier runs had corrected issues, omit that history; the clean final run is the authoritative result.]

For pure-math proofs, mark Rules 1, 2, and 6 as "N/A — pure computation, no empirical facts."

Section "Generator": Same footer as proof.md.

## proof.json structure

The machine-readable summary produced by proof.py. All four markdown documents derive their data from this file.

`ProofSummaryBuilder.emit(write_json_path=...)` writes `proof.json` as a file artifact AND prints the JSON to stdout (preceded by the marker line `=== PROOF SUMMARY (JSON) ===` — the marker INTRODUCES the JSON block, it does not close it). Templates pass an inline path computed from `__file__` so the file lands next to `proof.py` regardless of the caller's CWD. Both consumers — direct file read and stdout capture — receive identical content.

### v2 format (format_version: 2)

Required top-level fields:
- `format_version`: integer — set automatically by `ProofSummaryBuilder` (value: 3)
- `fact_registry`: dict of fact ID to FactRegistryEntry
- `claim_formal`: ClaimFormal dict
- `claim_natural`: string
- `verdict`: one of the VERDICT_TAXONOMY keys (string)
- `key_results`: dict of result key to value
- `generator`: Generator block with `name`, `version`, `repo`, `generated_at`

Optional top-level fields (v2):
- `citations`: dict of fact ID to CitationResult (verification status, method, url, quote, credibility)
- `extractions`: dict of fact ID to ExtractionInfo (extracted values and quote snippets)

### v3 format (format_version: 3)

v3 replaces the separate `fact_registry`, `citations`, and `extractions` maps with a single unified `evidence` map, and replaces the string `verdict` with a structured dict.

Required top-level fields:
- `format_version`: integer, must be `3`
- `evidence`: dict of fact ID to EvidenceEntry (replaces `fact_registry` + `citations` + `extractions`)
- `claim_formal`: ClaimFormal dict
- `claim_natural`: string
- `verdict`: structured dict `{value, qualified, qualifier, reason}` (replaces string verdict)
  - `value`: base verdict string, one of the VERDICT_TAXONOMY keys
  - `qualified`: boolean, true if a qualifier applies
  - `qualifier`: string or null — currently only `"unverified_citations"`
  - `reason`: optional string with additional explanation
- `key_results`: dict of result key to value
- `generator`: Generator block with `name`, `version`, `repo`, `generated_at`

EvidenceEntry structure (keyed by fact ID, e.g. `"B1"`, `"A1"`, `"S1"`):
- `type`: `"empirical"`, `"computed"`, or `"search"`
- `label`: human-readable description of the fact
- `sub_claim`: optional sub-claim tag (e.g. `"SC1"`)
- For `type: "empirical"`:
  - `source`: `{name, url, quote}` — the cited source and verbatim quote
  - `verification`: `{status, method, coverage_pct, fetch_mode, credibility}` — citation verification result
  - `extraction`: `{value, value_in_quote, quote_snippet}` — extracted value info
- For `type: "computed"`:
  - `method`: computation method description
  - `result`: human-readable result string
  - `depends_on`: list of fact IDs this computation depends on
- For `type: "search"`:
  - `search`: SearchRegistryEntry with query, url, result_count, verification

After loader normalization (tools/lib/loader.py), `proof_data` is always v3-shaped regardless of the source format version. Consumers should read from `evidence` and the structured `verdict` dict.

## proof_narrative.md structure

The plain-language narrative. Written AFTER proof.py, proof.md, proof_audit.md, and proof.json are complete. This is a **presentation** of the proof you already built — do not re-derive or reinterpret findings.

**Structure (all sections required):**

```
# Proof Narrative: <claim_natural>

## Verdict

**Verdict: <exact verdict from proof.json>**

<1-2 sentence hook — verdict-adapted tone>

## What Was Claimed?

<Plain-language restatement. Why someone might care. Do NOT copy CLAIM_FORMAL.>

## What Did We Find?

<3-6 paragraphs. Walk through evidence as a story, not a table.>
<Verdict-adapted: PROVED/DISPROVED = linear strongest-first; SUPPORTED = evidence then gaps;
PARTIALLY VERIFIED = what held then what didn't; UNDETERMINED = what was tried and why insufficient.>

## What Should You Keep In Mind?

<Mandatory caveats. Edge cases, what evidence doesn't address, what surprised, limitations.>

## How Was This Verified?

<2-3 sentences. Name the process. Include these links:>
[the structured proof report](proof.md)
[the full verification audit](proof_audit.md)
[re-run the proof yourself](proof.py)
```

**Constraints:**
- 200-800 words total
- No fact IDs (A1, B1, S1, etc.)
- No jargon — accessible to a general audience
- No tables — prose only
- No CLAIM_FORMAL reproduction
- Purpose-based language with explicit markdown links for formal outputs
- Verdict declaration must use the EXACT full verdict string from proof.json (including qualifiers like "with unverified citations")

## Consistency rules

- Every fact ID in proof.md must appear in the JSON summary's `fact_registry` and in proof_audit.md's evidence table. Exception: multi-source citations produce `{fact_id}_source_{N}` sub-entries in `evidence` and the evidence table that derive from the parent `fact_registry` entry. These sub-IDs do not appear in `fact_registry` itself.
- Every `S{N}` fact ID in proof.md must have a corresponding entry in `search_registry` via `fact_registry[S{N}].key`
- Verification statuses in proof.md must be derivable from JSON summary `evidence[fact_id].verification.status` (normalized field, not parsed from message)
- The verdict and key numbers must be identical across proof.md, proof_audit.md, and the JSON summary
- All Type A facts in proof_audit.md must have method/result from JSON summary `fact_registry` entries
- All extraction records in proof_audit.md must have value/value_in_quote from JSON summary `extractions`
- Sections labeled "Source: proof.py JSON summary" or "Source: proof.py inline output" must be traceable to actual proof.py output
- Sections labeled "Source: author analysis" must be clearly marked as such in proof_audit.md
- The `generator` block must appear in the JSON summary with `name`, `version`, `repo`, and `generated_at` fields

## Provenance labels

Use these exact formats as a trailing line in each section:

- `*Source: proof.py JSON summary*`
- `*Source: proof.py inline output (execution trace)*`
- `*Source: author analysis*

## Machine-readable outputs

These files are generated per proof during `python tools/build-site.py` (or per validation run for SARIF) and are not produced by `proof.py`. Proof authors do not need to create them — they are build-time outputs.

### provenance.json — W3C PROV-JSON

Generated by `tools/lib/prov.py`. Served at `proofs/<slug>/provenance.json`.

A W3C PROV-JSON provenance chain. Key records:
- **Entities**: `pe:claim` (the natural-language claim), `pe:evidence-{fact_id}` (one per evidence item), `pe:verdict`
- **Activities**: `pe:verify-{fact_id}` (CitationVerification, for empirical facts with a verification status), `pe:determine-verdict` (VerdictDetermination, uses all evidence entities)
- **Derivations** (`wasDerivedFrom`): computed facts (A-type) link back to the empirical facts (`depends_on`) they were computed from
- **Agent**: `pe:proof-engine` (SoftwareAgent with `schema:version` and `schema:url`)
- When a DOI is minted, `pe:doi` is set on the verdict entity

Consumers: included in the RO-Crate manifest. W3C PROV tooling can render the provenance graph.

### proof.ipynb — Jupyter Notebook

Generated by `tools/lib/notebook.py`. Served at `proofs/<slug>/proof.ipynb`.

Cell structure:
1. **Markdown intro** — title, verdict, date, link to canonical proof page, run instructions.
2. **Code cells** — `proof.py` split into sections using section-marker comments (`# ---\n# N. Section Name\n# ---` or `# N. Section Name`). Each section gets an optional markdown heading cell followed by a code cell. If `proof.py` has no section markers, a single code cell is emitted.
3. **Markdown footer** — link back to the full proof page.

No `pip install` cell is generated — users must have dependencies available. Compatible with JupyterLab, VS Code, and Google Colab.

Included in the RO-Crate manifest as `@type: ComputationalNotebook`.

### ro-crate-metadata.json — RO-Crate 1.1

Generated by `tools/lib/ro_crate.py`. Served at `proofs/<slug>/ro-crate-metadata.json`.

A standards-compliant research object manifest (`@context: https://w3id.org/ro/crate/1.1/context`). The root dataset links to the canonical URL, DOI (when minted), and concept DOI. Each proof artifact is listed as a `hasPart` entry with `@type`, `name`, `description`, and `encodingFormat`. File types and their roles:

| File | `@type` | Role |
|------|---------|------|
| `proof.py` | `SoftwareSourceCode` | Re-runnable verification script |
| `proof.json` | `Dataset` | Machine-readable proof data |
| `proof.md` | `ScholarlyArticle` | Structured proof report |
| `proof_audit.md` | `ScholarlyArticle` | Verification audit trail |
| `proof_narrative.md` | `Article` | Plain-language narrative |
| `provenance.json` | `CreativeWork` | W3C PROV provenance chain |
| `proof.ipynb` | `ComputationalNotebook` | Interactive re-verification notebook |

Only files present in the output directory are included (checked at build time).

### Schema.org JSON-LD (in-page)

Generated by `tools/lib/json_ld.py`. Injected into the `<head>` of each proof page as `<script type="application/ld+json">`. Not a separate downloadable file.

Top-level type is `ClaimReview`. Fields:
- `claimReviewed`: the natural-language claim text
- `reviewRating`: numeric rating 1–5 (`alternateName` = raw verdict string)
- `author`: Organization "Proof Engine" with repo URL
- `datePublished`: proof generation date
- `url`: canonical proof page URL
- `isBasedOn`: `proof.py` URL (SoftwareSourceCode) — the re-runnable verification script
- `mainEntity`: `proof.json` URL (Dataset) — the machine-readable proof data
- `about`: `provenance.json` URL (CreativeWork) — the W3C PROV chain
- `identifier`: raw DOI string (e.g., `"10.5281/zenodo.999"`) — only when DOI minted
- `sameAs`: list of `https://doi.org/` URLs for DOI and concept DOI — only when DOI minted

Discoverable by search engines and Linked Data clients from the page HTML. No action required by proof authors.

### SARIF 2.1.0 (validate_proof.py)

Generated by `tools/lib/sarif.py`. Not a site artifact — produced locally or in CI when `validate_proof.py` is invoked with `--format sarif`.

Usage:
```bash
python proof-engine/skills/proof-engine/scripts/validate_proof.py --format sarif proof.py
# Redirect stdout to file for GitHub Code Scanning or local inspection:
python proof-engine/skills/proof-engine/scripts/validate_proof.py --format sarif proof.py > proof.sarif
```

Each hardening rule maps to a stable rule ID:

| Rule | SARIF ID | Name |
|------|----------|------|
| Rule 1 | PE001 | NoHandTypedValues |
| Rule 2 | PE002 | CitationVerification |
| Rule 3 | PE003 | SystemTime |
| Rule 4 | PE004 | ClaimInterpretation |
| Rule 5 | PE005 | AdversarialCheck |
| Rule 6 | PE006 | IndependentCrosscheck |
| Rule 7 | PE007 | NoHardcodedConstants |
| FACT_REGISTRY | PE008 | FactRegistry |
| Contract | PE009 | EmitProofSummary |
| Verdict | PE010 | ValidVerdict |

Issues are `error` level; warnings are `warning` level. Compatible with GitHub Code Scanning (upload via `github/codeql-action/upload-sarif`), VS Code SARIF Viewer, and other SARIF-aware tooling.`
