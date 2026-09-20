# Independent runtime prerequisite review

Reviewed 2026-09-20 by a separate agent that did not author the capability
inventory or proposed ORM. This is technical review, not Maintainer approval
and not review of an implemented ORM. No ORM implementation exists in the
reviewed diff. The assessment concerns the complete requested production scope,
not whether a smaller demonstration can be written.

Sources: WFL revision `cb1dadaad96939a4450a6eb2b3a6a51678035b7f` and the downloaded
Windows nightly executable
`target/runtime/nightly-26.9.12/PFiles/wfl/bin/wfl.exe`, reporting WFL 26.9.12.
The source revision was independently checked with Git. These are local Windows
results; they do not substitute for the required resolved Docker digest and
final Blacksmith runs.

## Reviewed verdict

| Capability | Verdict for the full requested scope |
|---|---|
| Custom abort/rethrow | Qualified blocker: preflight validation and contextual result APIs work now; application-directed abort after an earlier write in a general transaction scope does not |
| SQLite rebuild with extension foreign keys | Blocker for general safe transactional parent-table rebuild; additive migrations without rebuild are feasible now |
| HTTP redirect inspection | Blocker for honest real HTTP installation/login/redirect/cookie assertions through the current native client |
| Per-child working directory | Blocker for preserving the portable runner's existing directory/disposable-Scribe contracts without a new native primitive or an independently verified compliant launcher |
| Spawned child diagnostics/completion | Spawn/kill/poll/finally work; stderr and reliable final stream retrieval are missing for a complete timed runner with preserved diagnostics |

Do not describe the runtime as lacking transactions, HTTP, subprocesses, or
error handling generally. Those facilities exist and several pass executable
probes. The missing behaviors below are specific.

## Validation results versus aborting an active transaction

`execute_transaction_statement` in `src/interpreter/mod.rs` commits normal
`return`, `break`, and `continue`. It rolls back runtime errors and abrupt
program exit. `database.rs` deliberately rejects SQL transaction-control
statements because ordinary operations use pooled connections. There is no
implemented user-defined throw/rethrow statement or explicit transaction abort.
The proposed `throw error "..."` probe reports `Undefined variable 'throw'`;
that is an unrelated failure, not supported error syntax.

The absence of throw is **not** a reason to reject every explicit-result API.
I wrote and ran `target/review-probes/result-preflight.test.wfl`: **2/2 passed**
on a synthetic file-backed database. It proves both:

1. A validation action can return an actionable failure map before a transaction
   begins, preserving all rows and cleanly accepting a later valid insert.
2. A real unique-constraint error rolls back earlier writes; a catch outside the
   transaction can preserve the database diagnostic and add safe operation and
   corrective context.

That is a foundation-aligned option for ordinary validation and a fixed batch
whose entire input can be checked in advance. An explicit result type can be
used consistently from the first example. It must not be represented as an
automatic rollback signal: the existing `orm-capabilities.test.wfl` probe
returns `no` after an insert and confirms that the row **commits**.

For a general user-composed transaction, later validation can depend on reads
and earlier operations inside the transaction. Returning a failure at that
point commits earlier writes. Catching an error inside the scope and returning
a failure has the same issue. Prevalidating a fixed list outside the scope does
not solve that broader requirement or protect database-dependent checks from
races. Killing the application, deliberately referencing an undefined name,
dividing by zero, or issuing deliberately invalid SQL is not an acceptable
normal API for requesting rollback.

**Required remedy for that broader scope:** a native, catchable application
error and rethrow facility, or a native scoped transaction abort with an
explicit failure result. It must run cleanup, preserve original diagnostics,
roll back the current transaction, propagate out of nested actions, and never
turn an aborted operation into success. Exact syntax is an upstream design
decision, not an assumed capability. Native rejection of nested transactions
before mutation is a valid initial documented nesting policy.

## SQLite rebuild and extension-owned foreign keys

Independently reran `target/capability-probes/rebuild-foreign-keys.wfl`:

```text
foreign_keys before toggle in transaction: 1
foreign_keys after toggle in transaction: 1
extension rows after rebuild: 0
```

The probe creates a managed parent and an extension-owned child with
`ON DELETE CASCADE`, then rebuilds the parent inside a native transaction.
Setting foreign keys OFF inside the transaction is ineffective; deferred
checking does not disable cascade actions. Dropping the old parent deletes the
child row despite replacing the parent with identical IDs.

WFL `database.rs::connect` constructs a file-backed pool with up to five
connections. Every ordinary query/execute can acquire a different connection;
the transaction reserves its connection only when it begins. Therefore a
pre-transaction `PRAGMA foreign_keys=OFF` cannot establish the required
connection-local state reliably. The current URL handling takes the SQLite
suffix as a filename, not a supported connection-options API.

SQLite's documented generalized rebuild procedure disables foreign-key
enforcement before beginning the transaction, rebuilds and checks the schema,
then restores enforcement after commit. Changing `foreign_keys` during an
active transaction has no effect. See the official
[ALTER TABLE procedure](https://www.sqlite.org/lang_altertable.html#making_other_kinds_of_table_schema_changes)
and [foreign_keys pragma](https://www.sqlite.org/pragma.html#pragma_foreign_keys).

Refusing an unsafe rebuild with an actionable explanation is the correct
current behavior, but does not deliver the requested complete migration
capability. Copying back cascading child rows is not a general remedy: unknown
extension triggers, constraints, and cascading relationships may create further
effects. Reordering rename/drop steps can rewrite references to the temporary
table. Editing `sqlite_schema` or slipping transaction SQL past the guard is not
a production substitute for connection ownership.

**Required remedy:** a native pinned connection/migration transaction facility
that configures foreign keys before BEGIN and restores the prior setting after
both success and failure; alternatively a documented dedicated connection
option applied to every connection plus verified transaction affinity. The
caller must be able to run foreign-key checks and abort before commit. Test
extension CASCADE/RESTRICT/SET NULL relationships, triggers, row preservation,
sequence high-water marks, rollback, interruption, and restoration of settings.
The ordinary ORM should continue enforcing foreign keys by default.

## HTTP redirects and authentication cookies

Independently reran `target/testing-probes/redirect.wfl`. The local child sends
a 302 with Location and Set-Cookie, then serves the redirect target. The WFL
caller receives only the final `status: 200`, `body: final response`; the initial
Location and synthetic session cookie are absent.

`IoClient::http_client` builds a shared reqwest client with its default redirect
policy. `HttpRequestStatement` has method/headers/body options but no redirect
control. `send_http_request` exposes only the response returned by that client.
Response headers become a map of one text value per name, collapsing duplicate
names. Stream entry points also use the same client.

A test that reads a new session ID directly from SQLite can check persistence,
but cannot prove that the login HTTP response delivered that cookie or the
expected redirect. Replacing the application's redirect response for tests is
also not the real application boundary. Raw socket clients or an external HTTP
driver are not available as an established WFL-only substitute here.

**Required remedy:** per-request redirect control, retaining existing following
behavior by default, with a no-follow choice returning the actual 3xx status,
body, Location and Set-Cookie values. Preserve repeated response headers through
a list-valued accessor without changing existing single-value header accesses.
Keep request deadlines, cancellation, and response-size limits in force. A
cookie jar is optional: tests can manage cookies explicitly in WFL once the
actual response headers are observable.

## Process isolation, output and cleanup

Independent runs of existing probes produced:

- `cwd.wfl`: the child launched by absolute path reports the repository CWD,
  not its isolated fixture directory. Process AST/parser and command builders
  have no working-directory argument; `wfl --help` and CLI parser expose none.
- `output.wfl`: foreground execution returns exit/stdout/stderr. A spawned
  nonexistent WFL file yields exit 1 but its diagnostic cannot be obtained with
  `read output from process`, which reads only stdout.
- `lifecycle.wfl`: output can be read before wait; after waiting, the process
  handle is invalid. `wait_for_process` removes the handle and returns only
  exit code, without joining the background collectors for stream EOF.
- Existing kill/finally probes and source show native kill, running-state poll,
  and cleanup on ordinary errors/assertion failures. They are useful available
  primitives, not blockers themselves.

The existing runner explicitly guarantees repository CWD even when invoked
elsewhere, a separate disposable Scribe CWD/build tree, per-suite timeout,
continued execution after failure, and diagnostics. The Python runner tests
assert these behaviors. Merely supplying an absolute script path does not
preserve them. Running Scribe against the real checkout's build tree weakens
the isolation guarantee.

Shell may provision or launch WFL under the user's task rules, but that does
not automatically establish a portable solution. A Unix launcher can replace
itself with WFL; a Windows `cmd` wrapper creates another process whose child is
not owned by WFL's process handle. Killing only that wrapper can leave the test
or server alive. Moving assertions, fixtures, or polling into shell would also
violate the task. No safe portable launcher was demonstrated in this review.

Foreground execution already captures both streams and bounds execution. It is
valid for simple commands and prevents a blanket claim that stderr capture is
impossible. It lacks a per-command timeout/CWD option in the current language,
while the spawned path needed for polling lacks stderr and a final-output
completion result. Reading stdout, waiting, and hoping the collectors drained
is not deterministic; an arbitrary delay does not prove complete diagnostics.

**Required remedy for the preserved portable runner:** per-command working
directory and timeout options with native process ownership, plus a completion
result containing exit code and fully drained bounded stdout/stderr. Preserve
existing syntax/results by adding options or a new explicit completion form.
Make cleanup deterministic and idempotent, including failures/timeouts, and
prove that no test/server child remains. A safely owned direct WFL child does
not require a general shell process-tree API; arbitrary descendants need an
explicitly documented ownership policy.

## Review boundaries and next evidence

The reviewed capability failures are not permission to weaken the requested
ORM, migration recovery, HTTP journeys, or WFL-only suite. Safe subfeatures can
be implemented while upstream prerequisites are addressed, but the full task
must not be declared complete on those subfeatures alone.

Upstream fixes need WFL regression scenarios for each failed behavior, including
negative cases, then the full Scriptorium suite and real HTTP/recovery checks
against the resolved nightly image. Revisit this document after those fixes:
it records the reviewed runtime revision, not permanent WFL limitations.

## Upstream remedy review, 2026-09-20

The baseline findings above remain evidence about `cb1dada`, not the updated
runtime candidates. The following reviews concern the prerequisite changes;
they do not constitute Maintainer approval or final Scriptorium acceptance.

- HTTP: branch `codex/http-response-controls`, Green commit
  `b8e5e8768a13c44aa033a3cd732b85f089262eff`, implements per-request
  `and without following redirects` for buffered and streaming responses and
  additive `header_values` arrays while retaining scalar `headers` and default
  redirect following. A different agent independently reviewed this author's
  change and found no blocking source issue. Its WFL regression suite passed
  8/8; the locked workspace suite passed 2,414 tests with 27 existing ignores;
  the existing gated runner passed 145 WFL programs with 24 existing skips.
  Formatting, strict Clippy, and fuzz-workspace compilation passed. Evidence
  and existing environment skips are recorded in the upstream commit.
- Transactions: independent source review identified a cancellation lifetime
  gap: a dropped transaction-body future could leave its transaction owned by
  the registry while the interpreter remained alive. The owner reproduced it
  with a real WFL concurrent HTTP peer and added an exact-slot
  `TransactionBlockGuard` from reservation through body/commit. Re-review
  confirmed that its synchronous registry removal releases the transaction on
  cancellation, allowing the connection guard to roll back and restore foreign
  keys. No remaining blocking source finding was identified; the owner's
  rebuilt WFL cancellation regression and final gates remain separate evidence.
- Processes: independent source review found that applying a child working
  directory after authorizing a relative explicit executable could change
  which file executed. Both launch paths now freeze the explicit executable's
  canonical parent-directory identity before applying child CWD. Review also
  found a source-fixer mismatch for the merged contextual `with code name`
  token; conservative operand protection fixes the rename mismatch. WFL
  regressions cover exact-path authorization across CWD and fix-then-run exit
  status. Re-review found both issues resolved and no remaining blocking source
  finding; final rebuilt tests and platform gates are the owner's evidence.

The ORM query-counter investigation did not establish another prerequisite.
WFL tests use an isolated environment, and each inherited mutable-value lookup
deep-clones the parent value. A module-scoped session therefore produces a new
container copy on another lookup; nested action argument binding itself retains
the instance. Tests should construct a local borrowed session for each case,
which retains real mutation and query-count assertions without sharing mutable
fixture state. The testing guide documents isolation generally; stable cached
copies of inherited mutable fixtures are not a documented contract.
