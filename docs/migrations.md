# Versioned SQLite migrations

Scriptorium runs immutable historical migrations at startup through
`scriptorium_migrate(conn)`. The compatibility entry point `db_migrate(conn)`
still returns `yes` and leaves the caller's native handle open. Current model
declarations never generate startup schema changes. Change the schema by adding
a migration, then update application models and queries in the same reviewed
change.

This implementation requires WFL's `raise_error` and
`in transaction on connection for schema changes` capabilities. Official
26.9.12 predates those prerequisites; official nightly 26.9.14 at source
`8d82d785` contains them. See [runtime verification](orm-verification.md) for
immutable publication provenance and [runtime review](runtime-review.md) for
the upstream safety evidence. An older installed executable that parses
ordinary transactions is insufficient.

## Commands and target selection

Run from the application root, as for `main.wfl`:

```text
wfl scripts/migrate.wfl status
wfl scripts/migrate.wfl plan
wfl scripts/migrate.wfl up
wfl scripts/migrate.wfl up --target 20200101000000
wfl scripts/migrate.wfl down --count 1
wfl scripts/migrate.wfl down --target 20200101000000
wfl scripts/migrate.wfl new add_post_summary
```

Every database command prints its selected target. The CLI uses the same
`.wflcfg` parser and `data_dir` rule as startup: an unset/empty directory selects
`./scriptorium.db`; a configured directory selects `<data_dir>/scriptorium.db`.
The first exact matching configuration key wins, and inline comments remain
part of the value, matching the application. `--database PATH` is an explicit
CLI override; it does not rewrite application configuration. Relative paths
resolve from the application root/current working directory.

`status` and `plan` inspect without applying or adopting anything. If the target
file is absent they report the fresh plan without opening SQLite or creating
directories. Existing databases are inspected with a consistent read
transaction. A legacy plan states the recognized adoption version and the
number of migrations up to the requested target. A target older than the
recognized legacy schema is refused.

`up` creates a missing database parent directory, performs supported legacy
adoption if necessary, and applies through the exact requested target (default
`latest`). It refuses a target older than the current version. `down` requires
exactly one of a positive `--count` or an exact `--target`; `zero` means no
applied migrations. Unknown targets, changed history, malformed arguments,
schema drift, locks, access failures and migration errors produce a nonzero
process exit and an actionable cause. A successful exit reports the applied and
pending versions.

The two historical application migrations are deliberately irreversible:

| ID | Historical change | Why rollback is refused |
| --- | --- | --- |
| `20200101000000` | Original seven application tables and rate-limit index | Dropping them destroys site records |
| `20200102000000` | Add `sessions.csrf_token` with empty-text default | Dropping it discards live session security state |

The engine supports reversible later migrations. It preflights the complete
requested rollback range before changing any version. A reversible index change
above an irreversible baseline is not partially rolled back when the requested
range also includes that baseline. Recreating an empty table or adding an empty
column is not restoration of its previous data.

## Legacy adoption

The accepted legacy inputs are intentionally limited to the inspected
[persistence inventory](persistence-inventory.md):

- No application-managed tables: apply the initial schema and CSRF migration.
- All seven original tables and the rate-limit index, without CSRF: adopt the
  first version, then apply the CSRF migration.
- All seven current legacy tables and the rate-limit index, with CSRF: adopt
  both versions without rewriting records.
- Only the exact original sessions table, with or without CSRF: preserve it,
  create the missing historical tables, and adopt the matching version before
  applying any later versions. This preserves the old supported partial state.

Other partial states, missing managed indexes, altered constraints or unknown
managed columns are refused before adoption writes. Inspection compares schema
tokens conservatively: whitespace and ASCII case outside literals, and quoting
of ordinary identifiers, are insignificant; literal bytes, identifier content,
column order, constraint clauses, collation, generated expressions, STRICT and
WITHOUT ROWID remain significant. Semantically equivalent but differently
authored constraint orders can be refused; they need deliberate review, not
blind stamping.

Adoption preserves IDs (including exact signed 64-bit identities), hashes,
session tokens, timestamps, NULLs, empty text, historical defaults, custom roles
and statuses, and orphan references permitted by the original schema. It does
not introduce foreign keys into application tables. Unmanaged extension tables,
indexes and triggers stay outside core history and are retained.

## Authoring a migration

`new ascii_name` creates a timestamped file under `app/migrations` and prints the
exact include and registry changes required. It never opens a database. The
generated declaration is deliberately incomplete: an empty `up_steps` list is
rejected. Complete and test the declaration before registering it.

WFL currently has no namespaced dynamic-module export mechanism. Versions
therefore form a static include chain: each new historical module includes its
predecessor, the application's migration bridge includes the newest module, and
`scriptorium_migration_registry` returns each version once in ascending order.
Replace the bridge's final historical include; do not add an include diamond.
The scaffold test completes, registers, applies and rolls back a generated
version, so the parent-provider reference is exercised through real execution.

An `OrmMigration` carries:

| Field | Meaning |
| --- | --- |
| `migration_id` | Unique increasing 14-digit UTC timestamp text |
| `migration_name` | Stable human-readable description |
| `managed_before`, `managed_after` | Complete historical managed table declarations at that version |
| `up_steps`, `down_steps` | Ordered typed steps, with an explicit SQL escape hatch |
| `irreversible_reason` | A specific explanation when data cannot be restored |
| `source_text` | Entire immutable version source, read from its registered file |

Each version declares historical `OrmModel`/`OrmField`/`OrmIndex` values wrapped
in `OrmSchemaTable`; it must not import or call the application's current model
registry. Consecutive after/before schemas must match. `OrmForeignKey` describes
physical foreign keys separately from the record ORM's logical relationships.
Its local/target field lists are explicit; supported actions are `NO ACTION`,
`RESTRICT`, `CASCADE`, `SET NULL` and `SET DEFAULT`. Composite foreign keys are
supported; the record model still requires a single primary key.

Schema helpers produce steps:

```wfl
store create_step as orm_migration_create_table of historical_table
store add_step as orm_migration_add_column of old_table and new_table and added_field
store index_step as orm_migration_create_index of new_table and declared_index
store undo_index as orm_migration_drop_index of new_table and declared_index
store rebuild_step as orm_migration_rebuild of old_table and new_table and ["id", "title"] and ["id", "title"]
store data_step as orm_migration_sql of "UPDATE settings SET svalue=? WHERE skey=?" and ["new value", "setting name"]
```

`orm_migration_drop_table` requires an irreversible reason in either direction.
Discarding column values in either direction also requires a reason; an explicit
lossless rename copy preserves the values. Rebuilds can alter column types,
nullability/defaults and other supported declarations; a transformation outside
the typed vocabulary must be explicit authored SQL with runtime values bound as
parameters. Review SQL steps for loss of data and honest reversibility. Do not
put user input in identifiers, schema SQL, defaults or migration names.

The reusable library exposes `orm_migrate(session, registry, target)`,
`orm_migration_status(session, registry)`,
`orm_migration_plan(session, registry, target)`,
`orm_rollback_count(session, registry, count)` and
`orm_rollback_to(session, registry, target)`. Targets are exact IDs, `latest` or
`zero`. These actions own their native transaction scopes and must be called
outside another transaction. A borrowed session leaves connection ownership
with its caller.

## History, atomicity and concurrency

`_orm_migrations` records the currently applied contiguous prefix, names,
checksums and timestamps. `_orm_migration_events` retains ordered apply, adopt
and rollback events even when a version is no longer applied. History validation
replays those events and checks the current ledger against the result; missing
files, edited sources, mismatched names, missing history tables and inconsistent
event order fail before execution. The `_orm_` prefix is reserved.

The `orm-migration-v1` checksum uses SHA-256 over deterministic ordered lists
containing the entire descriptor, typed schema and steps, explicit SQL and bound
values, reversibility reason, and entire source. Only CRLF becomes LF in source
text; other whitespace and comments participate. JSON map key iteration is not
used. Do not edit an applied or previously rolled-back version. Restore its
original source and append a new version. Preserve this fingerprint format when
evolving the library so existing history stays verifiable.

Each version's schema/data changes and ledger/event update commit together in a
native schema transaction. WFL pins one SQLite connection, disables foreign-key
enforcement before acquiring `BEGIN IMMEDIATE`, bounds connection/lock acquisition
at five seconds, checks every foreign key before commit, and restores enforcement
before reusing the connection. Errors roll back; `return no` is ordinary WFL
success and must never be used as an abort. Use `raise_error` for an actual
application validation failure.

The write lock covers one migration, not the whole multi-version command. The
engine re-reads history and schema under every acquired lock. Two same-target
writers converge without duplicate history; a writer that observes history
beyond its target or moving in the opposite direction raises a concurrency
error. Review status before retrying a conflict. Earlier committed versions
remain committed if a later version fails. Status/plan use one read snapshot to
avoid combining a pre-commit ledger with a post-commit schema.

## Rebuild and recovery

Rebuild copies run entirely inside SQLite, without converting rows or sequence
values through WFL floating-point numbers. Every retained field must have an
explicit same-name copy mapping; source and destination lists cannot repeat
fields. The table's AUTOINCREMENT high-water mark is preserved as exact decimal
text even when the highest row was deleted. The engine recreates declared
indexes and existing extension indexes/triggers from their stored SQL. It
refuses column removal while extension triggers still exist because SQLite can
accept a trigger that only fails later when it refers to a removed column;
author an explicit reviewed trigger migration first.

Native schema transactions preserve referencing rows while rebuilding a parent
table, including `ON DELETE CASCADE` children. Foreign-key validation before
commit catches invalid results and rolls back schema, data and history together.
An abandoned `_orm_rebuild_...` name is refused rather than guessed away.

Before a production migration, stop the application and its writers, then back
up the whole configured data directory: database, SQLite sidecars if present,
and matching uploads. With the legacy layout, back up `scriptorium.db` and its
sidecars together with `static/uploads`. Keep the matching application and
migration sources with that backup. Restore while the app is stopped; do not
combine a database from one point in time with uploads from another. Verify
`PRAGMA integrity_check`, `PRAGMA foreign_key_check`, migration status, login,
content and uploads before reopening traffic. An irreversible migration calls
for that matching backup, not ledger deletion or an edited checksum.

## Deployment and application-version compatibility

Treat the application revision, immutable migration sources, WFL runtime and
site configuration as one release. Keep those exact versions, custom themes
and extension files with the matching database-and-uploads backup. A database
backup alone cannot reconstruct deployment configuration or extension code.

1. Stop the application, extension writers and other migration runners. Record
   the current revision, runtime and `.wflcfg`, then make the stopped-site backup
   described above. Keep that backup separate from the working data directory.
2. Put the reviewed new application and migration sources in place and select
   the required WFL runtime. From that application's root, run
   `wfl scripts/migrate.wfl status` and `wfl scripts/migrate.wfl plan`. Check the
   printed database target against the intended site's configuration. Inspect
   the planned versions and any irreversible steps before proceeding.
3. Run `wfl scripts/migrate.wfl up`, or `up --target ID` when deploying a reviewed
   intermediate version, then run `status` again. An intermediate schema must
   match the application being deployed; normal application startup applies
   every pending version in that application's registry.
4. Check integrity, foreign keys and the site's retained data. Start the app
   with traffic held back, verify login, installation lockout, content, uploads,
   theme and extension behavior, then reopen traffic.

Startup supports fresh initialization and the legacy states listed above. It
does not promise that older application code can use a newer schema. Code with
this migration engine rejects history absent from its registry; older code
without that check must not be used to bypass it. Keep the deployed code's
registry and the database history together, including rolled-back source files
needed to validate migration events.

For an application downgrade, restore the older release and its matching backup
unless that exact older-code/current-data combination has been reviewed and
tested. A schema rollback alone does not authorize switching to an older
checkout: rollback events still require the newer immutable migration files,
and normal startup with that complete registry reapplies pending versions.

For a reviewed schema rollback while the application remains stopped, use the
**newer release's complete registry** to inspect and, only when every affected
migration is reversible, run `wfl scripts/migrate.wfl down --target ID`. Any
subsequent application release must explicitly support that schema, complete
event history and startup behavior. The two shipped historical migrations are
irreversible, so removing either requires restoration of a matching older
backup. If rollback is irreversible or fails preflight, keep the application
stopped and choose a reviewed forward repair or restore matching code, runtime,
configuration, database and uploads. Never delete ledger rows or edit checksums
to make older code start.

## Interrupted-upgrade recovery

1. Keep traffic closed and stop all application and migration writers. Preserve
   the failed command's diagnostics and the current database with any sidecars;
   do not delete sidecars or rebuild a table manually. Use the same immutable
   release sources, runtime, configuration and intended target as the interrupted
   attempt.
2. Run `wfl scripts/migrate.wfl status` and `wfl scripts/migrate.wfl plan`, checking
   the printed database target again. SQLite recovers an uncommitted transaction
   when the database is reopened. Each version must be either fully committed
   with its ledger entry or absent with no partial schema/data changes. A commit
   may have finished before command output was lost; use inspected history to
   decide what remains. Inspect integrity and foreign keys as well.
3. If history and schema validation succeed, rerun `up` with the original
   intended target. Applied versions are retained and only pending work runs.
   A lock conflict requires confirming the other owner has stopped before
   retrying. A checksum, history, schema or integrity failure requires diagnosing
   the cause or restoring a backup; do not force adoption or rewrite history.
4. After a successful retry, repeat deployment verification before reopening
   traffic. If restoring instead, stop all owners, replace the entire working
   data set with the complete backup (including matching uploads and sidecars),
   and restore its matching code, runtime and configuration. Remove the failed
   working data from the restore destination first so stale files cannot mix
   with the backup. For the legacy layout, replace the database and sidecars
   together with `static/uploads`. For a versioned release, recheck migration
   status, integrity, foreign keys and HTTP workflows before reopening traffic.
   A restored pre-ORM release has no migration CLI: use that release's database
   integrity and application verification procedure with its matching runtime.

The WFL suites exercise real file-backed databases, all supported legacy states,
edited/missing history, drift and unsafe copy maps, rollback/reapply, whole-range
irreversibility checks, SQLite read-only URI access, bad paths, a genuine
five-second lock, concurrent processes and killed transaction-owner recovery.
CLI tests invoke real child processes, including generated-source execution.
HTTP recovery tests stop and restore a complete disposable site with matching
uploads. Runtime cancellation and process-exit cleanup have additional upstream
WFL coverage. Read-only URI coverage is portable even for privileged CI accounts;
it does not claim OS ACL or permission testing on every host.
