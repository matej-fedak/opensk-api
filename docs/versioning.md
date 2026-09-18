# Versioning

OpenSK API is currently in pre-1.0 development.

The current project version is `0.13.0`. The public API namespace remains `/v1`, and response `metadata.version` remains `"v1"`.

Earlier `v1.x` labels in the changelog and commit history were internal development milestone labels. They are retained as historical notes, but they are not formal stable public releases.

Future formal releases should use semantic versioning:

- `1.0.0` is reserved for the first stable public API contract.
- `0.x` versions may still include breaking changes while the API is stabilizing.
- Public endpoints are usable during pre-1.0 development, but their long-term compatibility is not yet guaranteed.
- The `/v1` route prefix is an API namespace and does not mean the project has reached formal `1.0.0` release status.
- Git tags and GitHub Releases should only be created intentionally as part of a release process.

Before a true `1.0.0`, source/licence evidence, endpoint behavior, response shapes, deployment checks, and dataset coverage must be reviewed and documented. See `docs/1-0-readiness-audit.md` and `docs/release-readiness.md`.
