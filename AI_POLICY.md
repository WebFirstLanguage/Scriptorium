# Scriptorium AI Policy

## AI-assisted contributions are welcome

Generative AI, coding agents, and other automation are legitimate tools for
contributing code, tests, documentation, reviews, and design proposals to
Scriptorium. Evaluate the contribution by its correctness, usefulness,
maintainability, and compliance with project policy.

Do not reject a contribution or application, harass someone, or impose a higher
quality bar solely because AI was involved. Do not require contributors to
prove that every character was written by hand. These behaviors are covered by
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## The submitting person remains accountable

The person submitting work must understand it well enough to explain the
behavior, assumptions, and tradeoffs and must address review feedback. AI use
does not waive any requirement in [GOVERNANCE.md](GOVERNANCE.md),
[CONTRIBUTING.md](CONTRIBUTING.md), or [testing.md](testing.md).

| Responsibility | Required behavior |
|---|---|
| Correctness | Review the result and provide the required test evidence |
| Compatibility | Protect site data, routes, configuration, themes, and extension contracts |
| Licensing | Submit only work you have the right to contribute under Apache-2.0; preserve attribution |
| Honesty | Report actual checks and results; do not invent reviews, approvals, citations, or passing CI |
| Reviewability | Keep changes understandable and answer questions about them |
| Security and privacy | Protect credentials, vulnerability details, and site data |

The same requirements apply to work produced without AI. Reviewers may request
changes or reject a contribution for concrete quality, scope, security,
licensing, or policy reasons. They may also limit automated spam or excessive
volume that prevents useful review.

## Disclosure

Disclosure of AI assistance is optional and welcome. A short PR note such as
`Drafted with AI assistance; I reviewed the change and ran the checks listed
above` is sufficient when accurate. Lack of an AI-use label alone is not a
reason to reject a contribution.

Optional disclosure does not excuse false statements about authorship,
provenance, review, or validation. Attribution required by a third-party license
still applies.

## Private information and agent authority

Do not send live site databases, credentials, session cookies, unpublished
content, user uploads, production logs, or private vulnerability details to a
third-party AI service without the appropriate data owner's authorization.
Use synthetic examples or carefully sanitized reproductions for development
and review. Follow [SECURITY.md](SECURITY.md).

Agents must follow [CLAUDE.md](CLAUDE.md) and the root policies. A tool's ability
to change files, deploy a site, merge a PR, or publish a release does not grant
authority to do so. Maintainers remain accountable for project decisions and
must authorize any delegation for merges, releases, access, or infrastructure.
AI-generated approval does not substitute for required Maintainer approval.

## Changes to this policy

Amendments follow [GOVERNANCE.md](GOVERNANCE.md#7-disputes-and-amendments).
Reports of AI-related discrimination follow
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md#reporting).

Effective: 2026-09-12.
