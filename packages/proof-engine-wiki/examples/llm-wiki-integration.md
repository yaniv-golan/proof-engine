# Integrating proof-engine-wiki with llm_wiki

llm_wiki is a Tauri desktop app with an OpenAI-compatible LLM backend. The
adapter integrates via the CLI, not the Claude skill.

## Hook point: post-generate

After each ingest, llm_wiki writes a draft markdown page with numbered
references. Add a post-processing step:

    proof-engine-wiki ingest draft.md --registry-only --json

If any markers are unresolved, either:
- Show them in the llm_wiki review queue for the user to decide whether to
  commission a proof, or
- Run `proof-engine-wiki ingest draft.md` (without `--registry-only`) to
  auto-commission. This requires `proof-engine verify` and an
  `ANTHROPIC_API_KEY` in the environment.

## Marker convention

Teach the llm_wiki system prompt to wrap factual claims that warrant a proof
in `{{prove: ...}}`. Example addition to the ingest-prompt:

    When a generated wiki page contains a statistical, causal, or
    time-bounded factual claim that would benefit from independent
    verification, wrap the claim in {{prove: ...}}. Do not wrap every
    sentence — only claims whose truth a reader might want to verify.
