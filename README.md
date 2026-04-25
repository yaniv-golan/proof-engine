# Proof Engine

<p align="center">
  <img src="assets/banner.png" alt="Proof Engine" width="100%">
</p>

[![Install in Claude Desktop](https://img.shields.io/badge/Install_in_Claude_Desktop-D97757?style=for-the-badge&logo=claude&logoColor=white)](https://proofengine.info/static/install-claude-desktop.html)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills Compatible](https://img.shields.io/badge/Agent_Skills-compatible-4A90D9)](https://agentskills.io)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-F97316)](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/plugins)
[![Cursor Plugin](https://img.shields.io/badge/Cursor-plugin-00D886)](https://cursor.com/docs/plugins)

An AI agent skill that verifies claims through code and live sources — not by asking the LLM to check itself. Every fact is either computed by Python code anyone can re-run or backed by a specific source, URL, and exact quote. The LLM never asserts a fact on its own authority.

Uses the open [Agent Skills](https://agentskills.io) standard. Works with Claude Desktop, Claude Cowork, Claude Code, Codex CLI, Cursor, Windsurf, Manus, ChatGPT, and any other compatible tool.

## Why This Exists

LLMs hallucinate facts — and they hallucinate the checks on those facts. Ask an LLM to verify its own claim and it runs the same error-prone process again. The check is circular.

Proof Engine breaks the circle by routing every claim through a gate the LLM can't fake:

- **Computations are Python** — Python doesn't hallucinate. If the LLM sets up the wrong calculation, the result is wrong in a visible, re-runnable way.
- **Citations are fetched and matched** — the script hits the URL and searches for the quoted text on the live page. A fabricated citation fails the match; a partial match downgrades the verdict so the gap is visible.
- **9 hardening rules** close the remaining escape routes — don't hand-type values (parse them from quotes), don't trust the LLM's sense of today's date (use `date.today()`), don't hard-code constants (use reviewed libraries), and don't let prose citations drift from the registered sources that back them.

The LLM is useful: it finds sources, writes code, formalizes claims. But it is never trusted to *be* the verification. When it hallucinates, the pipeline breaks visibly instead of hiding the error.

The skill produces four core outputs: a re-runnable `proof.py` script, a structured `proof.md` proof report with verdict, a `proof_audit.md` with full verification details, and a `proof_narrative.md` reader-facing narrative summary. Published proofs on the [site](https://proofengine.info/) additionally include machine-readable formats: a Jupyter Notebook (`.ipynb`) for interactive re-verification, a W3C PROV-JSON provenance trace, and an RO-Crate 1.1 research object package. Verdicts: PROVED, SUPPORTED, DISPROVED, PARTIALLY VERIFIED, UNDETERMINED, or qualified variants with unverified citations.

## Installation

<details>
<summary>Platform-specific instructions (click to expand)</summary>

### Claude.ai (Web)

1. Download [`proof-engine.zip`](https://github.com/yaniv-golan/proof-engine/releases/latest/download/proof-engine.zip)
2. Click **Customize** in the sidebar
3. Go to **Skills** and click **+**
4. Choose **Upload a skill** and upload the zip file

### Claude Desktop

[![Install in Claude Desktop](https://img.shields.io/badge/Install_in_Claude_Desktop-D97757?style=for-the-badge&logo=claude&logoColor=white)](https://proofengine.info/static/install-claude-desktop.html)

*— or install manually —*

1. Click **Customize** in the sidebar
2. Click **Browse Plugins**
3. Go to the **Personal** tab and click **+**
4. Choose **Add marketplace**
5. Type `yaniv-golan/proof-engine` and click **Sync**

### Claude Code (CLI)

From your terminal:

```bash
claude plugin marketplace add https://github.com/yaniv-golan/proof-engine
claude plugin install proof-engine@proof-engine-marketplace
```

Or from within a Claude Code session:

```
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

> **Note:** ChatGPT Skills are currently in beta, available on Business, Enterprise, Edu, Teachers, and Healthcare plans only. See [OpenAI's documentation](https://help.openai.com/en/articles/20001066-skills-in-chatgpt) for the latest on plan availability.

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

</details>

## Published Proofs

Browse verified proofs at **[proofengine.info](https://proofengine.info/)** — a searchable catalog of claims that have been formally proved or disproved, with full audit trails. AI agents can fetch structured proof data via the [JSON API](https://proofengine.info/index.json) or paste the [llms.txt](https://proofengine.info/llms.txt) URL into any LLM for a quick overview.

Want to contribute? See [how to submit a proof](https://proofengine.info/submit/).

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
5. **Report** — deliver four files: `proof.py` (re-runnable script), `proof.md` (structured proof report with verdict), `proof_audit.md` (full verification details), and `proof_narrative.md` (reader-facing narrative summary). Published proofs also get three machine-readable formats: Jupyter Notebook, W3C PROV-JSON, and RO-Crate 1.1.

## Standalone: verify citations without the skill

The citation-verification primitive is also published as a standalone package for
consumers (e.g., LLM wikis) that only need that piece:

    pip install proof-citations

See [packages/proof-citations/README.md](packages/proof-citations/README.md).

## Headless usage

    proof-engine verify --claim "The sky is blue." --registry-check --json

Checks configured registries first; generates a new proof only if no hit.
Returns JSON verdict on stdout. Exit codes:

- 0 — pass verdict (PROVED/SUPPORTED/PARTIALLY VERIFIED)
- 1 — fail verdict (DISPROVED/UNDETERMINED)
- 2 — error
- 3 — registry-only mode with no hit

Spec: [docs/headless-verify.md](docs/headless-verify.md) and [docs/registry-protocol.md](docs/registry-protocol.md).

## Examples

See [`docs/examples/`](docs/examples/) for complete proof triplets generated by the skill:

| Example | Claim | Verdict |
|---------|-------|---------|
| [Purchasing Power Decline](docs/examples/purchasing-power-decline/) | US dollar lost >90% purchasing power since 1913 | PROVED |
| [Cortical Plasticity](docs/examples/cortical-plasticity/) | Adult brain incapable of experience-dependent reorganization | DISPROVED |

Each example includes a runnable `proof.py`, structured `proof.md`, detailed `proof_audit.md`, and reader-facing `proof_narrative.md`. Published proofs on the [site](https://proofengine.info/) additionally include a Jupyter Notebook, W3C PROV-JSON provenance trace, and RO-Crate 1.1 research object package — generated at build time from the core outputs.

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

## Citing Proofs

Every proof on the site includes a **"Cite this proof"** section with export formats for researchers, journalists, and tools:

- **APA / Chicago** — plain-text citation strings
- **BibTeX / RIS** — downloadable files for reference managers (Zotero, Mendeley, etc.)
- **DOI** — 30 proofs have permanent [Zenodo](https://zenodo.org) DOIs, resolvable via `https://doi.org/10.5281/zenodo.NNNNNNN`
- **JSON-LD** — machine-readable `ClaimReview` schema with DOI in `identifier` / `sameAs` fields
- **JSON API** — each proof's `proof.json` includes a `citation` block with DOI and export URLs

Citation files (`cite.bib`, `cite.ris`, `cite.txt`) are generated at build time. DOIs are stored in `doi.json` sidecar files that persist across proof regeneration.

### Minting DOIs

DOIs are minted via Zenodo's REST API. Requires a [Zenodo personal access token](https://zenodo.org/account/settings/applications/) with `deposit:write` and `deposit:actions` scopes.

```bash
# Set your token
export ZENODO_TOKEN=your-token-here

# Mint a DOI for a proof
python tools/proof-site.py mint-doi <slug> --site-dir site

# Create a new version of an existing DOI
python tools/proof-site.py mint-doi <slug> --site-dir site --force

# Test against Zenodo sandbox first
python tools/proof-site.py mint-doi <slug> --site-dir site --sandbox
```

After minting, rebuild the site to pick up the DOI in citation files and the proof page UI.

### Citing the tool itself

The repo includes a [`CITATION.cff`](CITATION.cff) file for GitHub's "Cite this repository" feature. This cites Proof Engine as software; individual proofs use their own per-proof citations.

## How This Differs From...

**"Just ask ChatGPT to check"** — The check uses the same mechanism that produced the error. If the LLM hallucinated a fact, asking it to verify the fact just hallucination-checks the hallucination. Proof Engine moves verification out of the LLM entirely — into Python code and live page fetches that either pass or fail mechanically.

**Search-grounded AI (Perplexity, etc.)** — Search-grounded tools find relevant pages but still let the LLM summarize and interpret what's on those pages. Proof Engine goes further: it fetches the URL, matches the quoted text against the live page, and extracts values programmatically. If the match is only partial, the verdict downgrades to flag it. The difference is between "the LLM read a source and told you what it said" and "here's the code that fetched the source, checked the text, and reported what matched — run it yourself."

**Theorem provers (Lean, Coq, Isabelle)** — These prove mathematical theorems from axioms. Proof Engine verifies real-world claims against web sources and computation. Lean can prove the irrationality of sqrt(2); it cannot verify that a country's GDP grew by 5% last year. Different problem, different tool.

**Probabilistic/Bayesian scorers** — The engine produces auditable pass/fail verdicts with full evidence trails, not confidence percentages. This is deliberate: a "73% confidence" score hides *why* it's 73%. The verdict system plus the complete audit trail lets reviewers see exactly which facts held and which didn't.

**RAG pipelines** — RAG retrieves context to help an LLM generate an answer. This engine forces the LLM to *prove* its answer with re-runnable code and exact quotes. The output is a Python script anyone can re-execute, not a chat response.

## Security Model

Proof scripts run in your existing agent environment (Claude Code, ChatGPT, etc.). The engine never uses `eval()` — computations use AST walking instead. `validate_proof.py` performs static analysis before execution, flagging rule violations. Code execution inherits whatever sandboxing your agent platform provides.

## The 9 Hardening Rules

| Rule | Closes Failure Mode |
|------|-------------------|
| 1. Never hand-type values | LLM misreads dates/numbers from quotes |
| 2. Verify citations by fetching | Fabricated quotes/URLs |
| 3. Anchor to system time | LLM wrong about today's date |
| 4. Explicit claim interpretation | Silent ambiguity in operators/terms |
| 5. Independent adversarial check | Confirmation bias |
| 6. Independent cross-checks | Shared-variable bugs |
| 7. Never hard-code constants | LLM misremembers formulas |
| 8. Evidence relevance for rejections | Weak rejection sources pass threshold |
| 9. Prose references mechanically resolvable | Hand-typed author/title drifts from registered source |

## Design

For a deeper look at the design principles, trust boundaries, hardening rules, and limitations, see [`docs/DESIGN.md`](docs/DESIGN.md).

- [Registry Protocol](docs/registry-protocol.md) — the JSON-over-HTTPS contract
  for public and self-hosted proof registries.
- [Proof Badges](docs/badges.md) — compact, embeddable verdict certificates
  (`badge.json` + `badge.svg`) with copy-paste embed snippets.

## License

MIT
