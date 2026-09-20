# ORM and migration runtime capability audit

This is an evidence record, not an ORM implementation or a readiness claim.
The requested production ORM and migration work has unresolved runtime
requirements. All executable probes in this record are WFL.

## Provenance and commands

Verified on Windows on 2026-09-20 with the official Windows nightly
**WFL 26.9.12**, extracted locally without replacing the installed 26.9.11:

```powershell
$wfl = 'G:\repos\Scriptorium\target\runtime\nightly-26.9.12\PFiles\wfl\bin\wfl.exe'
& $wfl --version
& $wfl --test tests/runtime/orm-native-baseline.test.wfl
& $wfl --test tests/runtime/transaction-validation-capability.test.wfl
& $wfl --test tests/runtime/rebuild-foreign-keys-capability.test.wfl
```

Downloaded MSI SHA-256: `34422e832d267b5add2e8380a2992a2a2f0756f2ed6984af20f724a590cff956`.
Extracted executable SHA-256: `4e9c8f63d02bf84497fdf23d9c20efda3a6c609b2925a2a4a94ee4348bd85afa`.

The source inspected is WFL commit
`cb1dadaad96939a4450a6eb2b3a6a51678035b7f`. The installed 26.9.11 also passed the
upstream native transaction and include-diamond suites, but it is not treated
as current-nightly evidence. Remote Docker provenance and results must be
recorded separately; these Windows results do not establish Linux behavior.

Portable commands, with the selected WFL on `PATH`:

```sh
wfl --test tests/runtime/orm-native-baseline.test.wfl
wfl --test tests/runtime/transaction-validation-capability.test.wfl
wfl --test tests/runtime/rebuild-foreign-keys-capability.test.wfl
```

These suites derive the checkout location from `script_directory`, use
synthetic file-backed databases under ignored `target/runtime-capability-results`,
and close and delete their databases in `finally`. They do not open site data.
Each capability suite has its own database name. Do not run the same suite
concurrently against the same checkout.

| Probe | Observed result on 26.9.12 |
|---|---|
| `orm-native-baseline.test.wfl` | 6 passed, exit 0; positive capabilities and explicitly labeled existing limitations |
| `transaction-validation-capability.test.wfl` | 1 failed, exit 1: expected zero retained rows, observed one |
| `rebuild-foreign-keys-capability.test.wfl` | 1 failed, exit 1: expected one extension row, observed zero |
| Upstream `TestPrograms/database_transaction_test.wfl` | 8 passed: commit, native-error rollback, read-own-writes, transaction SQL rejection, nested-block rejection |
| Upstream `TestPrograms/modules/include_diamond.wfl` | 2 passed |
| Upstream `TestPrograms/containers/documented_features.wfl` | 14 passed |

The failing probes assert the required safety outcome, rather than relaxing an
assertion to make the currently unsafe alternative green. Neither failure is
a parser error. They do not assert that the runtime promises Boolean-return
rollback or safe arbitrary table rebuilds today.

## Remote nightly evidence

[Blacksmith run 35499009581](https://github.com/WebFirstLanguage/Scriptorium/actions/runs/35499009581)
tested Scriptorium `a81ecf9c2c68784f3deace8b3521feae762e51ff` and pinned Scribe
`93d62af5a6ed6c3ce257ef888107fc3ca1e2dc1d`. The job freshly pulled the nightly,
resolved and ran `bsbyrdwfl/wfl@sha256:7ddc51e6320affa7cfe26263fece590ddbdebe5582659b7e660ca823ed3ddbf1`,
which reported **WFL 26.9.12**. Each suite ran in WFL in a disposable container;
no Python test implementation or runner was used by this capability workflow.

The native baseline passed 6/6. Transaction validation failed 1/1 with a
retained row; the rebuild failed 1/1 with its extension row deleted; HTTP failed
1/1 with final status 200 and no intermediate cookie; process control passed
1/4 and failed cwd isolation, post-wait output, and stderr preservation. All
failed assertions produced exit 1 and failed their CI jobs. All container cleanup
steps passed. This is prerequisite Red evidence, not successful validation of
the requested ORM or complete converted test suite.

The user subsequently authorized upstream WFL fixes and separate prerequisite
PRs, followed by completion of Scriptorium. Work is isolated into transaction,
HTTP response control, and process lifecycle branches. Existing Scriptorium
application code and Python checks remain unchanged until their replacements
can meet the full contracts. The existing five WFL application suites also
passed locally on 26.9.12 (60 tests); the runtime emitted its existing included-
action/type-analysis warnings. These local baseline results are not final PR CI.

## Capabilities available now

- Typed containers, mutable instance properties through actions, inheritance,
  interfaces, defaults, and lists of instances work in the upstream container
  suite. A small ORM can represent model, record, query and relationship
  state with containers.
- Maps can be declared, indexed and checked with `record contains "field"`.
  Presence distinguishes an absent field from an explicitly present `nothing`.
  Empty text remains a different value. Missing map indexing raises an error.
  A map's `for each` loop yields values, not keys. Direct indexed mutation
  (`change record["field"] to value`) is not supported by the assignment
  grammar. There is no registered map-key enumeration/mutation builtin.
  This is an API-design constraint, not by itself a proof that an ORM is
  impossible: a record container can encapsulate an ordered field collection.
- WFL `nothing` and SQL NULL compare as no value. Parsed JSON null also compares
  equal to `nothing`, but `typeof` reports `Nothing` for JSON null and `Null`
  for the literal/SQL value. Use `isnothing`, not a single `typeof` spelling,
  for the ORM's semantic null check.
- SQLite values are bound separately from SQL through `and parameters [...]`.
  An injection-shaped text value and a bound `nothing` round-trip unchanged.
  Write results contain `affected_rows` and `last_insert_id`.
- `sqlite_schema`, `pragma_table_info(?)`, and other SQLite introspection
  queries are available through normal parameterized queries. Migration
  adoption must inspect those results instead of assuming a baseline.
- Native `in transaction on conn:` pins one connection for its body. Database
  errors roll back preceding DDL and ledger writes together and preserve the
  original diagnostic through `when error` and `error_message`. Commits and
  rollbacks report failures instead of silently claiming success.
- Native nested transaction blocks on the same handle are explicitly rejected;
  raw BEGIN, COMMIT, ROLLBACK, SAVEPOINT and RELEASE through query/execute are
  also rejected. A documented reject-nesting policy is feasible; savepoint
  behavior must not be claimed.
- Include diamonds now work. The old architecture limitation is obsolete on
  this nightly, as is its statement that transactions do not exist. This audit
  does not authorize rearranging Scriptorium's existing include chain.
- SQLite integers become WFL floating-point numbers. The baseline demonstrates
  that SQL `9007199254740993` reads and rebinds as `9007199254740992`. Exact
  legacy IDs require an explicit text-preserving representation, including
  casts for reads; silently coercing every ID to Number loses data.

Relevant source at the inspected revision:

- [SQL parameters, connection configuration and pooling](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/interpreter/database.rs#L60)
- [Transaction SQL guard](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/interpreter/database.rs#L211)
- [Native transaction control](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/interpreter/mod.rs#L7092)
- [Integer decoding](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/interpreter/database.rs#L423)
- [Assignment grammar](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/parser/stmt/variables.rs#L120)
- [Include execution in the parent scope](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/interpreter/mod.rs#L8932)

## Required capability: application errors that abort a transaction

`save_then_reject` in the failing probe writes one row inside a native
transaction, then returns `no` to indicate a later validation failure. The
caller observes failure but the row is committed. That is the documented
native meaning of an ordinary return; changing all false returns to rollback
would be surprising and is **not** the proposed fix.

The problem is that WFL does not expose a native statement or standard-library
operation that raises an application error, or rethrows a caught error after
adding safe operation context. Its AST/registered builtins have no such
operation. The illustrative `throw error` in an older upstream example is
not implemented: a separate exploratory execution reports undefined variable
`throw`. This parser/symbol observation is supporting evidence, not the Red
regression test. `expect` cannot substitute: it is restricted to test mode,
and it also records a test failure before throwing there.

Returning an error object has the same ordinary-return problem. Catching a
native database exception and returning a failure value likewise consumes the
error that the transaction must see. Causing an unrelated division, parse or
SQL failure would obscure the actual cause and teach an implementation trick
instead of a coherent transaction/error API. Stopping the whole program does
not provide recoverable library error propagation.

Upstream should provide one natural-language application-error operation,
usable in ordinary actions and containers, with these semantics:

1. Raise a catchable runtime error with an application-supplied safe message;
   preserve the cause/diagnostic when propagating a caught error.
2. Unwind `finally` blocks and native transaction scopes, rolling back before
   the error reaches the caller.
3. Keep ordinary successful returns, including Boolean values, unchanged.
4. Surface uncaught errors through the CLI as nonzero failure.
5. Test nested calls, caught versus uncaught errors, rollback failures, and
   errors occurring after both schema and ledger writes on file-backed SQLite.

This is required for the requested composable validation/transaction API;
prevalidating one standalone save does not cover an arbitrary transaction
whose later operation fails application validation.

Source: [transaction return/rollback branches](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/interpreter/mod.rs#L7140),
[expect's test-mode restriction](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/interpreter/mod.rs#L13387),
and [error-handler parsing](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/parser/stmt/errors.rs).

## Required capability: connection setup before a migration transaction

The rebuild probe creates a managed parent and an extension-owned child with
`ON DELETE CASCADE`. It attempts the usual create/copy/drop/rename rebuild in
a native transaction after requesting `foreign_keys = OFF` and
`defer_foreign_keys = ON`. SQLite reports `foreign_keys = 1`: changing that
setting inside an active transaction does nothing. Dropping the old parent
then deletes the extension's child row, even though an equivalent parent
exists at commit and the deferred foreign-key check can pass.

This is an unsafe proposed migration strategy, not a claim that SQLite's
cascade semantics are defective. Existing extension relationships must be
preserved, so the migration system cannot simply assume they do not exist or
claim that deferred checks preserve the rows.

The runtime creates a five-connection pool for file-backed databases. An
ordinary PRAGMA before the block can configure a different connection than
the one the block later pins. The public database API offers neither
connection options for this setting nor a session/checkout scope that pins a
connection before starting the transaction. The URL remainder is passed as a
filename, not parsed as SQLite connection options. Repeating a PRAGMA until it
appears to stick is not proof that the future transaction uses that connection.

Upstream should expose a dedicated connection or connection-configuration
scope that guarantees setup and the subsequent transaction use the same
connection. A migration runner must be able to disable enforcement before
BEGIN, perform its rebuild and ledger update atomically, inspect
`foreign_key_check` and refuse commit on violations, then restore enforcement
and close its owned connection on every path. Per-connection options on a
separate migration pool could also provide the necessary guarantee if all its
connections receive those options. Normal application connections should keep
foreign-key enforcement enabled.

The complete migration implementation would still need tests for preserved
indexes, triggers, sequences, extension objects and every supported legacy
schema. This probe establishes the missing primitive for the proposed rebuild
strategy; it does not substitute for those implementation tests.

Source: [SQLite filename and pool construction](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/interpreter/database.rs#L104)
and [transaction creation](https://github.com/WebFirstLanguage/wfl/blob/cb1dadaad96939a4450a6eb2b3a6a51678035b7f/src/interpreter/database.rs#L345).

## Foundations acceptance

The full local `Docs/wfl-foundation.md` (Version 2) was read. The task's pasted
attachment contains the requested implementation requirements and quotes the
same No-Unlearning Invariant; it is not a second complete foundation text.
No contradictory version of the invariant was supplied.

The relevant acceptance criterion remains one API from the first model and
explicit migration through validation, composed queries and transactions.
The required upstream operations should fit that API without forcing callers
to replace Boolean-return examples with artificial parse failures, learn
connection-pool accidents, or accept silent data loss. These observations
block a production-ready claim; they do not justify a reduced feature set,
Python test fallback, or shipping an unintegrated prototype as the requested
finished ORM.

