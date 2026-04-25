# ADR-0001: Monorepo packages version in lockstep with the repo

- **Status:** accepted
- **Date:** 2026-04-25

## Context

Three Python packages live under `packages/`: `proof-citations`,
`proof-engine-registry`, `proof-engine-wiki`. `tools/bump-version.sh`
synchronizes the repo `VERSION` to all three packages' `pyproject.toml`
and `__init__.py` `__version__` strings.

Two reasonable strategies for SemVer in a monorepo:

1. **Lockstep** — all packages share the same version, bumped together.
2. **Independent** — each package has its own version.

## Decision

**Lockstep.** All three packages move together with the repo VERSION.

## Rationale

- The packages are tightly coupled: `proof-engine-wiki` imports
  `proof-engine-registry` and `proof-citations` at module scope; a
  registry protocol minor bump that changes `IndexEntry` would require
  the wiki adapter to track the same minor.
- Independent versions would force a dependency-resolution matrix per
  release that grows quickly.
- The Registry Protocol version is a separate concept (currently v0.1)
  and IS independent — it can move without bumping packages, as long as
  the package APIs continue to speak it.
- Lockstep makes troubleshooting easier: "what version is everything?"
  has one answer (`cat VERSION`).

## When to revisit

- A package's user base diverges meaningfully from the others (e.g.,
  `proof-citations` gets adopted as a generic citation tool outside the
  proof-engine ecosystem).
- Release cadence becomes a bottleneck (e.g., wiki-adapter churn slows
  registry releases).
- An explicit request for independent versioning.
