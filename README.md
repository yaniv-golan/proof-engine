# Proof Engine

<p align="center">
  <img src="assets/banner.png" alt="Proof Engine" width="100%">
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills Compatible](https://img.shields.io/badge/Agent_Skills-compatible-4A90D9)](https://agentskills.io)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-F97316)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/plugins)
[![Cursor Plugin](https://img.shields.io/badge/Cursor-plugin-00D886)](https://cursor.com/docs/plugins)

An AI agent skill that creates formal, verifiable proofs of claims. Every fact is either computed by Python code anyone can re-run or backed by a specific source, URL, and exact quote. The LLM never asserts a fact on its own authority.

Uses the open [Agent Skills](https://agentskills.io) standard. Works with Claude Desktop, Claude Cowork, Claude Code, Codex CLI, Cursor, Windsurf, Manus, ChatGPT, and any other compatible tool.

## What It Does

LLMs have two weaknesses that make them unreliable for factual claims: they hallucinate facts and they make reasoning errors. This skill overcomes both by:

- **Offloading facts to citations** — every empirical claim must have a source, URL, and exact quote
- **Offloading reasoning to code** — every computation is executable Python, not prose
- **Enforcing 7 hardening rules** — closing specific failure modes where proof code looks correct but is silently wrong
- **Optionally offline-reproducible** — embedded page snapshots let proofs run without network access
- **Multi-mode verification** — live fetch, embedded snapshots, Wayback Machine archive, and PDF support

The skill produces three outputs: a re-runnable `proof.py` script, a reader-facing `proof.md` summary with verdict, and a `proof_audit.md` with full verification details. Verdicts: PROVED, SUPPORTED, DISPROVED, PARTIALLY VERIFIED, UNDETERMINED, or qualified variants with unverified citations.

## Installation

### Claude Desktop

1. Click **Customize** in the sidebar
2. Click **Browse Skills**
3. Go to the **Personal** tab and click **+**
4. Add: `yaniv-golan/proof-engine`

### Claude Code (CLI)

```bash
/plugin marketplace add yaniv-golan/proof-engine
/plugin install proof-engine@proof-engine-marketplace
```

### Cursor

1. Open **Cursor Settings**
2. Paste `https://github.com/yaniv-golan/proof-engine` into the **Search or Paste Link** box

### Manus

1. Download [`proof-engine.zip`](https://github.com/yaniv-golan/proof-engine/releases/latest/download/proof-engine.zip)
2. Go to **Settings** -> **Skills**
3. Click **+ Add** -> **Upload**
4. Upload the zip

### ChatGPT

1. Download [`proof-engine.zip`](https://github.com/yaniv-golan/proof-engine/releases/latest/download/proof-engine.zip)
2. Upload at [chatgpt.com/skills](https://chatgpt.com/skills)

### Codex CLI

Use the built-in skill installer:

```
$skill-installer https://github.com/yaniv-golan/proof-engine
```

Or install manually:

1. Download [`proof-engine.zip`](https://github.com/yaniv-golan/proof-engine/releases/latest/download/proof-engine.zip)
2. Extract the `proof-engine/` folder to `~/.codex/skills/`

### Other Tools (Windsurf, etc.)

Download [`proof-engine.zip`](https://github.com/yaniv-golan/proof-engine/releases/latest/download/proof-engine.zip) and extract the `proof-engine/` folder to:

- **Project-level**: `.agents/skills/` in your project root
- **User-level**: `~/.agents/skills/`

## Published Proofs

Browse verified proofs at **[yaniv-golan.github.io/proof-engine](https://yaniv-golan.github.io/proof-engine/)** — a searchable catalog of claims that have been formally proved or disproved, with full audit trails. AI agents can fetch structured proof data via the [JSON API](https://yaniv-golan.github.io/proof-engine/index.json) or paste the [llms.txt](https://yaniv-golan.github.io/proof-engine/llms.txt) URL into any LLM for a quick overview.

Want to contribute? See [how to submit a proof](https://yaniv-golan.github.io/proof-engine/submit/).

## Usage

The skill auto-activates when you ask to prove, verify, or fact-check a claim. Examples:

```
Can you prove that the sum of the first 1000 prime numbers is itself prime?
```

```
Is it really true that the State of Israel is over 70 years old? Prove it rigorously.
```

```
Fact-check this: Earth's average temperature has risen by more than 1 degree Celsius since 1880.
```

The skill will:

1. **Analyze the claim** — classify as mathematical, empirical, or mixed; identify ambiguities
2. **Gather evidence** — search for supporting AND contradicting sources (adversarial)
3. **Write proof code** — a Python script importing bundled verification modules, with hardening rules enforced
4. **Validate and execute** — run static analysis, then execute the proof
5. **Report** — deliver three files: `proof.py` (re-runnable script), `proof.md` (reader summary with verdict), and `proof_audit.md` (full verification details)

## Examples

See [`docs/examples/`](docs/examples/) for complete proof triplets generated by the skill:

| Example | Claim | Verdict |
|---------|-------|---------|
| [Purchasing Power Decline](docs/examples/purchasing-power-decline/) | US dollar lost >90% purchasing power since 1913 | PROVED |
| [Cortical Plasticity](docs/examples/cortical-plasticity/) | Adult brain incapable of experience-dependent reorganization | DISPROVED |

Each example includes a runnable `proof.py`, reader-facing `proof.md`, and detailed `proof_audit.md`.

## What Claims Work Well?

The key limit is not hard vs easy, but **formalizable vs fuzzy**. The engine handles very nontrivial claims as long as they decompose into a finite set of extractable facts and a clear rule for what counts as proof or disproof.

Note: disproof is often easier than proof — for crisp factual claims, a single counterexample suffices. For consensus-style claims, the system requires multiple independent sources (default threshold: 3).

### Good fit

| Claim | Why |
|-------|-----|
| "The sum of the first 1000 primes is itself prime" | Pure computation — sympy answers definitively |
| "Israel is over 70 years old" | Empirical with clear textual sources + date arithmetic |
| "Earth's temperature has risen more than 1°C since 1880" | Multiple authoritative sources with extractable numbers |
| "The Fibonacci sequence's 100th term is divisible by 11" | Computation, no citations needed |

### Borderline — may result in PARTIALLY VERIFIED

| Claim | Why |
|-------|-----|
| "Coffee reduces the risk of type 2 diabetes" | Requires synthesizing multiple studies with conflicting findings |
| "The Roman Empire fell because of lead poisoning" | Causal inference from messy historical evidence; competing interpretations |
| "Transformer models are more efficient than RNNs" | Depends on metric, dataset, and task — needs precise scoping first |

### Bad fit — engine will decline or return UNDETERMINED

| Claim | Why |
|-------|-----|
| "Python is the best programming language" | Opinion / value judgment — no objective criteria |
| "AI will surpass human intelligence by 2030" | Future prediction — no verifiable evidence |
| "This painting is beautiful" | Subjective — no factual decomposition possible |
| "The defendant is guilty" | Requires legal interpretation, not fact-checking |

## How This Differs From...

**Theorem provers (Lean, Coq, Isabelle)** — These prove mathematical theorems from axioms. Proof Engine verifies real-world claims against web sources and computation. Lean can prove the irrationality of sqrt(2); it cannot verify that a country's GDP grew by 5% last year. Different problem, different tool.

**Probabilistic/Bayesian scorers** — The engine produces auditable pass/fail verdicts with full evidence trails, not confidence percentages. This is deliberate: a "73% confidence" score hides *why* it's 73%. The six-tier verdict system (PROVED, DISPROVED, PARTIALLY VERIFIED, UNDETERMINED, PROVED with unverified citations, DISPROVED with unverified citations) plus the complete audit trail lets reviewers see exactly which facts held and which didn't.

**RAG pipelines** — RAG retrieves context to help an LLM generate an answer. This engine forces the LLM to *prove* its answer with re-runnable code and exact quotes. The output is a Python script (importing bundled verification modules) anyone can re-execute, not a chat response.

## Security Model

Proof scripts run in your existing agent environment (Claude Code, ChatGPT, etc.). The engine never uses `eval()` — computations use AST walking instead. `validate_proof.py` performs static analysis before execution, flagging rule violations. Code execution inherits whatever sandboxing your agent platform provides.

## The 7 Hardening Rules

| Rule | Closes Failure Mode |
|------|-------------------|
| 1. Never hand-type values | LLM misreads dates/numbers from quotes |
| 2. Verify citations by fetching | Fabricated quotes/URLs |
| 3. Anchor to system time | LLM wrong about today's date |
| 4. Explicit claim interpretation | Silent ambiguity in operators/terms |
| 5. Independent adversarial check | Confirmation bias |
| 6. Independent cross-checks | Shared-variable bugs |
| 7. Never hard-code constants | LLM misremembers formulas |

## Design

For a deeper look at the design principles, trust boundaries, hardening rules, and limitations, see [`docs/DESIGN.md`](docs/DESIGN.md).

## License

MIT
