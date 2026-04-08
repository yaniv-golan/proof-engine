# Proof Narrative: If a company raises $5 million in Series A at a $25 million post-money valuation and exits at $500 million seven years later, the annualized return to the Series A investor exceeds 40% before dilution.

## Verdict

**Verdict: PROVED**

This is a clean mathematical result: the stated scenario produces an annualized return of about 53.4%, comfortably above the claimed 40% threshold.

## What was claimed?

The claim describes a specific Series A investment scenario and asks whether the annual return to the investor would exceed 40%. Anyone who has heard VC investors talk about "target returns" or "fund hurdle rates" has likely encountered numbers in this range — the claim is checking whether this particular deal structure actually clears that bar.

## What did we find?

The math here is straightforward. When a Series A investor puts in $5 million at a $25 million post-money valuation, they own exactly 20% of the company (5 ÷ 25 = 20%). If the company later exits at $500 million and the investor still holds that same 20% stake, their share of the exit proceeds is $100 million.

That turns a $5 million investment into $100 million — a 20× return (called a MOIC, or multiple on invested capital). Spread over 7 years, the annualized rate of return works out to 20^(1/7) − 1, which equals approximately 53.41% per year.

Two independent calculation methods — one using exact symbolic algebra (sympy) and one using a numerical equation-solver (scipy) — both produced 53.41%, agreeing to better than one part in ten trillion.

The claim's 40% threshold is therefore exceeded by about 13 percentage points. The claim is true.

## What should you keep in mind?

The single most important caveat is the phrase "before dilution." In the real world, a startup that raises a Series A will almost certainly raise additional rounds of financing before it exits. Each new round typically dilutes earlier investors — their percentage ownership shrinks as new shares are issued. If the Series A investor is diluted by 20% in each of three subsequent rounds, their stake would fall from 20% to roughly 10.24%, cutting their exit proceeds to about $51 million and reducing the annualized return to about 39.5% — just below the 40% threshold.

So the claim is mathematically true for the clean hypothetical it describes, but the "before dilution" qualifier does real work here. It is not a throwaway caveat.

## How was this verified?

This proof involves no empirical sources — it is pure mathematics, and the computation is machine-checked. You can read [the structured proof report](proof.md), review [the full verification audit](proof_audit.md), or [re-run the proof yourself](proof.py) with a standard Python installation (requires sympy and scipy).
