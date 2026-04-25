# Proof Badges

Compact, embeddable certificates for claim verification. Every published proof
gets a badge at two URLs:

- `/proofs/{slug}/badge.json` — machine-readable payload
- `/proofs/{slug}/badge.svg`  — shields-style inline SVG

## Copy-paste embeds

HTML:

    <a href="https://proofengine.info/proofs/{slug}/">
      <img src="https://proofengine.info/proofs/{slug}/badge.svg"
           alt="proof: SUPPORTED">
    </a>

Markdown:

    [![proof](https://proofengine.info/proofs/{slug}/badge.svg)](https://proofengine.info/proofs/{slug}/)

## Verdict colors (pinned)

| Verdict              | Color     |
|----------------------|-----------|
| PROVED               | `#2d8f5f` |
| SUPPORTED            | `#5eb88a` |
| PARTIALLY VERIFIED   | `#d4a017` |
| UNDETERMINED         | `#888888` |
| DISPROVED            | `#c75450` |

Changing these is a badge schema major version bump.

## Self-hosted registries

Self-hosted registries emit badges at the same paths. Point the `<img>` src at
your registry's `{base_url}/proofs/{slug}/badge.svg`.
