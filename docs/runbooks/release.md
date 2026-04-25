# Runbook: Cutting a release

Standard release flow. Follow top-to-bottom.

## Tag and push (one tag at a time)

```bash
# After the chore(release): vX.Y.Z commit is on main and CI is green:
git tag -a vX.Y.Z -m "vX.Y.Z — short summary"
git push origin vX.Y.Z
```

**Push tags individually.** Do NOT batch pushes like
`git push origin v1.28.0 v1.29.0 v1.30.0`. GitHub's Actions event
router silently drops workflow events for some refs in batched
multi-ref pushes; the result is that some tags get a Release workflow
run and others don't. This bit us once when retroactively tagging
v1.28.0 through v1.33.1 in one push — none fired.

For retroactive batches, push them one at a time in a loop:

```bash
for v in 1.34.0 1.34.1 1.34.2; do
  git push origin "v${v}"
  # Optional: wait for the Release workflow to start before pushing the next
  sleep 5
done
```

## Verify the Release workflow ran

```bash
gh run list --workflow Release --branch "vX.Y.Z" --limit 1
```

Should show `completed/success` after ~15 seconds. The workflow:

1. Builds the generic skill zip from the tag's tree.
2. Extracts release notes from `CHANGELOG.md`'s `## [X.Y.Z]` section.
3. Creates the GitHub Release with the zip attached.

## If the Release workflow did NOT fire

This happens when:
- Multiple tags were pushed in one `git push` command (see above).
- Branch protection or org-level workflow restrictions silently swallowed the event.
- Tags were pushed via a path that GitHub doesn't treat as a normal push (rare).

Recover by triggering the workflow manually with the same logic:

```bash
gh workflow run release.yml -f tag=vX.Y.Z
```

The `workflow_dispatch` input is identical to what the push-tag trigger provides — same zip, same notes, same Release.

## If the Release was created with the wrong artifact or notes

- Edit notes in place: `gh release edit vX.Y.Z --notes-file new-notes.md`.
- Replace artifacts: `gh release upload vX.Y.Z file.zip --clobber`.
- Mark a release as latest: `gh release edit vX.Y.Z --latest`.
- Yank a release (don't delete; preserves history): `gh release edit vX.Y.Z --draft` then update CHANGELOG with a deprecation note.

## Coordinating with PyPI

PyPI publication is a separate runbook ([pypi-namespace-reservation.md](./pypi-namespace-reservation.md) covers the first-time setup).

For subsequent releases:

```bash
# After tag push + GitHub Release lands:
for pkg in packages/proof-citations packages/proof-engine-registry packages/proof-engine-wiki; do
  rm -rf "$pkg/dist/" && (cd "$pkg" && python -m build --quiet)
  twine check "$pkg/dist/"*X.Y.Z*
  twine upload "$pkg/dist/"*X.Y.Z*
done

# Verify:
for name in proof-citations proof-engine-registry proof-engine-wiki; do
  curl -fs "https://pypi.org/pypi/$name/X.Y.Z/json" >/dev/null && echo "✅ $name X.Y.Z"
done
```

If something's wrong with a published version, you can `yank` (PyPI:
Manage → release → Yank). Yanking keeps the version installable by exact
pin but excludes it from new resolutions.
