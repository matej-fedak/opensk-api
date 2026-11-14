# Versioning

OpenSK is in pre-1.0 development. The authoritative project version is [`PROJECT_VERSION` in `version.py`](../version.py), also returned by `GET /` and OpenAPI. Change it there, not independently in routes or smoke tests.

The `/v1` route prefix and response `metadata.version: "v1"` identify the API namespace, not a stable project release. Pre-1.0 changes can still alter behavior; document intentional contract changes in the [changelog](../CHANGELOG.md) and retain explicit dataset limitations.

## Legacy release labels

Earlier `v1.x` changelog labels were internal development milestones. There is also an existing annotated Git tag **`v1.0.0`**, created on 2026-06-03, pointing to commit `e64ea38`; that commit reports **`1.0.0-rc.6`** in the application. This is a legacy release-label/version mismatch, not evidence that today's datasets or API have stable-release approval.

Do not delete, move or silently overwrite the published tag. Before a future stable release, explicitly choose and document an unused version/tag and a migration notice addressing this history. The stable milestone is called “1.0 readiness” in planning documents; that name does not reserve an already-used Git tag or authorize retagging it.

## Release policy

- Use semantic project versions; `0.x` remains pre-stable.
- Keep the API namespace independent from the project version.
- Create tags/releases only intentionally, after testing and deployment verification of the exact final versioned commit.
- Verify source reuse, privacy, coverage, response shapes and operational checks before describing a release as stable.
- Record historical facts as dated records; link current guidance rather than duplicating changing version numbers across policy pages.

See [candidate stable scope](1-0-scope.md), [release readiness](release-readiness.md) and the [historical readiness audit](1-0-readiness-audit.md).
