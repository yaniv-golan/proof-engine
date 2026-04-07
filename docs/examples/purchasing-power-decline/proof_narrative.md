# Proof Narrative: The purchasing power of the US dollar has declined by more than 90% since the Federal Reserve was established in 1913.

## Verdict

**Verdict: PROVED**

The US dollar has lost nearly 97% of its purchasing power since 1913 — far exceeding the claimed threshold of 90%, and robust to every serious challenge we tested.

## What was claimed?

The claim is that a dollar today buys less than one-tenth of what it bought when the Federal Reserve was created. This matters because it's a frequently cited argument in debates about central banking, monetary policy, and the long-term effects of inflation. If true, it means the cumulative erosion of purchasing power over the Fed's lifetime is not just significant — it's massive.

## What did we find?

The Federal Reserve Act was signed into law on December 23, 1913. That date is confirmed by two independent sources: the Wikipedia article on the Federal Reserve Act and the United States Senate Historical Office. There is no ambiguity here.

To measure how much purchasing power the dollar has lost since then, we used the Consumer Price Index — the standard government measure of what things cost over time. We pulled historical CPI data from two independent sources, both ultimately drawing from the US Bureau of Labor Statistics. The 1913 annual average CPI was approximately 9.9 (one source gives 9.883, the other rounds to 9.9 — a difference in display precision only). The 2024 annual average CPI was 313.689 in both sources, an exact match.

From those numbers, the math is straightforward: the dollar's purchasing power has declined by about 96.85%. Two independent calculations, using two independent data sources, agree within 0.005 percentage points. That kind of agreement is about as close as independently sourced data gets.

To put it concretely: one dollar in 1913 had the purchasing power of roughly three cents today. Or equivalently, you would need about $32 today to buy what cost $1 in 1913. The claim that this decline exceeds 90% understates it considerably — the actual figure is nearly 97%, clearing the threshold by almost 7 percentage points.

We also tested whether any reasonable challenge could bring the measured decline below 90%. Could the CPI be systematically overstating inflation due to quality adjustments? Even the most aggressive academic estimate of that bias, applied over 111 years, leaves the cumulative decline well above 90%. Does it matter whether you date the Fed's founding to 1913 (when the Act was signed) or 1914 (when the Reserve Banks opened)? No — using 1914 CPI data changes the result by about 0.03 percentage points. What if you used a different price index entirely, like the PCE deflator or the GDP deflator? No standard US price index over this period yields a decline below 90%.

## What should you keep in mind?

The CPI measures average price changes for a broad basket of consumer goods and services. It does not capture every individual's experience — someone who spends heavily on goods that have gotten cheaper (electronics, for example) will have experienced less purchasing power erosion than someone whose spending is concentrated in areas with above-average inflation (housing, healthcare). The 96.85% figure is a population average, not a personal one.

It's also worth noting that the CPI series used here was not called "CPI-U" until 1978. Before that, the BLS maintained a single CPI series that has been retroactively linked for continuity. The Minneapolis Fed has confirmed the pre-1978 data is "generally compatible through the present day," but the methodology has evolved over more than a century, and that evolution is baked into the numbers.

Finally, the claim attributes this decline to the Federal Reserve's establishment. The proof only addresses whether the decline happened — it does not verify causation. Many factors drive long-term inflation, including wars, government spending, supply shocks, and global economic forces. Whether the Fed caused, prevented, or merely presided over this erosion is a separate question that this proof does not answer.

## How was this verified?

This proof was built by retrieving CPI data and founding date records from live source URLs, cross-checking each key figure against two independent sources, computing the purchasing power decline mechanically from verified data, and stress-testing the result against four adversarial challenges. You can read [the structured proof report](proof.md) for the full evidence summary, review [the full verification audit](proof_audit.md) for citation details and computation traces, or [re-run the proof yourself](proof.py) to reproduce every number from scratch.