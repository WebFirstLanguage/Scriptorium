# Migration implementation evidence — 2026-09-20

This records focused migration evidence, separate from the repository's full
WFL, HTTP, tooling and pinned Scribe gates. The canonical behavior and operator
workflow are in [migrations.md](migrations.md).

## Runtime and scope

Final focused execution used the integrated WFL candidate at
`target/runtime/combined-df6ad9a2/wfl.exe`, SHA-256
`b96c06f6013a9a64d4d042c9b379a30af1c8d274d7855b5ebe9d7fe14a750d1c`.
It includes the reviewed native application-error/schema-transaction, HTTP
response and process-control prerequisites. The stock official 26.9.12 runtime
predates those capabilities; see [runtime review](runtime-review.md) for upstream
PR and gate evidence. This record does not itself claim a merged/published
nightly or deployment approval.

All new scenarios, fixture generation, assertions, process ownership and cleanup
are WFL. Tests use synthetic file-backed SQLite databases under ignored
`target/test-artifacts`, with native handles and owned child processes closed in
`finally`. No real site database, upload, password or token was used.

## Red and independent review

Commit `72a2d6d` preserves the initial behavioral Red. The prior `db_migrate`
retained a sessions-only legacy row, its exact 64-bit reference, NULL timestamp
and added CSRF default, but did not create migration history. The test failed
at the ledger assertion: expected one history table, observed zero. Its log is
`target/capability-probes/migration-adoption-red.log`; the unchanged acceptance
test passes through the new application compatibility wrapper.

Independent review found three additional concrete schema defects, reproduced
as WFL assertion failures in `target/testing-probes/migration-review.test.wfl`
and `target/migration-review-red.txt`:

1. Removing spaces from quoted identifiers could confuse `"ti tle"` with
   `title` and falsely accept drift.
2. A rebuild copy map could omit a retained nullable column and lose its value.
3. The managed object universe omitted tables declared only in `managed_before`.

Those cases are preserved in `TestPrograms/migration-schema-safety.test.wfl`.
Token-aware inspection, complete retained-field mappings and the union of all
historical before/after declarations pass all three. Independent re-review and
rerun also passed. A further review of target races added strict overshoot and
opposite-direction checks. Read-only plans now use one native transaction
snapshot to avoid mixing ledger/schema states across another process's commit.

The conflicting-target process test intentionally accepts refusal in either
the initial consistent plan or the locked recheck. It does not infer a specific
lock position from a sleep. Two real same-target runners are separately required
to both succeed with exactly one event per migration.

A final independent Red, committed as `af2b6ac`, found that a known historical
managed index could be reintroduced after rollback without being reported as
drift. `TestPrograms/migration-index-safety.test.wfl` preserves that case. The
managed index universe now includes every historical before/after declaration
and checks expected absence as well as presence. SQLite's ASCII-insensitive
object identity is respected, including an uppercase reintroduced name. The
regression passes on the corrected source.

## Final focused result

Each suite below was invoked as `wfl --test <path>` using the candidate above.
All nine suites passed on final source: **24 tests, zero failures**.

| WFL suite | Passed | Observed contract |
| --- | ---: | --- |
| `TestPrograms/migration-adoption.test.wfl` | 1 | Supported sessions-only upgrade, exact values and audited history |
| `TestPrograms/migration-engine.test.wfl` | 3 | Read-only plan, targeted/repeated apply, rollback/reapply events, full-range irreversible preflight, changed/missing history and drift |
| `TestPrograms/migration-failures.test.wfl` | 3 | SQLite read-only error, invalid registry/scaffold/destructive reversal, inaccessible child path |
| `TestPrograms/migration-legacy-matrix.test.wfl` | 3 | Both complete historical schemas, current sessions-only state, preserved seven-table data and extensions, refusal of unknown partial/altered schemas |
| `TestPrograms/migration-rebuild.test.wfl` | 3 | Exact 64-bit high water including an empty table, cascading children, extension index/trigger, failed rebuild rollback and retry |
| `TestPrograms/migration-schema-safety.test.wfl` | 3 | Independently reproduced inspection, copy-map and prior-only object regressions |
| `TestPrograms/migration-index-safety.test.wfl` | 1 | Reintroduced historical managed index after rollback, including ASCII case variation |
| `tests/tooling/migrations.test.wfl` | 4 | Real CLI exit codes, absent/configured/overridden targets, read-only legacy target planning, source edit detection, completed scaffold registration and actual up/down execution |
| `tests/integration/migrations-recovery.test.wfl` | 3 | Five-second contention bound, killed owner rollback, same-target convergence, conflicting target refusal |

Final logs are ignored `target/capability-probes/*-final.log`. The SQLite
read-only scenario opens a native `file:/absolute/path/site.db?mode=ro` URI,
so every pooled connection has the read-only restriction.
It checks a genuine SQLite read-only failure without depending on whether a
privileged CI user bypasses OS file permissions. It is not claimed as a
cross-platform ACL test. The lock test asserts elapsed time is
at least four seconds and less than eight around the native five-second bound.

The killed owner has entered a real schema scope, written a schema object,
record and uncommitted event, and signaled readiness before the parent terminates
and reaps it. The parent verifies that all three writes disappeared, history
remains valid, and a later migration succeeds. Separate upstream WFL tests cover
cancelled handler futures, process exit and ordinary-return compatibility.

Two fixture assumptions were corrected after failed executions. A preliminary
`PRAGMA query_only=ON` fixture could affect only one pooled connection; a rerun
observed three applied versions instead of the expected two. The native read-only
URI replaces that assumption without changing the migration assertion. Also,
bare pooled DROP/CREATE of the same synthetic index could report stale schema
during preparation; querying SQLite proved the DROP had occurred. That paired
fixture DDL now uses the documented native schema scope, with no arbitrary
sleep or retry. Production migration steps already use that pinned scope.

The full HTTP suite independently tests a stopped-site database-and-uploads
backup restore and a pre-CSRF installed site's extension/theme/login behavior.
Those results belong to the HTTP evidence record. Full repository discovery,
Linux/Windows CI and the final published-runtime verification remain the root
task's gates; focused local results do not substitute for them.
