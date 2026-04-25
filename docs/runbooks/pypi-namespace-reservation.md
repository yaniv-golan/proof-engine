# Runbook: Reserve PyPI namespace for the three packages

**When to run:** before any public announcement (HN, Twitter, blog post,
talk) that names the packages. The names `proof-citations`,
`proof-engine-registry`, `proof-engine-wiki` are unclaimed on PyPI as of
v1.32.0; if a third party registers them first, every reader of the
announcement who runs `pip install proof-citations` could install
something we don't control.

**Who can run:** the project maintainer with a PyPI account and the
authority to publish under the project's identity.

## Steps

1. **Verify the names are still available.**

   ```bash
   for name in proof-citations proof-engine-registry proof-engine-wiki; do
     curl -s -o /dev/null -w "%{http_code} %s\n" "https://pypi.org/pypi/$name/json" -- "$name"
   done
   ```

   - `404` → name available, proceed.
   - `200` → already taken. Stop and assess.

2. **Build wheels for the three packages from the current `main`.**

   ```bash
   pip install --upgrade build twine
   for pkg in packages/proof-citations packages/proof-engine-registry packages/proof-engine-wiki; do
     (cd "$pkg" && rm -rf dist/ && python -m build)
   done
   ```

   Each package's `dist/` should now contain a `.tar.gz` and a `.whl`.

3. **Verify wheel metadata locally.**

   ```bash
   for pkg in packages/proof-citations packages/proof-engine-registry packages/proof-engine-wiki; do
     echo "=== $pkg ==="
     twine check "$pkg/dist/*"
   done
   ```

   `twine check` validates the README renders on PyPI and that all
   required metadata is present.

4. **Upload to TestPyPI first** (sanity check; doesn't claim the real
   namespace).

   ```bash
   for pkg in packages/proof-citations packages/proof-engine-registry packages/proof-engine-wiki; do
     twine upload --repository testpypi "$pkg/dist/*"
   done
   ```

   Then verify each test page renders correctly:
   - https://test.pypi.org/project/proof-citations/
   - https://test.pypi.org/project/proof-engine-registry/
   - https://test.pypi.org/project/proof-engine-wiki/

5. **Upload to real PyPI.**

   ```bash
   for pkg in packages/proof-citations packages/proof-engine-registry packages/proof-engine-wiki; do
     twine upload "$pkg/dist/*"
   done
   ```

   This claims the namespace. From this point on, only the PyPI account
   used here can release new versions of those names.

6. **Verify the live URLs.**

   ```bash
   for name in proof-citations proof-engine-registry proof-engine-wiki; do
     curl -fs "https://pypi.org/pypi/$name/json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{d[\"info\"][\"name\"]}=={d[\"info\"][\"version\"]}')"
   done
   ```

7. **Configure `[project.urls]` Documentation/Issues/Changelog/Source**
   already done in `pyproject.toml` (see ADR commit). PyPI sidebar should
   show all the links once propagated (~5 min).

## After publication

- Update `README.md` and `packages/*/README.md` to recommend
  `pip install <name>` from PyPI rather than `-e packages/<pkg>`.
- Add a release note to CHANGELOG mentioning PyPI availability.
- Set up 2FA on the PyPI account if not already.
- Consider configuring [PyPI trusted publishers](https://docs.pypi.org/trusted-publishers/)
  via GitHub Actions so future releases don't require local credentials.

## If a name is already taken when you run step 1

1. Check who owns it. If it's a typosquat or unrelated package, you can
   try [PEP 541 name claim process](https://peps.python.org/pep-0541/) —
   slow but legitimate.
2. Otherwise, rename. Pick a less-collidable name (e.g.
   `proofengine-citations`) and update:
   - `packages/<pkg>/pyproject.toml` `name` field.
   - All install commands in `README.md`, `CONTRIBUTING.md`,
     `docs/**.md`, `bin/proof-engine`.
   - All `pip install -e` invocations.
   - The CI workflow.

## Emergency: name was taken between announcement and reservation

If someone registers the name in the window between this runbook
running and your announcement:

1. **Do not** install or run their package locally to inspect it.
2. Report to PyPI via [security@python.org](mailto:security@python.org)
   if the package is malicious.
3. Communicate the rename publicly via your announcement channels.
