# Deductive-Theorem Proof Template

> You are reading one template. See [proof-templates.md](proof-templates.md) for the full index and selection guidance.

For claims that are **universally quantified theorems over an unbounded (or arbitrarily-finite) domain**, where the verdict is established by a **deductive argument**, not by computation. Examples:

- "Every finite exact-potential game has a pure Nash equilibrium."
- "For every finite group G, every subgroup of G of index 2 is normal."
- "Let G be a finite strategic-form game with the finite improvement property; then ..."

Computation in these proofs cannot be load-bearing — sampling 10,000 instances does not prove a "for all" claim. Computation here is **regression-only**: it spot-checks the implementation that decided how to *interpret* the deductive argument, never the argument itself.

## What this template produces — and what it does NOT produce

**Read this section first.** A working game-theorist + formal-methods reviewer (2026-04-28) flagged that an earlier framing of theorem proofs in this engine overstated their epistemic status. This template was revised in response. Authors using this template should set expectations correctly:

**What proof-engine theorem artifacts ARE:**
- Paper-shaped, DOI-archivable, machine-runnable **companions** to a result.
- Verifiable presentations: the `## Proof` section is a structured re-exposition of an argument; the `## Implementation regression checks` in proof_audit.md spot-check that the code-side detectors (GOP, exact-potential, pure-NE, etc.) match the formal definitions used in the argument.
- Citation-hygiene tools: when a paper uses a theorem in software, the regression-clean implementation linked to the formalization gives reviewers a place to verify the implementation matches the math.

**What they ARE NOT:**
- A substitute for citing the primary source. If your claim is a known result (which is the common case in this engine), the **primary citation is the original paper**, not the proof-engine artifact. The artifact's job is to be a verifiable presentation, not a replacement source of authority.
- A mechanized proof in the formal-methods sense (Lean, Coq, Isabelle). The artifact does not provide machine-checked induction over all instances; it provides bounded model checking + property-based regression testing of the implementation. Sampling cannot establish a "for all" claim, and we do not claim it does.
- A vehicle for novel mathematical results. If you are tempted to use this template to make a *new* claim that has not appeared in the literature, **stop**. Submit a paper. Come back here when you want the published result archived as a verifiable companion.

**The honest verdict framing.** When the result is a known theorem (the common case):
- Set `attribution` in `CLAIM_FORMAL` to the primary source (e.g., `"Monderer & Shapley (1996), \"Potential Games,\" Games and Economic Behavior 14(1), 124–143"`). The site renders this prominently next to the verdict.
- The `## Proof` heading should be `## Proof (after <Author Year>)` to make the re-exposition status visible.
- The `## Conclusion` should attribute the result to the cited source, not claim that *this artifact* established it.
- The verdict label remains `PROVED` (the existing taxonomy), but the page reads as "PROVED, after Monderer & Shapley (1996)" rather than "PROVED by us right now."

If your result IS genuinely novel (rare; you should be very sure), omit `attribution`. The artifact then claims the result on its own authority — which is exactly the bar an external reviewer will hold it to. Don't bluff.

If your claim is a finite, closed-form computation (no quantifier over an unbounded domain), use [template-pure-math.md](template-pure-math.md) instead. The "Theorem-shaped claims" adaptation in that file covers boolean theorems whose verification IS the computation; this template is for theorems whose verification is the **prose argument**.

## Hardening Rule 10 (Quantifier–domain match)

This template is the canonical home for proofs governed by [Rule 10](hardening-rules.md#rule-10-quantifier-domain-match). Follow these structural disciplines or the validator will warn:

1. **Declare `claim_type: "theorem"` in `CLAIM_FORMAL`.** This is what flips the loader from the v2 section profile to the theorem-aware profile, and what the validator's quantifier-domain check looks for. **For re-exposed known results (the common case), also set `attribution`** in `CLAIM_FORMAL` — a string identifying the primary source (e.g., `"Monderer & Shapley (1996), \"Potential Games,\" Games and Economic Behavior 14(1), 124–143"`). The site renders this prominently next to the verdict; without it, the artifact reads as a novel claim and a careful external reviewer will hold it to that bar. **Also set `purpose: "methodology_demonstration"`** to declare the artifact's value-proposition explicitly: the citation target for the *mathematical result* is the cited primary source, and this artifact is citable only as evidence of how the proof-engine framework behaves on a known theorem. The site renders a "methodology demonstration" label next to the verdict chip and adds an explicit "cite this artifact only if your work evaluates the framework or its methodology" sentence under it. If you omit `purpose`, the loader infers `methodology_demonstration` from `claim_type: "theorem"` automatically — but setting it explicitly is preferred.
2. **The deductive argument is the primary evidence.** It lives under `## Proof` in proof.md as numbered steps — see the section list below.
3. **No sampling counts in proof.md body prose.** Sentences like "We verified this on 3,670 random games" do not belong in `## Proof`, `## Theorem statement`, `## Corollaries`, or `## Scope`. They belong in proof_audit.md, in `## Implementation regression checks`.
4. **Computation role disclosed in the `method` text of every sampling fact.** Each `add_computed_fact()` call whose method describes sampling (`"sampled"`, `"random"`, `"Monte Carlo"`, etc.) MUST include role-disclosing wording in the same string within ~80 characters of the sampling token. Phrases that qualify: `"Implementation regression"`, `"regression"`, `"sanity check"`, `"spot-check"`. Without one of these, Rule 10 will warn that the sampling fact reads as primary evidence.

   **Bad:** `method=f"Sampled {N} random 2x2 games to verify the GOP detector."`
   **Good:** `method=f"Implementation regression: sampled {N} games to spot-check the GOP-detector."`

   The proximity rule means you can keep the f-string interpolation; you only need to relabel the prose.

## Canonical section list (proof.md)

Authors write these as sentence-case `##` headings. The loader normalizes them to title case for schema/lookup; you write what's shown here.

```markdown
## Theorem statement
## Proof
## Corollaries
## Scope
## Relation to prior work
## What could challenge this verdict?
## Conclusion
```

Section-by-section guidance:

- **`## Theorem statement`** — the formal claim in display math, with hypotheses listed explicitly. This is the precise statement that `## Proof` discharges. No sampling counts. No motivation paragraphs. Hypotheses first, conclusion last. Example shape:

  > **Theorem.** Let \(G\) be a finite strategic-form game with the finite improvement property. Then \(G\) has at least one pure Nash equilibrium.

- **`## Proof`** — numbered deductive steps. **This is the FIRST major content section** (no `Evidence Summary` precedes it on theorem proofs — citation/computation tables move to proof_audit.md). The argument is the verdict-bearing evidence; treat it as you would the proof body in a textbook. Lemmas can be inlined or cross-referenced, but every step must follow either by definition, by a previously cited result, or by an earlier step. **No sampling counts in this section.** A closing sentence may reference proof_audit.md for implementation regression detail; that is not a sampling count.

  **Heading convention for re-expositions.** When the result is a known theorem (you set `attribution` in `CLAIM_FORMAL`), the section heading should be `## Proof (after <Author Year>)` — e.g., `## Proof (after Monderer & Shapley, 1996)`. This signals to the reader that you are re-presenting an existing argument, not establishing a new result. Only use the bare `## Proof` heading when the proof is genuinely your own (rare; if you're tempted, re-read "What this template produces — and what it does NOT produce" above).

- **`## Corollaries`** — at least one corollary, more if natural. Each corollary has a **statement** and a **one-paragraph proof sketch**. These are the statements that citing-paper authors will quote — invest in them. For the FIP/potential-games template instance, this means at minimum:
  - "Every finite exact-potential game has a pure Nash equilibrium."
  - "Every better-response path in a finite GOP game terminates in finitely many steps."

- **`## Scope`** — explicit bullet list of what is **NOT** proved. Typical exclusions for theorem proofs in this engine: mixed equilibria, infinite domains, convergence rates, broader learning dynamics, computational complexity bounds. The list should be short and specific — generic "this is just a theorem, not the universe" hedging is not useful.

- **`## Relation to prior work`** — when the theorem is a special case, forward direction, or instance of a known result, name it explicitly with citation. For prose attributions to prior work, wrap the entire bibliographic mention in `<!-- not-a-citation-start -->Author (Year), "Title," *Journal* vol(issue), pages<!-- not-a-citation-end -->`. Do NOT include the DOI in the prose — the `verify-prose` linter pattern-matches `doi:` even inside HTML-comment wrappers and will reject the line. If you need the DOI for machine consumption, put it in `proof.json` metadata or `meta.yaml`, not in proof.md prose. Example: *"This proves the forward direction of <!-- not-a-citation-start -->Monderer & Shapley (1996), \"Potential Games,\" *Games and Economic Behavior* 14(1), 124–143<!-- not-a-citation-end -->; the converse — FIP ⟺ existence of a generalized ordinal potential — is in the same paper and is not addressed here."* The `{{cite:...}}` marker form is deprecated for new proofs pending a toolchain fix (see Rule 9).

- **`## What could challenge this verdict?`** — existing convention; stays. Adversarial checks documented as prose; if a reader could imagine a hole in the argument or in the formalization, address it here.

- **`## Conclusion`** — keep non-empty. Lead with `**PROVED.**` or another verdict prefix on its own line. The verdict-summary extractor (`tools/lib/proof_loader.py:50-68`'s `extract_verdict_summary()`) reads this section to populate cards, JSON-LD, and listing pages — an empty or fallback-shaped Conclusion will produce a fallback card on every aggregate surface.

  **Conclusion attribution discipline for re-expositions.** When `attribution` is set in `CLAIM_FORMAL`, the Conclusion must attribute the result to the cited source — not claim that *this artifact* established it. The structure is roughly: `**PROVED.** [One-sentence attribution to the primary source.] [One sentence about what this artifact contributes — typically a regression-clean implementation and a verifiable presentation of the cited argument.]` Any author-year mention in prose — including inside the bolded verdict prefix — must either carry an identifier or be wrapped in `<!-- not-a-citation-start --><!-- not-a-citation-end -->` markers, because the `verify-prose` linter flags every bare `Author (Year)` it finds (including those inside `**...**` bold). Concrete example for a Monderer & Shapley re-exposition:
  > **PROVED, after <!-- not-a-citation-start -->Monderer & Shapley (1996)<!-- not-a-citation-end -->.** Theorem (A) follows their Lemmas 2.3 + 2.5; Theorem (B) is their Lemma 4.2 specialized. This artifact is a verifiable companion to the published result: it presents the deductive argument with the canonical structure used in this engine, and the implementation regression checks confirm that our GOP, exact-potential, and pure-NE detectors agree with the formal definitions on a sampled-and-constructive test suite. The mathematical authority is the cited source; this artifact is a runnable, DOI-archivable presentation of it.

  This is the framing that resolves the "uncanny valley" critique an external reviewer raised: the artifact is not claiming to be the formal proof of a known theorem, and it is not claiming to substitute for citing Monderer & Shapley. It is claiming to be a verifiable companion, which is a coherent and useful thing to be.

  **Attribution belongs in the Conclusion prose, not in the narrative Verdict line.** The attribution-first framing above applies to proof.md's `## Conclusion` and to the rendered site verdict cell (auto-emitted from `CLAIM_FORMAL.attribution`). It does **not** extend to proof_narrative.md's `**Verdict: X**` declaration line, which the narrative validator checks against `proof.json.verdict.value` with exact string match (`tools/lib/narrative_validator.py:141`). Write that line as `**Verdict: PROVED**` (or whatever the bare `verdict.value` is) and put "after Monderer & Shapley (1996)" or equivalent attribution into the hook sentence that follows the declaration, not the declaration itself. A line like `**Verdict: PROVED, after Monderer & Shapley (1996)**` fails validation and blocks the site build.

## Sampling moves to proof_audit.md

In proof_audit.md, add an `## Implementation regression checks` section. This is where:

- The N-game spot-check tables live.
- Random-seed disclosures live.
- The "verify the implementation matches the formalization" prose lives.
- The `add_computed_fact()` outputs are summarized for human review.

Authors should NOT duplicate this content in proof.md. Cross-reference once from `## Proof`'s closing line if useful, e.g. *"See proof_audit.md, Implementation regression checks, for the spot-checks confirming our GOP-detector matches the formal definition."*

## Code style for proof.py: textbook, not scratchwork

A canonical-citation theorem artifact is read by working mathematicians and academic referees. Your proof.py should read like the source listing of a published textbook — finished, deliberate, no visible reasoning trace — not like a transcript of you working through the math at a whiteboard.

Concretely, when you write a constructive example or a definitional helper:

- **Do NOT include verification arithmetic in comments.** A reader does not need to see the work; they need to see the answer.
- **Do NOT include false starts, retractions, or "let's redo" passages.** Pick the right convention, write it cleanly, move on. Your scratch derivations belong on a notepad you discard, not in the published artifact.
- **Do NOT include reasoning words** like "Hmm", "Wait", "Actually", "Mismatch", "let's try", "this gives", "check:". They mark the comment as in-progress thinking, not finalized documentation.
- **DO include a one-paragraph docstring** stating what the function constructs and the convention it uses. One paragraph is enough. The reader trusts you to have done the math correctly; the docstring states the what and why, not the how.
- **DO include short comments only when the WHY is non-obvious** — e.g. when a sign convention or normalization choice could surprise a reader who knows the standard form.

**Bad** — visible reasoning trace, verification arithmetic, retracted false start:

```python
def two_player_congestion_game():
    # Cost of resource with k users: c(k) = k.
    # Rosenthal potential: P(s) = sum over resources r of sum_{k=1..n_r(s)} c(k).
    # n_r(s) = #players using r. c(k)=k -> contribution = k(k+1)/2.
    # (0,0): both at r0 -> P = 1+2 = 3
    # (0,1): split        -> P = 1 + 1 = 2
    # (1,1): both at r1 -> P = 1+2 = 3
    # Hmm — this gives the same P for (0,0) and (1,1). Check exactness:
    # u_0(1,0)-u_0(0,0) = -1 - (-2) = 1; P(1,0)-P(0,0) = 2-3 = -1. Mismatch!
    # The Rosenthal potential SUMS over resources used; let's redo with
    # contribution = k (cost of the k-th joiner), not k*(k+1)/2.
    # ...
    P_exact = {(0, 0): -3, (0, 1): -2, (1, 0): -2, (1, 1): -3}
    return shape, payoffs, P_exact
```

**Good** — finished docstring, one terse comment for the non-obvious convention:

```python
def two_player_congestion_game():
    """Two-player two-resource Rosenthal congestion game. Strategy 0 -> r0,
    strategy 1 -> r1. Cost of a resource with k users is c(k) = k; payoff is
    -cost. Rosenthal's exact potential is the negation of the sum, over each
    resource r, of the cumulative cost c(1) + ... + c(n_r) (negated to match
    the payoff-as-negative-cost convention used here)."""
    shape = (2, 2)
    payoffs = {...}
    # n_r(0,0)=(2,0) -> P=-(1+2)=-3;  n_r(0,1)=(1,1) -> P=-(1+1)=-2;  ...
    P_exact = {(0, 0): -3, (0, 1): -2, (1, 0): -2, (1, 1): -3}
    return shape, payoffs, P_exact
```

**Why this rule matters specifically for theorem proofs.** When the deductive argument is the verdict and the regression code is supporting infrastructure, a reader who opens proof.py expects to see *clean implementation*, not a record of how you arrived at the construction. Visible reasoning traces make a sound theorem look provisional; they signal that the artifact is a demo, not a finished citation target. This was the single remaining weakness an external reviewer flagged in the first iteration of this template's flagship proof. Don't reintroduce it.

If, while writing, you find yourself working through the math in comments — stop, finish on a notepad, and rewrite the comment as if you'd known the answer all along.

## Mandatory grader subagent at Step 7

For theorem proofs (`claim_type: "theorem"`), the inline self-critique checklist at Step 7 is necessary but not sufficient. After running the checklist, you MUST spawn a separate grader subagent before publishing. The grader prompt is at [`agents/theorem-grader.md`](../agents/theorem-grader.md). Pass the artifact's working directory and treat the grader's report as the final quality gate: Section A (structural) and Section B (citation quality) failures block publish; Section C (code style) failures are strong recommendations.

This is **NOT optional**. The grader exists because author self-blindness on prose and code style is documented — an external reviewer caught chatty/exploratory comments that the author and inline self-critique both missed on the first iteration of this template's flagship proof. The grader catches what the author cannot see in their own work.

For non-theorem claim types, do NOT spawn the grader; SKILL.md Step 7 already says inline self-critique is sufficient there. The dichotomy is strict: theorem → always grade with subagent; everything else → never.

## Python skeleton

```python
"""
Proof: [theorem statement, one line]
Generated: [date]

This is a deductive theorem proof. The verdict is established by the
argument written in proof.md's `## Proof` section. The computations below
are *implementation regression checks* — they spot-check the code that
decides whether a given finite instance satisfies the formal hypotheses,
not the deductive argument itself.

proof.md ordering (sentence case as written; loader normalizes to title):
  ## Theorem statement
  ## Proof              <- primary evidence; numbered deductive steps
  ## Corollaries        <- statement + 1-paragraph sketch each
  ## Scope              <- explicit "NOT proved" bullets
  ## Relation to prior work
  ## What could challenge this verdict?
  ## Conclusion         <- leads with **PROVED.** verdict prefix
Sampling counts must NOT appear in proof.md body prose; they live in
proof_audit.md under `## Implementation regression checks`.
"""
import os
import sys

PROOF_ENGINE_ROOT = os.environ.get("PROOF_ENGINE_ROOT")
if not PROOF_ENGINE_ROOT:
    _d = os.path.dirname(os.path.abspath(__file__))
    while _d != os.path.dirname(_d):
        if os.path.isdir(os.path.join(_d, "proof-engine", "skills", "proof-engine", "scripts")):
            PROOF_ENGINE_ROOT = os.path.join(_d, "proof-engine", "skills", "proof-engine")
            break
        _d = os.path.dirname(_d)
    if not PROOF_ENGINE_ROOT:
        raise RuntimeError("PROOF_ENGINE_ROOT not set and skill dir not found via walk-up from proof.py")
sys.path.insert(0, PROOF_ENGINE_ROOT)

from datetime import date

from scripts.computations import prove_holds
from scripts.proof_summary import ProofSummaryBuilder

# 1. CLAIM INTERPRETATION (Rule 4)
CLAIM_NATURAL = (
    "Let G be a finite strategic-form game with the finite improvement "
    "property. Then G has at least one pure Nash equilibrium."
)
CLAIM_FORMAL = {
    "subject": "finite strategic-form games with FIP",
    "property": "existence of a pure Nash equilibrium",
    "operator": "holds",
    "claim_type": "theorem",   # <-- REQUIRED for Rule 10 + theorem section schema
    "operator_note": (
        "Universally quantified over the (unbounded) class of finite "
        "strategic-form games satisfying FIP. The verdict is established "
        "by the deductive argument in proof.md's `## Proof` section "
        "(termination of any better-response path under FIP yields a "
        "pure NE at the path's terminus). The computations below are "
        "implementation regression checks; they do not establish the "
        "theorem and could not — sampling cannot prove a 'for all' claim."
    ),
}

# 2. FACT REGISTRY — A-types only; all are regression, not primary evidence.
FACT_REGISTRY = {
    "A1": {"label": "GOP-detector regression spot-check", "method": None, "result": None},
    "A2": {"label": "Better-response path termination regression", "method": None, "result": None},
}

# 3. IMPLEMENTATION REGRESSION CHECKS
# These spot-check the *code that decides whether an instance satisfies
# the hypotheses* — they do not establish the theorem. Method/label text
# must include role-disclosing wording (e.g., "Implementation regression",
# "spot-check", "regression") within ~80 chars of any sampling token, or
# Rule 10 will warn.
N_SAMPLES = 3670
gop_regression_passed = True   # filled in by your sampling code
br_regression_passed = True    # filled in by your sampling code

# 4. ADVERSARIAL CHECKS (Rule 5)
# For theorem proofs the strongest adversarial work is questioning the
# argument and the formalization, not searching for empirical
# counter-evidence. Document hole-finding work here.
adversarial_checks = [
    {
        "question": "Does the FIP hypothesis silently exclude games of interest?",
        "verification_performed": "...",
        "finding": "...",
        "breaks_proof": False,
    },
    {
        "question": "Does the proof rely on finiteness in a way the statement doesn't make explicit?",
        "verification_performed": "...",
        "finding": "...",
        "breaks_proof": False,
    },
]

# 5. VERDICT
if __name__ == "__main__":
    any_breaks = any(ac.get("breaks_proof") for ac in adversarial_checks)
    # The verdict is set by the deductive argument in proof.md.
    # The regression checks must pass for the *implementation* to be
    # trustworthy, but they do not move the verdict from PROVED on their
    # own (a regression failure is a build issue, not a counterexample
    # to the theorem).
    if any_breaks:
        verdict = "UNDETERMINED"
    else:
        verdict = prove_holds(True, label="theorem established by deductive argument")
        verdict = "PROVED" if verdict else "UNDETERMINED"

    builder = ProofSummaryBuilder(CLAIM_NATURAL, CLAIM_FORMAL)

    # Note the role-disclosing language in `method`. Required by Rule 10.
    builder.add_computed_fact(
        "A1",
        label="GOP-detector regression spot-check",
        method=(
            f"Implementation regression: sampled {N_SAMPLES} games to "
            f"spot-check the GOP-detector against the formal definition."
        ),
        result=gop_regression_passed,
    )
    builder.add_computed_fact(
        "A2",
        label="Better-response path termination regression",
        method=(
            f"Implementation regression: sanity check that better-response "
            f"paths terminate on {N_SAMPLES} sampled FIP instances."
        ),
        result=br_regression_passed,
    )

    for ac in adversarial_checks:
        builder.add_adversarial_check(
            question=ac["question"],
            verification_performed=ac["verification_performed"],
            finding=ac["finding"],
            breaks_proof=ac["breaks_proof"],
        )

    builder.set_verdict(verdict)
    builder.emit()
```

**Note on `proof.json`.** `proof.py` does NOT write `proof.json` directly. `builder.emit()` prints the JSON summary to stdout, preceded by the marker line `=== PROOF SUMMARY (JSON) ===`. The publish toolchain (`tools/proof-site.py publish`) and the site-build loader capture from stdout. To inspect `proof.json` locally without publishing, run:

```bash
python proof.py | awk '/=== PROOF SUMMARY \(JSON\) ===/{flag=1; next} flag' > proof.json
```

## Key differences from other templates

- **No `Evidence Summary` at the top of proof.md.** Citation/computation tables — if any — live in proof_audit.md. The reader of a theorem proof should see the theorem statement, then the argument, before any tables.
- **No `compare(value, "==", threshold)` idiom.** Theorem claims are boolean; use `prove_holds()` (see template-pure-math.md's "Theorem-shaped claims" adaptation) and let the deductive argument be the verdict.
- **`method` strings carry role information.** This is Phase 1's deliberate choice — keep role information in prose so the change ships without schema bumps. A structured `role: "regression"` field on `add_computed_fact()` is on the Phase 2 roadmap, not in this template.
- **Corollaries are first-class authored prose.** Citing-paper authors quote corollaries, not the parent theorem. A theorem proof with no corollaries is incomplete.
