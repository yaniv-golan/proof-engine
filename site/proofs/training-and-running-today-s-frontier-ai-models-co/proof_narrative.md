# Proof Narrative: Training and running today's frontier AI models consumes more electricity than entire small countries.

## Verdict

**Verdict: PROVED**

The claim holds — and by a striking margin. A single facility dedicated to training and running frontier AI models consumes roughly 28 times the electricity of an entire nation.

## What was claimed?

The idea circulating in tech and climate discussions is that the electricity appetite of modern AI — not just training a model once, but continuously training new ones and running them for millions of users — rivals or exceeds what some sovereign countries consume in a full year. If true, that would have real implications for how we think about AI's environmental footprint and energy infrastructure planning.

## What did we find?

The International Energy Agency's 2025 *Energy and AI* report provides a clear benchmark: a typical AI-focused data centre — one that handles both model training and ongoing inference — consumes as much electricity as 100,000 US households. That's not a one-time surge during a training run; it's the facility's steady annual draw.

Translating that into absolute terms is straightforward. The US Energy Information Administration reports that the average American household uses about 10,500 kilowatt-hours per year. Multiply that by 100,000 and you get roughly 1,050 gigawatt-hours (GWh) annually for a single typical AI data centre.

For comparison, Nauru — a fully recognized United Nations member state in the Pacific with a population of about 11,000 people — consumes 37.89 GWh per year in total. One AI data centre therefore uses more than 27 times what the entire country of Nauru consumes in a year.

An independent line of evidence confirms the same picture at a much larger scale. A peer-reviewed 2025 study published in *Environmental Research Letters* by Harding and Moreno-Cruz found that AI-related electricity use across the United States alone is comparable to Iceland's total energy consumption — roughly 19,580 GWh per year. That's more than 500 times Nauru's annual total, and it comes from a completely different methodology and set of institutions than the IEA calculation.

Both paths — one built from IEA and US government data, one from an academic study — arrive at the same conclusion through independent routes, with no meaningful disagreement between them.

## What should you keep in mind?

The picture is clear at the facility level, but there are important nuances. A single older training run — GPT-3, for instance, trained in 2020 — used only about 1.3 GWh, which is actually less than Nauru's annual total. The claim is not that any individual training job outpaces a country; it's that the combined, ongoing infrastructure of training plus running frontier AI does. Today's AI data centres are the relevant unit of comparison, not a single historical training event.

It's also worth noting that energy efficiency in data centres has improved substantially over the past decade, so projections can shift quickly. The IEA figures used here are from 2025 and reflect current infrastructure, but the landscape continues to evolve.

Finally, the country comparison depends on which country you pick. Nauru is the clearest case, but dozens of other UN member states — including Tuvalu, Palau, and the Marshall Islands — fall below the consumption level of a typical AI data centre. The claim isn't tied to one cherry-picked example.

## How was this verified?

This claim was evaluated by identifying a precise, measurable threshold — Nauru's entire annual electricity consumption — and checking whether a typical AI-focused data centre crosses it, using two independent source chains. You can read the full reasoning and evidence in [the structured proof report](proof.md), examine every citation and computation step in [the full verification audit](proof_audit.md), or [re-run the proof yourself](proof.py).