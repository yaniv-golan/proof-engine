# Proof Narrative: <!-- not-a-citation-start -->Topaz et al. (2026)<!-- not-a-citation-end --> analyzed 2.5 million biomedical papers in PubMed Central from January 2023 through February 2026 and identified 4,046 references pointing to studies that do not exist, distributed across 2,810 papers.

## Verdict

**Verdict: PROVED**

The Topaz et al. 2026 *Lancet* correspondence reports exactly these four facts, and each one is confirmed by verbatim text in the paper itself.

## What Was Claimed?

The claim summarizes the headline findings of a recent study about citation integrity in biomedical research. A team led by Maxim Topaz at Columbia University built an automated pipeline to scan a very large slice of the published medical literature, looking for references that pointed to studies which — once you actually checked — did not appear to exist anywhere. The claim names the corpus size, the time period, the number of fabricated references found, and the number of distinct papers that contained them.

Why this matters: scientific papers cite each other to build chains of evidence. If a paper cites a study that does not exist, then any reader, peer reviewer, or clinical guideline writer relying on that citation is leaning on something fictional. The numbers in this claim describe the scale of that problem in 2023–2026 — a period that roughly overlaps with the rapid adoption of large language models, which are known to invent plausible-looking but fictitious references.

## What Did We Find?

The source paper does state all four figures, with very close textual matches.

The methods section says the team scanned "PubMed Central's Open Access subset from Jan 1, 2023, to Feb 18, 2026: 2 471 758 papers and 125 615 773 structured references." That is the corpus and the time window. The paper's own title rounds the corpus to "2·5 million biomedical papers," matching the claim's "2.5 million." The time window is summarized in the claim as "January 2023 through February 2026," which is a faithful month-level description of the exact endpoints.

The results section then says: "Among 97·1 million verified references, we identified 4046 fabricated references across 2810 papers." That is both of the remaining figures in the claim, in a single sentence. The paper's limitations section also independently restates the affected-paper count: "Of the 2810 affected papers, 98·4% had received no publisher action at the time of our audit."

A relevant nuance from the supplementary appendix is worth surfacing. The main paper uses the word "fabricated" as if these references definitely point to nothing. The supplement is more careful — it calls them "suspected fabricated references" and reports that the pipeline had 91% precision on a blinded validation by three independent reviewers. So while the paper headlines 4,046, the more rigorous reading is that roughly 91% of those — about 3,680 — are very likely true references to nothing, and the rest are likely false positives. That does not change what the paper *reports*, which is what the claim is about. But it is worth knowing if you are quoting the figure yourself.

The paper was published only eleven days before this proof was run, so there has been essentially no time for retractions or corrections to appear. No such notices are attached to the version on file.

## What Should You Keep In Mind?

This proof verifies what the paper says, not whether the world is exactly as the paper says. The pipeline's 91% precision means the 4,046 headline figure is the pipeline's count, not a ground-truth count of confirmed nonexistent studies — the rigorous count is somewhat lower. The pipeline also cannot estimate recall, so the true total of fabricated references in this corpus may be higher than 4,046 if any slipped past the filters. The paper excluded 23% of references that lacked a PubMed identifier or DOI; fabricated references could be more or less common in that excluded slice. And PubMed Central's Open Access subset is not the full biomedical literature — the paper acknowledges this. None of these caveats affects the claim, but they matter for anyone planning to *use* the 4,046 figure.

The paper itself is a single Lancet correspondence, not an independently replicated finding. As replication and follow-up work appear over time, the figures may need updating.

## How Was This Verified?

The proof located each numeric figure in a verbatim quote from the source PDF, then used the proof-engine's citation verifier to confirm that each quote actually appears in the paper. Four sub-claims, all confirmed. See [the structured proof report](proof.md) for the evidence summary, [the full verification audit](proof_audit.md) for the raw computation traces and source credibility assessment, or [re-run the proof yourself](proof.py).
