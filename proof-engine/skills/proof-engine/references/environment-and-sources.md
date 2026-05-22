# Environment and Source Handling

Read this when facing fetch failures, paywalled sources, or sandboxed environments.

## Environment-Specific Notes

- **Claude Code:** Has outbound HTTP from Python, so live fetch is the primary path. `verify_all_citations()` fetches URLs directly. WebFetch/WebSearch tools return processed summaries, NOT raw page text — do not use them to populate `snapshot` fields. Keep web research (Step 2) in the main conversation thread; subagents may not have web access.
- **ChatGPT:** Python sandbox has no outbound HTTP. Use the browsing capability during Step 2 to fetch each source page and include raw page text as the `snapshot` field in `empirical_facts`.
- **Other sandboxed environments:** If Python cannot fetch URLs, use the snapshot workflow — pre-fetch page text by any available means and embed it in `empirical_facts`.

### `proof-citations` install on space-constrained or managed sandboxes

The default install — `pip install proof-citations` — assumes a writable Python site-packages directory with sufficient free space. Some sandboxes (Cowork, ChatGPT code interpreter, certain CI runners) have a small read-write filesystem that can be 100% full, or pin site-packages read-only. When `pip install` fails with `No space left on device` or `Permission denied`, fall back to a `--target` install on a writable mount:

```bash
mkdir -p /tmp/py-deps
pip install --target=/tmp/py-deps proof-citations
export PYTHONPATH="/tmp/py-deps:${PYTHONPATH:-}"
python proof.py
```

`/tmp` is typically backed by a separate filesystem in sandboxes, has more space, and is wiped between runs — fine for a one-shot proof. Setting `PYTHONPATH` makes `proof_citations` importable for that Python invocation only; no system state is modified.

If the sandbox also restricts `/tmp`, try `$HOME/.local/lib/proof-citations` instead — most sandboxes have a writable home directory even when site-packages is read-only.

If neither mount is writable, the sandbox is incompatible with `proof-citations` and the proof cannot be run there. Surface this explicitly rather than failing silently — the proof author needs to know.

## Verification Fallback Chain

1. **Live fetch** — try to fetch the URL directly. If successful, verify against live page.
2. **Snapshot** — if live fetch fails and a `snapshot` field is present, verify against the pre-fetched text. This is deterministic and user-provided.
3. **Wayback Machine** — if live and snapshot both fail and `wayback_fallback=True`, try the Wayback Machine archive. This is opt-in to avoid silently changing existing proof behavior.

## Fetch Result Statuses

- `verified` — quote found (full match or >=80% fragment coverage)
- `partial` — only a fragment matched (degraded verification)
- `not_found` — page fetched but quote not there (wrong quote or URL)
- `fetch_failed` — could not obtain page text by any method
- `github_raw` — live content fetched from raw.githubusercontent.com (GitHub repo README)

## PDF Citations

When a source is a PDF (common for academic papers, government reports, and policy documents):

**During proof creation (Step 2, LLM available):**
1. Download the PDF via Python `requests.get()` or use the environment's file tools
2. Read the PDF content — Claude Code's Read tool natively reads PDFs; other environments can use PyMuPDF (`fitz`) or `pdfplumber`
3. Find the verbatim quote in the PDF text and copy it exactly into the `quote` field
4. **Include the full PDF text as `snapshot`** in `empirical_facts` — this ensures re-run verification works without any PDF library

**At re-run time (no LLM):**
- If a `snapshot` is present, `verify_all_citations()` uses it directly (no PDF library needed)
- If no snapshot is present and the URL returns a PDF, `fetch.py` attempts extraction via `pdfplumber` or `PyPDF2` (optional dependencies: `pip install pdfplumber`)
- If no snapshot and no PDF library → `fetch_failed`

**Best practice:** Always include a `snapshot` for PDF citations. This makes the proof self-contained and reproducible regardless of the runtime environment.

## arXiv and Academic Papers

For arXiv papers, prefer `ar5iv.labs.arxiv.org/html/PAPER_ID` over `arxiv.org/abs/PAPER_ID`:
- **ar5iv** serves the full paper as HTML — all sections, tables, and figures are verifiable
- **arxiv.org/abs/** is an abstract-only page with limited verifiable text
- **arxiv.org/pdf/** returns a PDF — usable with snapshot workflow but ar5iv HTML is simpler

Example: for paper 2410.05229, cite `https://ar5iv.labs.arxiv.org/html/2410.05229v1` instead of `https://arxiv.org/abs/2410.05229`. The ar5iv version contains full paper text that `verify_all_citations()` can match against.

Note: ar5iv renders math via MathML, which `normalize_text()` handles (step 1.7). However, MathML rendering may insert spaces around operators (`Ω m = 0.315`) — the math-spacing normalization (step 3a/3b) handles this.

## Handling Paywalled Sources

Many scientific papers and reports are behind paywalls. When a key source returns 403 or requires authentication:

**If you're on campus or institutional VPN:** Just run the proof. IP-based institutional access works transparently with `requests.get()` — no changes needed. Only intervene for citations that actually fail.

**Paywalled content policy:** Snapshots of paywalled content must NOT be embedded inline in `proof.py`. Use the `snapshot_file` approach:
- Write the snapshot text to a local file: `snapshots/{fact_id}_snapshot.txt`
- Reference it in `empirical_facts`: `"snapshot_file": "snapshots/B2_snapshot.txt"`
- The `snapshots/` directory is `.gitignore`d — paywalled content stays local
- Public-source snapshots (government sites, JS-rendered pages) may remain inline

**Relative `snapshot_file` paths are anchored to the proof.py directory.** All proof templates pass `snapshot_base_dir=<proof.py dir>` to `verify_all_citations()`, so a relative path like `"snapshots/B2_snapshot.txt"` resolves against the directory containing `proof.py`, not the caller's CWD. This means the published `proof.py` runs from any directory without breaking paywalled-content lookups. Absolute paths in `snapshot_file` are honored as-is. If you call `verify_citation()` directly, pass `snapshot_base_dir=os.path.dirname(os.path.abspath(__file__))` to get the same anchoring.

**Fallback strategy for paywalled sources:**

1. **Check for open-access versions** — many papers have preprints on arXiv, bioRxiv, medRxiv, or the author's institutional page. Use ar5iv for arXiv papers (see above).
2. **OA auto-discovery** — if the citation URL contains a DOI (or the `empirical_facts` entry has a `doi` field), `verify_all_citations()` will automatically query Unpaywall for an open-access version when the original URL fails. This resolves ~30-40% of paywalled citations automatically. Results show as `fetch_mode: "oa_variant"` — note in the audit doc that the OA version may differ from the published text.
3. **Cite the abstract** — if the abstract contains the key finding, cite the PubMed or DOI abstract URL. Note "cited from abstract; full text behind paywall" in the audit doc.
4. **Use browser to capture snapshot** — if browser use is available in your environment, navigate to the paywalled URL and capture the page text. Write it to `snapshots/` via `snapshot_file` (not inline). This works when the environment runs on a machine with institutional access.
5. **Ask the user** — if verification fails with 403, ask: "Citation B2 at [URL] returned 403 (paywall). Can you open this in your browser and paste the full page text (or the full abstract/section)? A single sentence is not sufficient — I need enough context for quote matching." Write the pasted text to `snapshots/` via `snapshot_file`.
6. **Find alternative sources** — if the claim is well-established, prefer open-access sources.
7. **Last resort** — cite with whatever quote is publicly visible and mark as "Not verified (paywall)" in the audit doc.

**`snapshot_source` tagging:** When using `snapshot_file`, include a `snapshot_source` field in `empirical_facts`:
- `"paywalled:user_provided"` — user pasted from their authenticated browser
- `"paywalled:browser_capture"` — captured via browser use in the LLM environment
- `"public:pre_fetched"` — public content pre-fetched to work around bot blocking
- `"public:browser_capture"` — public content captured via browser use

The `paywalled:` prefix signals that the content must use `snapshot_file`, not inline `snapshot`.

## NCBI / PubMed / PMC

`pubmed.ncbi.nlm.nih.gov` and `pmc.ncbi.nlm.nih.gov` both return 403 / CAPTCHA for automated requests — this is by design, intended to deter scraping. Avoid using these URLs as citation targets for automated `verify_all_citations()` runs without a snapshot.

**Use E-utilities for programmatic access:** `eutils.ncbi.nlm.nih.gov` is the canonical NCBI programmatic API and is **not** rate-limited or CAPTCHA-protected for unauthenticated requests (≤3 requests/sec without an API key, ≤10 with). It exposes:

- `esearch.fcgi` — keyword search returning a list of UIDs
- `esummary.fcgi` — fetch metadata for a list of UIDs (title, authors, journal, year, DOI)
- `efetch.fcgi` — fetch full record (abstract, MeSH terms, references)

`proof_citations.resolvers.pubmed` already uses E-utilities under the hood for identifier resolution — when a citation has a `("pmid", "12345")` identifier, the resolver hits `efetch.fcgi`, not the public PubMed page. This is why `verify_citation_record` works without a snapshot for PubMed-identified citations while `verify_citation` against a `pubmed.ncbi.nlm.nih.gov` URL needs one.

**Practical guidance:**
- For **quote-on-page verification** of a PubMed article: capture a snapshot from the PMC full-text page in Step 2 (browser or PMC FTP), use `snapshot_file`, and call `verify_citation` against the article URL.
- For **bibliographic metadata verification only** (no quote): use `verify_citation_record(("pmid", "..."), expected={...})` — no snapshot needed.
- For **literature search** (absence proofs, citation discovery): construct an `esearch.fcgi` URL with `term=...` parameter and include the URL in `search_registry` — the URL is reproducible and machine-checkable.

Direct PubMed/PMC URLs are still the right thing to put in `empirical_facts[*].url` (they're the canonical citation), but pair them with a snapshot for quote verification. Cite the E-utilities URL in `search_registry` for systematic searches.

NCBI E-utilities documentation: <https://www.ncbi.nlm.nih.gov/books/NBK25500/>.

## Government Statistics Sites (.gov)

BLS, FRED, Federal Reserve, Census, and similar .gov sites systematically return 403 to automated fetching. This is the norm, not the exception. For government statistics:
- **Preferred:** Use reliable aggregators as citation URLs: rateinflation.com, inflationdata.com (for CPI); measuringworth.com, officialdata.org (for historical data); fred.stlouisfed.org (for FRED series). These are tier 3 (established reference) in credibility scoring.
- **Fallback:** Use the snapshot workflow — fetch via browser during Step 2, embed as `snapshot` in `empirical_facts`
- Note in the audit doc that aggregator sources republish data from the primary authority (e.g., "sourced from BLS via rateinflation.com")

## International Organization Sites (.org / .int)

UN agencies, ICJ, WHO, and similar intergovernmental orgs frequently return 403 or serve JS-rendered pages. Common offenders: `unrwa.org`, `ohchr.org`, `un.org` subdomains, `who.int`, `icj-cij.org`.

- **Preferred:** Use the snapshot workflow — fetch via browser during Step 2, embed as `snapshot` in `empirical_facts`. Alternatively, use `wayback_fallback=True` — these domains are well-archived.
- **Fallback:** Cite official press releases (often static HTML and more fetchable than main site pages).
- **Last resort:** Cite major news coverage of the same finding. When doing this, warn that multiple news outlets may derive from the same press release or wire report — this does NOT count as independent sourcing for Rule 6. Note in the audit doc: "Primary source at [URL] returned 403; cited via [news outlet] coverage. Independence note: [outlet] reporting derives from [primary source] press release."
- When using any alternative URL for a primary source, always document the substitution in the audit doc.

## Major News and Advocacy Sites

Many news sites (timesofisrael.com, npr.org) and advocacy/think-tank sites (fdd.org, embassies.gov.il) also return 403 or block automated fetching. This is increasingly common, not limited to .gov/.int domains.

- **Preferred:** Use the snapshot workflow — fetch via browser during Step 2, embed as `snapshot` in `empirical_facts`.
- **Fallback:** Find the same reporting on a secondary outlet that is fetchable. Document the substitution in the audit: "Primary source at [URL] returned 403; cited via [alternative outlet]. Same underlying reporting."
- **Wayback:** Use `wayback_fallback=True` — major news sites are usually well-archived.

When multiple primary sources are unfetchable for a topic, this is a signal to prioritize snapshot pre-fetching during Step 2 rather than discovering 403s at citation verification time.

## Academic Conference and Review Sites

OpenReview (openreview.net), ACL Anthology, and similar academic platforms frequently return 403 to automated fetches. These are primary sources for ML/NLP paper reviews, rebuttals, and discussion — important when evaluating claims about research papers.

- **Preferred:** Use the snapshot workflow — fetch via browser during Step 2, embed as `snapshot` in `empirical_facts`.
- **Fallback:** For OpenReview, try the paper's PDF URL directly (often more fetchable than the HTML review page). For reviewer comments, use the snapshot workflow since there is no alternative URL.
- **Wayback:** OpenReview pages are sometimes archived, but coverage is inconsistent. Try `wayback_fallback=True` but don't rely on it.

## WebFetch / WebSearch Summaries Are Not Quotes

WebFetch and WebSearch return processed summaries, not raw page text. Text from summaries must never be used directly as the `quote` field in `empirical_facts` — the wording may be paraphrased, reordered, or condensed.

**Workflow for obtaining verbatim quotes:**
1. Use WebFetch/WebSearch during Step 2 to identify relevant sources and understand their content.
2. Note the key finding and a distinctive keyword or phrase.
3. Before writing `empirical_facts`, obtain the actual page text via one of:
   - (a) Python `requests.get()` in a scratch cell — search the response for your key phrase, then copy the exact surrounding sentence as your `quote`
   - (b) Browser fetch during Step 2, embedded as `snapshot`
   - (c) Wayback Machine archive
   - (d) For PDFs: Claude Code's Read tool, PyMuPDF, or pdfplumber — save full text as `snapshot`
4. **Copy-paste the exact sentence** from the raw page text into the `quote` field. Do NOT type it from memory or rephrase it. The quote must be a substring of the page text that `verify_all_citations()` will later fetch.
5. Run `verify_citation(url, quote, fact_id)` immediately to confirm the quote verifies. If it returns `partial` or `not_found`, check `closest_passage` in the result — it shows you what the page actually says. You likely paraphrased — go back to step 3.
