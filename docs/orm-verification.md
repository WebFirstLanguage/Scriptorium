# ORM verification record

This record separates local candidate verification from the required published
nightly-image result. The latter is still pending. Passing source-built runtime
tests does not establish that the published nightly supports this change.

## Runtime prerequisites

All three separate upstream changes have independent technical review and
successful exact-head remote CI. They remain prerequisites until merged and
included in an official nightly publication.

| Upstream PR | Tested head | Remote CI |
| --- | --- | --- |
| [HTTP redirect and repeated-header controls #737](https://github.com/WebFirstLanguage/wfl/pull/737) | `b8e5e8768a13c44aa033a3cd732b85f089262eff` | [35500755237](https://github.com/WebFirstLanguage/wfl/actions/runs/35500755237), Linux 169 and Windows 168 WFL programs passed |
| [Owned process lifecycle and diagnostics #738](https://github.com/WebFirstLanguage/wfl/pull/738) | `96aa48cb122f48c68e8e937dc4ac44cbe283f77f` | [35503440343](https://github.com/WebFirstLanguage/wfl/actions/runs/35503440343), Linux 173 and Windows 172 WFL programs passed |
| [Application errors and pinned schema transactions #739](https://github.com/WebFirstLanguage/wfl/pull/739) | `9defb44208fd3fdc10c3758b3dc1f3cc56706251` | [35502181204](https://github.com/WebFirstLanguage/wfl/actions/runs/35502181204), Linux 175 and Windows 174 WFL programs passed |

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
no active Python test implementation or driver. The only non-WFL files under
tracked tests/scripts are the hygiene checker implementation and the existing
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

- Publish the reviewed upstream changes through the official nightly workflow.
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
