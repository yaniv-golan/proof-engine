# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0] - 2026-03-26

### Added

- Source credibility assessment: new `scripts/source_credibility.py` module classifies citation URLs into 5 tiers (government, academic, major news, reference, unknown/unreliable) using bundled domain data — fully offline, no API keys
- Bundled credibility datasets in `scripts/data/`: government TLDs, academic publishers, major news orgs, established references, flagged unreliable/satire domains
- `credibility` field automatically included in `verify_citation()` and `verify_all_citations()` results
- Source Credibility Assessment section in proof_audit.md template
- Low-credibility source warnings in proof.md conclusion
- Self-critique checklist items for credibility assessment

### Fixed

- `verify_extraction()` boundary matching: numeric values use digit-boundary (`(?![\d])`) so "1913." (trailing period) matches; string/date values use simple substring match — fixes case-sensitivity and sentence-ending punctuation bugs reported in v0.4.0 field testing
- `verify_extraction()` date handling: `datetime.date` objects now match correctly against natural language dates ("December 23, 1913") in quotes
- CPI aggregator domains (rateinflation.com, inflationdata.com, measuringworth.com, etc.) elevated to tier 3 in credibility data — sites the skill recommends no longer flag as unclassified

### Changed

- Citation detail in JSON summary now includes `credibility` dict (domain, source_type, tier, flags, note)
- Type B Evidence Table in proof_audit.md adds Credibility column
- Example proofs updated to include credibility in citation details
- `compute_percentage_change()` gains `mode="decline"` parameter for purchasing power decline: `(1 - old/new) * 100`
- `verify_all_citations()` now runs credibility assessment automatically — `assess_all()` no longer needed in proof scripts
- Table-sourced numeric data pattern (`data_values` dict) documented in SKILL.md

## [0.4.0] - 2026-03-26

### Added

- Qualitative consensus proofs: `verify_extraction()` now works with keywords/phrases, not just numbers
- Compound claim support: `sub_claims` list with `conjunction` (AND/OR/BECAUSE/IMPLIES) in CLAIM_FORMAL
- Paywalled sources guidance in SKILL.md with .gov workarounds and snapshot-first workflow
- Pure-math proof template in hardening-rules.md (no citation/extraction boilerplate)
- `cross_check()` function in computations.py for tolerance-based value comparison across sources
- `compute_percentage_change()` function in computations.py
- `verify_extraction()` now handles `datetime.date` values with multiple format checks
- Guidance for citing structured/tabular data via `data_values` dict alongside quotes
- "Interpreting independent" guidance for government statistics and pure-math proofs (Rule 6)
- `verification_performed` field for adversarial checks (replaces `search_performed`, legacy accepted)
- "How This Differs From..." section in README: positions project vs theorem provers, probabilistic scorers, and RAG pipelines
- "Security Model" section in README: documents eval-free design, AST walking, and static analysis
- Entailment gap documented in SKILL.md Technical limitations
- Real proof examples in docs/examples/ (purchasing power decline, cortical plasticity)
- CI validation workflow (.github/workflows/validate.yml)
- 8 new eval cases (IDs 5–12): unit conversion disproof, compound AND claims, conflicting sources, multi-hop transitive chains, future prediction refusal, compound pure-math, percentage extraction, common misconception disproof

### Fixed

- Validator false positives on pure-math proofs: `_has_nonempty_empirical_facts()` distinguishes empty `empirical_facts = {}` from populated dicts
- Validator Rule 6 no longer warns about missing sources for pure-computation proofs
- Validator extraction check recognizes `parse_range_from_quote` and qualitative proofs using `verify_extraction()` without parse functions
- `explain_calc()` documented as unsuitable for list aggregations; descriptive `print()` recommended instead

### Changed

- SKILL.md workflow updated: Step 1 now covers compound claim decomposition, Step 2 covers pure-math cross-check planning
- Proof template structural requirements split into empirical vs pure-math variants
- `coverage_pct` documented as null for full_quote/unicode_normalized methods
- Eval suite expanded from 5 to 13 cases for broader coverage

## [0.3.0] - 2026-03-26

### Added

- Embedded page snapshots in `empirical_facts` for offline-reproducible proofs
- Hybrid verification fallback chain: live fetch → snapshot → Wayback Machine
- Wayback Machine fallback (opt-in via `wayback_fallback=True`)
- PDF citation verification via pdfplumber/PyPDF2 (optional dependencies)
- `fetch_mode` field in citation results: live / snapshot / wayback
- Eval 4: snapshot-mode proof (Tokyo population)
- Snapshot instructions for sandboxed environments (ChatGPT, cloud containers)

### Changed

- Proof template `__main__` reads structured dict fields directly — no message
  string parsing, no `import re` needed
- Citation verification details in proof_audit.md now include fetch_mode
- Environment Requirements section expanded with fallback chain documentation

## [0.2.0] - 2026-03-25

### Added

- Two-document report output: `proof.md` (reader-facing) + `proof_audit.md` (verification details)
- FACT_REGISTRY dict as single source of truth for cross-document fact IDs
- JSON summary block (`=== PROOF SUMMARY (JSON) ===`) with normalized structured fields
- `parse_range_from_quote()` for extracting ranges like "1.0°C to 2.0°C" from citations
- Provenance labels on audit doc sections (proof.py output vs author analysis)
- Empirical consensus proof guidance in template
- Eval 3: multi-source climate claim testing partial verification and cross-document consistency
- Claude Cowork support

### Fixed

- `explain_calc()` now preserves parentheses for lower-precedence sub-expressions
- `verify_extraction()` uses digit-boundary matching to prevent "1.1" matching inside "11.1"
- Rule 6 validator regex widened to match multi-word source keys (source_ipcc, source_noaa)
- Script path resolution: proofs use `PROOF_ENGINE_ROOT` instead of fragile `os.path` relative hack
- Marketplace `source` field compatible with Cowork remote API (named subdirectory, not root)
- `verify_citation()` returns "partial" for fragment-only matches instead of claiming full verification
- `verify_extraction()` raises ValueError by default instead of silently continuing
- `parse_number_from_quote()` raises ValueError (not IndexError) for missing capture groups
- Empty facts payload rejected by CLI instead of reporting "All citations verified"
- Citation normalization handles aggressive normalization and defaults to "Unknown method"

### Changed

- Plugin moved to `proof-engine/` subdirectory for Cowork marketplace compatibility
- Proof template split imports into structural (always needed) vs claim-specific (adapt per proof)
- `validate_proof.py` checks for FACT_REGISTRY, JSON summary block, and verify_extraction usage
- Report output changed from 1 file to 3 files (proof.py, proof.md, proof_audit.md)

## [0.1.0] - 2026-03-25

### Added

- Initial release
- 7 hardening rules that close specific LLM failure modes
- Bundled scripts: extract_values, smart_extract, verify_citations, computations, validate_proof
- Two-phase extraction for complex Unicode quotes
- 5-level verdict system (PROVED, PROVED with unverified citations, DISPROVED, PARTIALLY VERIFIED, UNDETERMINED)
- Cross-platform support: Claude Code, Cursor, Manus, Codex CLI
- Evaluation suite with test prompts
