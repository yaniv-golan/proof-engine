## What

Briefly describe what this PR changes.

## Why

The motivation. Link the issue if any: `Closes #N`.

## How tested

- [ ] Top-level suite: `python -m pytest tests/ -q`
- [ ] `proof-citations`: `(cd packages/proof-citations && python -m pytest -q)`
- [ ] `proof-engine-registry`: `(cd packages/proof-engine-registry && python -m pytest -q)`
- [ ] `proof-engine-wiki`: `(cd packages/proof-engine-wiki && python -m pytest -q)`
- [ ] Site builds clean: `python tools/build-site.py ...` (see CLAUDE.md)
- [ ] Manual smoke test: ...

## Conventions confirmed

- [ ] No version-string edits by hand (used `./tools/bump-version.sh` if needed)
- [ ] Commit messages follow Conventional Commits (`feat:`/`fix:`/`docs:`/`chore:`/`refactor:`/`test:`)
- [ ] No `git add -u` or `-A` used to stage
- [ ] If proof-related: re-runnable `proof.py` exists + verifies cleanly
