# Independent ORM and adapter review

Technical review on 2026-09-20; this is not Maintainer approval.

## Preserved Red evidence

`TestPrograms/db-review-contracts.test.wfl` ran with the combined WFL runtime
`ae5395d9bd215d0d9fa1c039e666f03c8897cf88` before the fixes. It reported **1 passed,
7 failed** (exit 1). The retained local log is
`target/review-probes/compatibility-promoted-red.log`.

The first six cases use only existing application wrapper APIs. Those same
cases passed **6/6** against application baseline
`4ec5c88d9e4ae27041599ad8293a28130b56fbf2` using the same runtime, with only the
include path changed. Log:
`target/review-probes/compatibility-promoted-baseline.log`.
The last two cases exercise the new ORM's promised read/write page equivalence;
there is no predecessor ORM API to test at the baseline.

Confirmed findings:

- Nullable author equality changed legacy `column = ?` with NULL from matching
  no rows into `IS NULL`, returning orphan posts and pages.
- Session insertion synthesized `last_insert_id = 0`, losing the native SQLite
  rowid metadata of a text-primary-key insert.
- Sensitive user updates synthesized zero insert metadata instead of preserving
  the native connection's most recent insert result.
- Bulk selection using a nullable key inside `IN (SELECT key ...)` omitted NULL
  keys. Expired NULL-ID sessions were not purged. Paged updates and deletes of
  ordinary SQLite tables also skipped the selected NULL-key row.

A guard case verifies `session_delete(conn, nothing)` remains a no-op. It passes
before the fixes and must continue to pass when bulk operations gain physical
row identity. The bulk cases contain two separate NULL-key rows and one named
key; their postconditions ensure the selected row changes without modifying or
removing its neighbors.

Expected remedies are confined to ordinary SQLite tables: retain physical row
identity for bounded mutation, preserve compatibility equality semantics in the
application wrappers, and return actual operation/connection metadata through
the ORM rather than synthesizing it. Final source review and Green results are
pending the owner's implementation.

## Reviewed areas without findings

The review covered model and field validation, identifier quoting, bound values,
predicate/operator validation, identity precision, defaults and missing-vs-NULL
mapping, sensitive assignment, safe bulk-write intent, ownership and errors,
relationship batching, and legacy result aliases/projections. No SQL injection
path was found in the ordinary value API. The explicit raw SQL escape hatch is
intentionally trusted application code. HTTP compatibility is separately
recorded in `tests/integration/EVIDENCE.md`.
