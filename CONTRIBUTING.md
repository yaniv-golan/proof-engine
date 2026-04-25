# Contributing

Thanks for considering a contribution to Proof Engine.

## Quick start

```bash
git clone https://github.com/yaniv-golan/proof-engine
cd proof-engine
pip install -r requirements.txt 2>/dev/null || pip install requests sympy python-dateutil pytest Jinja2 Markdown Pillow PyYAML pymdown-extensions regex unidecode jsonschema
pip install -e packages/proof-citations -e packages/proof-engine-registry -e packages/proof-engine-wiki
python -m pytest tests/ -q
```

Each package has its own test suite — run them separately to avoid pytest rootdir collisions:

```bash
python -m pytest tests/ -q
(cd packages/proof-citations && python -m pytest -q)
(cd packages/proof-engine-registry && python -m pytest -q)
(cd packages/proof-engine-wiki && python -m pytest -q)
```

## Submitting a proof

If you want to publish a new proof to the public catalog, see [the submit guide](https://proofengine.info/submit/). You don't need to clone the repo — generated proofs land via PR with the four canonical files plus `proof.json`.

## Code contributions

- **Tests pass.** All four suites green before submitting a PR.
- **No mocked verifications.** Proofs that pass against mocks but fail against real sources defeat the purpose of the project.
- **No version-string edits by hand.** Always use `./tools/bump-version.sh`.
- **Per-file `git add`.** Never `git add -u` or `-A` — it sweeps unrelated working-tree changes.
- **Commit messages** follow Conventional Commits style (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`).
- **Conventions** documented in [CLAUDE.md](CLAUDE.md) — quick reference for repo layout, version sync targets, fact types, hardening rules.

## Architecture pointers

- [`docs/DESIGN.md`](docs/DESIGN.md) — design principles, trust boundary, fact-type model.
- [`docs/registry-protocol.md`](docs/registry-protocol.md) — Registry Protocol v0.1 specification.
- [`docs/headless-verify.md`](docs/headless-verify.md) — headless verification CLI contract.
- [`docs/badges.md`](docs/badges.md) — proof badge format.
- [`proof-engine/skills/proof-engine/references/hardening-rules.md`](proof-engine/skills/proof-engine/references/hardening-rules.md) — the nine hardening rules every proof must satisfy.

## Reporting issues

- For functional bugs: GitHub Issues.
- For security issues: see [SECURITY.md](SECURITY.md).

## License

By contributing, you agree your contributions are licensed under the MIT license (same as the project).
