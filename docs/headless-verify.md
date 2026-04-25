# Headless Verification

`proof-engine verify` is the entry point for pipelines and tools that want a
machine-readable proof verdict.

## Modes

### Registry-check then generate (default with `--registry-check`)

    proof-engine verify --claim "..." --registry-check --json

Looks up the claim in configured registries; if found, returns the existing
proof without generation. Otherwise, generates a new proof and returns the
verdict.

### Registry-only (no generation)

    proof-engine verify --claim "..." --registry-only --json

Exit 0 on hit, exit 3 on miss. Use this in pipelines that want to decide
elsewhere whether to commission a full proof.

### Generate always

    proof-engine verify --claim "..." --json

No registry check; always generates.

## Configuration

Registries are read from `~/.config/proof-engine/registries.toml`. See
[docs/registry-protocol.md](./registry-protocol.md) for the file format.

## JSON shape

See the Verdict schema in [tools/lib/cli_verdict.py](../tools/lib/cli_verdict.py).
The `schema_version` field is pinned at `"1.0"` for this release.
