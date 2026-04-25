# ADR-0002: Monorepo packages version in lockstep with the repo

- **Status:** accepted
- **Date:** 2026-04-25
- **Decision driver:** public-OSS readiness review (item 17)

## Context

Three Python packages live under `packages/`:

- `proof-citations` (v1.32.0)
- `proof-engine-registry` (v1.32.0)
- `proof-engine-wiki` (v1.32.0)

`tools/bump-version.sh` synchronizes the repo `VERSION` to all three
packages' `pyproject.toml` and `__init__.py` `__version__` strings.

Two reasonable strategies for SemVer in a monorepo:

1. **Lockstep** — all packages share the same version, bumped together.
2. **Independent** — each package has its own version; PyPI consumers
   only see the package they care about.

## Decision

**Lockstep.** All three packages move together with the repo VERSION.

## Rationale

- The packages are tightly coupled: `proof-engine-wiki` imports
  `proof-engine-registry` and `proof-citations` at module scope; a
  registry protocol minor bump that changes `IndexEntry` would require
  the wiki adapter to track the same minor.
- Independent versions would force a dependency-resolution puzzle each
  release: which combinations are compatible? The matrix grows fast.
- The Registry Protocol version is a separate concept (currently v0.1)
  and IS independent — it can move without bumping packages, as long as
  the packages' clients can still speak it.
- Lockstep makes troubleshooting easier: "what version is everything?"
  has one answer (`cat VERSION`).

## Tradeoffs accepted

- A `proof-citations` user who only needs unicode normalization gets a
  patch-level bump every time `proof-engine-wiki` adds a feature. They
  pay no install-cost penalty (wheels are tiny) but the changelog
  signal is noisier.
- If one package develops a serious vulnerability, all three need a
  release even if the others are unaffected — but the security release
  doesn't FORCE any consumer of an unaffected package to upgrade.

## When to revisit

Revisit if:

- A package's user base diverges meaningfully from the others
  (e.g., `proof-citations` gets adopted as a generic citation tool
  outside the proof-engine ecosystem).
- Release cadence becomes a bottleneck (e.g., wiki-adapter churn slows
  registry releases).
- A consumer requests independent versioning explicitly.
