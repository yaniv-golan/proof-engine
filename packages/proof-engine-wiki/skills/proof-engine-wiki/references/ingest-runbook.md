# Ingest runbook (for Claude)

When asked to run ingest on a wiki page:

1. **Confirm the target.** Read the file or ask for its path.
2. **Dry-run first.** `proof-engine-wiki ingest PATH --dry-run --json`.
3. **Review the output.** Report to the user:
   - Total markers found
   - How many resolved from the registry (no cost)
   - How many would be commissioned (cost = one LLM proof per claim)
4. **Confirm with the user** before running without `--dry-run`, especially
   if `generated` would be > 0.
5. **Run for real** once confirmed.
6. **Report the final counts** and show the rewritten diff.

## Flags to know

- `--registry-only` — skip generation entirely. Use for CI or when cost is a
  concern.
- `--model sonnet` — cheaper than opus for straightforward claims.
- `--dry-run` — preview without writing.
