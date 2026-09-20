# ORM and versioned migrations

Status: implemented architecture with verification and independent review in
progress, 2026-09-20. The library and application integration are implemented;
final recovery checks and remote evidence remain required before release.
The actual API is documented in [orm.md](orm.md); administrative operations are
documented in [migrations.md](migrations.md).

## Foundations and compatibility

Read `G:\repos\wfl\Docs\wfl-foundation.md` in full. The local source revision
`cb1dadaad96939a4450a6eb2b3a6a51678035b7f` is also the source identified by the
2026-09-20 nightly release. Its foundations document includes the overriding
No-Unlearning Invariant, matching the quotation in the task attachment. The
only supplied attachment is the task text; it contains no separate copy of the
foundations, so a byte comparison with a second attachment is unavailable.
The local reference is the acceptance source specified by the task.

One API must serve first examples and advanced applications. Model definitions,
explicit immutable migrations, typed records, parameterized queries, and scoped
transactions are present from the first example. No automatic schema sync,
destructive convenience defaults, or replacement expert query language. Use WFL
actions and containers with readable names, ordinary WFL values, and the
standard database/filesystem/HTTP/process facilities. Unsupported syntax and
deliberately triggered unrelated runtime errors are not acceptable API forms.

The change is R3 under [testing.md](../testing.md). Preserve all existing
tables, data, IDs, sequence high-water marks, aliases, ordering, nullable values,
settings upserts, authentication and authorization behavior, extension hooks,
uploads, URLs, `data_dir`, and the 8080 port fallback. Legacy relationships do
not have foreign-key constraints or cascades; migration must not invent them.
Keep the Scribe gitlink and the existing application/include layout.

## Implemented architecture

The existing linear include chain now connects `db.wfl` through
`persistence-helpers.wfl` and `models.wfl` to `app/migrations.wfl`. That
bridge includes independent branches for `util.wfl`, the reusable ORM chain,
and immutable historical version definitions. Application model definitions
belong in `app/`; the ORM does not know Scriptorium's seven tables.
Existing `db.wfl` action names remain compatibility adapters. Explicit SQL
exceptions are limited to specialized SQLite time expressions or similarly
justified operations, use the same connection scope, and bind all values.

Models describe table/field names, types, primary keys, server defaults,
nullability, uniqueness, indexes, sensitive assignments and relationships.
Identifiers must be checked against model definitions and quoted. A record
distinguishes an omitted field from explicit null and empty text. Omission
selects a declared default; null is accepted only for nullable fields. Reads
return mapped records; no matching record is `nothing`. Unknown or protected
mass-assignment fields fail before SQL. Database constraints remain authoritative
for concurrent writes. Diagnostics name the operation/model and corrective
action without logging parameter values or credentials.

Queries compose predicates as an expression tree with explicit all/any groups,
null predicates, stable ordering, bounds, projection, count and existence.
Writes without a limiting predicate require explicit whole-table intent.
Relationships load explicitly; collection loads batch foreign keys so query
counts grow by bounded batches rather than one query per record. SQL text,
parameter count and query count are inspectable without exposing values.

The owner opens/closes each database handle. Scoped transactions must route all
ORM and escape-hatch operations to the same underlying connection, propagate
validation/database errors, and roll back reliably. Nested behavior must be
explicit and tested; rejecting nesting before mutation is an acceptable
initial behavior. No simulated transactions or swallowed errors.

## Migration lifecycle

A WFL administrative entry point resolves the same `.wflcfg` data directory as
startup and prints the target path before mutation. Commands scaffold immutable
ordered migrations, inspect status, plan without mutation, migrate all/up to a
target, and roll back a count/to a target only after checking reversibility.
Historical definitions and their checksums cannot depend on current models.

Runtime probes established that dynamic include aliases are unsupported.
Versions therefore use explicit static includes and an ordered typed registry.
Scaffolding creates a version file and gives exact registration instructions;
it does not pretend to discover dynamic exports. Checksums combine immutable
source (CRLF normalized to LF) with a deterministic ordered descriptor.

The ledger records identifiers, names, checksums, timestamps and ordered apply/
rollback events. Validate duplicate/order/history errors before schema writes.
Acquire SQLite serialization with a bounded lock policy. Each migration and its
ledger event share one real transaction. Interrupted work must leave neither
partial schema/data nor a successful event. Preflight irreversible rollback
before changing any migration in the requested range.

Fresh databases begin with a migration. Unversioned adoption compares managed
table columns, constraints and indexes against supported historical shapes,
including sessions without `csrf_token`; never blindly stamp a baseline.
Inspect only managed objects for drift, preserving extension-owned tables,
indexes and triggers. Reject unknown/ambiguous managed schemas with recovery
instructions. Startup applies supported additive upgrades, never rollback.

SQLite rebuilds must preserve actual rows, IDs, sequence state, constraints,
indexes, triggers and relationships; inspect foreign keys deliberately. A
discarded column's values cannot be recreated by adding an empty column.
Destructive changes require an irreversible declaration and forward repair or
a verified database-plus-uploads restore procedure.

## Implementation and evidence sequence

1. Inventory persistence and every existing test/driver. Verify source and
   executable nightly capabilities before committing to API syntax. Keep minimal
   WFL reproducers for any required upstream remedy.
2. Implement model/record/query/transaction primitives with WFL file-backed
   regression tests and executable progressive examples.
3. Implement versioned migration operations, legacy adoption, drift checks,
   rebuilds, locking and recovery tests before changing startup ownership.
4. Route every normal application persistence operation through the ORM and
   preserve wrapper contracts. Exercise real HTTP installation, authentication,
   publication, user/settings/media and throttling boundaries.
5. Replace Python tests and runner only after mapping their actual behavior to
   WFL replacements. WFL owns fixtures, assertions, discovery, subprocesses,
   HTTP requests, failure/timeout handling and cleanup. Shell/YAML only provision
   and invoke WFL. Preserve the non-test hygiene checker and pinned Scribe suite.
6. Run focused and full suites, intentional failure propagation, hygiene,
   backup/restore and adversarial recovery checks. Record exact runtime digest,
   versions, revisions and final Blacksmith/Governance results.
7. Obtain independent technical review of foundation alignment, SQL safety,
   transactions, adoption and recovery; fix findings and rerun affected checks.
   Audit every task requirement, update actual shipped documentation, then open
   the completed five-section PR. Maintainer approval/merge remains separate.

Any confirmed runtime blocker remains visible and prevents a production-ready
claim. Do not replace missing WFL test capabilities with another language or
mark this plan as the completed deliverable.
