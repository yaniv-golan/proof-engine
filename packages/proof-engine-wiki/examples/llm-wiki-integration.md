# Proposed integration: proof-engine-wiki + llm_wiki

> **Status: design sketch, not a shipped integration.** No code in
> [llm_wiki](https://github.com/nashsu/llm_wiki) currently invokes
> proof-engine-wiki. This document describes how a maintainer of either
> project (or a contributor) could wire the two together. If you're working
> on this, please open an issue or PR — we're happy to pair.

llm_wiki ([github.com/nashsu/llm_wiki](https://github.com/nashsu/llm_wiki))
is a Tauri desktop app with an OpenAI-compatible LLM backend. Because it
isn't Claude-Code-native, an integration would route through the
proof-engine-wiki CLI rather than the sibling Claude skill.

## Hook point: post-generate (proposed)

After llm_wiki finishes generating a draft markdown page (with numbered
references), the Tauri Rust backend would shell out to:

    proof-engine-wiki ingest draft.md --registry-only --json

`--registry-only` means: only resolve markers against existing proofs in
configured registries; never commission a new proof. This keeps the path
zero-cost in the common case.

If unresolved markers come back, llm_wiki has two reasonable choices:

- **Surface in the review queue** — let the user decide whether each
  unresolved claim warrants commissioning a proof. The default mode for
  a desktop wiki where the human is in the loop.
- **Auto-commission** — drop `--registry-only` and let `ingest` invoke
  `proof-engine verify` per miss. Requires `ANTHROPIC_API_KEY` in the
  environment because proof generation uses Claude. Fits CI-style or
  trusted-source workflows.

A Rust shell-out (sketch — not tested against llm_wiki's actual
codebase):

```rust
use std::process::Command;

let out = Command::new("proof-engine-wiki")
    .args(["ingest", &draft_path, "--registry-only", "--json"])
    .output()?;
let report: serde_json::Value = serde_json::from_slice(&out.stdout)?;
// Inspect report.misses, report.resolved_from_registry, etc.
```

## Marker convention

The contract is the `{{prove: ...}}` marker. For llm_wiki to feed claims
into the proof pipeline, its generation prompt would need a clause like:

> When a generated page contains a statistical, causal, or time-bounded
> factual claim whose truth a reader might want to verify independently,
> wrap the claim in `{{prove: ...}}`. Do **not** wrap every sentence —
> only claims that earn a proof.

The "not every sentence" rule is essential: proofs cost money or time.
Authors / generators should reserve markers for load-bearing claims,
not blanket every assertion.

## What's missing for an actual integration

- A llm_wiki contributor to add the post-generate shell-out and surface
  proof-engine-wiki findings in the app's review UI.
- A system-prompt patch teaching the generator to use `{{prove:}}`
  selectively.
- Bundling decisions: should llm_wiki ship with `proof-engine-wiki`
  pre-configured to point at the public proofengine.info registry?
  Should there be a "Settings → External proof registries" panel?

The marker contract and CLI surface of `proof-engine-wiki` are stable as
of v1.33.1. If you're contributing to llm_wiki — or any
non-Claude-Code-native LLM wiki — the CLI is the supported integration
surface. Open an issue at
[proof-engine](https://github.com/yaniv-golan/proof-engine/issues) or
mention the proof-engine-wiki package in an llm_wiki issue if you want
to pair on a real implementation.
