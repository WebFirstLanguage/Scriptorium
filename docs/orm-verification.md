# ORM verification record

This record distinguishes local candidates, verified official publication and
the complete runner's isolated remote failure proof. The final clean-run result,
exact PR head and GitHub merge checkout are recorded in the Validation section
of [Scriptorium PR #16](https://github.com/WebFirstLanguage/Scriptorium/pull/16).
Local candidate passes are not substitutes for that final official-image gate.

## Runtime prerequisites

The replacement official nightly
[35512196018](https://github.com/WebFirstLanguage/wfl/actions/runs/35512196018)
completed successfully at source `23c1a4577da68d853fa30c49a17773427471eca4`,
version **26.9.16**. It contains all four reviewed and approved upstream changes,
including #741's explicit finite invocation budget. Its version-only commit is
the direct child of #741's merge `3720dd74c82f4a1354aa64cfe66260ec3eccba93`;
tag `v26.9.16` resolves to that same source.

The published image is
`bsbyrdwfl/wfl@sha256:1092a0c557731113f08673c764e0deb9e0b053992b4488974863f0a8d692db91`.
Independent inspection of the Docker publication job verified version, source,
both current tags and all five consumer checks, including assertion-failure
exit 1. Both native packaging jobs and the complete release gates passed.
Each platform's integration job passed 164 WFL programs, 36 documentation
checks and three web checks, including the real 305-second assertion.

The exact governance provisioning script verified the fresh canonical manifest,
immutable Windows MSI sidecar and downloaded bytes, extracted without installing,
and confirmed version 26.9.16. MSI SHA256:
`73db4e8b9f725b6e1953ba453ca972e659a0388e0d343d4afea3b13fb8cfddec`.
Extracted executable SHA256:
`32375058e0111f6c159144a8ffa9bd5b3a3bde81f578eca015149053ea4c6cbb`.
The immutable Linux archive SHA256 is
`8cd9c852afe069f689fee014c71a9667202be9e92344f139f1605b5b167c3fe6`.
Both Governance job summaries independently record these platform artifacts,
version and source. The complete Scriptorium command now runs against this
official runtime; the isolated remote deliberate-failure proof follows below.

### Initial publication history

The initial three separate upstream changes have independent technical review,
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

## Official-image CI acceptance

Commit `b9e7903286495d6665b7cfdbd8916a4dc5abd952` adds a temporary WFL assertion
with marker `SCRIPTORIUM_INTENTIONAL_CI_FAILURE_PROOF`. On the combined local
runtime, `scripts/run_tests.wfl --group application` reports 24 suites,
23 passed, one failed, exit 1; only that deliberate suite fails. The retained
log is `target/ci-propagation-red-local.log`. Its required remote assertion-failure
proof has now completed, and the deliberate test is removed from the final
source. Normal complete-suite discovery contains 41 suites.

[Blacksmith run 35513765769](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35513765769),
[job 106086113517](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35513765769/job/106086113517),
tested PR head `58362064ac9594c0a7e35d66dd968e72220bc285` through merge checkout
`b3d92ba400ad55a49535e8393c1964bc3338904f` against base
`4ec5c88d9e4ae27041599ad8293a28130b56fbf2`. It freshly pulled and resolved the
official 26.9.16 image `sha256:1092a0c557731113f08673c764e0deb9e0b053992b4488974863f0a8d692db91`,
recorded WFL source `23c1a4577da68d853fa30c49a17773427471eca4` and unchanged
Scribe `93d62af5a6ed6c3ce257ef888107fc3ca1e2dc1d`, then executed
`wfl --execution-timeout 1200 scripts/run_tests.wfl`.

The result was **42 suites: 41 passed, one failed**, with runner and Actions
exit 1. The sole top-level failure was `TestPrograms/ci-propagation.test.wfl`,
showing the named marker and the exact deliberate assertion. Every functional
suite completed successfully, including all eight integrations, tooling,
runtime probes, executable progression and pinned Scribe. The runner's nested
negative fixtures are intentional assertions about failure propagation; their
containing suite passed. Container cleanup passed. Independent log review
confirmed no additional failure or parent deadline expiry. Suite execution ran
from 13:32:02.4093265 to 13:36:25.8055402 UTC (about 263 seconds); the separate
upstream 305-second tests establish the longer-budget boundary.

Both [Governance platforms](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35513765906)
passed three suites and 41 assertions each (28 hygiene, four migration CLI,
nine runner), plus static hygiene with 180 paths including the deliberate file.
All six [runtime/media gates](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35513764169)
passed 15 assertions and cleanup. Their runtime identities agree with the
official publication. After removing only the deliberate suite, the required
clean gate runs the same full command with 41 suites; final-head results and
provenance are retained in the PR's Validation section.

### Earlier official-image attempts and runtime review

The first full run on the published 26.9.14 image,
[35507634634](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35507634634),
tested PR head `07e8adcb7785c168c37fd56cc35e88492809a820` through merge checkout
`86185103700e28cd12ba9379f00adebdd056dfbd`. It reported **32 passed, 10 failed**,
exit 1: the intentional assertion, an oversized-upload transport failure, and
eight failures after the runner reached the runtime's 300-second whole-command
budget. This is not isolated failure-propagation proof. All five standalone
[runtime capability gates](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35507632213)
passed. Both [Governance platforms](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35507634656)
passed hygiene 28, migration CLI 4 and runner 9 cases (three suites), followed
by repository hygiene with 180 paths including the deliberate test.

The same published Windows runtime completed **42 suites: 41 passed, one
intentional failure**, exit 1, in approximately 160 seconds. Its executable
SHA256 is `da109d5926f6af4a2f24c45150140764c406c055aef2dd7e43e45b85278f1dfe`;
the log is `target/full-official-windows-red.log`. Independent timing comparison
found migration CLI tests took 35.1 seconds on native Linux, 36.1 in Docker and
12.6 on Windows. No connection leak or fixed delay was found. The longer full
Linux run needs an explicit finite invocation budget while retaining child
deadlines. The media fixture now uses a portable rejection boundary while still
requiring HTTP 413, no stored rows or files, and a subsequent successful request;
see `tests/integration/EVIDENCE.md`.

The next complete run,
[35508311002](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35508311002),
tested head `147b15c88c5fbd29e4826a32a0db5daf747ae59d` through merge checkout
`1c190c5a1798ca86244b9bb0142251f35c78b3b6` on the same official runtime.
Media passed **2/2** both within this complete run and in its new focused Linux
gate. The complete runner still reported **32 passed, 10 failed**, exit 1:
the intentional assertion and nine failures after the 300-second parent deadline.
Both Governance platforms and all six focused capability jobs passed. This is
evidence that the media correction works, not isolated deliberate-failure proof.

A fourth upstream change,
[WFL #741](https://github.com/WebFirstLanguage/wfl/pull/741) at
`358dc9eb15f61152f75f816d9e51c396cd24dd77`, has passed independent review and all
exact-head CI checks. It adds an explicit finite
`--execution-timeout` option for the shared invocation budget. The prepared
complete-suite command is `wfl --execution-timeout 1200 scripts/run_tests.wfl`.
It preserves existing per-suite timeouts and child process limits. Official
26.9.16 now contains this option; the isolated official-image Red is recorded
above and final clean-head acceptance is recorded in the PR.
Independent technical review found no remaining source or fixture blocker;
25 fast WFL cases, a real 305-second WFL boundary assertion, 2414 existing Rust
tests (27 existing ignored), formatting, strict Clippy and 36 documentation checks passed
locally. Exact-head upstream CI
[35510552984](https://github.com/WebFirstLanguage/wfl/actions/runs/35510552984),
Docker validation, configuration lint and CodeQL all passed. Both integration
jobs passed 164 WFL programs, 36 documentation checks and three web checks;
24 existing integration skips remain recorded. Program sweeps passed 188 on
Linux and 187 on Windows, with zero failures or timeouts. All seven new CLI
budget suites ran on both platforms. Independent log inspection verified the
real long-boundary assertion passed after 305.009 seconds on Linux and 305.161
seconds on Windows. These jobs tested merge checkout
`23a523bfcfe3d5015b1ab3da6dbb3272512f769f` containing the exact PR head.
The user approved this additional merge and publication. PR #741 is merged as
`3720dd74c82f4a1354aa64cfe66260ec3eccba93`; the replacement official nightly
publication is verified above.

The prepared command completed locally with the reviewed CLI candidate:
**42 suites, 41 passed, one intentional failure**, exit 1. Only
`TestPrograms/ci-propagation.test.wfl` failed; every functional suite completed.
The candidate reports WFL 26.9.15, with executable SHA256
`1185f150c8214d982a27431d4b88b94f7f20d6ce6c718161c35120deb817650f`.
It was built from upstream Red `84cb272c` plus the reviewed, frozen CLI source
change before its Green commit. Scriptorium was at
`2d1d6e2a5ca1ea98396f1d587218b7279144077f` plus the prepared command/help and
documentation changes; test scenarios were unchanged. The log
`target/full-cli-budget-candidate-red.log` spans 11:45:41–11:54:10 UTC on
2026-09-20, approximately 509 seconds by file metadata. Repository hygiene passed
with 180 paths including the intentional suite. This proves local consumer
behavior beyond 300 seconds, not a final official-image CI pass.

Subsequent review of #741 found that a shorter override could alter server HTTP
timeouts, a final duration wait could miss expiry, and dump modes could ignore
a misplaced option. The reviewed remedy preserves the original per-operation
duration, checks sleeping/receiving waits without dropping active WFL handlers,
and rejects the misplaced option before output. New WFL regressions cover
buffered and streamed HTTP, final waits, owned-child cleanup observed before any
test-side process reap, WebSocket listener release, and main-loop exemption.
All 25 focused WFL cases and the fresh 305-second boundary check passed locally.

The remedy at WFL `30ed9462` was retested against clean Scriptorium source
`df8039cc252e2e48772ed88b9d273b98e30a67c5` with the same complete command:
**42 suites, 41 functional passes, one deliberate failure**, exit 1. The WFL
26.9.15 candidate executable SHA256 is
`c0619c544b09551ce7988f58a564f50ff04e48a5e94a6f903c08a141b911c516`.
Log `target/full-cli-budget-reviewed-red.log` spans 12:16:55–12:20:17 UTC,
approximately 202 seconds. This latter consumer run does not itself prove the
300-second boundary; the separately repeated long WFL test does.

The first #741 CI run,
[35509162373](https://github.com/WebFirstLanguage/wfl/actions/runs/35509162373),
failed in an unchanged Windows trusted-proxy fixture when its previously probed
port was occupied before the WFL server bound it. Linux integration was canceled
by matrix fail-fast; neither long-duration step ran. The final fixture now binds
port zero and discovers the actual owned address, retaining all existing
assertions; its seven cases passed locally and in the successful final Windows
integration job. The replacement official publication also passed; no failed
or canceled job is counted as a pass.

The implementation and final-revision check record are in
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
