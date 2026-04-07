# Submit a Proof

Share your verified proofs with the community.

## How to Submit

1. **Generate your proof** using Proof Engine — this produces `proof.py`, `proof.md`, `proof_audit.md`, and `proof_narrative.md`

2. **Run your proof** and save the JSON output as `proof.json`

3. **Fork the repo**, add all five files to `site/proofs/your-claim-slug/`, and open a PR

CI validates your submission automatically. A maintainer reviews and merges. Your proof goes live on the next deploy.

## Optional: Custom Tags

By default, tags are auto-assigned from keywords in your claim. To override, add a `meta.yaml` to your proof directory:

    tags: [economics, inflation]
