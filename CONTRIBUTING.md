# Contributing to OpenSK API

Thank you for helping improve a consistent interface to Slovak public data. Follow the [Code of Conduct](CODE_OF_CONDUCT.md) and keep source coverage, provenance and reuse limitations explicit.

## Set up and verify

Follow the [local setup](README.md#local-development) using the Python version in `.python-version`. Install `requirements-dev.txt` with `--require-hashes`, then run:

```bash
python -m ruff check .
python scripts/check_docs.py
python scripts/validate_datasets.py
python scripts/check_referential_integrity.py
python -m pytest -q
python -m compileall -q main.py version.py scripts routers services tests schemas
git diff --check
```

Use synthetic inputs and pytest temporary directories. Tests must not overwrite production snapshots or delete a developer's existing generated previews. Source/coverage warnings are not permission to ignore a gate; explain accepted warnings in your PR.

## Changes and pull requests

1. Check [existing issues](https://github.com/matej-fedak/opensk-api/issues) and the [roadmap](docs/roadmap.md).
2. Branch from current `main`; keep one coherent change per PR.
3. Preserve `/v1` operation IDs and response behavior unless a pre-1.0 contract change is intentional, documented and tested.
4. Add regression tests for failure paths as well as successful examples. Keep runtime requests independent of upstream networks.
5. Update the relevant guide and the current `Unreleased` changelog entry. Mark historical research as historical instead of silently rewriting its original conclusions.
6. Describe the problem, solution, tests and any source/privacy/compatibility implications in the PR.

Use descriptive commits, for example `fix: reject non-ASCII pagination values` or `docs: clarify snapshot coverage`. Do not mix broad reformatting with behavioral changes.

## Dataset contributions

Follow [adding a dataset](docs/adding-a-dataset.md), the [import pipeline](docs/import-pipeline.md) and [dataset format](docs/dataset-format.md). New or refreshed data requires authoritative provenance, a reproducible permitted acquisition, reuse/redistribution evidence, privacy review, stable identifiers and validation.

- Code and original documentation contributions are provided under the repository's MIT licence.
- Third-party data and evidence retain their applicable source terms; they are **not automatically MIT**. You must have sufficient rights to contribute or redistribute them, preserve required attribution and disclose transformations.
- Do not contribute personal source captures, secrets, unsupported licence claims or invented acquisition timestamps.
- Do not scrape or automate sources whose documented acquisition rules prohibit it.
- Dry-run first, inspect the normalized diff, and promote only after all relevant gates pass. A source-owner redirect or sent request is not redistribution permission.

## Dependency and interpreter updates

`requirements.in` declares runtime dependencies; `requirements-dev.in` adds development tools and constrains runtime packages to the runtime lock. The generated `.txt` files pin the full dependency graphs and SHA-256 hashes for Linux and Windows.

With [uv](https://docs.astral.sh/uv/) installed, regenerate both locks from the repository root using the Python version in `.python-version`:

```bash
uv pip compile requirements.in --python-version 3.12.16 --universal --generate-hashes --no-emit-index-url --output-file requirements.txt
uv pip compile requirements-dev.in --python-version 3.12.16 --universal --generate-hashes --no-emit-index-url --output-file requirements-dev.txt
```

To intentionally refresh existing pins, add `--upgrade` to each command, compiling runtime first. Review both diffs, install in a fresh environment, and run the full checks plus:

```bash
python -m pip_audit -r requirements.txt --disable-pip --require-hashes
```

Audit the resolved set rather than assuming an unversioned package name is safe. Update the interpreter patch in `.python-version` and this regeneration example together; CI and Render use that declaration. Dependabot proposes weekly updates, but generated locks must remain synchronized and tested before merge.

## Bugs, questions and security

Use the [API bug template](https://github.com/matej-fedak/opensk-api/issues/new?template=bug_report.md) for ordinary bugs. Include the project version, method/path, synthetic reproduction, expected result and actual status/body. For local failures, include Python and OS versions. Redact real account identifiers and private data.

Questions and scoped suggestions can use [GitHub issues](https://github.com/matej-fedak/opensk-api/issues). Check the [quickstart](docs/quickstart.md), [limitations](docs/known-limitations.md) and current research decision first.

**Do not post vulnerabilities or sensitive data publicly.** Follow [SECURITY.md](SECURITY.md) for private reporting. This is a volunteer-maintained project; no guaranteed response time or support SLA is offered.
