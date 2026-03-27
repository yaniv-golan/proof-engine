# Changelog

All notable changes to this project will be documented in this file.

## [0.7.0] - 2026-03-27

### Added

- `references/proof-templates.md` — dedicated file with 3 complete templates: date/age, numeric/table data, and pure-math. The numeric/table template is first-class (not commented-out PATH B) and uses `verify_data_values()`, `compute_percentage_change(mode="decline")`, and `cross_check()` throughout.
- `cross_check()` mode heuristic in Gotchas: use `absolute` for computed results, `relative` for source-to-source comparisons
- .gov 403 note in Step 2 pointing to environment-and-sources.md
- JS-rendered site guidance expanded: static data ≠ static page metadata

### Changed

- Split `hardening-rules.md` from 714 lines to 339 lines (rules only) + `proof-templates.md` (templates and adaptation notes). Both are now under the 10k token read limit.
- Reference Files Index updated with proof-templates.md entry
- Step 3 now points to both hardening-rules.md (rules) and proof-templates.md (templates)

## [0.6.1] - 2026-03-27

### Added

- `verify_data_values(url, data_values, fact_id)` — fetches the source page and confirms each data_value string appears in the page text. Closes the verification gap where table-sourced numeric values were never checked against the live page.
- Step 1 now suggests checking worked examples for similar claims
- Adversarial checks documentation clarified: use past tense in `verification_performed` to signal these are Step 2 research results, not runtime operations

### Changed

- data_values workflow: `verify_data_values()` replaces blind trust in LLM-extracted table data
- Template in hardening-rules.md PATH B now shows `verify_data_values()` call before parsing

## [0.6.0] - 2026-03-27

### Changed

- **SKILL.md restructured for progressive disclosure** — reduced from 4,638 to 1,374 words (70% reduction)
- Detailed output specs moved to `references/output-specs.md` (read at Step 5)
- Advanced patterns (Two-Phase Extraction, Table-Sourced Data) moved to `references/advanced-patterns.md`
- Environment details, paywalled sources moved to `references/environment-and-sources.md`
- Self-critique checklist moved to `references/self-critique-checklist.md` (read at Step 6)
- Gotchas section promoted to top of SKILL.md (highest-signal content per Anthropic best practices)
- New Reference Files Index section with "read when" triggers for progressive loading
- Frontmatter: added `compatibility` and `license` fields, trimmed description to `[What] + [When] + [Capabilities]` format

### Fixed

- `bump-version.sh` sed pattern now matches unquoted YAML version field in SKILL.md (was silently failing since v0.3.0)
- SKILL.md version field synced to actual version (was stuck at 1.0.0)

## [0.5.4] - 2026-03-27

### Added

- Key function signatures section in SKILL.md: `cross_check()`, `compute_percentage_change()`, `explain_calc()`, `build_citation_detail()` with parameter names, modes, and return types
- Dynamic/JS-rendered site guidance in Gotchas: prefer static-content aggregators, expect partial matches on JS sites
- `cross_check()` example call with full signature in hardening-rules.md data_values section

### Fixed

- hardening-rules.md reading guidance: note file is large, start from template (search "Proof Template")
- data_values CPI example marked as worked example to prevent LLMs from copying stale values
- `explain_calc()` documented as returning the computed value (not just printing)

## [0.5.3] - 2026-03-27

### Added

- `build_citation_detail()` helper in verify_citations.py — replaces ~15 lines of boilerplate in every proof's `__main__` block
- Claude Code environment notes in SKILL.md: live fetch is primary path, WebFetch returns summaries (not raw text), keep web research in main thread
- Index base mismatch guidance in Gotchas: how to diagnose and handle different CPI base periods across sources
- `explain_calc()` vs `compute_*()` usage guidance: use named functions when they exist, explain_calc for ad-hoc expressions

### Fixed

- `validate_proof.py` extraction check: mixed-pattern proofs (both `verify_extraction()` and `data_values`) now get accurate message instead of claiming all extractions were "verified via verify_extraction()"
- Proof template in hardening-rules.md uses `build_citation_detail()` instead of inline loop
- Step 2 / adversarial checks clarified: adversarial research happens once in Step 2, proof code encodes results (not a second round)
- Government statistics guidance: aggregators promoted as preferred path over snapshot workflow

### Changed

- Self-critique checklist split into **Must-check** (structural — proof is broken if these fail) and **Verify** (quality/completeness) tiers
- Platform-specific environment notes replace generic "sandboxed environments (ChatGPT, cloud containers)" text

## [0.5.2] - 2026-03-26

### Fixed

- `validate_proof.py` extraction check: correctly recognizes `data_values` path (parse without `verify_extraction()`) instead of false-positive "verified via verify_extraction()"
- `parse_number_from_quote()` trace output now preserves original string precision: shows `Parsed '9.900' -> 9.9 (source text: '9.900')` when float repr differs
- Proof template in hardening-rules.md now shows both extraction paths: PATH A (free-text + verify_extraction) and PATH B (data_values + cross-check, no verify_extraction)

## [0.5.1] - 2026-03-26

### Fixed

- `verify_extraction()` trailing-zero float mismatch: 9.9 now matches "9.900" in quotes (generates zero-padded check forms)
- `verify_extraction()` on `data_values` is circular — documented to skip it; cross-check (Rule 6) is the verification for table data
- Added officialdata.org to reference_domains.json (tier 3)
- Aligned `data_values` guidance between SKILL.md and hardening-rules.md
- Documented multi-extraction naming convention (B1_cpi_1913, B1_cpi_2024) for multiple values from one source

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
