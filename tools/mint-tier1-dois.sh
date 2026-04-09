#!/usr/bin/env bash
set -euo pipefail

if [ -z "${ZENODO_TOKEN:-}" ]; then
  echo "ERROR: ZENODO_TOKEN not set. Run: export ZENODO_TOKEN=your-token-here"
  exit 1
fi

SITE_DIR="${1:-site}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOL="$SCRIPT_DIR/proof-site.py"

SLUGS=(
  # Health & nutrition myths
  "alkaline-water-or-alkaline-diets-meaningfully-improve-health-by-counteracting"
  "all-ultra-processed-foods-are-inherently-unhealthy"
  "contrast-therapy-alternating-sauna-and-ice-bath-is-scientifically-proven"
  "detox-diets-and-juice-cleanses-actually-remove-tox"
  "eating-eggs-significantly-raises-ldl-cholesterol-a"
  "glp-1-drugs-like-ozempic-cause-unavoidable-major-muscle-loss-and-ozempic-face"
  "high-protein-diets-above-1-6-g-kg-body-weight-damage-kidneys-in-healthy-people"
  "intermittent-fasting-is-scientifically-proven-supe"
  "multivitamins-and-most-supplements-provide-meaningful-health-benefits-for-the"
  "seed-oils-canola-sunflower-soybean-corn-oil-are-to"
  "sunscreen-is-more-dangerous-due-to-chemical-absorption-and-vitamin-d-blocking"
  "the-body-can-only-absorb-20-30-g-of-protein-per-meal-the-rest-is-wasted"
  "the-carnivore-diet-is-superior-for-health-longevity-and-reversing-chronic"
  "you-must-eat-animal-protein-to-meet-daily-protein"
  "you-need-to-drink-at-least-8-glasses-of-water-daily-for-optimal-health"
  "the-superior-method-for-enhancing-neuroplasticity"

  # AI & technology
  "ai-hallucinations-occur-on-fewer-than-5-of-factual"
  "ai-progress-in-capabilities-has-largely-plateaued"
  "ai-will-replace-over-50-of-white-collar-jobs-by-20"
  "current-ai-systems-have-already-achieved-artificia"
  "current-ai-systems-in-2026-have-near-zero-hallucinations-and-human-level"
  "deepfake-videos-are-now-indistinguishable-from-rea"

  # Science, climate & energy
  "extreme-weather-events-hurricanes-wildfires-floods"
  "nuclear-power-is-too-dangerous-to-be-a-major-part"
  "quantum-entanglement-enables-the-transmission-of-u"
  "adult-neurogenesis-occurs-in-the-human-neocortex"
  "the-mean-neutron-lifetime-measured-in-beam-experim"

  # Famous myths
  "humans-use-only-10-of-their-brain-at-any-one-time"
  "the-average-person-swallows-eight-spiders-per-year"
  "the-great-wall-of-china-is-the-only-man-made-objec"
  "lightning-never-strikes-the-same-place-twice"
  "the-pyramid-of-giza-was-built-by-slaves"
  "heavier-objects-fall-faster-than-lighter-objects-e"
  "the-phrase-rule-of-thumb-originated-from-an-old-en"

  # Geopolitical
  "the-claim-that-israel-maintains-an-illegal-occupat"
)

TOTAL=${#SLUGS[@]}
MINTED=0
FAILED=0

echo "Minting DOIs for $TOTAL Tier 1 proofs..."
echo "==========================================="

for slug in "${SLUGS[@]}"; do
  echo ""
  echo "[$((MINTED + FAILED + 1))/$TOTAL] $slug"
  if python3 "$TOOL" mint-doi "$slug" --site-dir "$SITE_DIR"; then
    MINTED=$((MINTED + 1))
    echo "  -> OK"
  else
    FAILED=$((FAILED + 1))
    echo "  -> FAILED"
  fi
  sleep 1
done

echo ""
echo "==========================================="
echo "Done. Minted: $MINTED  Failed: $FAILED  Total: $TOTAL"
