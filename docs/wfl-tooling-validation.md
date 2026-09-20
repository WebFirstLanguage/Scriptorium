# WFL tooling conversion evidence

The mapping in [wfl-test-inventory.md](wfl-test-inventory.md) preserves all eight
original runner requirements and all 28 hygiene requirements. The resulting
suite, its fixtures and helpers, and the complete runner are WFL. The unchanged
Python hygiene utility is only an implementation subject invoked by WFL.

## Local results, 2026-09-20

`wfl scripts/run_tests.wfl --group tooling` passed both suites:

| Suite | Result | Meaning |
|---|---|---|
| `tests/tooling/runner.test.wfl` | 9/9 | Eight original requirements plus complete default discovery of application, tooling, HTTP, examples and Scribe |
| `tests/tooling/hygiene.test.wfl` | 28/28 | Every inventory row, including binary source assets, all SQLite sidecars, synthetic Git indexes/gitlinks, ignored files, links and fail-closed setup errors |

The process-only source-built runtime at upstream `a32c74f1` passed first; the
combined runtime `ae5395d9bd215d0d9fa1c039e666f03c8897cf88` passed after the hygiene
profile changed to require WFL files. Both report WFL `26.9.12`; the published
26.9.12 release does not contain these changes. Combined executable SHA256:
`76F612CA1BBAF4484B2CC2BDA86D876588BC765DE9C38B7DAA8951BAD143B911`.
Local detailed output is ignored at `target/tooling-combined-results.txt`.

The runner suite executes a deliberately failing WFL expectation and a distinct
runtime-error fixture. It requires runner exit 1, both stdout and stderr
diagnostics, and successful execution of the later suite. The timeout case owns
a WFL child/grandchild, verifies the descendant started, and asserts its delayed
write never occurs after the hard timeout. Scribe tests verify a separate cwd,
fresh build directory, exclusion of Git/cache metadata, removal of the temporary
copy, and unchanged original bytes. No retry or expected-failure wrapper hides
these outcomes. Fixture syntax errors during development are not Red evidence.

Independent root-agent source review accepted the runner/helper and the
37-case behavior mapping before removal of the Python runner and tooling
suites. Review is technical; Maintainer acceptance remains separate.

## Changes to the command contract

The complete command includes all groups and pinned Scribe by default. Use
`--group` for an explicitly focused run. The default executable is the exact
runtime which launched the runner; `--wfl` still overrides it. Captured stderr
content is labeled in the runner's output, since WFL's display facility writes
stdout. The runtime handles user interruption and owns shutdown cleanup;
Python's specific KeyboardInterrupt message/status is not a portable promise.
Timeouts use finite positive JSON-number notation up to one year.

## Final acceptance still required

The full application/ORM/migration/recovery/HTTP/example suite and final-revision
remote jobs are recorded with the overall PR. Governance retains Blacksmith
Linux and GitHub-hosted Windows tooling coverage with explicit WFL provisioning.
The complete nightly job still pulls `bsbyrdwfl/wfl:nightly`, resolves its digest,
records runtime and source revisions, and invokes the WFL runner in a writable
disposable copy of a read-only checkout. Python executes only the hygiene
checker subject. A source-built local pass does not establish a published
nightly pass. Remote intentional-failure evidence followed by the clean final
revision remains required before the PR is described as ready to merge.
