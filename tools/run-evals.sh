#!/bin/bash
# Run proof-engine evals on a batch of claims.
#
# Usage: ./tools/run-evals.sh <claims-file> [options]
#
# Options:
#   --model <opus|sonnet>   Model to use (default: sonnet)
#   --parallel <N>          Max parallel jobs (default: 3)
#   --force                 Re-run all claims, even those with .success marker
#   --timeout <seconds>     Per-claim timeout in seconds (default: 900 = 15 min)
#   --output-dir <dir>      Output directory (default: eval-results)
#
# Claims file: one claim per line. Blank lines and lines starting with # are skipped.
#
# Output structure:
#   <output-dir>/
#     001-slug/
#       proof.py, proof.md, proof_audit.md   (proof artifacts)
#       phase1.log                            (raw CLI output from proof phase)
#       feedback.md                           (skill improvement feedback)
#     summary.md                              (aggregated feedback from all claims)
set -uo pipefail
# NOTE: no set -e — we handle errors explicitly. Workers always exit 0;
# aggregation greps may match nothing. We don't want either to abort the script.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Defaults ---
MODEL="sonnet"
PARALLEL=3
FORCE=false
OUTPUT_DIR="$REPO_ROOT/eval-results"
CLAIMS_FILE=""
TIMEOUT=900  # 15 minutes per claim (both phases combined)

# --- Parse args ---
while [ $# -gt 0 ]; do
    case "$1" in
        --model)   MODEL="$2"; shift 2 ;;
        --parallel) PARALLEL="$2"; shift 2 ;;
        --force)   FORCE=true; shift ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,/^[^#]/p' "$0" | grep '^#' | sed 's/^# \?//'
            exit 0 ;;
        *)
            if [ -z "$CLAIMS_FILE" ]; then
                CLAIMS_FILE="$1"; shift
            else
                echo "Error: unexpected argument '$1'" >&2; exit 1
            fi ;;
    esac
done

if [ -z "$CLAIMS_FILE" ]; then
    echo "Usage: $0 <claims-file> [--model opus|sonnet] [--parallel N] [--force]" >&2
    exit 1
fi

if [ ! -f "$CLAIMS_FILE" ]; then
    echo "Error: claims file not found: $CLAIMS_FILE" >&2
    exit 1
fi

case "$PARALLEL" in
    ''|*[!0-9]*) echo "Error: --parallel must be a positive integer (got: $PARALLEL)" >&2; exit 1 ;;
esac
if [ "$PARALLEL" -lt 1 ]; then
    echo "Error: --parallel must be >= 1 (got: $PARALLEL)" >&2
    exit 1
fi

case "$TIMEOUT" in
    ''|*[!0-9]*) echo "Error: --timeout must be a positive integer (got: $TIMEOUT)" >&2; exit 1 ;;
esac
if [ "$TIMEOUT" -lt 1 ]; then
    echo "Error: --timeout must be >= 1 (got: $TIMEOUT)" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# --- Portable timeout (macOS lacks GNU timeout) ---
if command -v timeout >/dev/null 2>&1; then
    TIMEOUT_CMD="timeout"
elif command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_CMD="gtimeout"
else
    # Pure bash fallback: run command in background, kill it and descendants on timeout
    portable_timeout() {
        local secs="$1"; shift
        "$@" &
        local cmd_pid=$!
        (
            sleep "$secs"
            # Kill child processes first (descendants), then the main process
            pkill -TERM -P "$cmd_pid" 2>/dev/null
            kill -TERM "$cmd_pid" 2>/dev/null
            sleep 2
            pkill -KILL -P "$cmd_pid" 2>/dev/null
            kill -KILL "$cmd_pid" 2>/dev/null
        ) &
        local watchdog_pid=$!
        wait "$cmd_pid" 2>/dev/null
        local exit_code=$?
        kill "$watchdog_pid" 2>/dev/null
        wait "$watchdog_pid" 2>/dev/null
        return $exit_code
    }
    TIMEOUT_CMD="portable_timeout"
fi

# --- Slugify helper ---
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | tr -cs '[:alnum:]' '-' | head -c 50 | sed 's/-$//'
}

# --- Read claims, skip blanks and comments ---
CLAIMS=()
CLAIM_INDEX=0
while IFS= read -r line || [ -n "$line" ]; do
    # Skip blank lines and comments
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    CLAIM_INDEX=$((CLAIM_INDEX + 1))
    CLAIMS+=("$line")
done < "$CLAIMS_FILE"

TOTAL=${#CLAIMS[@]}
echo "=== Proof-Engine Eval Run ==="
echo "Claims file: $CLAIMS_FILE"
echo "Claims to process: $TOTAL"
echo "Model: $MODEL"
echo "Parallel: $PARALLEL"
echo "Output: $OUTPUT_DIR"
echo "Force re-run: $FORCE"
echo ""

# --- Track results ---
SKIPPED=0
STARTED=0
RUNNING_PIDS=()
RUNNING_DIRS=()
CLAIM_DIRS=()  # all claim dirs for this batch (for scoped aggregation)

# --- Wait for a job slot to free up ---
wait_for_slot() {
    while [ ${#RUNNING_PIDS[@]} -ge "$PARALLEL" ]; do
        # Check which PIDs are still running
        NEW_PIDS=()
        NEW_DIRS=()
        for i in "${!RUNNING_PIDS[@]}"; do
            if kill -0 "${RUNNING_PIDS[$i]}" 2>/dev/null; then
                NEW_PIDS+=("${RUNNING_PIDS[$i]}")
                NEW_DIRS+=("${RUNNING_DIRS[$i]}")
            fi
        done
        RUNNING_PIDS=("${NEW_PIDS[@]}")
        RUNNING_DIRS=("${NEW_DIRS[@]}")
        if [ ${#RUNNING_PIDS[@]} -ge "$PARALLEL" ]; then
            sleep 2
        fi
    done
}

# --- Dispatch claims ---
for i in "${!CLAIMS[@]}"; do
    CLAIM="${CLAIMS[$i]}"
    NUM=$(printf '%03d' "$((i + 1))")
    SLUG="$(slugify "$CLAIM")"
    DIR_NAME="${NUM}-${SLUG}"
    CLAIM_DIR="$OUTPUT_DIR/$DIR_NAME"

    CLAIM_DIRS+=("$CLAIM_DIR")

    # Idempotent: skip if .success marker exists (unless --force)
    # NOTE: .success means both phases completed. .failed or missing marker = retry.
    if [ "$FORCE" = false ] && [ -f "$CLAIM_DIR/.success" ]; then
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    wait_for_slot

    STARTED=$((STARTED + 1))
    echo "[$STARTED/$TOTAL] Dispatching: $DIR_NAME"

    # Run worker in subshell from the claim directory, with timeout
    (
        mkdir -p "$CLAIM_DIR"
        cd "$CLAIM_DIR"
        if ! $TIMEOUT_CMD "$TIMEOUT" "$SCRIPT_DIR/run-single-eval.sh" "$CLAIM_DIR" "$MODEL" "$CLAIM"; then
            echo "Timed out after ${TIMEOUT}s" > "$CLAIM_DIR/.failed"
            echo "[$(date '+%H:%M:%S')] TIMEOUT: $(basename "$CLAIM_DIR")"
        fi
    ) &

    RUNNING_PIDS+=($!)
    RUNNING_DIRS+=("$CLAIM_DIR")
done

# --- Wait for all remaining jobs ---
echo ""
echo "Waiting for remaining jobs to finish..."
wait

echo ""
echo "=== All jobs complete ==="
echo "Started: $STARTED  Skipped: $SKIPPED  Total: $TOTAL"

# --- Aggregate feedback ---
echo ""
echo "Aggregating feedback..."

SUMMARY="$OUTPUT_DIR/summary.md"
{
    echo "# Eval Feedback Summary"
    echo ""
    echo "**Generated:** $(date '+%Y-%m-%d %H:%M:%S')"
    echo "**Model:** $MODEL"
    echo "**Claims file:** $(basename "$CLAIMS_FILE")"
    echo "**Total claims:** $TOTAL"
    echo ""
    echo "---"
    echo ""

    SUCCEEDED=0
    FAILED_COUNT=0
    INCOMPLETE_COUNT=0
    NO_ISSUES=0

    for dir in "${CLAIM_DIRS[@]}"; do
        [ -d "$dir" ] || continue
        dir_name="$(basename "$dir")"

        # Classify run state
        if [ -f "$dir/.failed" ]; then
            FAILED_COUNT=$((FAILED_COUNT + 1))
            echo "## $dir_name (FAILED)"
            echo ""
            cat "$dir/.failed"
            echo ""
            echo "---"
            echo ""
            continue
        fi

        if [ ! -f "$dir/.success" ]; then
            INCOMPLETE_COUNT=$((INCOMPLETE_COUNT + 1))
            echo "## $dir_name (INCOMPLETE)"
            echo ""
            echo "No .success or .failed marker — worker may have been interrupted."
            echo ""
            echo "---"
            echo ""
            continue
        fi

        SUCCEEDED=$((SUCCEEDED + 1))
        feedback_file="$dir/feedback.md"

        if [ ! -f "$feedback_file" ]; then
            echo "## $dir_name (missing feedback.md)"
            echo ""
            echo "---"
            echo ""
            continue
        fi

        # Count issues by looking for Component entries
        ISSUE_COUNT=$(grep -c "^\- \*\*Component:\*\*" "$feedback_file" 2>/dev/null || true)
        if [ "${ISSUE_COUNT:-0}" -eq 0 ]; then
            NO_ISSUES=$((NO_ISSUES + 1))
        fi

        echo "## $dir_name"
        echo ""
        cat "$feedback_file"
        echo ""
        echo "---"
        echo ""
    done

} > "$SUMMARY"

# --- Collect feedback files for this batch only ---
BATCH_FEEDBACK_FILES=()
for dir in "${CLAIM_DIRS[@]}"; do
    [ -f "$dir/feedback.md" ] && BATCH_FEEDBACK_FILES+=("$dir/feedback.md")
done

# --- Quick stats via grep across this batch's feedback files ---
BLOCKER_COUNT=0
MAJOR_COUNT=0
MINOR_COUNT=0
if [ ${#BATCH_FEEDBACK_FILES[@]} -gt 0 ]; then
    BLOCKER_COUNT=$(grep -rl "Severity.*blocker" "${BATCH_FEEDBACK_FILES[@]}" 2>/dev/null | wc -l | tr -d ' ' || true)
    MAJOR_COUNT=$(grep -rl "Severity.*major" "${BATCH_FEEDBACK_FILES[@]}" 2>/dev/null | wc -l | tr -d ' ' || true)
    MINOR_COUNT=$(grep -rl "Severity.*minor" "${BATCH_FEEDBACK_FILES[@]}" 2>/dev/null | wc -l | tr -d ' ' || true)
fi
BLOCKER_COUNT="${BLOCKER_COUNT:-0}"
MAJOR_COUNT="${MAJOR_COUNT:-0}"
MINOR_COUNT="${MINOR_COUNT:-0}"

# Append aggregate stats
{
    echo ""
    echo "## Aggregate Stats"
    echo ""
    echo "- **Succeeded:** $SUCCEEDED / $TOTAL"
    echo "- **Failed:** $FAILED_COUNT"
    echo "- **Incomplete:** $INCOMPLETE_COUNT"
    echo "- **Skipped (already done):** $SKIPPED"
    echo "- **Clean runs (no issues):** $NO_ISSUES"
    echo "- **Runs with blockers:** $BLOCKER_COUNT"
    echo "- **Runs with major issues:** $MAJOR_COUNT"
    echo "- **Runs with minor issues:** $MINOR_COUNT"
    echo ""

    # Top components by issue count
    echo "### Most-mentioned components"
    echo '```'
    if [ ${#BATCH_FEEDBACK_FILES[@]} -gt 0 ]; then
        grep -h "^\- \*\*Component:\*\*" "${BATCH_FEEDBACK_FILES[@]}" 2>/dev/null \
            | sed 's/.*Component:\*\* //' \
            | sort | uniq -c | sort -rn \
            || echo "(none)"
    else
        echo "(none)"
    fi
    echo '```'
} >> "$SUMMARY"

echo "Summary written to: $SUMMARY"
echo "Done."
