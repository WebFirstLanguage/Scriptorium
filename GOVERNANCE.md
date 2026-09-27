# Scriptorium Project Governance

Scriptorium uses a **maintainer-led** model. This document defines project
authority, contribution roles, and the policies used to review changes.

| Project | Value |
|---|---|
| Repository | [WebFirstLanguage/Scriptorium](https://github.com/WebFirstLanguage/Scriptorium) |
| Purpose | A WFL content management system with SQLite storage and Scribe templates |
| Stage | MVP under active development |
| Primary Maintainer | Brad |
| Project contact | info@logbie.com |
| License | [Apache-2.0](LICENSE) |

## Common contribution policy — version 1.0 (2026-09-27)

This version records Brad's approved Logbie LLC governance and subsequent dev
merge and CEO delegations of 2026-09-26. It governs contribution authority;
the repository's technical, compatibility, testing and licensing rules remain
binding. Report substantive conflicts on the owning issue instead of silently
relaxing a rule.

### Branches and review

- Start a short-lived feature, fix or documentation branch from current `dev`;
  open its PR into `dev`. Never push directly to `dev`, `main` or a release
  branch, or force-push shared branches. Promotion is `dev → main` by PR.
- Yomi reviews the current revision against governance and testing policy.
  The PR author, including an agent author, may merge their own PR into `dev`
  only after applicable CI passes on that reviewed revision and findings are
  addressed. This delegation needs no separate per-PR Brad approval.
- Let triggered bot reviews finish; inspect reviews, inline comments and
  discussions. Fix actionable findings or record a reasoned disposition and
  resolve required discussions. Recheck checks and reviews immediately before
  merging. Material changes require fresh applicable CI and Yomi review.
- The PR owner remains responsible while CI or bot review is pending. Use an
  actual scheduled monitor or event-driven continuation, not a promise to watch.
- Do not bypass protections, use an administrator override, remove a check, or
  rerun a genuine failure merely to manufacture green. Access is not authority.

### Evidence and testing

- Behavior changes start with a test failing for the intended reason, followed
  by implementation and passing evidence. Retain exact commands, revisions,
  results and run links under the repository testing policy.
- GitHub Actions on the current reviewed revision is merge evidence; local
  checks supplement it. Enumerate required jobs and their individual results.
  Missing tools, environment failures, missing/pending checks and skipped,
  cancelled or failed required suites are blocked verification, never passes.
  An aggregate green result cannot stand in for an unrun required suite.
- For prose-only work, record “Behavior tests N/A — documentation only” with
  the reason and relevant documentation, link and policy checks. This does not
  waive required CI. Existing risk classes and stricter technical gates remain.
- Run agent-operated runtime tests on Starnet test VM 136 or 104, never VM 143;
  coordinate risky-test snapshots with Nodoka. Preserve the repository's approved
  GitHub Actions execution environments and record their actual results.

### Promotion, release and production authority

Azusa, CEO of Logbie LLC, may approve and perform builds, releases, merges to
`main`, release promotions, tags and production deployments only when every
required check passed on the exact commit being acted on: none skipped,
missing, pending, flaky or failing. Record the SHA, required-check set and
individual result links, then recheck immediately before acting. A different
SHA or aggregate green is insufficient; a flaky rerun is not a waiver.
Anything short of fully green stops for Brad's explicit authorization.
Yomi's current-revision review and handled bot feedback remain required.

Always Brad's decisions regardless of CI: spending money; deleting data,
agents or repositories; anything touching secrets; VM configuration changes;
and removing or weakening required checks. Release/deploy workflow changes,
organization settings/membership and deletion of branches, rulesets or
workflows also require Brad's explicit approval through the owning issue.

Production hosts are read-only for agents: authorized config/log inspection
only, without exposing secrets. No edits, restarts, installs or migrations.
The conditional CEO production-deployment authority above is limited to the
authorized deployment; it grants no general production administration.
Other production changes go to Brad through Azusa.

### Credentials, exceptions and enforcement

Never commit, print, log or paste credentials into files, comments, PRs,
command arguments or remote URLs. Inject authorized tokens through environment
variables from approved storage, with minimal scope. Suspected exposure:
stop propagation, report safe metadata, and coordinate response with Brad.
Do not borrow another agent's or a human's credentials.

Tie governed changes to an owning issue. Record exceptions with scope, reason,
risk, owner, expiry and follow-up, and obtain Brad's explicit approval before
acting. A deviation note is not approval and cannot silently amend policy.

Policy text does not configure GitHub. Verify effective protections and actual
required checks via the API. Report missing controls, identities and platform
limits explicitly; never call a convention machine-enforced. In particular,
a shared author identity cannot supply independent GitHub approval. Deferred
identity enforcement does not authorize bypass or replace Yomi's review.

## 1. Policy map

These root documents are binding project policy:

| Document | Responsibility |
|---|---|
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Respectful participation, reporting, and enforcement |
| [AI_POLICY.md](AI_POLICY.md) | AI inclusion and contributor accountability |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow and applications for elevated access |
| [SECURITY.md](SECURITY.md) | Private vulnerability reporting, support scope, and data protection |
| [testing.md](testing.md) | Test evidence and review gates appropriate to the change |
| [REPOSITORY_HYGIENE.md](REPOSITORY_HYGIENE.md) | Layout, tracked content, temporary outputs, and exceptions |

[CLAUDE.md](CLAUDE.md) is the canonical shared agent guidance;
[AGENTS.md](AGENTS.md) points to it. Developer instructions must stay consistent
with this policy suite. The [architecture](docs/ARCHITECTURE.md) and
[theming guide](docs/THEMING.md) describe the application contracts that changes
must account for.

## 2. Roles and authority

| Role | Responsibilities and access |
|---|---|
| **Maintainer** | Decides project direction, accepts changes, appoints collaborators, manages releases and security response, and approves policy amendments |
| **Contributor** | A participant explicitly granted elevated project access; helps with review, triage, or implementation within delegated responsibilities |
| **Participant** | Anyone proposing changes, reporting bugs, reviewing work, or contributing through a fork and pull request |

Anyone may propose changes in any area. Formal Contributor status is optional
and does not determine the value of a person's work. Elevated repository access
does not by itself authorize merging to `main`, publishing releases, managing
credentials, or changing repository settings; those actions belong to
the specific dev/CEO/Brad delegations in the common policy above; repository
settings still require explicit assigned scope.

Brad is the current primary Maintainer and has the final decision when a
technical or governance disagreement remains unresolved. Additional Maintainers
may be appointed explicitly, with their responsibilities recorded here.

These roles describe project authority; they do not assert that GitHub branch
protections, teams, or other access settings are already configured.

## 3. Decision process

Ordinary changes are proposed and reviewed in pull requests. Use an issue first
for substantial design changes when practical, especially changes to stored
data, authentication, public URLs, themes, or extension interfaces. Public
discussion informs the decision; a Maintainer makes it and records significant
decisions in the associated issue, PR, or maintained documentation.

PRs follow the title and body format in
[CONTRIBUTING.md](CONTRIBUTING.md#pull-request-format), using the canonical
[PR template](.github/pull_request_template.md). Authors and automation use
the same format; required evidence must satisfy [testing.md](testing.md)
before merge.

Maintainers decide whether a contribution fits the project and has sufficient
review, validation, documentation, and compatibility handling. Review should
identify concrete issues and apply the same quality bar to all contributors,
including those using AI. Silence or a bot-generated review is not approval.
Explicitly delegated automation may carry out approved actions within its scope.

Security details use the private process in [SECURITY.md](SECURITY.md).
Conduct reports use [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Maintainers may
act immediately to contain a security incident or serious conduct violation,
then record an explanation when it is safe to do so.

## 4. Binding technical policies

### Protect sites and compatibility

Existing content and working sites are the compatibility baseline. Prefer
additive changes and preserve existing behavior when configuration is absent.
Review compatibility effects on:

- SQLite schema, stored content, account roles, and session handling;
- `data_dir`, the default database and upload locations, and asset URLs;
- public routes, published slugs, and admin form behavior;
- theme lookup and fallback, template names and context, and
  `app/site_ext.wfl`'s boot and dispatch contracts;
- the WFL runtime requirements and the pinned Scribe revision.

A breaking change needs an explicit Maintainer decision, a documented reason,
an upgrade or migration path, and relevant compatibility tests. Data migrations
must explain backup and recovery requirements and the effect on existing
databases. Do not silently reset a site, discard content, reopen the installer,
or overwrite deployment-specific configuration or extensions during an upgrade.
Security fixes may require an expedited change with the impact documented.

Scriptorium has no fixed deprecation window or supported-release series yet.
WFL's language-level versioning and deprecation schedules do not automatically
become Scriptorium's release policy.

### Tests and documentation accompany behavior changes

Follow [testing.md](testing.md) for risk assessment, regression coverage,
Red-to-Green evidence, and the checks required for the affected layers. Record
the commands run and their actual results, including any unavailable checks.
Do not claim a passing check that was skipped or could not run.

Update user-facing instructions, architecture notes, examples, and configuration
documentation in the same change as the behavior they describe. Documentation
must distinguish implemented behavior from plans and known limitations.
Commit messages follow the conventional prefixes described in
[CONTRIBUTING.md](CONTRIBUTING.md).

### Respect the existing architecture and repository layout

Scriptorium is deliberately grandfathered under the house layout standard for
new WFL projects. Its `main.wfl`, include chain, `TestPrograms/`, and existing
theme layout remain supported. A structural migration is a separate Maintainer
decision, not incidental cleanup. Follow [CLAUDE.md](CLAUDE.md) and
[REPOSITORY_HYGIENE.md](REPOSITORY_HYGIENE.md).

Scribe is a pinned dependency at `lib/scribe`. Library changes belong upstream;
Scriptorium updates the submodule pin through a reviewed change with relevant
tests. Dependency update automation proposes changes and does not bypass
review or grant itself release authority.

### Protect security and privacy

Preserve authorization, CSRF checks, parameterized SQL, output escaping, and
safe filesystem handling. Changes at these boundaries require negative tests
and review of the affected request paths. Treat extensions and themes as
trusted deployment inputs, not a sandbox for untrusted code.

Never commit credentials, live databases, session tokens, private content,
uploaded user files, or production logs. Use synthetic or sanitized fixtures.
Follow [SECURITY.md](SECURITY.md) for vulnerability reports and private data.

## 5. Contributor and Maintainer appointments

Apply for Contributor status through the process in
[CONTRIBUTING.md](CONTRIBUTING.md#becoming-a-contributor). Maintainers consider
judgment, quality, respectful communication, and willingness to maintain the
work. Credentials, contribution counts, and avoiding AI tools are not
prerequisites. There is no automatic promotion timeline.

Maintainers may invite established Contributors to take on Maintainer duties.
Appointments, delegated responsibilities, and changes to standing access must
be explicit. Access may be reduced or withdrawn for inactivity, a changed
responsibility, security needs, or policy violations.

## 6. Releases, assets, and licensing

Official releases follow the common policy’s conditional CEO/Brad gate.
Publishing credentials and any secret changes remain Brad’s decisions.
Release notes must identify the source revision, relevant dependency changes,
upgrade instructions, and known limitations. The security support scope lives
in [SECURITY.md](SECURITY.md); no release cadence or backport period is implied.

Contributions are submitted under the repository's [Apache-2.0 license](LICENSE).
Contributors must have the right to submit their work and preserve applicable
third-party licenses and attribution. Contributions do not transfer copyright
ownership to the project. No separate CLA or DCO sign-off process is established
by this policy. Any proposed license change requires a documented decision and
the necessary permissions from the relevant rights holders.

Project contribution access does not grant access to deployed sites. Deployment
operations, credentials, site content, and backups remain under the authority
of each site's operator; follow the relevant infrastructure instructions.

## 7. Disputes and amendments

Resolve technical disagreements through specific evidence and discussion on
the relevant issue or PR. The primary Maintainer resolves disputes that remain.
Conduct and security concerns follow their respective reporting policies.

Propose policy changes in a pull request and allow reasonable comment for
material changes. Maintainer approval makes an amendment effective. Update all
affected root policies and agent guidance together; editorial corrections need
no extended discussion. Record any urgent exception with its scope and reason,
keeping sensitive details private where necessary.

Effective: 2026-09-12.
