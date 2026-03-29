# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-03-29

### Added

- **Per-proof OG verdict card images** — auto-generated 1200x630 social sharing cards at build time using Pillow, with verdict badge, claim text, source count, and optional 240x240 thumbnail
  - Submitter-provided `thumbnail.png` takes priority over default thumbnail
  - Custom thumbnails also displayed on proof detail pages (floated right of claim title)
  - JetBrains Mono Bold font bundled for consistent CI rendering (OFL license)
- **Share buttons on proof pages** — X/Twitter post (with pre-filled verdict text), copy verdict, and copy link buttons after the verdict banner
  - Share text varies: "verified with sources" vs "verified by computation" based on proof type
  - All claim text safely escaped via data-attributes (no inline JS interpolation)
- **How-it-works pipeline diagram** — 5-step CSS/HTML flow on landing page: claim → fetch sources → verify quotes → run proof.py → verdict. Responsive (stacks vertically on mobile)
- **GitHub stars badge** on landing page (shields.io, live count)
- **Trust line** on landing page: "X sources checked across Y proofs" using unique verified source names
- **"Star on GitHub" nudge** on proof detail pages near downloads
- **Twitter Card meta tags** (`twitter:card`, `twitter:title`, `twitter:description`) on all pages
- **Schema.org WebSite JSON-LD** on landing page
- **Claude Desktop one-click install** button and redirect page
- **Proof thumbnails** for 7 proofs generated via Nano Banana Pro
- Seeded 38 new proofs from eval rounds (hot topics, nutrition claims, more)

### Changed

- **CTA hierarchy** — landing page hero now has single primary "browse proofs" button; "install skill" and "ai agents" demoted to text links below
- **Evidence table** on proof detail pages leads with source name (linked), fact ID as secondary column
- **Download labels** humanized: "run the proof (Python)", "full audit trail", "raw data (JSON)"
- Source line contrast improved from `--text-muted` to `--text-secondary` for WCAG AA compliance

### Fixed

- Source line contrast ratio below WCAG AA minimum (2.5:1 → 7:1)
- OG verdict badge vertical padding too tight for long verdict text like "DISPROVED (with unverified citations)"
- `verify_citation` now respects monkeypatched `requests=None` via `skip_live_fetch` parameter
- Proof output directory created before thumbnail copy
- Unknown `proof.json` keys (`sub_claim_verdicts`, `sub_claim_results`) added to ProofData TypedDict
- Redundant `sub_claim_verdicts`/`sub_claim_results` removed from proof artifacts
- Install redirect page fallback and auto-redirect improvements

## [1.0.0] - 2026-03-28

### Added

- GitHub Pages site for publishing verified proofs ([yaniv-golan.github.io/proof-engine](https://yaniv-golan.github.io/proof-engine/))
  - Searchable proof catalog with client-side filtering
  - Machine-readable JSON API (`index.json` + per-proof `proof.json`)
  - Schema.org ClaimReview JSON-LD for search engine discoverability
  - SEO metadata: meta descriptions, OpenGraph tags, canonical URLs on all pages
  - `sitemap.xml` and `robots.txt` generated at build time
  - `llms.txt` agent entry point for AI agents to discover and interact with the catalog
  - PR-based community proof submissions with CI validation
  - Methodology page generated from DESIGN.md and hardening rules
- **Site visual refresh** — "Forensic Terminal x Dark Scholar" theme
  - JetBrains Mono typography for UI elements, Georgia serif for claim text
  - Warm slate card design with rounded corners and source line previews
  - Structured evidence tables with clickable source links on proof detail pages
  - Linked Source Credibility and Extraction Records audit tables
  - Verdict symbol prefixes (checkmark/X/half-circle/?) scoped to detail page banners
  - Q.E.D. tombstone favicon and touch icons
  - GitHub Octocat icon in navigation (replaces text link)
  - Google Analytics 4 integration
  - Responsive breakpoints for mobile (640px) and tablet (768px)
  - Landing page stats: Proved/Disproved counts replace ambiguous "Fully Resolved %"
  - Source names on proof cards (top 3 cited sources with "+N more" overflow)
  - Pure computation proofs labeled "Pure computation — no external sources"
  - All inline styles removed from templates and JavaScript
- **Absence-of-Evidence Proof Template** — new template for claims about absence of published evidence, with `search_registry` data structure, `verify_search_registry()` verification, Type S facts in FACT_REGISTRY, and `SUPPORTED` verdict
- **SUPPORTED verdict** — 7th and 8th verdicts (`SUPPORTED`, `SUPPORTED (with unverified citations)`) for absence-of-evidence proofs where the epistemic claim is inherently weaker than deductive proof. Blue badge, own catalog filter.
- **Academic citation normalization** — `normalize_text()` now strips inline reference markers (`<sup>[1]</sup>`, `<a class="xref">[1,2]</a>`) from PMC and journal HTML before quote matching, fixing false-negative citation verification on academic sources
- **Rule applicability matrix** in hardening-rules.md — documents which validator rules auto-pass for each proof type
- **Qualitative gotchas** in SKILL.md — 4 new gotchas for qualitative and absence proofs
- Validator: Rule 2 and Rule 6 now support `search_registry` for absence proofs
- `validate-site-proof.py`: absence proofs require `search_registry`; authored search metadata validated for completeness; dynamic verdict list in error messages
- SKILL.md: edge-case guidance for fictitious source attributions, partial-period data, and missing constants
- proof-templates.md: open-problem and proof-by-contradiction adaptation notes
- SKILL.md: actionable WebFetch paraphrasing gotcha
- TypedDict definitions for all proof artifact shapes (`scripts/proof_types.py`) with contract tests
- AST-based source analysis helpers (`scripts/ast_helpers.py`) for reliable import/call-site detection
- HTTP transport layer extracted to `scripts/fetch.py` (live -> snapshot -> Wayback fallback chain)

### Changed

- `verify_citations.py` fetching logic extracted to `fetch.py` (public API unchanged)
- `validate_proof.py` migrated from regex to AST for import analysis, call-site detection, and dict key extraction
- `scripts/__init__.py` documents the dual-audience purpose of the scripts directory

### Fixed

- README: updated Claude Desktop installation instructions with correct marketplace flow
- README: added Claude.ai (web) installation instructions
- Validator: detect missing `proof_direction` key in disproof proofs (silent 180° verdict flip)
- Validator: warn when compound sub-claim has fewer than 2 sources (prefix-based heuristic)
- Validator: require call site for `verify_all_citations` / `verify_data_values` / `verify_search_registry` (import alone no longer satisfies Rule 2 or unused-import check)
- Source credibility: add missing academic domains (IOPscience, A&A, AMS, AIP, etc.) and reference domains (BrainFacts, SimplyPsychology, Snopes, etc.)

## [0.9.0] - 2026-03-28

### Added

- **Generator signature** on all proof artifacts: JSON summary includes `generator` block (`name`, `version`, `repo`, `generated_at`); proof.md and proof_audit.md end with a footer line. Version is read at runtime from `VERSION` file in the skill directory.
- `build_citation_detail()` now handles multi-source empirical facts — emits `{fact_id}_source_{N}` entries for facts with a `sources` list, preserving "one row per source" contract.
- Validator: `check_table_data_integrity()` — enforces correct table-data verification patterns:
  - `data_values` present requires `verify_data_values()` call (hard failure)
  - `verify_extraction()` on `data_values`-derived values detected as circular (hard failure)
  - Pseudo-quote fields (`*_quote`) with bare numeric/date literals parsed as evidence (hard failure)
  - Multiple numeric `_quote` fields without `data_values` (warning)
- 9 new validator tests for table data integrity checks, including regression fixtures for the purchasing-power anti-pattern.
- Negative example in proof-templates.md showing the rejected pseudo-quote pattern.
- Gotcha in SKILL.md: "Never create pseudo-quote fields for table data."
- Unit tests added to CI workflow (`.github/workflows/validate.yml`).

### Fixed

- `parse_range_from_quote()` no longer misparses ISO dates (`2020-01-01`) as numeric ranges. Uses `re.finditer` to skip date-shaped matches and keep scanning.
- `verify_citations.py` no longer calls `sys.exit(1)` at import time when `requests` is missing. HTTP calls are guarded individually; snapshot-only verification works without `requests`.
- `validate_proof.py` `_extract_empirical_facts_keys()` no longer crashes on unterminated strings in malformed source code.
- `cross_check()` now raises `ValueError` on unknown `mode` instead of silently falling to absolute comparison.
- Release workflow: fixed `mv` collision that nested the temp dir inside existing `proof-engine/`; `${CLAUDE_SKILL_DIR}` placeholder now stripped from all markdown files (was only SKILL.md).
- Broken links in `docs/examples/purchasing-power-decline/` proof.md and proof_audit.md.
- `docs/cross-platform.md` release snippet synced with corrected workflow.
- Purchasing-power example (`docs/examples/purchasing-power-decline/proof.py`) converted from pseudo-quote fields to `data_values` + `verify_data_values()`.

### Changed

- `output-specs.md` updated to document multi-source citation sub-entries and generator signature.
- `bump-version.sh` now copies `VERSION` to skill directory for runtime access by generated proofs.

## [0.8.0] - 2026-03-27

### Added

- **Qualitative Consensus Proof Template** — full template for source-counting proofs (affirm + disprove variants). Uses `proof_direction` field to control verdict mapping. Replaces the 3-sentence adaptation note.
- **Compound CLAIM_FORMAL template** — complete worked example for AND claims with per-sub-claim confirmation lists, labeled `compare()` calls, and full verdict block with PARTIALLY VERIFIED handling.
- **6th verdict: DISPROVED (with unverified citations)** — completes the 2x2 verdict matrix (claim_holds × citation_status). Updated all templates, output-specs, README.
- `compare(label=)` parameter — traces now print `SC1: 3 >= 3 = True` instead of `compare: 3 >= 3 = True`. Eliminates manual annotation of computation traces.
- Validator: `check_claim_holds_computed()` — flags hardcoded `claim_holds = True/False` and variants (`subclaim_a_holds`, `overall_claim_holds`).
- Validator: `check_unused_imports()` — warns when scripts.* functions are imported but never called.
- Validator: `check_verdict_branches()` — flags single hardcoded verdict assignments, warns on missing else fallback.
- Test suite: 40 pytest tests covering `cross_check`, `parse_number_from_quote`, and all validator checks.
- Eval harness (`tools/run-evals.sh`, `tools/run-single-eval.sh`) — batch-tests claims against the skill with structured feedback collection.
- Claim generation prompt (`evals/generate-claims-prompt.md`) — meta-prompt for generating diverse test claims by domain.

### Fixed

- `cross_check(a, a, tolerance=0)` now returns AGREE (was DISAGREE due to `<` instead of `<=`).
- `parse_number_from_quote` handles leading-zero-omitted decimals (`.24`, `-.33`) common in statistics papers.
- Validator Rule 6 counts actual `empirical_facts` dict keys instead of regex-matching `source_name` fields.

### Changed

- Adversarial sources guidance: sources that argue against the proof's conclusion go in `adversarial_checks`, not `empirical_facts`. Prevents citation failures from contaminating the verdict.
- Cross-reference fix: qualitative consensus pointer now correctly points to proof-templates.md (was hardening-rules.md).
- Step 3 now lists qualitative consensus as a template option alongside date/age, numeric/table, and pure-math.
- output-specs.md: computation traces section updated for qualitative proofs and labeled compare() output. Provenance label format specified.
- self-critique-checklist.md: fixed stale reference to hardening-rules.md.

### Gotchas added

- **WebFetch paraphrases quotes** — AI fetch tools silently reformat text; always verify verbatim before committing to empirical_facts.
- **Handle `verify_data_values()` failures** — don't use unverified data_values as primary computation input; cross-checking two unverified sources is circular.

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
