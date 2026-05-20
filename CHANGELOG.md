# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.38.0] - 2026-05-20

### Changed

- **`tools/lib/reference_resolver.py` renamed to `tools/lib/proof_cache.py`.** The file's job after v1.37.0 — when the heavy-lifting registry backends moved into `proof_citations.registry` — was never really *resolution*. It's the site's per-proof on-disk cache (`depends_on_resolved.json`), the legacy `ResolvedReference` dataclass that 132 committed cache files use, and the site-specific publish-pipeline glue (`collect_identifiers` walks `meta.yaml depends_on` + `proof.json evidence`, both of which are conventions of this repo). The new name makes the layering clear: identifier resolution is `proof_citations.registry`; cache is `tools.lib.proof_cache`. All 22 internal import references in 9 caller files (`tools/proof-site.py`, `tools/migrate-prose-refs.py`, `tools/lib/prose_reference_scan.py`, plus 6 test files) updated in lockstep. Public surface (`ResolvedReference`, `resolve`, `load_cache`, `save_cache`, `collect_identifiers`, `identifier_from_url`) preserved unchanged so the rename is internally-mechanical only.
- **`tests/test_reference_resolver.py` → `tests/test_proof_cache.py`** in the same move.

### Notes

This release is purely the layering cleanup deferred from v1.37.0's "do this as a follow-up" note. No behavior change, no schema change, no API change to external consumers. Closes the original v1.35 → v1.37 design's step 5 ("migrate site-tooling callers; drop the shim"). The result is a clean separation:

```
proof_citations.registry              ← identifier resolution (pip package)
proof_citations.compare               ← metadata comparison (pip package)
proof_citations.verify_citation       ← quote-on-page (pip package)
proof_citations.verify_citation_record ← high-level orchestrator (pip package)

tools/lib/proof_cache.py              ← per-proof on-disk cache (site)
tools/lib/prose_reference_scan.py     ← {{cite:}} marker scan (site)
tools/lib/cite_expander.py            ← {{cite:}} → prose expansion (site)
tools/proof-site.py                   ← publish pipeline (site)
```

The pip package is portable; the `tools/` directory is site-specific. The current 1394-test suite passes against the renamed layout.

## [1.37.0] - 2026-05-20

### Changed

- **Registry backends consolidated into `proof_citations.registry`.** Crossref, DataCite, arXiv, Open Library, Software Heritage, Handle, and OG-extraction URL backends — which had lived in `tools/lib/reference_resolver.py` since the registry layer was first written — moved into per-source modules under the pip-installable `proof_citations.registry` package. Each backend returns the canonical `ResolvedRecord` introduced in v1.35.0. Auto-registered in `proof_citations.registry._BACKENDS` at import time, so `proof_citations.resolve(("doi", "10.x/y"))` now works end-to-end for external `pip install proof-citations` users, not just for the proof-engine site. Closes the layering issue called out in the v1.35.0 design doc: citation hygiene is now one cohesive library.
- **`tools/lib/reference_resolver.py` is now a translation shim.** Down from 408 lines to ~270. The site-facing `ResolvedReference` dataclass (with the legacy `authors: list[str]` shape) and `_BACKENDS` dispatch are preserved unchanged for backwards compatibility — all 9 existing callers (`prose_reference_scan`, `cite_expander`, `proof-site.py`, etc.) and all 132 committed `depends_on_resolved.json` files continue to work without modification. Each `_resolve_X` wrapper calls into `proof_citations.registry.resolve()` and translates the returned `ResolvedRecord` back to the legacy `ResolvedReference` shape via the new `_record_to_reference()` translator. `identifier_from_url` is now a thin alias for `proof_citations.identify`. The cache loader (`load_cache`) silently drops unknown payload keys so newer caches written by future code don't break older readers — forward-compat policy applied retroactively to the 1.x cache format.

### Added

- **`proof_citations.registry.doi`** — Crossref + DataCite backend with publication-type, ISSN, page/volume/issue, and retraction signals from Crossref's `update-to` block (sets `update_status` to `retracted` / `expression_of_concern` / `corrigendum` with linked DOIs in `update_refs`).
- **`proof_citations.registry.arxiv`** — Atom-feed parser with primary-category, version capture, DOI cross-reference, and `published_date` extraction.
- **`proof_citations.registry.isbn`** — Open Library `bibkeys` lookup with author parsing, publish-date year extraction, publisher → venue mapping, `publication_type: "book"`.
- **`proof_citations.registry.swhid`** — Software Heritage `api/1/resolve` lookup with origin-URL → title mapping.
- **`proof_citations.registry.handle`** — CNRI Handle lookup (used for some institutional repositories).
- **`proof_citations.registry.url`** — OG-meta / `<title>` extraction with Wayback fallback for publisher-blocked / Cloudflare-gated landing pages.

### Notes

This release is a pure internal refactor — no behavior change for site callers, no breaking change for `pip install proof-citations` users (all v1.36.0 API surface remains). The architectural payoff: the citation-hygiene library now owns identification + resolution + comparison + verification end-to-end. Anyone who `pip install proof-citations` gets the whole capability; the proof-engine site is a consumer of the library, not the source of registry backends. Closes the layering issue introduced when v1.28.0 extracted only the HTML-quote-verification slice.

The committed test suite (1135 site tests + 156 proof-citations + 84 proof-engine-registry + 19 proof-engine-wiki = 1394 total) all passes against the refactored layout.

## [1.36.0] - 2026-05-20

### Added

- **`proof_citations.compare_metadata(resolved, expected)` — metadata-chimera detector.** Pure-function primitive that compares a `ResolvedRecord` against a dict of claimed bibliographic fields (`title`, `journal`, `year`, `doi`, `issn`, `authors`, `volume`, `issue`, `pages`). Returns a structured verdict — `genuine`, `metadata_chimera`, `title_chimera`, `partial_match`, or `no_expected` — plus per-field `field_matches`, a list of `mismatches`, and the title-similarity score. Title comparison uses `SequenceMatcher` after NFKC + lowercase + punctuation-strip + whitespace-collapse normalization, with a 0.85 match threshold and a 0.50 chimera threshold tuned against the Ren-audit / CITADEL corpus. Journal comparison checks ISSN-equality first, then exact-after-normalize, then a small bundled NLM-ISO abbreviation table (~40 entries seeded from common biomedical journals), then a 0.80 fuzzy fallback. DOI comparison strips URL prefixes and lowercases (DOIs are case-insensitive). Author comparison does first-author family-name match by default, supports full surname lists in order if the claim provides them. Absent fields in `expected` are "not asserted" — they neither pass nor fail.
- **`proof_citations.verify_citation_record(identifier, expected)` — high-level orchestrator.** Combines identifier resolution and metadata comparison into one call. Accepts `(type, value)` tuples, `"type:value"` strings, or full URLs (passed through `identify()`). Returns a uniform dict with `status` (`verified`, `metadata_chimera`, `title_chimera`, `partial_match`, `resolved`, `unresolvable`, `fetch_failed`), the resolved record, field-level match details, and human-readable message. Backwards-compat with existing `verify_citation` callers: this is a new entry point, no existing behavior changes.
- **`proof-citations verify-records --input audit.json [--output report.json]` CLI.** Batch-verify a list of citations against authoritative registries. Input is a JSON file with a `references` list of `{ref_id, identifier, expected: {title, journal, year, doi, authors}}` entries. Emits a structured report with per-reference verdicts plus a summary block (`total`, `by_status`, `verified`, `chimeras`, `unresolvable`). Exit code is 1 if any reference is anything other than `verified` or `resolved`. Productionizes the ad-hoc Ren-audit / CITADEL workflow as a first-class capability.
- **Bundled `proof_citations/data/journal_abbreviations.json`.** Small lookup table mapping common biomedical-journal NLM-ISO abbreviations to canonical full titles. Used by `compare_metadata` to bridge `J Urol` ↔ `The Journal of Urology` style mismatches. Extensible — drop in additional entries as new failure modes surface; backwards-compatible with future tables (keys prefixed with `_` are treated as metadata).

### Notes

This release closes the gap surfaced by the Ren-audit / Topaz CITADEL exercise: metadata-chimera fraud (real PMID, fabricated journal/year/volume) is now detectable end-to-end via `verify_citation_record`. The `expected_metadata` proof-side schema field (so the skill's empirical-facts pipeline can populate claimed metadata declaratively) is the next step — landing in a future release once the regression corpus has confirmed the comparator's thresholds are well-calibrated.

## [1.35.0] - 2026-05-20

### Added

- **`proof_citations.registry` — identifier-to-metadata registry layer.** Foundation for catching the "metadata chimera" citation-fraud class (real PMID/DOI, fabricated journal/year/volume) that the existing quote-on-page verifier cannot detect. Each backend submodule implements one identifier source behind a common interface; dispatch lives in `proof_citations.registry`. Public surface: `resolve(identifier, *, cache=None, session=None) -> ResolvedRecord`, `register_backend(type_name, resolver_fn)`. Backends auto-register at import; callers can add custom ones. This is the first step in the consolidation that will eventually unify the site's `tools/lib/reference_resolver.py` (Crossref, DataCite, arXiv, Open Library, SWHID, OG-extraction) with the pip package — those backends move in a later release.
- **`proof_citations.registry.pubmed` — NCBI E-utilities backend.** First-class PubMed resolution via `esummary` (`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json`), returning structured JSON with title, journal (source / fulljournalname), publication date, volume / issue / pages, authors, DOI cross-reference, and retraction/expression-of-concern signals derived from PubMed's `pubtype` field. Closes the gap an earlier audit surfaced where 5 of 33 PubMed citations could not be verified by HTML-body-text scraping because the title was only present in `<h1>` / `<meta>` markup. Honors `NCBI_API_KEY` env var for ~10 req/sec rate limit (vs. ~3 req/sec unauthenticated).
- **`proof_citations.identify(url_or_string)` — typed identifier extraction.** Recognizes PubMed URLs (`pubmed.ncbi.nlm.nih.gov/{pmid}/`, legacy `ncbi.nlm.nih.gov/pubmed/{pmid}`), PMC URLs, DOI URLs (`doi.org/`, `dx.doi.org/`, IOPscience), arXiv URLs (`arxiv.org/abs|html|pdf`, `ar5iv.labs.arxiv.org`), Software Heritage IDs, and the corresponding bare-identifier forms (`PMID: 12345`, `doi:10.x/y`, `arxiv:2106.09685`, bare DOIs). Returns `(type, value)` for recognized inputs, `("url", original)` for unrecognized URLs, `None` for empty / unstructured input.
- **`proof_citations.ResolvedRecord` — canonical bibliographic record.** Shared dataclass returned by every registry backend. Carries `identifier_type`, `identifier_value`, `canonical_url`, `title`, `authors: list[Author]`, `year`, `venue`, `publisher`, `publication_type`, `published_date`, `issn`, `doi` (cross-reference), `pmid` (cross-reference), `arxiv_id` (cross-reference), `volume`, `issue`, `pages`, `language`, `update_status` (retracted / expression_of_concern / corrigendum), `update_refs`, `resolved_at` (ISO-8601 UTC), `source_api`, `raw` (original API payload). Backwards-compatibility policy is strictly additive: future versions may add fields with safe defaults; never remove or rename. `from_dict` silently drops unknown keys so older code reading newer caches doesn't crash. `to_dict(include_raw=False)` produces a compact form suitable for committed caches without dropping the round-trip-safe core record.
- **`proof_citations.Author` — structured author record** with `family`, `given`, `orcid`, `raw`. Replaces the legacy `list[str]` pattern that complicated family-name matching. Helpers: `display()` renders `'Family, G.I.'`, `matches(query)` does case-insensitive family-name containment, `from_full_name(s)` heuristically parses both `'Family, Given'` and `'Given Family'` shapes. Backends with structured upstream data (Crossref, PubMed) populate `family` and `given` directly.
- **`proof_citations.Cache` protocol + `InMemoryCache` + `FileCache`.** Library ships with two default cache implementations so external users aren't forced to roll their own (or, worse, hammer rate-limited APIs without backoff). `InMemoryCache` is thread-safe dict-backed; `FileCache` is JSON-file-backed under `~/.cache/proof-citations/cache.json` (or whatever `XDG_CACHE_HOME` points at), with atomic tempfile+rename writes, corrupt-file tolerance, and an `include_raw=False` default that keeps committed caches small. `resolve()` accepts `cache=None` (no caching, the default) or any `Cache`-protocol implementation.
- **`proof_citations.HTTPSession` — centralized polite HTTP client.** Per-process shared `requests.Session` wired with retry/backoff via `urllib3.Retry` (honors HTTP 429 + `Retry-After`), a polite `User-Agent` of `proof-citations/{version} (https://proofengine.info/; mailto={email})` satisfying Crossref's polite-pool policy and NCBI's `tool=` recommendation, and a 15-second default timeout. Contact email comes from `PROOF_CITATIONS_CONTACT` env var; falls back to a placeholder. `get_default_session()` returns the shared singleton (constructed lazily so import is cheap).
- **`proof_citations.ResolutionError`** with structured `kind` field (`not_found`, `fetch_failed`, `malformed_response`, `rate_limited`) and `details` dict so downstream `except` clauses can branch on failure mode rather than parsing exception messages.

### Notes

This release adds the foundation; it does NOT yet integrate the registry into the citation-verification flow. The integration (a `verify_citation_record` orchestrator + opt-in `expected_metadata` kwarg on `verify_citation` + a proof-side schema change for `expected_metadata` on FACT entries) lands in v1.36.0 alongside the metadata-comparison primitive. v1.35.0 is intentionally shippable in isolation: external `pip install proof-citations` users get registry resolution + the building blocks, the proof-engine site is unchanged.

## [1.34.1] - 2026-05-20

### Added

- **Python 3.10 support for the three pip-installable subpackages.** `proof-citations`, `proof-engine-registry`, and `proof-engine-wiki` now declare `requires-python = ">=3.10"` (was `>=3.11`) and add a `Programming Language :: Python :: 3.10` classifier. The only 3.11-only import in the package sources — `tomllib` in `proof_engine_registry.config` — is now shimmed (`import tomllib` on 3.11+, `import tomli as tomllib` on 3.10), and the `tomli>=2.0; python_version<'3.11'` conditional dependency that was already declared on `proof-engine-registry` now actually does work. Repo-level dev environment and CI workflows continue to pin 3.11.

### Fixed

- **`stage_proof` preserves the `snapshots/` directory.** The publish staging step copied only the fixed `REQUIRED + OPTIONAL` artifact list, dropping any sibling `snapshots/` directory the proof used as a citation-verification surface. Without those files the staged `proof.py` would fall through to a live URL fetch, hit a 403 on Cloudflare-gated publishers (e.g. The Lancet), and crash schema validation (`verification.method` becomes `None`, which the schema rejects with `None is not of type 'string'`). `stage_proof` now copies `source_dir/snapshots/` into the staging dir when present. The directory is still gitignored repo-wide (`**/snapshots/`), and CI deploy-site continues to use `--structural-only` and never re-executes `proof.py`, so this only affects the local publish flow.

## [1.34.0] - 2026-05-20

### Added

- **Deductive-theorem proof type (`claim_type: "theorem"`).** First-class support for theorem-shape proofs that the existing skill could only handle awkwardly. New `template-deductive-theorem.md` with canonical section list (Theorem statement → Proof → Corollaries → Scope → Relation to prior work → What could challenge this verdict? → Conclusion) and "textbook, not scratchwork" code-style guidance with bad/good examples. New `agents/theorem-grader.md` prompt for Step 7 grading; SKILL.md Step 7 has a strict IF/ELSE rule keyed on `claim_type` ("theorem" → always apply grader rubric, with subagent-or-inline fallback; everything else → never). New Hardening Rule 10 (Quantifier–domain match) enforced at two boundaries: source-level checks in `validate_proof.py` (with f-string AST handling) and section-presence checks in `proof_loader.py`. New `v2_theorem` schema profile in `proof_format_schema.json`, with "Implementation Regression Checks" required in `proof_audit.md`. `proof-templates.md` and SKILL.md decision flowcharts route theorem claims to the new template; new self-critique checklist item enforces textbook-style code review. Triggered by external reviewer feedback that the prior `potential-games-fip-and-pure-nash` artifact read like a "demo," not a canonical citation target.
- **Attribution-first framing for re-exposed results (`CLAIM_FORMAL.attribution`).** New optional field naming the primary source (e.g., `"Monderer & Shapley (1996), 'Potential Games,' Games and Economic Behavior 14(1), 124–143"`). When set, the artifact is presenting a verifiable companion to a published result; the primary mathematical authority is the cited source. Verdict scoreboard cell shows "after \<attribution\>" directly under the PROVED chip; verdict-source paragraph attributes the deductive argument to the cited source; renderer aliases parenthetical-suffix section headings (`## Proof (after Monderer & Shapley, 1996)` → also accessible as `Proof`) so theorem-mode template lookups work with the actual heading-as-written rendered to the reader. Resolves the "uncanny valley between textbook mathematics and software unit testing" critique a second reviewer raised.
- **`CLAIM_FORMAL.purpose` field declaring artifact value-proposition.** Five values: `fact_verification`, `computation`, `absence_search`, `consensus_review`, `methodology_demonstration`. The first four describe the engine's empirical-claim work (the bulk of the corpus); the fifth describes theorem-shape artifacts as verifiable companions to a published result — citation target is the framework, not the math. `default_purpose_for_claim_type()` and `resolve_purpose()` helpers in `tools/lib/proof_loader.py`: theorem and open_problem default to `methodology_demonstration`; everything else defaults to `fact_verification`. The existing 134-proof corpus continues to work with no per-file edits required; new proofs override by setting `purpose` explicitly. Verdict scoreboard cell now shows a "methodology demonstration" label directly under the PROVED chip when applicable, followed by the existing "after \<attribution\>" line. Following the third reviewer's strategic question — "are you looking for the math, or evaluating the proof-engine methodology?" — the artifact's purpose is now explicit on the page.
- **Proof regeneration pipeline.** Generic OpenRouter-based agent loop (`tools/proof_agent.py`) with tool dispatch, retry/backoff/fallback, per-run cap, terminate-condition gate, and transcript writing. Sandbox env-scrubbing + path containment + file ops + `run_proof_py` (`tools/lib/sandbox.py`). `tools/regen_queue.py` queue management CLI (`seed`, `pick`, `mark`, `report`); `tools/regen-queue.yaml` seeded with the 134 published proof slugs. `tools/regen_compare.py` with claim/verdict comparison and strict-claim gate. `tools/regen_pr_body.py` Markdown PR body renderer with agent stats and stripped-keys warning. `.github/workflows/daily-regen.yml` (dispatch-only) and `regen-merged.yml` (auto-flips queue on PR merge). Currently disabled pending model-quality review — cross-check gaps and citation issues observed in dry-runs aren't yet meeting the publishing bar; re-enable via the standing comments when ready. Ops runbook at `docs/regen-pipeline-ops.md`; DESIGN.md "Regeneration pipeline" section.
- **`proof-citations` PyPI package declared as runtime dependency in skill manifest.** `SKILL.md` frontmatter `compatibility:` field now lists `proof-citations` alongside `requests`; new "Setup" section in the skill body points at `pip install proof-citations` where the LLM operating the skill will see it. New `requirements.txt` next to `SKILL.md` declares `proof-citations>=1.33.0` for plugin hosts that auto-install from skill directories. All 6 shim scripts (`verify_citations`, `fetch`, `oa_lookup`, `source_credibility`, `latex_text`, `smart_extract`) wrap their `from proof_citations.X import Y` in `try/except ImportError`, re-raising with an actionable "pip install proof-citations" message instead of a bare `ModuleNotFoundError`. Covers both package-context imports and direct script execution. Reported by an external Cowork agent in a sandboxed environment that had only the skill files (no monorepo) and hit the cryptic import error.
- **DOI on embedded `Dataset` in JSON-LD.** Per-proof `ClaimReview.mainEntity` (a `Dataset` describing `proof.json`) now carries `identifier` (the DOI URL) and `sameAs` (DOI + concept-DOI URLs) when the proof has a minted Zenodo DOI. The DOI was already on the parent `ClaimReview`; surfacing it on the embedded `Dataset` deepens the dataset record for Google's Dataset rich-result crawler and any DataCite-aware consumer reading the embedded entity directly. Unminted proofs are unchanged.
- **`/sitemap_index.xml` sitemap-index file.** A standard `<sitemapindex>` document referencing the existing `/sitemap.xml`. `robots.txt` now declares both. Exists to give Google Search Console a fresh sitemap URL that bypasses the URL-level failure cache from a one-off bad fetch on `/sitemap.xml` (the fetcher recorded "Sitemap could not be read" on 2026-04-26 during the Cloudflare proxy transition and entered long backoff; resubmitting the same URL doesn't reset that). The new index URL is what GSC should be pointed at going forward.
- **New proofs.** `potential-games-fip-and-pure-nash` (deductive theorem, after Monderer & Shapley 1996; the proof that motivated the theorem-type work). `childhood-vaccines-never-placebo-tested` (absence claim). `birdsong-traffic-noise-mental-health` (qualitative).

### Fixed

- **Narrative `**Verdict: X**` declaration line carrying attribution suffix.** Option A's "attribution everywhere" framing for re-expositions leaked into `proof_narrative.md`'s verdict declaration line, which the narrative validator checks against `proof.json.verdict.value` with exact string match (`tools/lib/narrative_validator.py:141`). `template-deductive-theorem.md` now explicitly warns that the narrative verdict line must be the bare `verdict.value`; attribution belongs in the hook sentence below the declaration. `tools/generate-narratives.py` extracts `verdict.value` from the v3 structured-verdict dict before passing to `validate_narrative()`, matching `validate-site-proof.py`'s normalization.
- **Bare author-year in bolded Conclusion prefix.** The template's `**PROVED, after Monderer & Shapley (1996).**` example was unwrapped, and `verify-prose`'s `pass4_dangling_sweep` (`tools/lib/prose_reference_scan.py:542`) scans inside markdown bold. Corrected example wraps the author-year in `<!-- not-a-citation-start --><!-- not-a-citation-end -->` markers; template now explicitly notes that bold spans don't escape the linter.
- **Wayback fallback for bot-blocked URLs in `resolve-deps`.** University WAFs (e.g. `publichealth.jhu.edu`) reject programmatic fetches with 403, breaking the publish gate even when the proof itself verifies the citation via Wayback. `tools/lib/reference_resolver.py` now mirrors the wayback fallback that `proof-citations` already uses for citation verification: on live-fetch failure, retry via `web.archive.org` and tag `source_api` as `og_extraction_wayback`.
- **Whitespace canonicalization before DOI identity check in publish.** Subtle whitespace differences in the claim string (NFC normalization, trailing newline, multi-space collapse) caused `proof-site.py publish` to mis-detect a re-publish as a new proof and trip the DOI-already-minted guard. Whitespace is now collapsed prior to the identity check, matching the canonicalization used elsewhere in the pipeline.
- **Embed-panel code block readability.** Code blocks inside the `/proofs/{slug}/` embed panel inherited a low-contrast text color from a parent rule. Restored the panel's own text color so the copy-paste HTML/Markdown/SVG-URL snippets are legible.
- **Regen agent reliability.** `claim_natural` `None` guard in the regen agent loop; agent-key validation before use; cap check uses `_total_attempts` not `_calls` (per spec §3.7); None-guard for cost accumulation across multi-call runs.

## [1.33.2] - 2026-04-25

### Added

- **shields.io endpoint per proof.** Each proof now also emits `/proofs/{slug}/shields.json` in shields.io's endpoint-badge schema. Embedders point shields.io at it and pick any style: `[![proof](https://img.shields.io/endpoint?url=https://proofengine.info/proofs/SLUG/shields.json)](https://proofengine.info/proofs/SLUG/)`. Style flexibility (flat, flat-square, for-the-badge, etc.) and CDN caching come from shields.io; we emit ~70 bytes of JSON per proof. Spec: `docs/registry-protocol.md` §`GET /proofs/{slug}/shields.json`. Reference server route added; CORS header so shields.io can fetch from a browser context.

## [1.33.1] - 2026-04-25

### Changed

- **`proof-registry serve` warns on misconfigured `--base-url`.** If `--base-url` omits a port and the server is bound to a non-default port, generated `proof_url` / `homepage` fields no longer match where the server is listening. Now flagged loudly with a fix hint.
- **`proof-registry serve` shuts down gracefully on `SIGTERM`.** Previously systemd / Docker stop signals killed the process mid-request. Implemented by raising `KeyboardInterrupt` from the signal handler so the existing `except` block runs `srv.shutdown()` from the outer frame (calling `shutdown()` directly from a signal handler deadlocks because `shutdown()` waits for `serve_forever`, on the same thread).
- **`bin/proof-engine` Python preflight.** Clear error message when run on Python <3.11 instead of a cryptic `ImportError` deep in package modules.
- **`bin/proof-engine --help`** lists the four `verify` exit codes (0/1/2/3) and points at `docs/headless-verify.md`.
- **`proof-citations verify --quote` help text** warns against pre-escaped sequences (e.g. `\xc3\x97`) that land as literal backslash text and never match.
- **Catch-all 404 `detail` cleaner.** `_serve_file`'s 404 now echoes the request URL (`"no resource at /claims/..."`) instead of the on-disk filename. The URL is the client's input and meaningful to them; the on-disk path is an internal abstraction.

### Fixed

- **Deploy Site CI broke after v1.28.0** because `tools/build-site.py` imports from `proof_engine_registry` but `deploy-site.yml` never installed the local packages. Fixed in `139e648`.

## [1.33.0] - 2026-04-25

### Changed

- **Registry Protocol error responses now use RFC 7807 Problem Details.** All JSON error bodies emit `application/problem+json` with the canonical IETF fields (`type`, `status`, `title`, `detail`) plus a non-standard `code` extension preserving the legacy short machine key for log-aggregation tooling. Protocol version stays at 0.1; the change is in-place. Spec: `docs/registry-protocol.md` §Error shapes.

### Added

- `proof_engine_registry.problems` — catalog mapping each error code to (HTTP status, type URI path, title). Self-hosted registries can override the type URI base via `RegistryServer(problem_type_base=...)`.
- `proof_engine_registry.schema.Problem` dataclass + `registry-problem.schema.json` JSON schema (Draft 2020-12).
- 5 server tests + 1 conformance test pinning the new error shape (Problem body content type, required fields, type URI absoluteness, no body/traceback echo).

## [1.32.0] - 2026-04-25

### Added

- **`proof-engine-wiki` package and Claude skill.** Adapter for LLM-wiki projects (Karpathy pattern, OmegaWiki, llm_wiki). Authors mark factual statements with `{{prove: claim}}`; `proof-engine-wiki ingest PAGE.md` extracts markers, looks them up in configured registries, rewrites the page with inline link + badge embeds. `lint WIKI/` reports unresolved markers and unreachable proof URLs. Marker regex masks code fences, inline code, HTML comments, and YAML frontmatter so documentation about the syntax doesn't trigger lookups. Sibling Claude skill at `packages/proof-engine-wiki/skills/proof-engine-wiki/`.
- **Integration runbooks** for OmegaWiki and llm_wiki under `packages/proof-engine-wiki/examples/`.

## [1.30.0] - 2026-04-25

### Added

- **Per-proof badges.** Every published proof now ships a `badge.json` (compact certificate payload — claim, verdict, confidence, doi, proof_url, badge_svg_url) and a deterministic `badge.svg` (shields-style inline SVG, byte-identical across builds). Available at `/proofs/{slug}/badge.json` and `/proofs/{slug}/badge.svg` on both the public site and self-hosted registries.
- **Embed panel** on proof detail pages with copy-paste HTML, Markdown, and SVG-URL snippets.
- **Pinned verdict colors** (`PROVED`/`SUPPORTED`/`PARTIALLY VERIFIED`/`UNDETERMINED`/`DISPROVED` → fixed hex codes). Color resolution uses prefix matching so qualified verdicts (e.g. `"SUPPORTED (with unverified citations)"`) inherit the family color.

## [1.29.0] - 2026-04-25

### Added

- **Headless verify CLI.** `bin/proof-engine verify --claim "..." [--registry-check] [--registry-only] [--json]` produces a stable Verdict JSON contract (claim, claim_hash, verdict, confidence, registry_hit, generated artifacts, errors) with documented exit codes (0 pass, 1 fail, 2 error, 3 registry-only miss). Spec: `docs/headless-verify.md`.
- **Unified `bin/proof-engine` dispatcher** routing `verify`/`registry`/`citations` to the right entry points with preflight checks for missing Python modules.
- **`tools/lib/cli_verdict.py` + `tools/lib/cli_verdict_parser.py`** — verdict dataclass and v3-proof.json parser. (Note: `tools/lib/cli_verdict.py` is distinct from the pre-existing `tools/lib/verdict.py` which holds `VERDICT_TAXONOMY`.)
- **`generate-proof.sh` accepts `--`** as end-of-options separator so a claim beginning with `--` cannot be parsed as a flag.

## [1.28.0] - 2026-04-25

### Added

- **`proof-citations` package.** Standalone pip-installable library extracted from the bundled skill — `verify_citations.py`, `fetch.py`, `source_credibility.py`, `oa_lookup.py`, `latex_text.py`, plus the unicode-normalize helpers from `smart_extract.py`. Public API: `verify_citation(url, expected_quote, fact_id, ...)` returning a dict with status in `{verified, partial, not_found, fetch_failed}`. CLI: `proof-citations verify --url URL --quote "QUOTE" --fact-id ID`. The skill scripts under `proof-engine/skills/proof-engine/scripts/` are now thin shims that re-export from the package, preserving backwards compatibility for all 1062 pre-existing tests.
- **`proof-engine-registry` package and Registry Protocol v0.1.** JSON-over-HTTPS protocol for querying ("is this claim already proven?") and optionally publishing proofs. The public `proofengine.info` site emits the protocol as static JSON at build time (`/.well-known/proof-registry.json`, `/index.json`, `/claims/{hash}.json`, `/proofs/{slug}.json`). Self-hosted deployments use `proof-registry serve <proofs-dir>` (stdlib `ThreadingHTTPServer`, bearer-token auth via `hmac.compare_digest`, publish lock for concurrent-publish safety, `do_HEAD` support). Same conformance suite (10 tests) runs against both implementations. Spec: `docs/registry-protocol.md`.
- **Claim hashing.** `sha256(normalize(claim))` where normalize = NFC + lowercase + whitespace collapse + trailing-punctuation strip. Stable, pinned, treated as protocol breaking change to alter.
- **No-implicit-fallback rule.** Configured registries are queried in order; a miss does NOT cascade to the next registry unless that next registry has `fallback = true`. Privacy guarantee for private/public registry pairs.
- **`tools/build-site.py` integration.** Site builds emit Registry Protocol JSON alongside existing artifacts. Determinism preserved via fixed timestamps when supplied.

### Changed

- **Site catalog moved from `/index.json` to `/catalog.json`.** `/index.json` now serves the Registry Protocol index (different shape: claim hashes, verdicts, DOIs, badge URLs). The legacy catalog with richer per-proof metadata is at `/catalog.json`. `llms.txt`, README, and DESIGN.md updated accordingly.

## [1.27.0] - 2026-04-24

### Added

- **Evidence rail — sub-claim confidence meter.** Each proof page now shows a "SUB-CLAIM CONFIDENCE" rail card when sub-claims are present. Each SC row displays a 5-cell discrete meter (mint = holds, dark-red = fails) and is click-to-expand: clicking reveals the full sub-claim label and a confidence reason (e.g. "1 of 3 sources confirmed — threshold not met"). Data is extracted from `claim_formal.sub_claims` + `key_results` with multi-format normalisation and threshold inference.
- **Source ledger mini now collapsible.** The existing sources rail card is now wrapped in a `<details>` element alongside the SC card, with responsive layout: stacked at >1100 px, inline row at 760–1100 px, collapse-to-disclosure at <760 px.

### Fixed

- **Robustness score direction.** The ROBUSTNESS scoreboard cell previously showed `n_broke / n_total` (lower = better), which reads as a failure count. Now shows `n_withstood / n_total` (higher = better). Sublabel shows "adversarial challenges withstood" when all pass, or "N adversarial check(s) broke the proof" only when failures exist.

## [1.26.0] - 2026-04-24

### Added

- **Inspector mode split-pane layout.** The INSPECTOR tab now shows a `1.25fr / 1fr` two-column grid: narrative prose on the left, syntax-highlighted `proof.py` on the right. Replaces the previous single-panel layout.
- **Bidirectional prose↔code binding.** Every narrative paragraph is mapped to its corresponding `proof.py` section via `# ===` boundary parsing. Clicking a paragraph scrolls and highlights the matching lines; hovering a code line activates the owning paragraph. ESC unpins.
- **Dynamic `proof.py` loader.** `proof.py` is fetched on inspector activation and rendered with a lightweight regex-based Python syntax highlighter (keywords, strings, comments, constants, function calls). No bundler dependency.
- **Line-range label in code panel header.** Shows the active range (e.g. `· line 33–57`) as the user navigates sections.

### Fixed

- **`applyMode` initialization order.** `loadProofPy()` was called before `codeViewer` and `proofPyUrl` were assigned, causing an early return and leaving the code panel stuck on "loading proof.py…". Fixed by deferring `applyMode(savedMode)` until after all inspector DOM variables are set.
- **CSS grid `min-width` collapse.** `white-space: pre` code lines forced the `.src-panel` min-content to ~944 px, consuming the entire grid width and collapsing the prose column to 2 px. Fixed with `.split > * { min-width: 0; }`.
- **Double-separator section parser.** `proof.py` uses `# ====` / `# SECTION NAME` / `# ====` triple-block headers; the closing separator was parsed as a new section, producing 1-line ranges. Fixed by skipping separators whose following line does not start with `# `.

## [1.25.1] - 2026-04-22

### Added

- **`<lastmod>` per URL in `/sitemap.xml`.** `tools/build-site.py` now emits the committer date (YYYY-MM-DD, via `git log -1 --format=%cs`) of the most recent commit touching each proof's source directory. Aggregate pages (home, `/proofs/`, `/methodology/`, `/submit/`, tag pages) inherit the newest lastmod of the proofs they surface. Gives Google's crawler a priority signal for updated proofs instead of having to re-fetch and diff every URL blindly. Falls back to omitting `<lastmod>` when git history is unavailable (e.g. test fixtures built in tmp dirs) — preserves the legacy format for those assertions.

### Changed

- **Deploy workflow fetches full git history** (`fetch-depth: 0` on `actions/checkout@v4`) so `build-site.py` can resolve per-proof lastmod dates. Shallow clones only expose the tip commit and would collapse every URL's lastmod to the same date.

## [1.25.0] - 2026-04-19

### Added

- **Canonical `/proofs/` hub URL.** The proof catalog now lives at `/proofs/` instead of `/catalog/`. The URL hierarchy matches the content tree (`/proofs/` → `/proofs/:slug/`), which is the convention users path-trim to and which search engines treat as a structural signal. `/catalog/` is served as a permanent static redirect shim with `rel="canonical"` pointing to `/proofs/` and `noindex` so Google consolidates on the new URL; any old external link or bookmark keeps working.
- **Branded `/404.html` page** with a themed "proof trace" that treats the 404 itself as a claim the pipeline DISPROVED. Client-side JS infers the requested path from the URL/referrer, stamps a deterministic trace_id, and computes a nearest-slug count by running Levenshtein against a new slim `/search-index.json`. Includes a search box and three quick-jump cards (home / catalog / submit).
- **`/search-index.json`** — a slim `[{slug, claim, url}, ...]` emitted by `build-site.py`, kept separate from the full `/index.json` so the 404 path doesn't pay for audit metadata it doesn't need.
- **Reserved-slug guard in `proof-site.py publish`** — rejects slugs that would collide with top-level routes or files (`index`, `404`, `tags`, `methodology`, `submit`, `static`, `doi-index`, `sitemap`, `robots`, `llms`, `og-image`, `catalog`). Prevents a future publish from silently overwriting the hub, the redirect shim, or the 404 page.
- **`?q=` query-parameter support on the catalog hub** — `catalog.js` now pre-populates its search box from `?q=`, so the 404 page's search form and hint chips can deep-link into filtered results.

### Changed

- **`/proofs/` replaces `/catalog/` in the sitemap and `llms.txt`.** Internal hrefs across `base.html`, `landing.html`, and `proof.html` all point at `/proofs/`. The catalog hub's `<title>` and `<h1>` were updated from "catalog" to "all proofs" to match the new URL.
- **`base.html` now emits `rel="canonical"` and `og:url` only when `canonical_url` is set**, and honours an optional `noindex` context flag — used by the 404 page.

## [1.24.2] - 2026-04-19

### Fixed

- **Dataset structured data on proof pages.** `tools/lib/json_ld.py` now emits `description`, `creator`, and `license` on the `mainEntity.Dataset` in the embedded JSON-LD. Google Search Console was flagging the missing `description` as a critical issue (prevents pages from appearing in rich results) and `creator`/`license` as non-critical warnings on every proof page.

## [1.24.0] - 2026-04-19

### Added

- **`prove_holds()` theorem-mode verdict helper** in `scripts/computations.py`, the boolean counterpart to `compare()`. Pure-math claims that are inherently boolean (implications, structural theorems, existence/uniqueness) no longer have to fake a numeric comparison via `compare(x, "==", True)` — the audit output now reads as a theorem ("holds") rather than a pretend-numeric check. Coerces via `bool()` so numpy/sympy booleans (`np.bool_`, `BooleanTrue`) work correctly; raises `TypeError` on `None` so an uninitialized FACT_REGISTRY entry cannot silently disprove a theorem.
- **"Adaptation: Theorem-shaped claims" section** in `references/template-pure-math.md` with a filled-in convex-composition example, four Rule 6 cross-check options (symbolic re-derivation, exhaustive small-case, structural decomposition, or explicit `UNDETERMINED` when no mechanical check is feasible), and notes on `bool()` coercion behaviour.
- **Proof-type skim guide** in `SKILL.md` Gotchas section: a short table routing pure-math / absence-of-evidence proofs past gotchas that only apply to empirical proofs (citation handling, most source-behaviour pitfalls, `verify_extraction()`). Addresses a cowork finding that pure-math authors were being forced through empirical-only guidance.
- **Binder runtime-deps note** at the top of `references/template-pure-math.md`: the Binder launcher image ships only `sympy`, `requests`, `python-dateutil`, and `Pillow` on top of the standard library. Proofs that need `numpy`/`scipy` would crash on re-run; the template now documents this and sets a preference order (`sympy` first, stdlib second, `numpy`/`scipy` only when necessary with an explicit dep comment).

### Changed

- **Site migrated to custom domain `proofengine.info`.** `CNAME` file added at repo root; `.github/workflows/deploy-site.yml` and `validate.yml` invoke `build-site.py` with `--site-url https://proofengine.info`; `README.md` and `docs/cross-platform.md` references updated. The old `yaniv-golan.github.io/proof-engine` URL continues to work as GitHub Pages redirects to the custom domain.
- **`ClaimFormal.threshold` TypedDict widened** to accept `bool | None` so theorem-shaped claims can omit the threshold key (or set it to `None`) without failing schema validation. `claim_type` comment now lists `"theorem"` alongside `"open_problem"`.
- **Formal-summary string in `build-site.py`** omits the threshold token entirely when the value is `None` or empty, so theorem-shaped proofs render as `subject: property holds` instead of `subject: property holds None` or with a trailing space.
- **Validator (`scripts/validate_proof.py`) teaches three checks about `prove_holds()`:** `check_claim_holds_computed` accepts `prove_holds(` as a valid verdict source; `check_hardcoded_compare_input` regex is broadened to `(compare|prove_holds)` so the theorem-mode path can't bypass the hardcoded-input check; `CRITICAL_FUNCTIONS` gains `prove_holds` so unused-import detection stays correct.

### Fixed

- **`ProofSummaryBuilder` numpy scalar coercion.** `scripts/proof_summary.py` now duck-types on `.item()` to coerce numpy scalars (`np.bool_`, `np.int64`, `np.float64`) to native Python types before JSON serialization. Previously a proof that used numpy comparisons for a fact-registry `result` would fail jsonschema validation or serialize as a type that downstream consumers couldn't parse.

## [1.23.0] - 2026-04-19

### Changed

- **SKILL.md restructured.** Gotchas section grouped by theme; long-form material extracted into `references/` subfiles (progressive disclosure). Rule count synced to the canonical 9 hardening rules; step numbers renumbered after the prior edit truncation.

### Fixed

- **`bump-version.sh` sed anchoring.** The `SKILL.md` frontmatter version-line substitution previously used an unanchored pattern that also matched `format_version: 3` in the body, quietly rewriting it on every release. The sed command is now anchored to the frontmatter's `  version:` line specifically.

## [1.22.1] - 2026-04-18

### Fixed

- **Restored truncated gotchas in SKILL.md.** A prior edit had silently dropped several gotcha entries; this release restores them, syncs the rule count, and renumbers the remaining steps so the document reads coherently end-to-end.

## [1.22.0] - 2026-04-18

### Added

- **"Open in Binder" card on every published proof, not just minted ones.** Previously the re-execute call-out only appeared when a proof had been deposited to Zenodo (`doi.json` present) — roughly half of the ~127 proofs on the site. Un-minted proofs now render a Binder URL that pins to the current commit SHA (`?slug=<slug>&ref=<40-hex-sha>`), so the one-click re-execution path is available for every published proof. The trust anchor is the commit SHA embedded in the URL: the launcher fetches `proof.py` from `raw.githubusercontent.com/yaniv-golan/proof-engine/<sha>/…` — same bytes the "View proof source" section on the page rendered at that commit.
- **`--commit-sha` CLI flag on `tools/build-site.py`** (validated `^[0-9a-f]{40}$`). Falls back to `git rev-parse HEAD` when omitted; aborts with a clear message pointing at `--commit-sha` if git is unavailable (tarball builds). `.github/workflows/deploy-site.yml` passes `--commit-sha "${GITHUB_SHA}"` explicitly — auditable pin, redundant with the fallback for a `push` trigger but still wired through.
- **`tools/lib/binder_config.py`** hosting the shared `BINDER_LAUNCHER_REPO` and `BINDER_LAUNCHER_TAG` constants (previously inline in `tools/proof-site.py`). Both `proof-site.py` and `build-site.py` now import from here — `proof-site.py` can't be imported as a Python module (the filename has a hyphen), so the constants have to live in a shared library.
- Provenance copy in the "Re-execute" section branches on mode: DOI proofs say "Re-execute the exact bytes deposited at Zenodo"; un-minted proofs say "Re-execute from GitHub commit `<short-sha>` — same bytes shown above".
- `tests/test_build_site_source.py::test_unminted_proof_has_slug_mode_binder_url` end-to-end regression for the SHA-pinned rendering path.

### Changed

- **`build_citation_context` signature: `doi_data`, `binder_url_fallback`, and `commit_sha` are now keyword-only** (after a `*`). All existing call sites in `tests/test_citation.py` already passed `doi_data` by keyword, so this is source-compatible.
- **Companion to `proof-engine-binder` v1.22.0** (extension renamed `binder_doi_capture` → `binder_capture`, dual-mode capture `?doi=` OR `?slug=&ref=`, launcher cells 1/2/4 branch on mode, `postBuild` clones `proof-engine` at `v1.22.0`). Both must ship together: the main-repo `VERSION` bump to 1.22.0 is what moves `BINDER_LAUNCHER_TAG` from `v1.21.0` to `v1.22.0`, so un-minted proof Binder URLs point at the new launcher image. A stale browser tab holding a Binder URL against the pre-1.22.0 image will fall back to the built-in example DOI rather than crash.

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
