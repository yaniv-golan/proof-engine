# Proof Narrative: In venture capital, the top 10% of investments generate more than 75% of total portfolio returns, following a power law distribution.

## Verdict

**Verdict: SUPPORTED (with unverified citations)**

The core idea — that VC returns are dominated by a tiny fraction of investments — is well supported by real data. But the specific numbers in the claim ("top 10%" and "more than 75%") are not confirmed verbatim by any publicly accessible primary study.

## What was claimed?

The claim is that venture capital returns follow a power law: a small minority of portfolio investments drive the overwhelming majority of total gains. Specifically, it puts numbers on that intuition — the top 10% of deals generate more than 75% of total returns. This framing appears frequently in VC circles, used to argue that the asset class rewards concentrated bets, that fund managers must swing for large outcomes, and that conventional diversification logic from public markets does not apply.

## What did we find?

The directional claim is credible. The best available empirical evidence comes from an Andreessen Horowitz analysis of Horsley Bridge Partners' portfolio — more than 7,000 venture investments made between 2000 and 2014. That dataset found that roughly 6% of investments, representing just 4.5% of capital deployed, generated approximately 60% of all returns. That is a striking concentration: the bottom 94% of deals produced only 40% of the gains.

Cambridge Associates has separately reported that the top 10% of VC fund managers generate more than 90% of the industry's total returns — a power law at the manager level rather than the individual deal level.

Together, these findings confirm that power law concentration is real in venture capital. The pattern shows up at multiple levels of analysis: within a single fund's portfolio (a16z/Horsley Bridge data), and across the universe of fund managers (Cambridge Associates).

However, the specific "10% of investments → >75% of returns" threshold in the claim could not be verified from any publicly accessible primary source. The a16z/Horsley Bridge finding points to an even more extreme concentration (6% of deals → 60% of returns), which is directionally consistent but numerically different. The Cambridge Associates figure applies to managers, not individual investments. The "10%/75%" framing circulates widely as a convenient rule of thumb in VC writing, but it appears to be a stylized approximation rather than a direct finding from a primary dataset. Additionally, one of the three cited sources (an HBR article) returned an HTTP 404 error and could not be verified at all.

## What should you keep in mind?

The concept of "top 10%" is slippery. Does it mean the top decile by number of investments, or by capital deployed? Measured by count, the Horsley Bridge data suggests the concentration is even more severe — only 6% of deals (not 10%) drove 60% of returns. Measured by capital, the picture shifts depending on whether a "top" investment is one that generated the most return or one that received the most capital upfront.

The power law pattern also varies by fund type and stage. Early-stage seed and Series A funds tend to show more extreme concentration than growth-stage funds, because early failures are complete write-offs while early winners compound for longer. A claim about "venture capital" as a monolithic category blurs these differences.

Finally, it is worth noting that both Cambridge Associates and Preqin are subscription-only benchmarking services. Much of the quantitative data cited in popular VC discourse traces back to proprietary databases that are not publicly verifiable, which is part of why the specific "10%/75%" threshold cannot be confirmed from public sources.

## How was this verified?

This proof fetched three citations live, extracted numeric values from verified text via `parse_number_from_quote()`, and ran three adversarial checks to test whether the specific threshold was verifiable. You can read [the structured proof report](proof.md) for the full evidence summary, review [the full verification audit](proof_audit.md) for citation details, or [re-run the proof yourself](proof.py) to reproduce the analysis.
