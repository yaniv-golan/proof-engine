# Proof Narrative: Nuclear power is the safest form of electricity generation with the lowest death rate per TWh produced.

## Verdict

**Verdict: UNDETERMINED**

This is a claim that sounds settled — and in some circles is treated as fact — but the data behind it is more complicated than it first appears.

## What was claimed?

The claim is that nuclear energy kills fewer people per unit of electricity produced than any other source — that if you rank every way we generate electricity by how deadly it is, nuclear sits at the very bottom. This matters because safety comparisons between energy sources come up constantly in debates about climate policy, energy transitions, and the risks of keeping nuclear plants running versus replacing them with renewables.

## What did we find?

We looked at the most widely cited dataset on this topic, compiled by Our World in Data from two peer-reviewed studies. When you rank all electricity sources by deaths per terawatt-hour — including coal, oil, gas, nuclear, hydro, solar, wind, and biofuels — nuclear comes in second, not first. Biofuels from power plants (biogas and biomass electricity) register a lower death rate than nuclear by the best available estimates.

That's the first problem. The second is more fundamental: nuclear has two substantially different death-rate estimates from two credible research teams, and they disagree by nearly eight times. One study counted mainly accident deaths (Chernobyl, Fukushima, and similar events) and put nuclear at 0.0097 deaths per TWh. Another included occupational deaths and some air-pollution effects and came up with 0.074 deaths per TWh. Under that second estimate, nuclear is actually less safe than solar and wind on a straight comparison of numbers.

There's no scientific consensus on which estimate is correct, because the disagreement is methodological — researchers genuinely differ on which categories of death should count. The data source itself, Our World in Data, explicitly flags this problem. They write that comparing nuclear, solar, and wind at the low end of the chart is "misguided" because the uncertainty ranges around these values likely overlap. In other words, the world's leading reference on this question tells us not to draw the exact conclusion this claim makes.

What isn't in dispute: nuclear is dramatically safer than fossil fuels by any measure. Coal kills roughly 2,500 times more people per unit of electricity than nuclear by the lower estimate. Gas is about 290 times more lethal. The gap between nuclear and fossil fuels is so large that it holds up even under the higher nuclear death-rate estimate.

## What should you keep in mind?

The claim as stated — that nuclear is definitively *the* safest — requires a precision the evidence can't support. The question of whether nuclear, solar, wind, or biofuels sits at the very bottom of the ranking depends entirely on which methodology you use for nuclear, and no agreed standard exists. If the M&W 2007 method is correct, nuclear isn't the safest among low-carbon sources at all. If Sovacool 2016 is correct, biofuels still edges it out.

It's also worth noting that the comparison between low-carbon sources involves very small absolute numbers. The difference between nuclear at 0.0097 and solar at 0.019 deaths per TWh is tiny in practice — both are extraordinarily safe compared to anything that burns fuel. The ranking within that group is genuinely uncertain, and the researchers who compiled the data say so.

## How was this verified?

This verdict was reached by fetching and cross-checking the underlying data from Our World in Data live, verifying all nine death-rate values against the source dataset, and running three independent adversarial checks — including one that found direct counter-evidence from the Markandya & Wilkinson (2007) nuclear estimate. You can read the full reasoning in [the structured proof report](proof.md), examine every source fetch and verification step in [the full verification audit](proof_audit.md), or [re-run the proof yourself](proof.py).