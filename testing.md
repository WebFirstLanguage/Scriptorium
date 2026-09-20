# Scriptorium testing policy and project profile

This is Scriptorium's binding testing policy, adapted from WFL's testing
governance to this WFL application. It defines both required evidence and the
limits of the tooling that exists today. It does not claim that the repository
already implements every gate required for a release.

- Policy and profile version: 1.1.
- Adopted: 2026-09-12; CI profile updated: 2026-09-20.
- Test-suite and infrastructure owner: the Maintainer named in
  [GOVERNANCE.md](GOVERNANCE.md).
- Next adoption-gap review: 2026-10-12, or before the next affected behavioral
  change or release, whichever comes first.

## Required evidence

MUST means required; SHOULD means the normal expectation with a written reason
for a deviation. A change record is the PR or issue that retains scope, results,
review, and any accepted limitation.

Every behavior change MUST have a regression test at the lowest useful layer
and exercise every affected boundary. A fix MUST reproduce the defect. Use
Red → Green → Refactor → Broaden → Record:

1. State observable acceptance criteria and identify the affected contracts.
2. Run a new or strengthened test against the previous implementation. It must
   fail for the intended behavioral reason. A syntax error or broken fixture
   does not count as Red.
3. Make the implementation pass, then refactor with tests passing.
4. Run the full application suites and affected boundary and risk checks.
5. Retain exact commands, tool versions, expected failure, passing results,
   tested revision, and limitations in the change record.

For pure refactoring, characterize the affected behavior first and show Green
before and after. For prose, formatting, or other work without behavior changes,
verify the relevant links, commands, or structure; application regression tests
are not required simply to change wording. New validation or test-runner logic
is behavior and needs failure-path tests.

Tests MUST assert outcomes rather than merely mirror implementation. A component
test that calls an action does not prove its router, real HTTP response, browser
journey, or persisted-file recovery. Use the real boundary for that claim.
Required failures MUST NOT be hidden with retries, skips, relaxed assertions, or
quarantine. Investigate infrastructure failures with evidence before rerunning;
keep the original failure visible. A flaky required test is a failure to fix.

## Change risk

Use the highest applicable class and have the reviewer check the assessment.

| Class | Typical Scriptorium change | Required scope |
|---|---|---|
| R0 | Prose, comments, formatting with no behavior change | Relevant documentation and hygiene checks |
| R1 | Isolated utility or development-tool behavior | Red/Green regression, boundaries and negative cases, affected suites |
| R2 | Routing, templates, theme resolution, extension contract, Scribe pin | R1 evidence plus real affected integration and user journey |
| R3 | Auth, roles, CSRF, installer, uploads, schema, data location or recovery | R2 evidence plus adversarial cases, data integrity/recovery checks, and independent domain review |

Independence means the reviewer did not author the implementation and inspects
the actual diff and evidence. An independent review agent can provide technical
review, but project acceptance and merge authority remain with the Maintainer.
Missing automation does not exempt new or changed behavior from these rules.

## Runtime and environment

The application needs WFL with its web server, SQLite, crypto, and testing
built-ins, plus the exact Scribe commit recorded at `lib/scribe`. Initialize
submodules with `git submodule update --init --recursive`. Python 3.11 or newer
and Git are needed to exercise the existing hygiene checker; every test
scenario, fixture, assertion, helper and driver is WFL. Run individual suites from the
Scriptorium root so relative includes, templates, and assets resolve correctly.

WFL 26.9.3 on Windows is the local adoption baseline: the five application
suites passed there on 2026-09-12. This is a recorded observation, not a complete
supported-platform matrix or a minimum-version promise. Record `wfl --version`,
OS, Scriptorium revision, and Scribe revision with runtime evidence. No Linux,
macOS, alternate WFL version, or production configuration is release-verified
merely because these suites passed on Windows.

The original five suites include in-memory SQLite and direct action calls.
Additional ORM, migration and HTTP suites use disposable file-backed databases.
They need no external credentials or service. Test data MUST be synthetic. For HTTP/UI and
file-backed tests, use a disposable checkout, a temporary `data_dir`, loopback
binding, and an isolated port. Avoid a live site's database or uploads. Keep
test output in the approved locations in
[REPOSITORY_HYGIENE.md](REPOSITORY_HYGIENE.md).

## Executable checks

The complete portable entry point recursively discovers regular `*.test.wfl`
files under `TestPrograms/`, `tests/tooling/`, `tests/integration/`, and
`examples/`, sorts each group, then runs the pinned Scribe suite:

```sh
wfl scripts/run_tests.wfl
wfl scripts/run_tests.wfl --group application
wfl scripts/run_tests.wfl --group tooling
wfl scripts/run_tests.wfl --group integration
wfl scripts/run_tests.wfl --group examples
wfl scripts/run_tests.wfl --group scribe
```

The default executable is `current_executable`, the exact runtime that launched
the runner. `--wfl /absolute/path/to/wfl` selects another executable; a bare
program name uses native PATH lookup. The resolved absolute identity is passed
to every suite as `args[0]`. `--timeout 120` sets the
maximum seconds per suite; 120 is the default. The runner executes suites
sequentially from the proper working directory, preserves stdout and stderr
contents in its output (stderr has a label),
reports every suite's result, and exits nonzero if any suite fails or times out.
An empty selected group, missing interpreter, invalid timeout, or missing
requested Scribe source is an error before suites start. Suite failure and
timeout exit 1; setup/cleanup failure exits 2. There are no automatic retries.
The runner owns child process trees, including on hard timeout. All temporary
fixtures remain under ignored `target/test-artifacts/` and are removed after
their suites. A terminated host/CI container can leave disposable files; it
does not authorize reuse of a live site's data. Helpers do not end in `.test.wfl`.

The default command executes upstream `tests/scribe.test.wfl` from a temporary
copy of the pinned submodule, excluding `.git`, existing `build/`, and caches,
with a fresh `build/` for its fixtures. `--include-scribe` remains a compatibility
option to add Scribe to a focused group.
This avoids writing test output into the dependency checkout. Run it for Scribe
pin changes and changes affecting Scribe integration. CMS-specific Scribe
regressions remain in `TestPrograms/scribe.test.wfl` even when upstream tests
also cover related behavior.

The HTTP port configuration checks start disposable Scriptorium processes and
exercise `/install` using synthetic temporary databases:

```sh
wfl scripts/run_tests.wfl --group integration
```

These checks use the selected WFL executable and require an available loopback
port 8080 for default-port cases. They preserve configured/default port and
startup URL checks and extend real installer, auth, content, users, media,
throttling and restore workflows. See [the integration suite](tests/integration/README.md)
for individual scenarios and fixture ownership. No environment-variable
interpreter override is needed; use the shared `--wfl` option.

| Existing suite | Direct command from the repository root | What it currently exercises |
|---|---|---|
| Utilities | `wfl --test TestPrograms/util.test.wfl` | Slugs, number/field helpers, parsing, config values and valid/default ports, installer validation |
| Data | `wfl --test TestPrograms/db.test.wfl` | In-memory SQLite CRUD helpers, sessions, installer state, rate-limit records, legacy CSRF-column migration |
| Auth | `wfl --test TestPrograms/auth.test.wfl` | CSRF helper acceptance/rejection and session token binding |
| Scribe integration | `wfl --test TestPrograms/scribe.test.wfl` | Markdown, safe-marker/filter propagation, escaping, nested blockquotes |
| Theme configuration | `wfl --test TestPrograms/render.test.wfl` | Theme path selection defaults and traversal rejection |

The data suite tests migration idempotency and the legacy session-column
upgrade. The auth suite does not test the login router or complete role matrix.
The render suite tests path selection; it does not render every theme template
through HTTP. Keep these distinctions in PR descriptions.

Repository tooling checks use the same WFL runner:

```sh
python scripts/check_repo_hygiene.py
wfl scripts/run_tests.wfl --group tooling
```

The tooling suites check the validation and runner failure paths. They do not
substitute for the application suites. Application tests stay in the existing
`TestPrograms/` layout; WFL tooling tests live in `tests/tooling/` and HTTP tests
in `tests/integration/`. The [conversion inventory](docs/wfl-test-inventory.md)
maps all eight original runner requirements and 28 hygiene cases.

## CMS boundaries and critical journeys

When a change touches a journey below, add or extend automated coverage for
the changed behavior and verify the real affected HTTP/UI boundary. Before a
release, exercise all applicable journeys against the exact candidate and
configuration that will be deployed. Record setup, input, expected outcome,
actual outcome, and cleanup. Manual browser checks supply UI evidence while
the automated journey harness remains an explicit adoption gap.

1. **Installation:** fresh database redirects to the installer; valid setup
   creates the administrator and site settings; invalid or mismatched tokens
   fail without mutation; setup locks afterward, including a repeated POST.
   Existing databases start without reopening the installer.
2. **Authentication and authorization:** login, invalid credentials, expiry,
   logout, admin-only operations, and author ownership. Check rejected requests
   leave records and sessions unchanged; exercise the rate-limit boundary.
3. **Content publication:** admin/author create and edit posts and pages,
   draft visibility, publication, navigation, pagination, and deletion. Verify
   the public response and safe rendering of untrusted content.
4. **CSRF and HTTP methods:** valid and missing/wrong tokens for forms and
   multipart uploads; GET requests to mutating routes cannot mutate data.
5. **Media:** accepted uploads, rejected type/size/input, generated storage
   names, authorization to delete, file/database consistency, and retrieval
   under `/assets/uploads/` for default and configured `data_dir`.
6. **Themes and extensions:** default base theme; configured `body/` and legacy
   `templates/` layouts; partial-theme fallback and invalid paths; stock
   extension fallthrough; extension-owned route and boot timing with migrated
   tables; inherited post/page/404 behavior.
7. **Persistence and recovery:** restart preserves users, settings, content,
   and media; upgrading a representative prior schema preserves data; repeated
   migration is safe; a backup restores the database and matching uploads.

UI changes also require keyboard navigation, focus, accessible labels, error
presentation, and narrow-screen checks for affected forms and navigation.
Screenshots can supplement these observations but cannot prove authorization,
keyboard behavior, or data integrity.

## Risk-triggered checks

- **Security:** test allowed and denied cases through the affected boundary,
  including cross-user access, missing/expired sessions, malformed tokens,
  untrusted HTML/Markdown, path traversal, oversized and malformed uploads,
  and injection attempts. Test the actual implemented upload checks; the CMS
  currently uses an extension allowlist, not image-content decoding. Do not
  describe an unimplemented content-inspection defense as verified.
- **Schema, installer, and storage:** use synthetic file-backed databases from
  the previous schema as well as a fresh database. Verify repeated boot,
  partial completion, data preservation, invalid or unwritable paths, and a
  concrete restore or forward-repair plan. An in-memory migration test alone
  does not prove crash recovery or database/upload consistency.
- **Configuration:** exercise unset/default keys and explicit values for
  `web_server_port`, `data_dir`, `theme`, and `theme_root`, including malformed
  values. Account for the current whole-line-comment parsing and out-of-tree
  theme paths.
- **Dependencies:** inspect the actual pinned Scribe diff, run both local and
  upstream suites, and exercise affected rendering paths. Runtime upgrades also
  require the application suites and affected web/SQLite/crypto boundaries.
- **Lifecycle or performance:** changes to request processing or resource
  limits require bounded timeouts, failure handling, restart, and representative
  workloads. Set measured budgets before claiming a capacity or latency target.
- **Test infrastructure:** runner, workflow, discovery, filters, or hygiene
  changes require positive and negative cases, the full tooling suite, and
  Maintainer review. A change must not weaken its own validation to pass.

## CI, merge, and release gates

[Governance](.github/workflows/governance.yml) runs repository hygiene and tooling
checks on Blacksmith Linux and GitHub-hosted Windows.
[WFL tests](.github/workflows/wfl-tests.yml) runs the complete WFL suite via
`wfl scripts/run_tests.wfl` on
`blacksmith-2vcpu-ubuntu-2404`. Both workflows run for pushes and pull requests to
`main` and support manual dispatch.

WFL tests pulls `bsbyrdwfl/wfl:nightly` from Docker Hub for every run, resolves
the image digest, and uses that immutable image for that run's runtime checks.
Python and Git are installed only for the hygiene checker subject. No Python
test runner or test implementation executes. The source checkout is mounted
read-only and copied into the writable disposable container for fixtures.
The job summary records the resolved image digest,
`wfl --version`, and tested Scriptorium and Scribe revisions. The nightly tag is
moving: retain the run URL and digest with PR evidence so a later nightly does
not obscure which runtime was tested. The nightly workflow is not a declaration
that every nightly, platform, or production configuration is supported.

Governance provisions the latest published nightly release on Linux and Windows
and records its asset URL, SHA256 and runtime version before running WFL tooling
regressions. The runner requires WFL's owned-process cwd/timeout/full-result/close
API, explicit exit status and `current_executable`; the HTTP/ORM suites also need
the redirect and transaction remedies described in [runtime review](docs/runtime-review.md).
A source-built candidate passing locally does not establish a published nightly
pass; final immutable nightly and Windows/Linux remote results remain merge gates.

Automated HTTP suites cover application journeys; browser interaction and
accessibility coverage remain separate requirements. The
scheduled Scribe updater only proposes dependency changes; its successful run
alone is not runtime test evidence.

Before merge, required checks MUST pass on the final proposed revision, evidence
MUST cover the affected behavior and risk, and blocking reviews MUST be resolved.
Recheck after changes that invalidate prior results. Maintainers configure
required status checks and review protections on GitHub; repository files alone
do not activate host settings. Bot PRs follow the same review and test rules;
approve pending workflow runs or manually dispatch both Governance and WFL tests
on the proposed branch and verify that their revisions match the proposal.

Before a production release, the Maintainer MUST identify the immutable
Scriptorium and Scribe revisions, runtime version, deployed configuration, and
candidate artifact if packaged. Run the application suites and real critical
journeys for that candidate, including installation, upgrade, data recovery,
and the affected security cases. Keep recovery instructions and evidence with
the release record. An untested journey or platform cannot be called verified;
a failed required test blocks release.

No coverage percentage, performance budget, accessibility conformance level, or
availability guarantee is currently measured by this profile. Establish the
measurement and passing criteria before making such a claim.

## Adoption gaps and follow-through

The Maintainer owns this dated register as of 2026-09-20. Each item requires an
owned issue before implementation and a link here when that issue exists.

WFL application-test automation is implemented by the WFL tests workflow under
[issue #13](https://github.com/WebFirstLanguage/Scriptorium/issues/13), owned by
Brad. [PR #14](https://github.com/WebFirstLanguage/Scriptorium/pull/14) retains
the Blacksmith runtime evidence, including an intentional assertion failure
used to verify that failures reach GitHub Actions. Host protection settings
remain a separate adoption item below.

| Gap | Required next step and trigger |
|---|---|
| No browser automation or full accessibility evidence | Retain real HTTP boundary regressions and add browser checks for changed interactions; verify critical journeys before production releases. |
| No declared compatibility matrix or release-candidate workflow | Define supported runtime/platform/configuration tuples and retain candidate results before the next production release. |
| No coverage measurement, performance budgets, or scheduled extended tests | Establish baselines and risk-based targets before claiming those properties; review at the next profile review. |
| Host protection settings are external | Maintainer verifies required checks and review rules on GitHub at adoption and after workflow changes. |

Existing gaps do not authorize new untested behavior or a claim of full
compliance. Update this register when tooling or host settings are verified.

## Exceptions and completion

The Maintainer may approve a narrow temporary exception for unavailable
evidence or an emergency mitigation. Record the exact rule, revision, reason,
approver, compensating checks, recovery plan, expiry, and an owned repair issue
with a deadline. An author cannot be the only reviewer of their exception.
Ordinary exceptions expire within 30 days and R3 exceptions within seven days;
they must not silently roll forward to another release.

An exception records missing evidence; it does not convert it into a pass.
Known authorization bypass, exposed secrets, data loss or corruption, or a
reproducible required-test failure cannot be waived into a normal release.
For an active incident, a minimal reversible mitigation may reorder Red/Green
work with Maintainer approval; complete regression coverage and affected suites
within 24 hours and before closing the incident or making another normal
deployment of the affected component.

A change is ready to merge only when its acceptance criteria, required tests,
review, documentation, recovery instructions where applicable, and durable
evidence are complete. Preserve PR evidence with the change record; preserve
release, migration, security, and exception evidence for the supported life of
the affected release. Evidence MUST exclude secrets and uncontrolled personal
data. Unmet requirements remain visible as pending or blocked work.
