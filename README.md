# Proof Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills Compatible](https://img.shields.io/badge/Agent_Skills-compatible-4A90D9)](https://agentskills.io)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-F97316)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/plugins)
[![Cursor Plugin](https://img.shields.io/badge/Cursor-plugin-00D886)](https://cursor.com/docs/plugins)

An AI agent skill that creates formal, verifiable proofs of claims. Every fact is either computed by Python code anyone can re-run or backed by a specific source, URL, and exact quote. The LLM never asserts a fact on its own authority.

Uses the open [Agent Skills](https://agentskills.io) standard. Works with Claude, Codex CLI, Cursor, Windsurf, Manus, ChatGPT, and any other compatible tool.

## What It Does

LLMs have two weaknesses that make them unreliable for factual claims: they hallucinate facts and they make reasoning errors. This skill overcomes both by:

- **Offloading facts to citations** — every empirical claim must have a source, URL, and exact quote
- **Offloading reasoning to code** — every computation is executable Python, not prose
- **Enforcing 7 hardening rules** — closing specific failure modes where proof code looks correct but is silently wrong

The skill produces two outputs: a re-runnable `.py` proof script and a readable `.md` summary with a verdict (PROVED, DISPROVED, PARTIALLY VERIFIED, UNDETERMINED, or PROVED with unverified citations).

## Installation

### Claude Desktop

1. Click **Customize** in the sidebar
2. Click **Browse Plugins**
3. Go to the **Personal** tab and click **+**
4. Add: `yaniv-golan/proof-engine`

### Claude Code (CLI)

```bash
/plugin marketplace add yaniv-golan/proof-engine
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
2. Upload as a skill in ChatGPT settings

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
3. **Write proof code** — a self-contained Python script with hardening rules enforced
4. **Validate and execute** — run static analysis, then execute the proof
5. **Report** — deliver a `.py` proof script and `.md` summary with verdict

## What Claims Work Well?

The key limit is not hard vs easy, but **formalizable vs fuzzy**. The engine handles very nontrivial claims as long as they decompose into a finite set of extractable facts and a clear rule for what counts as proof or disproof.

Note: disproof is often easier than proof — a single counterexample or source contradiction is enough to disprove, while proof may require exhaustive coverage.

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

## License

MIT
