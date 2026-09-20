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

The candidate complete runner passed 40/40 discovered suites before independent
review added the historical-index regression. The final expanded source gate
is pending. The earlier 40-suite log is
`target/full-candidate-df6ad9a2-green.log` (ignored local evidence).

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

The initial runtime-capability Red in
[35499009581](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35499009581)
used Scriptorium `a81ecf9c2c68784f3deace8b3521feae762e51ff` and image
`bsbyrdwfl/wfl@sha256:7ddc51e6320affa7cfe26263fece590ddbdebe5582659b7e660ca823ed3ddbf1`.
It proves the original runtime gaps; it is not a substitute for deliberate
failure-propagation proof through the completed new test runner.
