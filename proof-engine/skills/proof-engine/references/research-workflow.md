# Research Workflow Reference

Detailed workflow for **Step 2 (Gather Facts)**. SKILL.md gives you the three core searches; this file covers the rest of the loop — recency check, academic-paper deep dives, snapshot pre-fetching, quote harvesting, and the verify-as-you-go pattern.

For environment-specific fetch behavior (Claude Code vs. ChatGPT vs. sandboxed), paywalls, and `.gov` workarounds, see [environment-and-sources.md](${CLAUDE_SKILL_DIR}/references/environment-and-sources.md).

## Recency check

If your best sources are older than 12 months, search specifically for newer data. Fast-moving fields (AI benchmarks, politics, economics, medicine) require sources from the current year when available. Prefer recent primary sources over older ones when they cover the same data.

## Academic paper claims — additional searches

When the claim is *about* a research paper (its findings, validity, or implications), the three standard searches are necessary but insufficient. Also perform:

4. **Search for follow-up work by the same authors** — researchers often publish extensions, corrections, or reinforcing results. Search for the lead authors' names + the topic (e.g., "Mirzadeh Bengio reasoning LLM 2025"). This catches sequels the original paper's citation page may not yet list.
5. **Search for the broader phenomenon, not just the specific benchmark** — generate synonym and hypernym search terms. If the paper introduces "GSM-NoOp," also search for "irrelevant information robustness LLM," "distractor reasoning models," "math word problem perturbation." Benchmark names are jargon; the phenomenon they test has multiple names in the literature.
6. **Read the actual paper, not just its metadata** — fetch and read the PDF (or at minimum the full-text HTML). Abstracts omit methodology caveats, appendix rebuttals, and statistical details that are often decisive. If the paper has multiple arXiv versions, read the latest version and note substantive changes between versions. Use PyMuPDF or pdfplumber for PDF extraction.
7. **Check the citation network** — search for "paper title" + "cited by" or check Google Scholar / Semantic Scholar for papers that cite it. Look specifically for replications, critiques, and meta-analyses that reference the original work.

## Search for real-world demonstrations, not just benchmarks

After finding academic benchmark sources, search separately for practical applications where the claimed mechanism has been demonstrated in the wild — production systems, notable achievements, or high-profile case studies. These often live in different communities and vocabularies than the academic literature, and can provide qualitatively stronger evidence.

Example searches: "[mechanism] real-world success," "[mechanism] breakthrough application," "[domain] solved using [approach]." A benchmark paper shows something *can* work under controlled conditions; a real-world demonstration shows it *does* work. The strongest proofs combine both.

## Pre-fetch snapshots early, not late

Many news and advocacy sites now return 403 to automated fetches — not just `.gov`/`.edu`. During Step 2 research, pre-fetch the full page text for every source you plan to cite and include it as the `snapshot` field in `empirical_facts`. This avoids discovering fetch failures late during `verify_all_citations()`, which forces source substitution under time pressure.

Note: WebFetch and `verify_all_citations()` use different HTTP clients — a WebFetch 403 does not mean the script will also get 403, and vice versa. If both fail, the snapshot is your only recourse. See [environment-and-sources.md](${CLAUDE_SKILL_DIR}/references/environment-and-sources.md) for details.

## Quote harvesting (required before Step 3)

For each source you plan to cite, obtain the verbatim quote from the *rendered* page text — not from WebSearch/WebFetch summaries (which paraphrase). Open the URL in a browser or use Python to fetch and extract the visible text. The quote should match what a human reader sees on the page, not the raw HTML — `verify_all_citations()` strips HTML tags and decodes entities before matching, so your quote should be plain text without markup.

For PDFs, use your PDF Read tool or PyMuPDF. For pages that 403, use the snapshot workflow or Wayback. WebFetch/WebSearch are fine for *discovering* sources, but never use their returned text as a quote — it's summarized, not verbatim.

**Delegated research carries the same risk:** if you use a subagent, parallel tool call, or any other delegation layer to perform Step 2 research, treat all returned quotes exactly like WebSearch/WebFetch output — assume they may be paraphrased rather than verbatim. Run `verify_citation()` on each quote before writing it to `empirical_facts`, regardless of how the source was obtained.

Pay attention to:
- Lowercase vs uppercase in paper titles and benchmark names (e.g., `gsm8k` not `GSM8K`)
- En-dashes vs hyphens, curly vs straight quotes
- LaTeX artifacts on academic pages (`$\Lambda$CDM`, `$H_0$`)
- For arXiv papers, prefer `ar5iv.labs.arxiv.org/html/PAPER_ID` over `arxiv.org/abs/PAPER_ID` — the former serves full paper HTML with verifiable quotes; the latter is an abstract-only page with limited text

## Verify as you go

After assembling each `empirical_facts` entry (including its `snapshot` if pre-fetched), run a quick verification before moving to the next source:

```python
from scripts.verify_citations import verify_citation
result = verify_citation(url, quote, "test",
                         snapshot=snapshot_text,  # pass pre-fetched snapshot if available
                         wayback_fallback=True)
print(result["status"], result.get("closest_passage", ""))
```

If the status is `not_found` or `partial`, check `closest_passage` in the result — it's a **diagnostic hint** showing approximately where on the page your quote might be. Do NOT copy `closest_passage` directly into your quote — it uses simplified HTML cleaning and may have word-boundary artifacts. Instead, use it to locate the right region on the page, then copy the visible rendered text (what a reader sees, not raw HTML). If `closest_passage` is `None`, the page likely doesn't contain relevant text — find a different source.

Always pass the `snapshot` field if you have one — many sources 403 on live fetch, and omitting the snapshot will produce false `fetch_failed` results.

Do not proceed to Step 3 with fixable `not_found` or `partial` results — these usually mean the quote was paraphrased and can be corrected. However, `fetch_failed` from known-unfetchable sources (403, JS-rendered, paywalled) is expected — document these and proceed. The "with unverified citations" verdict exists for exactly this case.
