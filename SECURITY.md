# Security policy

## Reporting privately

Do not publish vulnerabilities, exploitable details, real IBANs, credentials or private source captures in public issues or pull requests.

Contact the maintainer privately at **matejfedak.dev@gmail.com**, the existing public maintainer contact. Use a subject such as `OpenSK API security report`. If GitHub's private reporting feature is enabled, you can also use [Report a vulnerability](https://github.com/matej-fedak/opensk-api/security/advisories/new).

Include the affected commit/version, a minimal synthetic reproduction, expected versus actual behavior, and your assessment of impact. Avoid sending personal source records unless a safe transfer has been agreed. No encryption key, guaranteed acknowledgement time or remediation SLA is currently published.

## Supported versions and responsible testing

The current pre-1.0 development line receives fixes on `main`; older snapshots and legacy tags are not maintained release branches. Check `version.py` or `GET /` for the project version, independently of the `/v1` namespace.

Test against a local clone using synthetic data. Do not run denial-of-service, rate-exhaustion, large-payload or privacy-invasive tests against the hosted service or upstream publishers. Report source/privacy concerns privately when disclosure could expose individuals.

## Operational boundaries

The API reads local snapshots and has no user accounts or API keys. IBAN validation responses are `no-store`, and the supplied server commands disable Uvicorn access logging. Hosting proxies/CDNs have separate logging controls; the application cannot guarantee their redaction or retention policies.

Dependencies are hash-locked, checked in CI and proposed for update by Dependabot. CI also runs a pinned, checksum-verified Gitleaks scanner over reachable Git history with redacted output. This reduces risk but is not a security certification. Source-data reuse permissions remain separate from software security and the MIT code licence.
