#!/bin/bash
# Generate a proof for publishing to the site.
#
# Usage: ./tools/generate-proof.sh "<claim>" [options]
#
# Options:
#   --output-dir <dir>    Directory to write proof artifacts (default: proofs-draft/<slug>)
#   --model <model>       Claude model to use (default: sonnet)
#
# Workflow:
#   1. Run /proof-engine skill on the claim
#   2. Validate the generated proof.py
#   3. Print next steps (review, thumbnail, publish)
#
# Does NOT publish automatically — human review before publish is intentional.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/proof-engine"

MODEL="sonnet"
OUTPUT_DIR=""
CLAIM=""

while [ $# -gt 0 ]; do
    case "$1" in
        --model)      MODEL="$2"; shift 2 ;;
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,/^[^#]/p' "$0" | grep '^#' | sed 's/^# \?//'
            exit 0 ;;
        *)
            if [ -z "$CLAIM" ]; then
                CLAIM="$1"; shift
            else
                echo "Error: unexpected argument '$1'" >&2; exit 1
            fi ;;
    esac
done

if [ -z "$CLAIM" ]; then
    echo "Usage: $0 \"<claim>\" [--output-dir <dir>] [--model <model>]" >&2
    exit 1
fi

slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | tr -cs '[:alnum:]' '-' | head -c 60 | sed 's/-$//'
}

if [ -z "$OUTPUT_DIR" ]; then
    SLUG="$(slugify "$CLAIM")"
    OUTPUT_DIR="$REPO_ROOT/proofs-draft/$SLUG"
fi

mkdir -p "$OUTPUT_DIR"

echo "=== Generating proof ==="
echo "Claim:  $CLAIM"
echo "Model:  $MODEL"
echo "Output: $OUTPUT_DIR"
echo ""

# --- Step 1: Generate proof ---
echo "[$(date '+%H:%M:%S')] Running proof-engine skill..."
claude -p \
    --plugin-dir "$PLUGIN_DIR" \
    --dangerously-skip-permissions \
    --model "$MODEL" \
    "Using /proof-engine, prove that: $CLAIM

Write the four output files to this exact directory: $OUTPUT_DIR/
Use exactly these filenames: proof.py, proof.md, proof_audit.md, proof_narrative.md" \
    > "$OUTPUT_DIR/generation.log" 2>&1

echo "[$(date '+%H:%M:%S')] Generation complete."
echo ""

# --- Verify all four artifacts were written ---
MISSING=""
for artifact in proof.py proof.md proof_audit.md proof_narrative.md; do
    [ -f "$OUTPUT_DIR/$artifact" ] || MISSING="$MISSING $artifact"
done

if [ -n "$MISSING" ]; then
    echo "ERROR: Missing artifacts:$MISSING" >&2
    echo "See generation log: $OUTPUT_DIR/generation.log" >&2
    exit 1
fi

# --- Step 2: Validate ---
echo "[$(date '+%H:%M:%S')] Validating proof.py..."
VALIDATE_EXIT=0
PYTHONPATH="$REPO_ROOT" python \
    "$PLUGIN_DIR/skills/proof-engine/scripts/validate_proof.py" \
    "$OUTPUT_DIR/proof.py" \
    > "$OUTPUT_DIR/validation.txt" 2>&1 || VALIDATE_EXIT=$?

cat "$OUTPUT_DIR/validation.txt"
echo ""

if [ $VALIDATE_EXIT -ne 0 ]; then
    echo "Validation failed. Fix issues in proof.py, then re-validate:"
    echo "  PYTHONPATH=. python proof-engine/skills/proof-engine/scripts/validate_proof.py $OUTPUT_DIR/proof.py"
    echo ""
    echo "When fixed, publish with:"
    echo "  python tools/proof-site.py publish $OUTPUT_DIR --site-dir site"
    exit 1
fi

# --- Step 3: Next steps ---
echo "=== Next steps ==="
echo ""
echo "1. Review the proof:"
echo "   $OUTPUT_DIR/"
echo ""
echo "2. Add a 240×240 thumbnail (optional but recommended):"
echo "   $OUTPUT_DIR/thumbnail.png"
echo ""
echo "3. Publish to site:"
echo "   python tools/proof-site.py publish $OUTPUT_DIR --site-dir site"
echo ""
echo "4. Feature on landing page (optional):"
echo "   python tools/proof-site.py feature <slug> --site-dir site"
