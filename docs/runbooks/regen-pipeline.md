# Runbook: Regeneration pipeline

Day-to-day operations for the proof regeneration queue. Follow each section
top-to-bottom; sections are independent.

## Check queue status

```bash
python tools/regen_queue.py report
```

Output columns: slug, status (`pending` / `in_progress` / `pr_open` /
`merged` / `failed`), last-updated timestamp.

Summary line at the bottom shows counts per status.

## Reset a stuck or failed slug

Use when a slug is stuck in `in_progress` (workflow crashed mid-run) or
`failed` and you want to retry it:

```bash
python tools/regen_queue.py mark <slug> --status pending
git add tools/regen-queue.yaml
git commit -m "regen: reset <slug> to pending"
git push
```

## Trigger a regen run for a specific slug

Manually dispatch the daily-regen workflow on GitHub Actions:

```bash
gh workflow run daily-regen.yml -f slug=<slug>
```

Watch the run:

```bash
gh run list --workflow daily-regen.yml --limit 5
gh run watch   # streams the most recent run
```

Expected outcome: a PR opens on the `regen/<run_id>/<slug>` branch.
If the run completes with no PR, check the "Pick next proof" step — it
may have skipped the slug because it was not in `pending` state.

## Run the proof agent locally

Useful for debugging a specific slug before dispatching to CI.

```bash
# Pull the current claim from the published proof
CLAIM=$(python -c "
import json; print(json.load(open('site/proofs/<slug>/proof.json'))['claim_natural'])
")

PYTHONPATH=. python tools/proof_agent.py \
  --slug <slug> \
  --claim "$CLAIM" \
  --output-dir /tmp/regen-<slug> \
  --skill-dir proof-engine/skills/proof-engine \
  --old-proof-dir site/proofs/<slug> \
  --model openai/gpt-4o \
  --fallback-model anthropic/claude-opus-4-7 \
  --transcript /tmp/regen-<slug>/transcript.json
```

Requires `OPENROUTER_API_KEY` in the environment (stored in `.env` — `source .env`).

Exit codes:

| Code | Meaning |
|------|---------|
| 0 | All artifacts produced, termination gate passed |
| 3 | Agent gave up (exhausted iterations without passing gate) |
| 4 | Invalid output (artifacts missing or malformed) |
| 2 | LLM/quota/auth error |

After a successful local run, artifacts are in `/tmp/regen-<slug>/`.

## Review a regen PR

The PR body has four sections:

**Verdict table** — old vs. new verdict. A `⚠️ changed` flag means the
verdict shifted; look at the evidence before approving.

**Claim** — verbatim from the old proof. The gate confirmed this matches
the new `claim_natural` (whitespace-normalized); you're reviewing the
same question.

**Artifacts** — byte sizes of the five output files. Unusually small
`proof.py` or `proof.json` (< 1 KB) is a sign something went wrong.

**Agent stats** — iteration count, model used, elapsed time. High
iteration counts (> 60) may indicate the agent struggled; review the
proof more carefully.

Review checklist (also in the PR body):

- [ ] Sources look plausible — URLs resolve, quotes are faithful
- [ ] Verdict matches the evidence presented
- [ ] No hardcoded dates or values (check hardening rules)
- [ ] Citations verified (or noted as unverified in the verdict)
- [ ] Claim unchanged from original

If the PR has a `⚠️ Stripped proof.json keys` warning, the agent wrote
fields the current schema doesn't recognise. Check whether they're
intentional new fields that should be added to `proof_types.py`.

## Force-mark a slug as merged (after manual merge)

If a regen PR was merged outside the normal flow (squash, direct push,
etc.) and `regen-merged.yml` didn't fire:

```bash
python tools/regen_queue.py mark <slug> --status merged
git add tools/regen-queue.yaml
git commit -m "regen: $slug → merged (manual)"
git push
```

## Change the daily schedule

The cron trigger in `.github/workflows/daily-regen.yml` is commented out
pending the first successful dry-run. To enable it:

1. Uncomment the `schedule:` block in `daily-regen.yml`.
2. Adjust the cron expression if needed (current default: `0 2 * * *` = 02:00 UTC daily).
3. Commit, push, and verify the first scheduled run in Actions.

After enabling the schedule, bump the version (`./tools/bump-version.sh`)
and tag both `proof-engine` and `proof-engine-binder` at `vMAJOR.MINOR.0`.
