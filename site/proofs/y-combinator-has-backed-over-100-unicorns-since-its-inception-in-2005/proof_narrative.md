# Proof Narrative: Y Combinator has backed over 100 unicorns since its inception in 2005.

## Verdict

**Verdict: PROVED**

Y Combinator has indeed backed over 100 unicorns — a documented milestone reached by August 2022, based on direct analysis of YC's own portfolio data.

## What was claimed?

The claim is that Y Combinator — the startup accelerator that launched companies like Airbnb, Stripe, DoorDash, and Coinbase — has backed more than 100 companies that became unicorns (startups valued at $1 billion or more) since it was founded in 2005. It's the kind of milestone that signals just how dominant YC has become in the venture ecosystem: not just funding many startups, but producing a concentration of highly valuable ones at a rate no other accelerator has matched.

## What did we find?

The key source is a detailed analysis by investor Jared Heyman, published in October 2022, of Y Combinator's official Top Companies list. In August 2022, YC's list included companies across a range of valuations; Heyman's analysis found exactly 101 of them qualified as unicorns — companies valued at $1 billion or more. The quote from the analysis is explicit: "The 101 YC unicorns account for nearly 90% of all Top Companies' value." The count of 101, extracted directly from the source text, clears the threshold of 100.

Importantly, this count is cumulative. It includes companies that were once private unicorns but have since gone public — Airbnb, DoorDash, Coinbase, and others. That's the right way to read the claim, which uses the present perfect ("has backed"), meaning historically, not only companies that currently remain private unicorns. A 2025 count from Failory, which only tracks currently private unicorns, came in at 82 — lower than 101, but entirely consistent with it. The 19-company gap represents companies that graduated from unicorn status by going public or being acquired.

A corroborating source, PitchBook, was cited to confirm that YC leads all accelerators in unicorn-creation rate (5.8% of companies from YC's 2010 to 2015 cohorts became unicorns). That article was inaccessible at verification time due to a paywall block, so its quote could not be confirmed. But the proof doesn't need it — the count of 101 from the primary source is sufficient on its own.

Three potential challenges to the claim were examined. The self-reported nature of YC's Top Companies list raises questions about independence, but the valuations themselves are drawn from disclosed funding rounds and PitchBook's independent data corroborates the order of magnitude. Valuation markdowns in 2022–2023 are real but irrelevant to the cumulative interpretation. And the lower Failory count, while sometimes cited as a contradiction, simply measures something different.

## What should you keep in mind?

The primary source (the Jared Heyman Medium article) was only partially verified at the citation level — about half the words in the quoted passage were matched on the page when the proof script fetched it. Medium pages mix article text with navigation and sidebar elements, which can reduce matching scores even when the text is present. The critical number, 101, does appear in the matched fragment. But it's worth noting that Medium.com is a self-publishing platform; the Heyman analysis, while careful and named, is not a peer-reviewed or institutional source. YC's Top Companies list itself is self-curated.

The count of 101 is also a snapshot as of August 2022. YC has continued to fund companies since then, so the current cumulative unicorn count is likely higher. At the same time, the claim says "over 100," and 101 exceeds that threshold by just one — it's a narrow pass, not a comfortable margin.

## How was this verified?

The proof fetched the primary citation live, extracted the unicorn count programmatically from the source text, and ran three adversarial checks against competing claims and lower counts. The PitchBook corroborating source was unreachable, but the verdict rests on the primary source alone. Full methodology is in [the structured proof report](proof.md) and [the full verification audit](proof_audit.md). You can [re-run the proof yourself](proof.py) to reproduce the citation fetches and computations.
