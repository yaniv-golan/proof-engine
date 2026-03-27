#!/bin/bash
# Runs a single proof-engine eval claim through Claude Code CLI.
# Called by run-evals.sh — not typically invoked directly.
#
# Usage: run-single-eval.sh <output-dir> <model> <claim>
#
# Phase 1: Run /proof-engine on the claim
# Phase 2: Ask for skill-improvement feedback
#
# Writes proof artifacts + feedback.md to <output-dir>.
# On success, creates .success marker. On failure, creates .failed marker.
# The worker NEVER exits nonzero — failures are recorded, not propagated.
set -uo pipefail
# NOTE: no set -e — we handle errors explicitly so one failed claim
# doesn't kill the orchestrator's wait.

OUTPUT_DIR="$1"
MODEL="$2"
CLAIM="$3"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/proof-engine"

mkdir -p "$OUTPUT_DIR"

# Clean stale markers and artifacts from previous runs
rm -f "$OUTPUT_DIR/.success" "$OUTPUT_DIR/.failed"
rm -f "$OUTPUT_DIR/proof.py" "$OUTPUT_DIR/proof.md" "$OUTPUT_DIR/proof_audit.md"
rm -f "$OUTPUT_DIR/phase1.log" "$OUTPUT_DIR/feedback.md"

# Save the original claim for later reference
echo "$CLAIM" > "$OUTPUT_DIR/claim.txt"

# Generate session ID for two-phase conversation
SESSION_ID="$(uuidgen | tr '[:upper:]' '[:lower:]')"

echo "[$(date '+%H:%M:%S')] Starting: $(basename "$OUTPUT_DIR")"

# --- Phase 1: Run the proof ---
PHASE1_EXIT=0
claude -p \
    --plugin-dir "$PLUGIN_DIR" \
    --dangerously-skip-permissions \
    --model "$MODEL" \
    --session-id "$SESSION_ID" \
    "Using /proof-engine, prove that: $CLAIM" \
    > "$OUTPUT_DIR/phase1.log" 2>&1 \
    || PHASE1_EXIT=$?

if [ $PHASE1_EXIT -ne 0 ]; then
    echo "[$(date '+%H:%M:%S')] Phase 1 FAILED (exit $PHASE1_EXIT): $(basename "$OUTPUT_DIR")"
    echo "Phase 1 failed with exit code $PHASE1_EXIT. See phase1.log for details." > "$OUTPUT_DIR/.failed"
    exit 0  # exit 0 so orchestrator's wait doesn't fail
fi

echo "[$(date '+%H:%M:%S')] Phase 1 done: $(basename "$OUTPUT_DIR")"

# --- Phase 2: Collect feedback ---
read -r -d '' FEEDBACK_PROMPT << 'FEEDBACK_EOF' || true
You just ran the proof-engine skill. You are now a QA tester filing bug reports — not writing a review. Be specific and critical. Vague praise is useless. "N/A" is better than "worked fine."

Before answering, re-read the generated proof.py, proof.md, and proof_audit.md files in the current directory. Also re-run the validator on proof.py using its full path from the skill's scripts directory (the same path you used during the proof workflow). Base your answers on what you observe in the actual files and validator output, not just your memory of writing them.

Only report issues the SKILL could fix. If the claim was inherently hard or ambiguous, that's not a skill issue.

For each probe below, you MUST output the probe heading exactly as shown (e.g., "## Probe 1: Script errors"), followed by either your issue report(s) in the format below, or just "N/A" on the next line. Every probe heading must appear in your output.

### Format per issue (repeat block if multiple issues under one probe):
- **Component:** [exact filename: SKILL.md | hardening-rules.md | proof-templates.md | output-specs.md | self-critique-checklist.md | advanced-patterns.md | environment-and-sources.md | extract_values.py | verify_citations.py | computations.py | smart_extract.py | source_credibility.py | validate_proof.py]
- **Function:** [exact function name, or "N/A" if not function-specific]
- **Severity:** [blocker | major | minor]
- **What happened:** [one concrete sentence describing the observable problem]
- **Expected:** [what should have happened instead]
- **Workaround:** [what you did instead, or "none — proof failed"]

---

## Probe 1: Script errors
Did any bundled script throw an error, return unexpected results, or fail to handle your input?

## Probe 2: Instruction gaps or contradictions
Was there any point where SKILL.md or a reference file didn't tell you what to do, told you conflicting things, or you had to guess? Quote the confusing or missing instruction.

## Probe 3: Validation accuracy
Did validate_proof.py flag something that was actually correct (false positive)? Did you find a bug in your proof that validate_proof.py missed (false negative)?

## Probe 4: Template fit
Did the template from proof-templates.md match your claim type? Did you have to significantly modify it or build from scratch?

## Probe 5: Workflow deviations
Did you follow Steps 1–6 in order? If you backtracked, skipped, or improvised, describe what and why.

## Probe 6: Output format
Was output-specs.md clear enough for writing proof.md and proof_audit.md? Were the JSON summary requirements clear?

## Probe 7: Anything else
Anything that slowed you down, felt wrong, or that you'd want fixed if you ran this skill 100 more times?
FEEDBACK_EOF

PHASE2_EXIT=0
claude -p \
    --plugin-dir "$PLUGIN_DIR" \
    --dangerously-skip-permissions \
    --model "$MODEL" \
    --resume "$SESSION_ID" \
    "$FEEDBACK_PROMPT" \
    > "$OUTPUT_DIR/feedback.md" 2>&1 \
    || PHASE2_EXIT=$?

if [ $PHASE2_EXIT -ne 0 ]; then
    echo "[$(date '+%H:%M:%S')] Phase 2 FAILED (exit $PHASE2_EXIT): $(basename "$OUTPUT_DIR")"
    echo "Phase 2 failed with exit code $PHASE2_EXIT. Phase 1 succeeded — see phase1.log." > "$OUTPUT_DIR/.failed"
    exit 0
fi

# Validate feedback.md has all 7 probe headings
MISSING_PROBES=""
for n in 1 2 3 4 5 6 7; do
    if ! grep -q "^## Probe $n" "$OUTPUT_DIR/feedback.md" 2>/dev/null; then
        MISSING_PROBES="$MISSING_PROBES $n"
    fi
done
if [ ! -s "$OUTPUT_DIR/feedback.md" ] || [ -n "$MISSING_PROBES" ]; then
    echo "[$(date '+%H:%M:%S')] Phase 2 produced malformed feedback: $(basename "$OUTPUT_DIR")"
    echo "Phase 2 exited 0 but feedback.md is missing probe headings:$MISSING_PROBES. Phase 1 succeeded." > "$OUTPUT_DIR/.failed"
    exit 0
fi

# Mark success — this is the idempotency marker (NOT feedback.md)
touch "$OUTPUT_DIR/.success"
echo "[$(date '+%H:%M:%S')] Done: $(basename "$OUTPUT_DIR")"
