# Runbooks

Operational procedures the maintainer runs by hand. Each runbook is
self-contained: copy commands top-to-bottom, expect the documented outputs.

| Runbook                                        | When                                                                                              |
|------------------------------------------------|---------------------------------------------------------------------------------------------------|
| [release.md](./release.md)                     | Cutting a release: tag, push, verify Release workflow, publish to PyPI, account-hygiene checklist. |
| [regen-pipeline.md](./regen-pipeline.md)       | Operating the proof regeneration queue: check status, reset slugs, dispatch runs, review PRs.    |
