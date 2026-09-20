# Models, records and queries

The SQLite ORM lives in `lib/orm/` and has no application imports. Include
`lib/orm/migrations.wfl` for the complete API, or a lower module when schema
management is not needed. Includes form one chain. Scriptorium connects that
chain to its existing `util → db → auth → render` tree in
`app/migrations.wfl`; Scribe remains an unchanged upstream dependency.

Run the executable progression from the repository root:

```text
wfl --test examples/orm/progression.test.wfl
wfl scripts/run_tests.wfl --group examples
```

The first example applies explicit versions before saving a record. The next
uses the same records and queries inside a native transaction, then loads a
relationship explicitly. The final example plans, reverses and reapplies an
index migration without losing rows. Current models and immutable historical
definitions are separate files. There is no automatic schema synchronization.

## Declare a model

```wfl
create new OrmField as identity_field:
    field_name is "id"
    value_type is "identity"
    primary_key is yes
    generated is yes
end
create new OrmField as title_field:
    field_name is "title"
end
create new OrmModel as notes:
    table_name is "notes"
    fields is [identity_field and title_field]
end
```

This declares a mapping; a versioned migration creates its physical table.
Models require exactly one primary key. Composite primary keys are unsupported.
Fields declare `nullable`, `unique_value`, `sensitive`, `has_default` and
`default_value`. A text field can use `server_default is "current timestamp"`
for SQLite's UTC `datetime('now')`. Declare ordinary or unique indexes using
`OrmIndex` (`index_name`, `field_names`, `unique_values`) in the model's
`indexes` list. Identifiers must contain ASCII letters, digits or underscores
and start with a letter or underscore. They are quoted before use in SQL.

| Type | WFL value | Stored SQLite affinity |
| --- | --- | --- |
| `text` (default) | Text, including empty text | TEXT |
| `integer` | Whole Number within ±9,007,199,254,740,991 | INTEGER |
| `number` | Finite Number | REAL |
| `boolean` | `yes` or `no` | INTEGER, mapped from 1 or 0 |
| `identity` | Canonical signed 64-bit decimal Text | INTEGER |

Identities use text because WFL Numbers cannot represent every SQLite integer.
For example, `"9007199254740993"` remains exact. There is no numeric coercion:
`"1"` is an identity, `1` is an integer, and `yes` is a boolean. Stored
values are validated when mapped; invalid existing data produces a repair
diagnostic rather than a lossy conversion. Database uniqueness and other
constraints remain authoritative under concurrent writers.

## Save and find records

```wfl
store draft as orm_record of notes
call orm_set with draft and "title" and "Publish the release"
store saved as orm_save of session and draft
store loaded as orm_find_key of session and notes and (orm_get of saved and "id")
```

`orm_save` returns the mapped saved record, including database-generated values.
Keep that return value when editing an existing record. A new record remains
new if the caller discards it. Saving a persisted record updates its assigned
non-key fields; a deleted record or changed primary key raises an error.

| Situation | Behavior |
| --- | --- |
| Unassigned field | `orm_has` is false; `orm_get` raises an actionable error |
| Explicit `nothing` | Stored as NULL only if the field is nullable |
| Empty text | An ordinary text value, distinct from missing and NULL |
| Missing field with a default | Omitted on INSERT; the database supplies the default |
| Missing required field | Rejected before INSERT |
| No matching row | `orm_first` and `orm_find_key` return `nothing` |
| Empty collection | `orm_find` returns an empty list |
| Projected-out field | Missing, never silently represented as NULL |

`orm_assign(record, assignments)` takes explicit
`orm_value(field_name, field_value)` assignments. It validates the entire batch
before changing the record. Unknown fields, repeated fields, invalid types and
sensitive fields are rejected. Use `orm_set_sensitive` only after the
application has authorized that particular password, role or token change.
It is an explicit trusted operation, not a form-data mass-assignment path.

`orm_insert_if_absent(session, record, conflict_field)` ignores only the
declared unique/key conflict. Other constraint failures still raise.
`orm_upsert` updates explicitly assigned non-key fields on that conflict.
Neither performs a race-prone existence check followed by an unprotected insert.

## Compose queries

Start with `orm_query(model)`; modify it with `orm_where`, `orm_select`,
`orm_order_by` and `orm_page`, then use `orm_find`, `orm_first`,
`orm_count` or `orm_exists`. The predicate constructor is
`orm_compare(field_name, comparison, value)`. Combine predicates with
`orm_all(list)`, `orm_any(list)` and `orm_not(predicate)`.

Comparisons: `equal`, `not equal`, `less than`, `less or equal`,
`greater than`, `greater or equal`, `in`, `is null`, `is not null`,
`contains`, and `starts with`. NULL equality compiles to IS NULL, and NULL
inequality to IS NOT NULL. Other comparisons use SQL's three-valued logic:
unknown results do not match, including after NOT. IN lists can contain NULL
explicitly and hold at most 500 values; empty IN matches nothing. Empty ALL
matches everything; empty ANY matches nothing. Text search escapes literal
`%`, `_` and escape characters before binding the pattern. Case behavior
is SQLite's default LIKE behavior; the ORM does not promise Unicode folding.

Order directions are exactly `ascending` and `descending`. The primary key
is appended to ordering for stable pages. Stored integer identities sort
numerically even though the returned identity is text. Pages default to 100,
allow 1–1000 rows, and require a nonnegative safe integer offset. Counts and
existence checks describe the filter and ignore the page window.

`orm_update(session, query, assignments)` and `orm_delete(session, query)`
honor the query's bounded page and ordering. They reject a known unrestricted
predicate unless `orm_whole_table(query)` explicitly records that intent.
Bulk updates reject primary-key changes and unchecked sensitive assignments.
The explicit trusted `orm_update_sensitive(session, query, field, value)`
counterpart authorizes one field while retaining the same selection guards.
For a large operation, use an explicit transaction and deliberate batches;
avoid offset pagination when deleting rows that shift subsequent offsets.

## Load relationships explicitly

`OrmRelationship` declares `relation_name`, `related_model`,
`local_field`, `related_field` and `many`. Add it with
`model.relate(relationship)`. Types must agree; a scalar relationship requires
a unique target field. Logical relationships do not add physical foreign keys,
cascades or cleanup. Migration schema declarations own those decisions.

Call `orm_load(session, records, relation_name)`, then
`orm_related(record, relation_name)`. Reading a relationship never issues SQL.
An unloaded relationship raises, an absent scalar returns `nothing`, and
an absent collection returns an empty list. Orphan references remain intact.

Loading accepts at most 1000 parents, groups up to 100 distinct keys per query,
and reads related rows in pages of 1000. The total eager result is limited to
10,000 related records. Exceeding the limit raises before any source record is
marked loaded; query the related model in explicit pages for larger results.
101 distinct parent keys with a small result take two queries. 1001 children
of one parent take two queries. An exact multiple of 1000 requires an empty
final page to establish completion. Matching uses in-memory scans across the
bounded parent/result sets, so cost grows with both sizes.

## Connections, transactions and diagnostics

`orm_open(path)` owns a SQLite connection. Close it in a `finally` block.
`orm_borrow(conn)` wraps an application-owned native handle; closing the ORM
session does not close that handle. Closing a session is idempotent, and later
operations on that session fail.

```wfl
store conn as session.connection
in transaction on conn:
    store saved as orm_save of session and draft
end transaction
```

Use the same native transaction form at every level. It pins the connection,
commits on normal completion (including a normal return), and rolls back on an
error. A false return value is normal completion, not a rollback request.
Raise an error inside the block; catch it outside. Nested transactions on the
same connection are rejected and no savepoints are implied. Migration schema
transactions add the explicit `for schema changes` clause and perform foreign
key validation before commit. See [migrations](migrations.md).

`session.query_count`, `last_sql` and `last_parameter_count` expose query
cost and generated SQL without logging bound values. SQL errors retain useful
database diagnostics with assigned text redacted; validation errors identify
the operation and corrective action without printing rejected values.
`orm_sql_query(session, authored_sql, bound_values)` and
`orm_sql_execute` are the clearly marked escape hatch. Bind all runtime
values; identifier and SQL-expression safety remains the author's responsibility.
Native WFL rejects raw transaction-control SQL.

The supported schema uses ordinary SQLite rowid tables. Models must declare
all stored columns that shadow a rowid alias. Nullable text primary
keys use a nonshadowed physical rowid to distinguish and order NULL-key rows
in bulk pages. Leave at least one of `_rowid_`, `rowid`, or `oid` undeclared.
INSERT records expose the exact physical identity as `inserted_rowid`, separate
from the logical primary key; this preserves the legacy session insert result.

## Application compatibility and foundations

`app/db.wfl` retains the application's map-returning actions. Normal data
access for users, sessions, posts, pages, settings, media and login attempts
uses ORM models and queries. The explicit SQL exceptions in
`app/persistence-helpers.wfl` read SQLite's clock and year; historical timestamp
semantics remain unchanged. The adapters preserve aliases, ordering, empty
settings, nullable fields and orphan references. Ordinary IDs remain Numbers;
IDs outside the safe numeric range are exact text through lookups and routes.
The installer now commits its user and settings atomically.

The No-Unlearning Invariant is implemented by one model/record/query API,
explicit migrations from the first runnable example, and the same native
transaction form throughout. Advanced use adds predicates, projections and
relationships to existing queries. Validation is explicit and errors suggest
repair. Safe defaults include bound values, identifier validation, protected
fields, bounded reads and guarded bulk writes. Query counters, documented
batching and hard eager limits make performance visible. SQLite-specific
schema behavior is documented rather than hidden behind speculative backends.
