# ORM implementation evidence

This is an incremental engineering record, not a completion or release claim.
Application integration and the WFL-only runner conversion are implemented.
Migration recovery expansion, review fixes and final Scriptorium CI remain in
progress; this record is not a completion claim.

## Implemented library contracts

The reusable library under `lib/orm` has no application imports. Its linear
include chain implements declarative fields/models/indexes/relationships,
record presence and validation, safe assignment, composed SQL predicates,
bounded ordered queries, owned/borrowed connections, CRUD/upserts and explicit
batched relationship loading. The public operations raise actionable errors
through the upstream `raise_error` prerequisite. They use native WFL database
handles, parameter binding and transaction scopes.

`identity` fields represent SQLite integer identities as canonical signed
64-bit decimal text. They are opaque identifiers, not floating-point quantities.
Projection uses SQL `CAST` before WFL sees the value; comparisons bind the exact
text to the stored integer column. Sorting qualifies that stored column so its
numeric ordering survives the text projection. `integer` arithmetic fields use
the exact WFL numeric range; `number`, `text` and `boolean` are distinct types.
Null, an omitted field, an empty string and a missing record remain distinct.

Queries default to 100 records, allow pages of 1–1000, and add the primary key as
a deterministic tie-breaker. Counts and existence describe the filter, ignoring
pagination. Bulk writes honor the requested page and ordering and reject a
structurally unrestricted filter without explicit `orm_whole_table` intent.
Null equality means `IS NULL`, null inequality means `IS NOT NULL`, and Boolean
groups retain SQLite's three-valued logic. Membership explicitly includes null
when requested. Text pattern searches escape SQL wildcard characters.

Relationship access never issues implicit SQL. Loading batches at most 100
distinct keys per query and pages related results in groups of 1000; a complete
page requires a following query to establish exhaustion. Loading is limited to
1000 source and 10000 related records; larger collections use explicit child
queries. Assembly currently compares collected rows to source keys in memory;
this is transparent bounded work, not a query per source row. Empty and orphan
relationships preserve their absence rather than deleting or rejecting rows.

## Local WFL evidence

All scenarios, assertions and fixture generation below are WFL. They ran on
Windows against the upstream transaction candidate reporting 26.9.12. The
candidate is an implementation build, not the published nightly. Relevant
capability and provenance evidence remains in `runtime-capabilities.md`.

| Suite in `TestPrograms` | Latest result | Important boundary |
|---|---:|---|
| `orm-types.test.wfl` | 6 passed | Type/null/default checks, malicious identifiers, signed 64-bit identity bounds |
| `orm-models.test.wfl` | 5 passed | Duplicate identifiers, indexes, relationship uniqueness and model isolation |
| `orm-records.test.wfl` | 5 passed | Missing/null/empty, atomic assignment, sensitive fields, redacted errors |
| `orm-predicates.test.wfl` | 7 passed | File-backed injection, Boolean/null/membership semantics and literal wildcard searches |
| `orm-crud.test.wfl` | 10 passed | Defaults, exact generated IDs, projections, upserts, paging, guarded writes, native and nested rollback, connection reuse and ownership |
| `orm-query-order.test.wfl` | 1 passed | Numeric ordering with exact-text identity projection |
| `orm-relationships.test.wfl` | 3 passed | Two SQL queries for 101 parent keys, explicit loading, null/orphan results and no lazy queries |

| `orm-relationship-limits.test.wfl` | 3 passed | 1001 children take two queries; 10001 fail without partial state; 1001 parents fail before SQL |
| `db-contracts.test.wfl` | 5 passed | Legacy result behavior, exact large IDs and atomic installer rollback |
| `db-review-contracts.test.wfl` | 8 passed | Independent NULL lookup, mutation metadata and nullable-key page regressions |

The executable progression in `examples/orm/progression.test.wfl` passes three
cases using explicit migrations from the first saved record through composed
queries, transactions, relationship loading and reversible index changes.
The final combined candidate is `df6ad9a2`, executable SHA256
`b96c06f6013a9a64d4d042c9b379a30af1c8d274d7855b5ebe9d7fe14a750d1c`.
All 16 existing database cases, three authentication cases and six rendering
cases pass. The final complete gate passed 41/41 suites, including the HTTP
review cases, legacy upgrade, migration recovery and pinned Scribe, on source
`3bc7b4f`. [The verification record](orm-verification.md) retains the exact local
provenance and distinguishes the still-pending official nightly acceptance.

### Retained regression chronology

- `052ba8d` records the new field contract before implementation. Its initial
  run failed because the library did not exist; this is feature absence, not a
  claimed behavioral regression.
- `afb4f9d` preserves a real isolation failure: adding a relationship to one
  model also changed another model through a shared container list default
  (expected 0, actual 1). Copy-on-write updates pass all five model assertions.
- `3f2ad08` preserves a real ordering failure: SQLite sorted the exact-text
  projection alias, yielding identity 10 before 2. Qualifying the underlying
  table column passes the unchanged order assertions.
- Record error assertions fail against the official runtime because the
  required application error primitive is absent; they pass with the candidate.
- `ffeebbb` preserves large-ID rounding (expected exact text, actual rounded
  Number) and partial installer state (expected zero users, actual one) before
  replacing the application data layer; both now pass.
- `c0d0603` preserves independent review's seven failures plus a passing NULL
  session guard. Physical row identity, explicit trusted updates and legacy
  NULL-equality adaptation pass the unchanged eight assertions.

### Timing and fixture isolation

The original 60-second whole-file budget expired after five CRUD cases with a
debug build and seven with a release build. A timestamped release probe isolated
roughly 10.2 seconds in the two SQLite table-reset statements on this Windows
drive; the following insert and lookup took approximately 26 ms combined.
Durability settings were not relaxed. `TestPrograms/.wflcfg` now gives complete
database suites 180 seconds. Lock, HTTP and subprocess tests retain independent,
shorter deadline assertions, and the new runner must own a hard child timeout.

WFL test blocks isolate parent variables by copying mutable values on parent
lookup. Mutable fixture objects such as an `OrmSession` therefore belong inside
each test. Relationship tests borrow the fixture's native handle into a local
session and assert changes on that same local instance. An independent source
inspection confirmed these test-environment semantics; they are not a lost
mutation bug in ordinary action calls. No query-count assertion was weakened.
