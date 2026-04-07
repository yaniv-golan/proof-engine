# Proof Narrative: AI-generated code has fewer security vulnerabilities than typical human-written code

## Verdict

**Verdict: DISPROVED (with unverified citations)**

The evidence runs in the opposite direction: across multiple independent studies, AI-generated code consistently shows *more* security vulnerabilities than code written by humans without AI assistance.

## What was claimed?

The claim is that using AI tools to write code — think GitHub Copilot, ChatGPT, Claude, or similar assistants — actually makes your code safer, producing fewer security holes than a human developer would on their own. It's a belief that's spread quickly as AI coding tools have become mainstream, and it matters: if true, it would be a compelling reason to adopt these tools widely. If false, developers relying on AI-generated code may be unknowingly shipping vulnerabilities.

## What did we find?

Four independent studies from different research teams, using completely different methods, all reached the same conclusion: AI-generated code is not more secure than human-written code — it's less secure.

A controlled experiment at Stanford University put this to the test directly. Researchers gave 47 developers a set of programming tasks, some with access to an AI assistant and some without. The result was unambiguous: participants who used the AI assistant wrote significantly less secure code. Strikingly, they were also more confident that their code was secure — a combination that is particularly dangerous in practice.

Veracode tested over 100 large language models across 80 real-world coding tasks specifically designed to probe for common security weaknesses. In 45% of test cases, the models produced code containing vulnerabilities from the OWASP Top 10 — the industry's standard list of the most critical security risks. In Java specifically, the security failure rate reached 72%. These weren't obscure edge cases; they were well-documented vulnerability classes that secure development practices are specifically designed to prevent.

A third analysis took a different angle, looking at actual code being submitted to real open-source projects. CodeRabbit examined 470 GitHub pull requests — 320 that included AI-generated code, and 150 written entirely by humans. AI-authored pull requests had 1.7 times more issues overall, and security issues specifically were up to 2.74 times higher than in human-written code.

Finally, researchers at Georgia Tech tracked confirmed security vulnerabilities in open-source software that could be attributed to AI-authored code, finding 74 CVEs across tens of thousands of analyzed advisories. The researchers were explicit: given how widely AI coding tools are now used, the idea that AI code is dramatically safer simply isn't credible.

## What should you keep in mind?

The research spans 2023 through early 2026, meaning some early studies tested older AI models like Codex. However, the more recent studies — including Veracode's 2025 report and CodeRabbit's December 2025 analysis — tested current-generation models and found the same pattern. Improved syntax accuracy (AI models have gotten much better at writing code that *runs*) has not translated into improved security.

The evidence here is about AI-generated code in general, not every possible narrow context. It's conceivable that for specific, well-constrained tasks, AI tools perform differently — but no study has established such a domain.

One of the four sources (a Georgia Tech study reported by The Register) was only partially verified during this proof process, meaning its specific quote couldn't be matched with full confidence. However, the disproof doesn't depend on it: the three fully verified sources alone exceed the evidence threshold.

Three of the four citations come from industry publications or company research blogs rather than academic journals. The findings from those sources are independently corroborated by the Stanford academic study, and each reports research from credible institutions. Still, readers who want maximum rigor should weight the Stanford study most heavily.

## How was this verified?

This claim was evaluated by collecting independent sources that bear directly on whether AI-generated code is more or less secure than human-written code, then verifying each source by fetching it live and confirming quoted findings. The process required at least three independent, verified sources finding equal or greater vulnerability rates in AI code to render a disproof. You can read [the structured proof report](proof.md) for a full evidence summary, inspect [the full verification audit](proof_audit.md) for source credibility assessments and citation verification details, or [re-run the proof yourself](proof.py) to reproduce the findings.