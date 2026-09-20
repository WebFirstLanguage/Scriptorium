# HTTP integration evidence

## Baseline characterization, 2026-09-20

Executed on Windows with WFL reporting `26.9.12`, built from combined upstream
revision `ae5395d9bd215d0d9fa1c039e666f03c8897cf88`. Executable SHA-256:
`76F612CA1BBAF4484B2CC2BDA86D876588BC765DE9C38B7DAA8951BAD143B911`.

Application source baseline: Scriptorium
`4ec5c88d9e4ae27041599ad8293a28130b56fbf2`, extracted into ignored
`target/http-baseline-4ec5c88`. Both that revision and the current checkout pin
Scribe `93d62af5a6ed6c3ce257ef888107fc3ca1e2dc1d`. Git archive provisioned the
baseline source; WFL created every actual site, configuration, database, upload,
request, assertion and cleanup operation.

Each suite used this command shape from `G:/repos/Scriptorium`:

```text
G:/repos/wfl/target/codex-worktrees/integration/target/release/wfl.exe --test tests/integration/<suite>.test.wfl G:/repos/wfl/target/codex-worktrees/integration/target/release/wfl.exe G:/repos/Scriptorium/target/http-baseline-4ec5c88
```

| Suite | Passed | Retained local log |
|---|---:|---|
| server-port | 3/3 | `target/http-baseline-ports.log` |
| authentication | 2/2 | `target/http-baseline-authentication.log` |
| content-users | 2/2 | `target/http-baseline-content-users.log` |
| media | 2/2 | `target/http-baseline-media.log` |
| throttle | 1/1 | `target/http-baseline-throttle-green.log` |
| recovery | 1/1 | `target/http-baseline-recovery.log` |

Total: **11/11**. The media case exercises both configured and legacy storage
layouts. No assertions were removed or relaxed to obtain these results.
`target/test-artifacts/http` contained zero residual fixture directories after
the runs. Each WFL stop helper asserts its owned process is no longer running.

The first throttle run failed because the test reused `login_cookie` outside
the `try` scope that declared it. Moving the cookie/token declarations to the
test's enclosing scope fixed that fixture defect; its original log remains
`target/http-baseline-throttle.log`. This is not a production defect or Red
evidence for the application. Earlier parse/smoke attempts using separate,
incomplete prerequisite binaries could not resolve all new APIs and are not
counted as integration evidence.

The interpreter emits advisory undefined-action warnings for actions supplied
by the included helper and unused-variable warnings for values read by test
assertions. They remain visible in the logs; every suite exits zero and reports
the passing counts above. A separate OS process-list audit was unavailable
because Windows denied the read; cleanup evidence is the owned-process checks
and empty fixture directory, not a claim of an independent OS-wide audit.

## Updated application candidate

The same six suites ran against the updated application working tree on
2026-09-20 with the same combined runtime, omitting the baseline-source argument.
All **11/11** passed on their first candidate run:

| Suite | Passed | Retained local log |
|---|---:|---|
| server-port | 3/3 | `target/http-candidate-ports.log` |
| authentication | 2/2 | `target/http-candidate-authentication.log` |
| content-users | 2/2 | `target/http-candidate-content-users.log` |
| media | 2/2 | `target/http-candidate-media.log` |
| throttle | 1/1 | `target/http-candidate-throttle.log` |
| recovery | 1/1 | `target/http-candidate-recovery.log` |

These runs cover the first integrated ORM/migration adapters before the later
independent nullable-key and write-metadata compatibility fixes. Those fixes
have separate Red/Green tests in `TestPrograms/db-review-contracts.test.wfl`.
The application was still an uncommitted working tree, so this evidence is not
a claim that an immutable final application commit has passed. The complete
runner must also test the final proposed commit. Linux/nightly container
evidence and its immutable image digest remain separate required checks;
local Windows results do not establish those results.

The original three Python port cases map directly to the three WFL port cases,
including installer status/content type/form/CSRF, configured/legacy/default
ports and startup messages. The Python file was removed only after its WFL
replacement passed against both baseline and the updated application.

## Independent review

An independent agent reviewed fixture process ownership and the stopped-site
backup/restore protocol. It found no blocking source issue: unique owned
directories, cleanup after failures, reaping before copying all data/sidecars,
and HTTP plus SQLite checks after restore. This is technical review, not
Maintainer approval or release acceptance.

## Legacy extension and theme upgrade boundary

`legacy-upgrade.test.wfl` passed **1/1** on 2026-09-20 with the same combined
runtime against the working candidate after the compatibility fixes. Log:
`target/http-candidate-legacy-upgrade.log`. This adds a twelfth HTTP case.

WFL creates the original seven-table schema without `sessions.csrf_token` or a
migration ledger, a synthetic Argon2 administrator, an installed flag, published
content, a live legacy session and an extension-owned payload. It copies a WFL
extension into the disposable site's documented seam and generates a configured
custom theme. Actual boot adopts the schema and creates extension boot markers.
HTTP proves both installer methods remain locked, the extension owns `/` before
stock dispatch, the custom theme renders extension and stock post routes, the
retained user can log in, and a legacy empty CSRF token cannot mutate settings.

A stopped/reaped restart preserves identical ledger rows/checksums/timestamps,
retained extension payload and managed rows; only the extension's expected boot
count increments. Integrity and foreign-key checks pass. The fixture has no
requirement for the ignored Git-archive baseline and no non-WFL test logic.

Independent source review found no fixture ownership or application-boundary
issue. It requested ordered ledger snapshots so map iteration order cannot cause
false failures; the test now serializes ordered lists of explicit fields.
