# Manual developer pilot

**Next after 0.23.12:** ask **5–10 external developers** to try the API and report concrete integration friction. There are currently no known real external users; this is a proposed pilot, not completed outreach or proof of adoption.

The **maintainer** selects and contacts participants, with honest pre-1.0, snapshot and source-reuse caveats. Public promotion remains gated by PortalVS compliance; keep any pilot appropriately scoped and do not imply permission to redistribute unresolved source data. Possible contacts: slovensko.digital community, Slovak university CS/data students, civic-tech developers, and builders of Slovak geography/business/finance utilities. No messages are sent automatically.

## A short task, not a survey campaign

Start with only the [quickstart](quickstart.md) and [Swagger](https://opensk-api.onrender.com/docs), without a repository walkthrough. Ask each participant to try:

1. One lookup, such as municipality `528595` or PSC `01001`; explain what a local 404 means.
2. One filtered collection; distinguish page `count` from matching `total`.
3. One utility, such as a business-day check or synthetic IBAN validation.
4. `/v1/sources`; decide whether a chosen dataset's coverage/freshness/reuse suits their task.
5. If relevant, load OpenAPI in their usual client tooling and try generation **locally**. No project SDK publication or generation framework is part of this milestone.

Ask them to note first-success time and where they needed help. No scoring threshold or 1.0 promise: the point is finding repeatable confusion and real demand.

## Collect manually

Use an issue or maintainer notes, with participant consent; do not collect account numbers, personal addresses, secrets or raw IPs.

| Prompt | Notes to collect |
| --- | --- |
| Endpoint attempted | Method/path and nonsensitive example parameters |
| Intended task | What they wanted to build or decide |
| Friction | What was confusing; where they stopped |
| Contract | Missing fields, nullable/array/page surprises, client-tool errors |
| Failure | HTTP status/error code, expected versus observed result |
| Documentation | Missing explanation or copy-paste example |
| Value | Would they use OpenSK again, and for what? |

Triage repeated integration failures first, then documentation gaps, then requested fields/features with actual use cases. Keep coverage or source-permission requests separate from contract bugs. Avoid an SDK until outside developers demonstrate the OpenAPI is useful and identify a concrete need. Monitor source-owner replies separately; do not automatically reopen PSC research or choose another dataset. **PSC successor migration stays PARKED / NO_GO_SUCCESSOR_PSC.**

No analytics, tracking infrastructure, automatic outreach or marketing plan is required. After the pilot, summarize actual tasks, recurring blockers and proposed fixes before choosing the next implementation milestone.
