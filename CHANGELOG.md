# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.21.4] - 2026-04-18

### Fixed

- **Pygments syntax highlighting now actually ships in the deployed site.** v1.21.2 enabled `codehilite` in the Markdown pipeline and v1.21.3 wired up a dark-theme stylesheet, but the deployed pages still rendered the inline proof source as plain `<pre><code class="language-python">` with no token spans. Root cause: `Pygments` was missing from `.github/workflows/deploy-site.yml`'s `pip install` line, so codehilite silently fell back to the `fenced_code` output (no `.highlight` wrapper, no token classes — nothing for the dark theme to colour). The `validate.yml` workflow already installed Pygments, which is why local builds and CI checks looked correct. Adding `Pygments` to the deploy workflow makes the syntax highlighting actually reach production.

## [1.21.3] - 2026-04-18

### Fixed

- **Inline proof source is now actually readable on the dark site theme.** v1.21.2 shipped Pygments' light `default` style on the dark page background, which collapsed all syntax tokens into low-contrast washes of the same colour. Replaced with the `github-dark` style (background tweaked to match `--bg-card`); strings are now bright cyan, keywords red, comments dim italic, identifiers light. The `.proof-source-section` and `.rerun-section` containers also switch from hardcoded light colours (`#fafafa`, `#f0f7ff`) to the site's CSS variables (`--bg-card`, `--blue-bg`) so they integrate with the dark theme instead of fighting it.

## [1.21.2] - 2026-04-18

### Added

- **Inline proof source on every proof page.** New collapsible "View proof source" section renders the full `proof.py` server-side with Pygments syntax highlighting, so auditors can inspect the verification code without leaving the page or downloading artifacts. `Pygments` added as a build dependency; `codehilite` enabled in the Markdown pipeline.
- **Re-execute call-out lifted to its own section.** The Binder "Open in Binder" card moves out of the `machine-readable formats` row into a dedicated "Re-execute this proof yourself" block with primary CTA styling — re-running a proof is an action, not a download target.
- **Methodology page documents three re-run options** (local clone, Binder one-click, Zenodo download), so the skeptic path is described in one place.
- **`site/doi-index.json`** emitted at the site root: a DOI→slug map consumed by the launcher's verdict cell to deep-link back to the matching proof page (concept and versioned DOIs both resolve).
- Regression tests in `tests/test_build_site_source.py` covering the inline-source template wiring and `doi-index.json` emission.

### Changed

- **Companion to `proof-engine-binder` v1.21.2** (multi-cell launcher, `anywidget` removed, source display moved to the proof page). Both ship together so the values-aligned UX — confirmer reads cached verdict, auditor inspects source on the page, skeptic re-executes via transparent cells on Binder — lands in one coordinated step.

## [1.21.1] - 2026-04-18

### Fixed

- **"Open in Binder" DOI pre-population actually works end to end.** The 1.21.0 launcher shipped with a URL-fragment scheme (`#doi=...`) that could never reach the server and that JupyterLab's SPA router strips from the client before any widget JS runs. The launcher repo's `v1.21.0` tag was moved to a fixed commit that installs a Jupyter Server extension to capture `?doi=` server-side and write it to `/tmp/binder_doi`; this release updates the main-repo emitter (`proof-site.py`), the one-shot migrator, and all 74 published `doi.json` `binder_url` values to the query-parameter shape that the server extension can actually see. Also refreshes `docs/DESIGN.md` to describe the real mechanism.

## [1.21.0] - 2026-04-18

### Added

- **Binder launcher.** All published proofs now have a working "Open in Binder" link, routed through the new [`yaniv-golan/proof-engine-binder`](https://github.com/yaniv-golan/proof-engine-binder) repo. The launcher notebook reads a Zenodo DOI from a `?doi=` query parameter (captured server-side by a Jupyter Server extension, since JupyterLab's SPA router strips query strings before client JS runs), fetches `proof.py` from Zenodo, and runs it in a pinned Python environment. Proof pages render a new "Open in Binder" format card when a DOI is minted.
- **`PROOF_ENGINE_ROOT` env-var override** in generated `proof.py` now supports an env-var override with a hardcoded fallback, enabling portable execution under Binder while keeping local-only proofs working unchanged.
- **`tools/migrate-proof-root.py`**: one-shot script that converts legacy `proof.py` files (hardcoded and `__file__`-traversal forms) to the env-var pattern.
- **`tools/migrate-binder-urls.py`**: one-shot script that converts legacy `binder_url` values in `doi.json` to the launcher-repo URL.

### Changed

- **Landing page redesign.**
- **`mint-doi` emits launcher-repo URLs for `binder_url`** instead of `mybinder.org/v2/zenodo/...` URLs (which never worked because Zenodo deposits lack a dependency manifest). The launcher tag is derived from `VERSION` so `bump-version.sh` propagates it automatically; a drift test pins the derivation.
- **All 6 proof-template references updated** to generate proofs with the new `PROOF_ENGINE_ROOT` env-var shape.
- **All published `proof.py` files (127) and minted `doi.json` files (74) migrated in place.** No Zenodo re-mints required — `binder_url` lives only in this repo.

### Fixed

- **"Open in Binder" on every proof page now works.** Prior URLs 404'd on the Zenodo-provider path and the link was never rendered in the template.

## [1.20.1] - 2026-04-17

### Added

- **`ZENODO_SANDBOX_TOKEN` env var**. `mint-doi --sandbox` now reads
  `ZENODO_SANDBOX_TOKEN` first and falls back to `ZENODO_TOKEN`, so
  operators can keep prod and sandbox credentials side by side in
  `.env` instead of swapping a single variable.

### Fixed

- **`mint-doi --sandbox` no longer touches prod `doi.json`**. Previously,
  running a sandbox smoke test against a proof that already had a
  production DOI either failed with "DOI already exists" or — with
  `--force` — tried to create a new version of a prod record ID against
  the sandbox API (guaranteed 404). Sandbox mode is now fully ephemeral:
  it ignores existing `doi.json` for existence checks, bypasses the
  `--force` new-version path, and does not write the sandbox DOI back
  to disk. `--force` is a no-op under `--sandbox`. This removes the
  operator workaround of manually moving `doi.json` aside before each
  sandbox run.

## [1.20.0] - 2026-04-17

### Added

- **`mint-doi`: propagate the full `depends_on` graph into Zenodo
  `related_identifiers`**. Zenodo records now include every originating
  paper, upstream proof DOI, Software Heritage archive, and external URL
  declared in a proof's `meta.yaml depends_on`, with the correct DataCite
  `relation` (`isDerivedFrom`, `references`, etc.) and — where unambiguous
  — a DataCite `resource_type` (`arxiv` → `publication-preprint`, `swhid`
  → `software`, `isbn` → `publication-book`). The synthetic
  `isSupplementedBy` edge to the proof's webpage is preserved as edge 0.
  Brings our DataCite metadata in line with standard practice for
  derivative scholarly deposits. Applies to both first-mint and
  `--force` new-version paths; existing records are unaffected until
  re-minted.
- New module **`tools/lib/zenodo_metadata.py`** — pure helper (no network)
  that converts parsed `depends_on` entries into the Zenodo API's
  `related_identifiers[]` shape. Uses a Zenodo-local canonical-identifier
  precedence (`doi > arxiv > swhid > handle > isbn > url > slug`)
  deliberately distinct from the internal `canonical_identifier()` order,
  because arXiv and URL are more broadly resolvable than SWHID and slug
  for external DataCite consumers. `resource_type` is emitted only for
  identifier types with an unambiguous DataCite mapping — DOIs are
  omitted so Zenodo/DataCite can resolve the target's own type rather
  than having us hard-code `publication-article` for what may actually
  be a dataset, software record, or book.
- Dedup key for related identifiers is `(identifier, relation, scheme)`,
  so literals like `10.5072/FK2` that parse validly as both a DOI and a
  Handle are preserved as two distinct records (Zenodo treats them as
  separate edges).

### Changed

- `mint-doi` now emits a stderr `warning: skipping...` line when a
  `depends_on` entry resolves to a slug-only identifier (upstream proof
  not yet minted), instead of silently dropping it. Re-run with
  `--force` after minting the upstream to pick it up.

## [1.19.0] - 2026-04-17

### Added

- **Rule 9: prose references mechanically resolvable** — new hardening rule closing the hand-typed-attribution escape route (e.g., a correct arXiv link laundering an incorrect "R. Cheng" author name in prose). Prose authors and titles in `proof.md`, `proof_audit.md`, and `proof_narrative.md` must either be rendered from `{{cite:<type>:<value>[:<style>]}}` tokens or agree with a registered identifier's resolved metadata. Documented in `references/hardening-rules.md` and the methodology page (`docs/DESIGN.md`).
- **`tools/lib/reference_resolver.py`** — identifier-resolution library. Parses arXiv IDs, DOIs, SWHIDs, Handles, ISBNs, and URLs (`collect_identifiers`); resolves to canonical author/title metadata via arXiv API, DataCite, Crossref, Handle.Net, and OpenLibrary backends; caches per-proof in `depends_on_resolved.json`.
- **`tools/lib/prose_reference_scan.py`** — four-pass prose verifier. Pass 1 discovers identifier mentions (literal or inside link targets); Pass 2 cross-checks nearby authors/titles against the resolved metadata with Unicode-folded compound-surname matching and Jaccard title similarity; Pass 3 advises on bare identifiers lacking attribution; Pass 4 sweeps dangling attributions not backed by any registered identifier. Verification windows bound at blank-line breaks so same-paragraph attributions are covered without absorbing cross-paragraph text.
- **`tools/lib/cite_expander.py`** — renderer for `{{cite:<type>:<value>[:<style>]}}` tokens. Three styles (full / short / inline); idempotent — re-running over already-expanded output is a no-op; leaves a sidecar comment so the verifier treats the rendered region as trusted.
- **CLI subcommands on `tools/proof-site.py`** — `resolve-deps` (populate or refresh a proof's resolved-metadata cache), `cite-expand` (render cite tokens, with `--check` mode for gating), and `verify-prose` (run the four-pass scan).
- **Pre-flight gates**:
  - **`publish`** — three-step offline pre-stage gate: `resolve-deps`, `cite-expand --check`, `verify-prose`. Preserves an existing `depends_on_resolved.json` cache on `--force` republish.
  - **`mint-doi`** — two-step pre-flight: `cite-expand --check` + `verify-prose` before minting.
  - **`validate-site-proof`** — invokes `verify_prose` on the staged directory as its sixth validation step; CI fails on prose-reference mismatches.
- **`tools/migrate-prose-refs.py`** — one-time migration tool that resolves identifiers and runs the four-pass verifier over every proof under `site/proofs/`, writing `migration-report.md` with per-proof status.

### Changed

- **`SKILL.md`** — "The 8 Hardening Rules" → "The 9 Hardening Rules"; Rule 9 row added.
- **README.md** — hardening-rule count and rule table updated to include Rule 9.
- **`docs/DESIGN.md`** — new "Prose Reference Verification" section describing the four passes and the `{{cite:...}}` workflow. Methodology page registers the section via `tools/build-site.py`.

### Notes

- Existing site proofs do not need to be regenerated. Caches populate lazily on the next per-proof republish; a one-shot backfill can be done any time via `tools/migrate-prose-refs.py`.

## [1.18.0] - 2026-04-16

### Added

- **KaTeX math rendering** — mathematical notation in proof claims and narratives now renders as typeset math across all site surfaces. Three rendering paths: KaTeX client-side for headings and narrative markdown, `pymdownx.arithmatex` for markdown pipeline protection, and `strip_latex()` Unicode conversion for plain-text surfaces (OG tags, JSON-LD, citations, page titles).
- **`tools/lib/latex_utils.py`** — `strip_latex()` function converts `\(...\)` LaTeX delimiters to Unicode equivalents (Greek letters, sub/superscripts, operators) for contexts where client-side rendering is unavailable.
- **`tools/add-latex-to-claims.py`** — interactive script for retroactive conversion of math-heavy proof claims to use LaTeX delimiters. Supports dry-run mode, manual editing, and preserves proof.json/proof.py provenance parity. Skips DOI-backed proofs.
- **KaTeX v0.16.45 vendored** — self-hosted CSS, JS, auto-render plugin, and 60 font files at `site/static/vendor/katex/`.
- **`pymdownx.arithmatex`** — integrated into the markdown sanitizer to protect `\(...\)` and `\[...\]` delimiters from markdown processing. Configured with `inline_syntax: ["round"]` and `block_syntax: ["square"]` to avoid `$...$` currency collisions.
- **Math rendering in catalog** — `renderMathInElement` called after card rendering in both `catalog.js` and `catalog-enhance.js`.

### Changed

- **`tools/build-site.py`** — registers `strip_latex` as a Jinja2 filter; pre-strips `claim_natural` in pipeline example data.
- **`tools/lib/json_ld.py`** — applies `strip_latex()` to `claimReviewed` field.
- **`tools/lib/citation.py`** — applies `strip_latex()` to citation claim text.
- **`site/templates/proof.html`** — `strip_latex` filter on title, OG tags, meta description, and share bar; `<h1>` left raw for KaTeX client-side rendering.
- **`site/templates/landing.html`** — `strip_latex` filter on myth-card claims and featured proofs data.
- **CI workflows** — `pymdown-extensions` added to pip install in `validate.yml` (both jobs) and `deploy-site.yml`.
- **SKILL.md** — added LaTeX delimiter guidance for proof authors.

## [1.17.0] - 2026-04-16

### Added

- **`proof_format_schema.json`** — single source of truth for proof markdown section requirements, shared between the proof-engine skill (producer) and site builder (consumer). Defines v1/v2 profiles for `proof.md`, `proof_audit.md`, and `proof_narrative.md`, plus conditional sections and template fallback mappings.

### Changed

- **`proof_loader.py`** — section requirements now read from `proof_format_schema.json` instead of hardcoded constants. Profile selection uses `original_format_version` to choose v1 or v2 validation rules.
- **`narrative_validator.py`** — required narrative sections now sourced from schema instead of a hardcoded list.
- **`proof.html`** — replaced `format_version` branching with fallback chains (`Quality Checks` or `Hardening Checklist`, `Source Data` or `Extraction Records`, audit or proof.md `Claim Interpretation`).
- **`output-specs.md`** — added schema reference, documented `ProofSummaryBuilder` as primary emission path, fixed narrative heading casing to title-case.
- **`SKILL.md`** — documented `ProofSummaryBuilder` in Bundled Scripts table and Key function signatures, updated `emit_proof_summary` gotcha, fixed narrative heading casing.

### Fixed

- **Legacy `emit_proof_summary()` now defaults `format_version` to 2** — proofs generated via the legacy path no longer land with missing `format_version`, which caused the loader to apply v1 section requirements to v2-style proofs.

## [1.16.0] - 2026-04-15

### Added

- **`rejection_statement` field for disproof proofs** — each `empirical_facts` entry in a disproof must include a `rejection_statement` field: the verbatim phrase from the quote that explicitly rejects the claim. `validate_proof.py` warns when the field is absent and raises an issue when it is present but not a substring of the associated `quote`. Replaces the 25-pattern `REJECTION_MARKERS` vocabulary scan.
- **`is_time_sensitive` field in `CLAIM_FORMAL`** — proofs that depend on the current date declare `"is_time_sensitive": True` in `CLAIM_FORMAL`. `validate_proof.py` uses AST to read this field and enforces four behavioral branches (declared+today → pass; declared+no today → issue; today without declaration → warning; hardcoded date without today → issue). Replaces comment-strip + regex keyword scan.
- **`verbatim` field per `empirical_facts` entry** — authors can declare `"verbatim": False` when a quote is paraphrased. `validate_proof.py` checks this field structurally: warns on `verbatim: False`, raises an issue on `verbatim: True` with an ellipsis (contradiction), and nudges on ellipsis without any declaration. Replaces ellipsis-only heuristic.
- **`subclaim_to_sources` map in `CLAIM_FORMAL`** — compound proofs can declare an explicit `subclaim_to_sources` dict mapping each sub-claim ID to its list of `empirical_facts` keys. `validate_proof.py` Path 1 uses this map directly; Path 2 falls back to key-prefix inference for proofs that don't provide it.
- **AST-based Rule 5 check** — `adversarial_checks` is verified via AST list-element count, not vocabulary scanning. Empty list → issue; `count ≥ 1` → pass with count; non-list or missing → regex fallback.
- **W3C PROV-JSON export** — `tools/lib/prov.py` generates `provenance.json` per proof: a W3C PROV-JSON provenance chain mapping each evidence entity, citation-verification activity, and cross-check derivation back to the Proof Engine agent. Included in RO-Crate packages.
- **SARIF 2.1.0 export** — `tools/lib/sarif.py` converts `validate_proof.py` results to SARIF 2.1.0. Each hardening rule maps to a stable rule ID (`PE001`–`PE010`); issues are `error` level, warnings are `warning`. Enables integration with GitHub Code Scanning and other SARIF-aware tooling.
- **RO-Crate 1.1 packaging** — `tools/lib/ro_crate.py` generates `ro-crate-metadata.json` per proof: a standards-compliant research object manifest listing all proof artifacts (`proof.py`, `proof.json`, `proof.md`, `proof_audit.md`, `proof_narrative.md`, `provenance.json`, `proof.ipynb`) with typed schema.org roles and DOI links.
- **Jupyter Notebook export** — `tools/build-site.py` generates `proof.ipynb` per proof: a two-cell Jupyter Notebook that installs dependencies and re-runs `proof.py` in an interactive environment. Included in the RO-Crate manifest as a `ComputationalNotebook`.
- **Enhanced Schema.org JSON-LD** — proof pages now include `isBasedOn` (links to each cited source URL), `mainEntity` (the `ClaimReview` block), and `sameAs` provenance links. Improves search engine and Linked Data discoverability.

### Changed

- **`validate_proof.py` design principle** — all new checks read structured fields declared by the LLM at generation time; validator does mechanical verification only (substring containment, list length, field presence). No semantic inference from free text.
- **Hardening rules documentation** — updated validator notes for Rule 3 (is_time_sensitive behavioral branches), Rule 5 (AST non-empty list check), and Rule 8 (rejection_statement enforcement).
- **`output-specs.md`** — added `rejection_statement`, `Verbatim status`, and `Time sensitivity` to Citation Verification Details.
- **`template-qualitative.md`** — added `is_time_sensitive` comment to `CLAIM_FORMAL`, `verbatim` comment to `empirical_facts`, and expanded disproof variant to show `rejection_statement` field explicitly.
- **`template-date-age.md`** — `is_time_sensitive: True` now included in `CLAIM_FORMAL`.
- **`template-compound.md`** — commented `subclaim_to_sources` block added to `CLAIM_FORMAL`.

## [1.15.0] - 2026-04-11

### Added

- **Proof detail page redesign** — restructured proof detail template with verdict qualifier line, jump links (summary · caveats · sources · audit trail), promoted counter-evidence section ("What could challenge this verdict?"), canonical sources table, collapsible downloads, and single generator footer
- **Format version support** — `format_version` field in `proof.json` enables v1/v2 proof format branching in loader and template. V2 proofs use renamed sections (Quality Checks, Source Data) and move Claim Interpretation to the audit trail
- **`_SOURCE_TYPE_DISPLAY_LABELS`** — capitalized source-type labels for the detail page, separate from the lowercase landing-page labels

### Changed

- **Proof detail template** — evidence accordion slimmed to 3 sections (Evidence Summary, Proof Logic, Conclusion); audit trail reordered with format-version-aware section list; page title truncated at 50 chars
- **Output specs (v2)** — renamed Counter-Evidence Search → "What could challenge this verdict?", Hardening Checklist → Quality Checks, Extraction Records → Source Data; Claim Interpretation moved from `proof.md` to `proof_audit.md`
- **Proof loader** — v1/v2 required/optional section lists; `format_version` hoisted to top-level proof dict; Claim Specification made optional for v1 (3 existing proofs lack it)

### Fixed

- **Generator footer stripping** — regex handles both plain and italic-wrapped (`*Generated by...*`) footers
- **Dead inline analytics script** — removed from template (proof-enhance.js handles it)
- **Jump links spacing** — fixed Jinja2 whitespace control for dot separators

## [1.14.0] - 2026-04-11

### Added

- **Tag evolution** — automatic vocabulary growth when proof catalog grows. `audit_vocabulary()` uses Sonnet to propose new tags when 3+ proofs cluster around an uncovered topic. Triggered automatically during `proof-site.py publish` when 10+ new proofs exist since last audit, or manually via `retag-proofs.py --audit`
- **`tags_manual: true`** in `meta.yaml` — marks tags as human-curated so they are never overwritten by automatic retagging
- **`retag_pending` flag** in `tag_vocabulary.json` — makes the audit+retag cycle restartable across interruptions
- **`--verbose` flag** on `retag-proofs.py` — prints per-proof skip reasons and tag changes

### Changed

- **TAG_VOCABULARY extracted to JSON** — vocabulary and audit metadata now live in `tools/lib/tag_vocabulary.json` instead of a Python dict in `tagger.py`
- **`retag_proof()` raises on failure** — returns `True` (changed) / `False` (no change), raises `RuntimeError` on LLM failure instead of silently returning `False`

### Fixed

- **LLM response parsing** — handles single-backtick wrapping and extra text after valid JSON from Claude CLI
- **Test fixtures** for `test_build_site.py` and `test_mint_doi.py` — provide cached tags via `meta.yaml` so tests don't require the Claude CLI

## [1.13.0] - 2026-04-11

### Added

- **Paywalled source access via `snapshot_file`** — proofs can reference local snapshots of paywalled content, wired through `fetch_page()`, `verify_citation()`, `verify_all_citations()`, and `verify_data_values()`
- **Open Access fallback via Unpaywall** — new `oa_lookup.py` module extracts DOIs and queries the Unpaywall API for OA variants; integrated into `verify_citation()` as automatic fallback after fetch failure
- **`oa_variant` fetch mode** in `proof_types.py` and `build-site.py` — proofs resolved via OA lookup are tagged accordingly

### Fixed

- **Site proof validator** accepts `snapshot_file` verdict and `key_results` degradation levels
- **Unpaywall API calls** URL-encode DOIs; `oa_variant` recognized in proof types and build-site
- **Section matcher ignoring parenthetical suffixes** — `validate_required_sections` now strips suffixes like `(Rule 5)` before matching, so audit headings like `## Adversarial Checks (Rule 5)` correctly match the expected section name `Adversarial Checks`

### Changed

- **Paywall handling guidance** rewritten with `snapshot_file` workflow and OA discovery documentation
- **README** rewritten with core thesis ("prove, don't assert") and practical comparisons
- **Site homepage and methodology copy** improved for clarity

### Content

- **`snapshots/` directories** added to `.gitignore` per paywalled content policy

## [1.12.0] - 2026-04-09

### Added

- **`apply_verdict_qualifier()` helper** in `computations.py` — validates base verdict against the 5-value taxonomy and only appends "(with unverified citations)" to the 3 qualifiable verdicts (PROVED, DISPROVED, SUPPORTED). Prevents agents from constructing invalid verdict strings
- **`emit_proof_summary()` helper** in `computations.py` — validates proof summary keys against the `ProofData` TypedDict schema before printing, raising `ValueError` on unknown keys. Prevents agents from inventing schema fields
- **Verdict validity check** in `validate_proof.py` — detects invalid verdict strings and the `+=` antipattern for building verdicts
- **FACT_REGISTRY format check** in `validate_proof.py` — ensures registry entries are dicts (not plain strings) with required keys per fact type
- **`claim_natural` key check** in `validate_proof.py` — warns when bare `"claim"` is used instead of the required `"claim_natural"` key
- **`emit_proof_summary` adoption check** in `validate_proof.py` — warns when proofs use raw `json.dumps` instead of the schema-validated helper
- **Type guard in `verify_citations.py`** — `build_citation_detail()` raises `TypeError` with actionable message when FACT_REGISTRY entries are strings instead of dicts
- **Key stripping in `proof_runner.py`** — unknown keys are silently stripped from proof JSON during publish, with stderr warning. Last line of defense after generation-time validation

### Changed

- **All 6 proof templates** refactored to use `apply_verdict_qualifier()` and `emit_proof_summary()`, replacing manual verdict construction and raw `json.dumps`
- **`check_json_summary()`** updated to recognize `emit_proof_summary()` as a valid summary output method
- **Missing-section errors** in `proof_loader.py` now include the list of found sections for easier debugging

## [1.11.0] - 2026-04-08

### Added

- **Inline LaTeX `$...$` stripping** in `normalize_text()` — arXiv abstract pages with raw LaTeX like `$\Lambda$CDM` and `$H_0 = 67.4\pm 0.5$` now normalize correctly. Three-pass regex handles complex LaTeX, single-letter variables, and unadorned multi-letter tokens
- **Scoped Greek-to-ASCII transliteration** — Greek letters from LaTeX output (Λ→L, Ω→O, etc.) are transliterated for matching, while non-LaTeX Greek (μm, ρ) is preserved to avoid false positives
- **Math operator spacing collapse** — ar5iv MathML rendering produces `Ω m = 0.315 ± 0.007` with spaces; new steps 3a/3b collapse Greek-Latin spacing and operator spacing
- **Closest-passage suggestion engine** — `_find_closest_passage()` uses Jaccard word-set similarity to show a diagnostic hint when quotes fail verification. Ephemeral (console output only, not persisted to proof.json)
- **GitHub raw README fallback** — bare `github.com/owner/repo` URLs that return a JS-rendered React shell now fall back to `raw.githubusercontent.com` with multiple README filename candidates. Reports `fetch_mode='github_raw'`
- **Ellipsis detection in `validate_proof.py`** — AST-based quote extraction warns when quotes contain `...` or `…`, a strong signal of spliced non-adjacent text
- **Real-world demonstration search directive** — Step 2 now prompts searching for practical applications of the claimed mechanism (not just benchmarks), after field testing revealed this gap

### Changed
 
- **Verbatim quoting enforcement** — SKILL.md, hardening-rules.md, and environment-and-sources.md now explicitly prohibit paraphrased quotes with bad/good examples, a Quote Harvesting gate in Step 2, a pre-flight citation check in Step 3, and a Citation Recovery Loop as Step 5.5
- **PDF citation guidance** — rewritten to recommend snapshot workflow using Claude Code's native PDF reading; arXiv section added recommending ar5iv HTML over arxiv.org/abs
- **Self-critique checklist** — added verbatim quote verification and PDF snapshot checks

## [1.10.0] - 2026-04-07

### Added

- **Formal citation support** — every proof page now has a "Cite this proof" section with APA, Chicago, BibTeX, and RIS formats via CSS-only tab switching
- Citation export files (`cite.bib`, `cite.ris`, `cite.txt`) generated at build time for each proof
- **Zenodo DOI minting** — `proof-site.py mint-doi <slug>` creates permanent DOIs via Zenodo REST API; `--force` creates new versions under the same concept DOI
- `doi.json` sidecar pattern for DOI persistence across proof regeneration, with claim identity check on force-publish
- `CITATION.cff` at repo root for GitHub's "Cite this repository" widget; version synced via `bump-version.sh`
- JSON-LD `ClaimReview` enriched with `identifier` (DOI) and `sameAs` (DOI URLs) when DOI is present
- Built `proof.json` includes `citation` block (doi, concept_doi, url, cite_bib_url, cite_ris_url)
- `index.json` includes `doi` field per proof entry
- Zenodo client library (`tools/lib/zenodo.py`) and citation generation library (`tools/lib/citation.py`)
- JS progressive enhancement: copy button for citation text (clipboard API)

### Content

- **30 proofs minted with permanent Zenodo DOIs** across health, climate, neuroscience, cosmology, political/historical, economics, and AI categories

## [1.9.0] - 2026-04-07

### Added

- **Rule 8: Evidence Relevance for Rejection Verdicts** — subject-match requirement (≥2 of 3 rejection sources must directly study the claim's subject) and hedged-language downgrade (sources using "questions"/"challenges" language downgrade verdict to SUPPORTED)
- Validator: `check_hardcoded_compare_input()` — flags variables hardcoded to `True`/`False` that are passed as first arg to `compare()`, preventing circumvention of evidence-based verdict computation
- SKILL.md: normative claim guardrails — normative claims must be declined or disclosed as proxy operationalizations; entailment gaps between generic citations and specific claims must be documented
- SKILL.md: "Citation presence ≠ citation entailment" gotcha — distinguishes quote-found-on-page from quote-supports-conclusion
- SKILL.md: "Don't hardcode decisive variables" gotcha
- SKILL.md: formalization fidelity check at end of Step 3 — verify CLAIM_FORMAL captures all elements of natural-language claim
- Output-specs: mandatory "Formalization scope" note in Claim Interpretation section
- Output-specs: citation entailment clarification for Type B "Verified" status
- Self-critique checklist: formalization fidelity check item
- Tests: 4 new validator tests for hardcoded-compare-input detection

### Changed

- Site framing: "Every Claim, Machine-Verified" → "Every Fact Cited, Every Calculation Re-Runnable" (landing page title, meta, JSON-LD, hero)
- Site framing: "No LLM trust required." → "Reasoning transparent and auditable." (landing page meta, proof page trust bar)
- Hardening rules count: 7 → 8 across SKILL.md, validate_proof.py, self-critique-checklist.md, hardening-rules.md

### Content

- **TikTok/Riemann proof** re-run: `rh_is_solved` now derived from citation evidence via `compare()` instead of hardcoded; B3 updated to Clay Institute "Unsolved" status label
- **Neurogenesis proof** re-run: replaced cross-species macaque study and hedged review with Spalding 2013 (direct human C14 study); threshold 3→2 with domain-scarcity justification per Rule 8
- **Math washing proof** re-framed: normative claim ("is valid scientific practice") → factual claim ("violates the hypothetico-deductive method"); verdict DISPROVED → PROVED; entailment gap documented throughout

## [1.8.0] - 2026-04-07

### Added

- **proof_narrative.md** — fourth required output artifact. Plain-language, verdict-adapted narrative for readers with zero context. Five sections: Verdict (with hook), What Was Claimed?, What Did We Find?, What Should You Keep In Mind?, How Was This Verified?
- Narrative validation library (`tools/lib/narrative_validator.py`) — structural and semantic checks: required sections, word count (200–800), fact ID rejection with context-aware filtering (vitamin B12 etc. excluded), table rejection, verdict match, hook length, claim drift warning
- Proof loader: loads and validates `proof_narrative.md` sections, parses verdict declaration and hook text for template rendering
- Site template: narrative sections are now the primary proof page content; proof.md sections moved to collapsible "Detailed Evidence" panel
- Social sharing: meta description and share text use verdict hook instead of raw claim
- proof.md and proof_narrative.md now available as downloads from proof pages
- Migration script (`tools/generate-narratives.py`) — generates narratives for existing proofs via `claude -p` CLI with validation and rollback on failure. Supports `--proof-dir`, `--batch`, `--all-in`, `--dry-run`
- CI: example proof narrative validation step in GitHub Actions workflow
- Eval tooling: `run-single-eval.sh` enforces four-file output (proof.py, proof.md, proof_audit.md, proof_narrative.md)
- SKILL.md: `### proof_narrative.md` output spec section (numbered list format)
- `output-specs.md`: narrative structure reference
- Tests: 17 narrative validator tests, 7 proof loader narrative tests, 3 site validator narrative tests, updated build/publish/eval fixtures

### Changed

- Publication gate requires `proof_narrative.md` in `REQUIRED_ARTIFACTS`
- Site validator checks narrative presence and delegates to `validate_narrative()`
- Build pipeline renders narrative sections and verdict hook, copies proof.md and proof_narrative.md to output
- Documentation updated from "three artifacts" to "four artifacts" across README.md, DESIGN.md, submit.md, evals.json

### Content

- 107 site proofs: proof_narrative.md generated and validated (0 failures)
- 2 example proofs: proof_narrative.md generated and validated

## [1.7.0] - 2026-04-06

### Added

- Scripts: context-dependent `<sup>`/`<sub>` handling — superscripts in running prose are stripped (e.g., footnote markers), but preserved as exponents in mathematical/scientific contexts (e.g., "10²", "m²")
- Scripts: inline HTML tag stripping without injecting spaces — tags like `<span>`, `<em>`, `<a>` inside quotes no longer break matching
- Scripts: two-pass matching — first try exact match on cleaned text, then fall back to substring search
- Scripts: expanded Unicode invisible character normalization — strips zero-width spaces (U+200B), zero-width non-joiners (U+200C), zero-width joiners (U+200D), word joiners (U+2060), left-to-right/right-to-left marks (U+200E/U+200F), soft hyphens (U+00AD), and variation selectors (U+FE00–U+FE0F)
- Scripts: MathML `<math>` tag extraction — extracts `alttext` attribute content and converts LaTeX notation to readable text via new `latex_text.py` module
- Scripts: `latex_text.py` — converts LaTeX math notation (fractions, Greek letters, operators, superscripts/subscripts) to plain text for citation matching
- Tests: integration tests for all three false-negative classes (superscript/inline-tag, invisible Unicode, MathML alttext)

### Fixed

- 4 site proofs upgraded from "with unverified citations" to clean verdicts: `smartphone-screens...`, `the-assertion-that-no-arab-state...`, `the-schwarzschild-radius...`, `current-ai-systems-have-already...`

## [1.6.0] - 2026-04-05

### Added

- Skill: **contested qualifier pattern** in compound template — claims with epistemic qualifiers ("verified," "confirmed," "proven") decompose into SC1 (provenance) + SC2 (epistemic warrant). SC1 holds + SC2 fails → DISPROVED (not PARTIALLY VERIFIED). Auto-detected via `"qualifier" in operator_note`
- Skill: **COI framework** — 6-category conflict-of-interest taxonomy (financial, institutional, ideological, geographic, personal, litigation) with mechanical verdict override: >50% same-direction COI among confirmed sources → UNDETERMINED. Provenance sub-claims (SC1) bypass COI gate
- Skill: split `proof-templates.md` (1,217 lines) into 6 focused template files: `template-date-age.md`, `template-numeric.md`, `template-qualitative.md`, `template-compound.md`, `template-absence.md`, `template-pure-math.md` — with 34-line decision index
- Skill: epistemic qualifier routing in SKILL.md Step 3 — directs claims with "verified"/"confirmed"/"proven" to compound template's contested qualifier pattern
- Skill: early snapshot guidance in Step 2 — pre-fetch all source pages during research, not just .gov/.edu
- Skill: adversarial evidence prose-only gotcha — documents that adversarial_checks are not citation-verified, with mitigation strategies
- Skill: WebFetch/verify_citations HTTP client divergence note
- Skill: environment guidance for major news and advocacy site 403s
- Scripts: `CoiFlag` TypedDict (5 fields) and expanded `CrossCheck` TypedDict (3→13 fields) in `proof_types.py`
- Scripts: 13 UN agency domains added to `government_tlds.json` (tier 5)
- Scripts: 7 news domains added to `major_news.json` including jpost.com, semafor.com, axios.com
- Validator: COI flags presence check — warns when empirical proof has `cross_checks` without `coi_flags`
- Validator: contested qualifier awareness — suppresses `proof_direction` false positive when `is_contested_qualifier` branch detected
- Validator: `compound_operator` presence check for compound proofs
- Tests: 7 contested qualifier verdict regression tests
- Tests: 5 COI validator tests, 4 compound operator/proof direction tests
- Tests: parametrized credibility tests for all new domains

### Changed

- Hardening rules: Rule 4 adds epistemic qualifier interpretation guidance
- Hardening rules: Rule 5 adds adversarial precision — counter-evidence must come from genuinely independent investigation
- Hardening rules: Rule 6 adds COI assessment requirement with taxonomy and override mechanics
- Templates: all 6 templates now include `import os` (was missing from 5)
- Templates: qualitative and absence templates add `else: verdict = "UNDETERMINED"` fallback branch
- Templates: qualitative and compound templates add `if coi_flags else 0` guard on `max()` calls
- Self-critique checklist: COI assessment item added, stale template reference fixed
- Eval harness: component list updated for split template files

## [1.5.0] - 2026-04-02

### Added

- Site: redesigned landing page hero — new headline "Every claim, machine-verified", 3-stat bar (Proofs, Domains, Sources checked), updated CTAs, removed GitHub stars badge
- Site: interactive "how it works" pipeline accordion — walks through a real proof's claim, sources, citations, code, and verdict with auto-cycle animation
- Site: myth-busting "think you know the answer?" featured proofs section — hover-to-reveal verdicts with colored borders, quiz mode for disproved claims
- Site: proof thumbnails displayed on myth-busting cards when available (64px, floated right)
- Site: `PIPELINE_EXAMPLE_DATA` embed — build pipeline selects a featured disproved proof with citations and serializes its full proof data for the accordion
- Site: `verdict_summary` field extracted from proof.md Conclusion section, strips bold verdict prefixes, used in myth cards and data embeds
- Site: `pipeline-enhance.js` — pipeline accordion with keyboard navigation, auto-cycle, Pretext auto-fit for claim text
- Site: shared `autoFitFontSize` export from `pretext-measure.js` — reusable by hero, pipeline, and myth-card modules

### Changed

- Site: featured proofs use `<article>` elements with `data-proof-url` instead of `<a>` wrappers — enables tap-to-reveal on mobile
- Site: hero-enhance.js no longer hides the static pipeline section (responsibility moved to pipeline-enhance.js)
- Site: `FEATURED_PROOFS_DATA` embed now includes `filter_value` and `verdict_summary`

## [1.4.0] - 2026-04-01

### Added

- Skill: `breaks_proof: True` now forces UNDETERMINED in ALL proof templates (was missing from date/age, numeric/table, pure-math)
- Skill: adversarial rebuttal requirement — `breaks_proof: False` requires explicit rebuttal when counter-evidence found (Rule 5)
- Skill: `proof_direction` support in compound template — enables DISPROVED verdict for disproof-direction compound claims
- Skill: causal vs associational evidence guardrail — causal claims decomposed into SC-association + SC-causation via compound template
- Skill: threshold reduction quality gates — `threshold: 2` requires domain-appropriate source quality, no majority COI, documented domain scarcity
- Skill: `uncertainty_override` flag in numeric/date templates — UNDETERMINED when cited source flags overlapping uncertainty ranges

## [1.3.1] - 2026-03-30

### Fixed

- OG images: moved metadata and branding higher to avoid being hidden by Twitter's card title overlay
- OG title: added verdict prefix (e.g., "DISPROVED:") to og:title so Twitter card overlay shows the verdict
- Citation verification: decode HTML entities (`&rsquo;`, `&nbsp;`, `&#8217;`, etc.) before quote matching — fixes false "partial" results on pages using HTML entities instead of Unicode characters
- Citation verification: sliding-window fragment matching replaces fixed first-half-only approach — long quotes no longer always produce ~50% coverage
- Citation verification: broadened academic ref regex to handle PMC variants with nested `<span>` and `id` attributes on `<sup>` elements
- Citation verification: unify single and double quotes during matching — pages using "toxic" now match proof quotes using 'toxic'
- Citation verification: collapse tag-stripping artifacts in compound terms — `CO 2` → `CO2`, `n -6` → `n-6` from stripped `<sub>`/`<sup>` tags
- Citation verification: add `∞` → `infinity` to Unicode normalization registry

## [1.3.0] - 2026-03-30

### Added

- **`tools/proof-site.py` CLI** — single tool for publishing proofs to the site and managing featured proofs, replacing the manual seeding workflow. Subcommands: `publish`, `feature`, `unfeature`, `repair-featured`
- **Centralized featured proofs** — `site/proofs/featured.json` replaces per-proof `featured` flags in `proof.json`/`meta.yaml`. Featured status is now site-scoped, resolved in `load_all_proofs()`.
- `tools/lib/featured.py` — featured.json read/write with atomic writes and validation
- `tools/lib/slug.py` — slug derivation from claim text and duplicate claim detection
- `tools/lib/publish.py` — proof staging, thumbnail validation (240x240), and atomic swap finalization
- `tools/lib/proof_runner.py` — extracted shared `run_proof_and_extract_json` from `validate-site-proof.py`
- `tools/migrate-featured.py` — one-time migration script (already run, 10 proofs migrated)
- **Structured citation verification summary** — replaces the noisy "Citation Verification Details" audit section with a data-driven summary badge (green/amber/red) that highlights only what's interesting. Clean proofs collapse to "3/3 verified"; flagged proofs show per-citation details with reasons (partial match, not found, fetch failed, Wayback fetch, unreliable source). Original audit markdown preserved as "Original audit log" expandable.
- `build_citation_summary()` function in `build-site.py` — computes citation health, flag reasons, and unflagged counts from `proof.json` structured data
- 22 new tests (12 unit + 10 integration) covering all citation status/method combinations, fallback rendering, and stale-audit scenarios

### Changed

- `proof_loader.py` — `load_proof()` no longer reads featured status; `load_all_proofs()` resolves it from `featured.json`
- `validate-site-proof.py` — `featured` key in `proof.json` is now a hard error (rejected, not just warned)
- `proof_loader.py` — `featured` key in `meta.yaml` is now a hard error
- `load_all_proofs()` skips dot-prefixed directories (staging, backups)
- `proof_types.py` — removed `featured: bool` from `ProofData` (kept on `LoadedProof`)
- Removed `proofs[:3]` fallback from `build-site.py` landing page — empty featured set now shows no featured proofs instead of silently selecting arbitrary ones
- Download link label changed from "full audit trail" to "original audit log" to reflect that `proof_audit.md` may be stale relative to `proof.json`
- Evidence table now shows "Fetch Failed" (instead of "No") for `fetch_failed` and legacy `failed` citation statuses
- `proof.json` is authoritative for citation status; `proof_audit.md` is treated as a historical record

## [1.2.0] - 2026-03-29

### Added

- **Web search required for source discovery** — SKILL.md Step 2 now explicitly requires using the environment's web search tool instead of relying on LLM memory. Includes structured search protocol (claim, recent data, counter-evidence), recency check for fast-moving fields, and audit trail when search is unavailable. Works across all supported environments (Claude Code, ChatGPT, Cursor, Windsurf, Gemini CLI).
- **GA4 custom events** — track CTA clicks (landing page), share button usage (proof pages), download clicks, and audit trail expansion

### Changed

- **Proof page layout** — claim title now appears first (above verdict banner), not fourth. Previous order showed the answer before the question.
- Proof page section spacing increased for readability (section heading margin-top: 32px → 40px, added paragraph/list bottom margins)
- Added `width`/`height` attributes to images for Lighthouse performance
- Improved muted text contrast ratio for accessibility

### Fixed

- Proof page content sections cramped against divider borders
- 5 proof thumbnails resized from 2048x2048 to correct 240x240

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
