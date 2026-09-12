<!--
Title: <type>(<optional scope>): <imperative summary>
Example: fix(auth): reject expired sessions

Keep the headings below and replace the prompts with concrete details.
Scale the detail to the change. Use "N/A — reason" for an inapplicable field;
record missing checks as "Not run — reason", never as a pass. Drafts may mark
unfinished evidence as pending. Keep the title and body aligned with the final diff.
-->

## Summary

<!-- Explain the problem and resulting behavior. Include a brief before/after
example when useful, observable acceptance criteria, and related issue links. -->

## Changes

<!-- List the material changes and why they are needed. Include only details
that help a reviewer assess the implementation; omit the work-session history. -->

## Compatibility and risk

- **Risk class and reason:** <!-- R0, R1, R2, or R3; see testing.md. -->
- **Affected contracts:** <!-- URLs, schema/data/uploads, configuration, themes,
  extension hooks, runtime requirements, or the Scribe pin; say none if unaffected. -->
- **Upgrade and recovery:** <!-- Migration, backup, rollback or forward-repair
  steps. Link the approved transition plan for a breaking change, or explain N/A. -->
- **Remaining risks or gaps:** <!-- Untested boundaries, limitations, and any
  exception with its approval, scope, expiry, and follow-up issue; or none. -->

## Validation

- **Tested revision and environment:** <!-- Commit, OS, relevant tool versions;
  include WFL and pinned Scribe revisions for runtime checks. -->
- **Regression evidence:** <!-- Intended failure before the fix and passing
  result afterward; Green before/after for a refactor; explain N/A for prose. -->

| Check or exact command | Result and evidence |
|---|---|
| <!-- Required automated check --> | <!-- Actual result, counts or CI run link; identify failures and checks not run. --> |
| <!-- Affected HTTP/UI, security, accessibility, or recovery check --> | <!-- Setup, expected/actual outcome, and evidence; or N/A with reason. --> |

## Checklist

- [ ] The title, summary, and risk assessment match the final diff.
- [ ] Required validation is recorded above; failures and missing checks are explicit.
- [ ] Documentation, examples, and upgrade/recovery guidance are updated where applicable.
- [ ] I reviewed the diff for repository hygiene, secrets, and private site data.

Follow [CONTRIBUTING.md](https://github.com/WebFirstLanguage/Scriptorium/blob/main/CONTRIBUTING.md),
[testing.md](https://github.com/WebFirstLanguage/Scriptorium/blob/main/testing.md), and
[REPOSITORY_HYGIENE.md](https://github.com/WebFirstLanguage/Scriptorium/blob/main/REPOSITORY_HYGIENE.md).

Report undisclosed vulnerabilities privately using [SECURITY.md](https://github.com/WebFirstLanguage/Scriptorium/blob/main/SECURITY.md).
