# Security Policy

## Reporting an issue

Please report suspected security issues privately to **yaniv@lool.vc**.

Include:
- The affected component (e.g. `proof-citations`, `proof-engine-registry` server, the public site).
- Steps to reproduce.
- Affected versions if known (`VERSION` file is the source of truth).
- Your assessment of impact.

Do **not** file a public GitHub issue or pull request for an unpatched issue.

## What to expect

- Acknowledgement within 72 hours.
- An initial assessment within 7 days.
- A fix or mitigation timeline based on severity, communicated back to the reporter.
- Public disclosure coordinated with the reporter once a fix ships.

## Scope

In scope:
- The `proof-engine` skill and bundled scripts (`proof-engine/skills/proof-engine/`).
- The three Python packages under `packages/` (`proof-citations`, `proof-engine-registry`, `proof-engine-wiki`).
- The public site at `proofengine.info` and its build pipeline (`tools/build-site.py`).
- The Registry Protocol specification (`docs/registry-protocol.md`) and the reference server.

Out of scope:
- Issues in third-party dependencies — please report those upstream.
- Issues in self-hosted deployments where the deployer has not followed the
  TLS-termination guidance in the registry protocol spec.
- Social-engineering or phishing scenarios that don't involve a defect in the code.

## Supported versions

Only the latest minor release receives fixes. Older versions are out of support unless explicitly stated.
