# ORM verification record

This record separates local candidate verification from the required published
nightly-image result. The latter is still pending. Passing source-built runtime
tests does not establish that the published nightly supports this change.

## Runtime prerequisites

All three separate upstream changes have independent technical review,
successful exact-head remote CI and approved merges. Official nightly
[35506079498](https://github.com/WebFirstLanguage/wfl/actions/runs/35506079498)
completed successfully for their combined source
`8d82d785ea59300834de1c48b04a7ba0e187a1cd`, version `26.9.14`.

Published Docker digest:
`bsbyrdwfl/wfl@sha256:8498abec67995274cb4d6cc2ee9580be11f70e15af20497bb62e51d4b2058e3c`.
The immutable Windows MSI SHA256 is
`a3ff0b5c8dd2141536004298583fb698c20596fb5a49ad90d53f56d4ac15e3d4`;
the Linux archive SHA256 is
`b6b74d37ad4baae4bf7333c8a27f5dcc332104cdf7257c6da6754ea1fc7c809d`.
The exact governance provisioning script downloaded, verified and extracted
the Windows MSI locally and confirmed its version. Both publication jobs and
all nightly validation gates passed. The same-day GitHub mirror remains at
26.9.12 by its immutable-release policy; governance uses the canonical CDN.
A retained one-hour CDN cache entry initially returned the old manifest even
with `Cache-Control: no-cache`. A unique request key returned the verified new
manifest and is now part of governance provisioning. Immutable asset downloads
and checksums are still independently verified.

| Upstream PR | Tested head | Remote CI |
| --- | --- | --- |
| [HTTP redirect and repeated-header controls #737](https://github.com/WebFirstLanguage/wfl/pull/737) | `b8e5e8768a13c44aa033a3cd732b85f089262eff` | [35500755237](https://github.com/WebFirstLanguage/wfl/actions/runs/35500755237), Linux 169 and Windows 168 WFL programs passed |
| [Owned process lifecycle and diagnostics #738](https://github.com/WebFirstLanguage/wfl/pull/738) | `f54243f43769b8d6e8ebe0b8f54ed2b2a735b234` | [35505056152](https://github.com/WebFirstLanguage/wfl/actions/runs/35505056152), Linux 174 and Windows 173 WFL programs passed |
| [Application errors and pinned schema transactions #739](https://github.com/WebFirstLanguage/wfl/pull/739) | `59709aed97d045dbd9a04093fff5c32ae60a95e3` | [35505568741](https://github.com/WebFirstLanguage/wfl/actions/runs/35505568741), Linux 181 and Windows 180 WFL programs passed |

The merge commits are `eecd658c32e23abdb6f4e0cc881d8af26dacd2d2` (#737),
`d6993e77578892e0a93d3b8c8b08d6b1b55eede8` (#738), and
`8d82d785ea59300834de1c48b04a7ba0e187a1cd` (#739). The final schema PR's
combined Linux/Windows integration gates each passed 157 programs, 36
documentation checks and three web checks. Its Rust gate passed 2429 tests
with 27 existing ignored tests.

The listed WFL gates had zero failures and zero timeouts. Existing platform
skips remain recorded by upstream CI; these counts do not claim every upstream
scenario ran on every platform. Workspace tests, formatting, strict Clippy,
database integration, documentation and web checks also passed in those runs.

The combined local candidate is WFL source
`df6ad9a2f9f401d943edfdec2e3804941a9c513f`, reporting version `26.9.12`.
Its Windows executable SHA256 is
`b96c06f6013a9a64d4d042c9b379a30af1c8d274d7855b5ebe9d7fe14a750d1c`.
Scribe remains pinned to `93d62af5a6ed6c3ce257ef888107fc3ca1e2dc1d`.

## Local complete-suite gate

The final candidate complete runner passed **41/41 discovered suites**, zero
failures, exit 0, on Scriptorium source
`3bc7b4faaf9c000047d940f0e420067b777db5c9`. This includes the historical-index
review regression, strengthened CLI CRLF fixture and nested HTTP probe cleanup.
The exact command was `target/runtime/combined-df6ad9a2/wfl.exe scripts/run_tests.wfl`.
The ignored local log is `target/full-candidate-final.log`. The earlier complete
40-suite result is retained in `target/full-candidate-df6ad9a2-green.log`.

`python scripts/check_repo_hygiene.py` passed with 179 candidate paths; Git
reported a clean worktree and `git diff --check` passed. The source audit found
no active Python test implementation or driver. The only non-WFL executable code
under tracked tests/scripts is the hygiene checker implementation and the existing
Scribe update utility.

The hygiene checker fixtures create disposable Git repositories and need child
Git execution permission. A first sandboxed complete run passed 39/40 suites;
the tooling suite received an OS access denial starting Git. With child-process
access, the unchanged assertions passed. This environment failure is not
represented as a product test pass or hidden by skipping the fixture cases.

Runtime analysis can print nonfatal type diagnostics while executing these
tests. [The independent analysis report](type-analysis-review.md) distinguishes
reproduced analyzer limitations from intentional unknown-type safety checks.
This record does not claim a clean static-analysis gate.

## Outstanding remote acceptance

Commit `b9e7903286495d6665b7cfdbd8916a4dc5abd952` adds a temporary WFL assertion
with marker `SCRIPTORIUM_INTENTIONAL_CI_FAILURE_PROOF`. On the combined local
runtime, `scripts/run_tests.wfl --group application` reports 24 suites,
23 passed, one failed, exit 1; only that deliberate suite fails. The retained
log is `target/ci-propagation-red-local.log`. Its remote assertion-failure proof
and removal are still required; the full suite temporarily contains 42 suites.

- Push an actual intentionally failing WFL test, observe the new runner and
  its Blacksmith CI job fail, then remove it and verify a clean run.
- Inspect all required checks on the final proposed Scriptorium revision.
- Record the freshly pulled and resolved `bsbyrdwfl/wfl:nightly` image digest,
  runtime version, Scriptorium checkout revision and unchanged Scribe revision.

The implementation is available in draft
[Scriptorium PR #16](https://github.com/WebFirstLanguage/Scriptorium/pull/16).
Its first complete-suite attempt,
[35504493284](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35504493284),
successfully pulled the official image and provisioned the disposable container,
then failed before test execution because that image lacks the new process CWD
syntax. The log also reports `current_executable` as undefined. This is the
expected unmet runtime prerequisite, not an accepted failing test or the
deliberate assertion-failure proof.

That attempt used PR head `26bc1c2eb9e19a604bf91c9b43171e433ff56101`, GitHub's
tested merge checkout `4545f6246dbdaac704aa0f18c19b76e30a0073bd`, WFL `26.9.12`,
Scribe `93d62af5a6ed6c3ce257ef888107fc3ca1e2dc1d`, and image
`bsbyrdwfl/wfl@sha256:7ddc51e6320affa7cfe26263fece590ddbdebe5582659b7e660ca823ed3ddbf1`.
Container cleanup succeeded. Both Linux and Windows
[Governance jobs](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35504493283)
also provisioned the official nightly successfully and failed on the same
missing process syntax; their later hygiene steps were skipped, not passed.

The initial runtime-capability Red in
[35499009581](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35499009581)
used Scriptorium `a81ecf9c2c68784f3deace8b3521feae762e51ff` and image
`bsbyrdwfl/wfl@sha256:7ddc51e6320affa7cfe26263fece590ddbdebe5582659b7e660ca823ed3ddbf1`.
It proves the original runtime gaps; it is not a substitute for deliberate
failure-propagation proof through the completed new test runner.
