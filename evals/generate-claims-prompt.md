Generate exactly <n> claims in the domain of <y> for testing a formal proof-verification system. The system proves or disproves claims using Python code, web citations, and mathematical reasoning.

Your goal: generate claims that STRESS-TEST the system, not easy wins. Weight toward claims that are harder to verify formally.

## Distribution (approximate)

- ~15% pure math/logic claims (computations, primality, divisibility, inequalities)
- ~25% numeric empirical claims (statistics, percentages, measurements requiring multiple sources and cross-checks)
- ~20% compound claims (X AND Y, X BUT NOT Y, if X then Y — requiring decomposition)
- ~15% common myths or widely-believed-but-false claims (the system should disprove these)
- ~15% conflicting-evidence claims (where reputable sources disagree, or the truth is nuanced)
- ~10% traps the system should REJECT: opinions disguised as facts, unfalsifiable predictions, claims requiring unavailable data

## Rules

1. Each claim must be a single declarative sentence, stated as fact
2. Do NOT include the expected verdict or answer
3. Claims must be specific enough to have a definitive true/false evaluation (except traps, which intentionally don't)
4. Vary difficulty: some claims should be straightforward to verify, others should require multiple sources, careful interpretation, or non-obvious computation
5. For empirical claims, prefer claims verifiable from publicly accessible sources (.gov, .org, Wikipedia, major news). Avoid claims that require paywalled databases or proprietary data
6. For math claims, vary between arithmetic/number-theory (solvable with basic Python) and claims requiring symbolic math (sympy)
7. Compound claims should use different logical connectives (AND, OR, BUT NOT, IF-THEN, comparative chains like A > B > C)
8. Myths should be things many people believe that are actually false or misleading
9. Do NOT prefix claims with their category or type — just the claim text
10. One claim per line, no numbering, no blank lines, no commentary

## What makes a claim hard to verify (prefer these)

- Requires reconciling data from sources that use different methodologies or time periods
- Involves percentages or ratios where the base matters (e.g., "GDP growth" — real vs nominal?)
- Has commonly-cited numbers that are slightly wrong (e.g., popular approximations)
- Requires distinguishing correlation from causation
- Has ambiguous terms that need explicit interpretation (e.g., "largest" — by area? population? GDP?)
- Involves thresholds where the truth is close to the boundary (e.g., "more than 50%" when it's actually 51%)

Output ONLY the claims, one per line. No headers, no categories, no explanations.
