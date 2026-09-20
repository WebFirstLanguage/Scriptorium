# ORM acceptance audit

This audit tracks the complete requested deliverable. Local candidate evidence
does not substitute for the final resolved nightly-image CI run. The final
candidate passed 41/41 complete suites and repository hygiene; see
`orm-verification.md`. The ready-to-merge PR, remote failure-propagation proof
and final revision provenance remain pending.

| Requirement | Implementation and executable evidence |
| --- | --- |
| Read governing policies, foundations and existing architecture | `orm-migrations-design.md`, `persistence-inventory.md`, `wfl-test-inventory.md`, `runtime-capabilities.md` record the sources and resolved attachment limitation |
| Verify real runtime capabilities | Five WFL suites in `tests/runtime/`; initial Blacksmith Red in `a81ecf9`; separate reviewed upstream HTTP, process and schema-transaction PRs |
| One progressive API and explicit migrations from the beginning | `examples/orm/progression.test.wfl` passes first-record, composed-query/relationship/transaction and reversible-index examples; `orm.md` maps the No-Unlearning Invariant |
| Models, types, defaults, nullable fields, identifiers and indexes | `lib/orm/types.wfl`, `models.wfl`, `schema.wfl`; `orm-types` and `orm-models` suites |
| Missing, NULL, empty and not-found semantics | `records.wfl`, `queries.wfl`; `orm-records`, `orm-crud`, `db-contracts` suites |
| Unknown and protected mass-assignment rejection | Atomic assignment validation and explicit single-field trusted setters/updates; `orm-records`, `orm-write-review` |
| Database constraints remain authoritative | INSERT/UPDATE and conflict-targeted upsert use SQLite constraints; `orm-crud` duplicate/unique cases; no check-then-insert uniqueness shortcut |
| CRUD, composed Boolean/NULL filters, ordering, pages, count and existence | `predicates.wfl`, `queries.wfl`, `writes.wfl`; `orm-predicates`, `orm-crud`, `orm-query-order` |
| Values parameterized, identifiers and directions validated | Predicate/query/schema constructors; malicious-value and identifier cases in `orm-types`, `orm-predicates`, `orm-write-review` |
| Guard bulk writes and preserve their selected page | Explicit whole-table intent, bounded physical row selection for nullable keys; independent Red `c0d0603`, Green `db-review-contracts` |
| Explicit batched relationships and visible cost | `relationships.wfl`; 101 parents use two queries; 1001 children use two; 10001 children fail without partial state; `orm-relationships`, `orm-relationship-limits` |
| Ownership, rollback, nesting and reusable connections | `connections.wfl`, native WFL transaction scopes; `orm-crud` rollback, nested rejection, post-failure reuse and borrowed-close cases |
| Actionable errors without assigned secrets | `orm_fail`, bound-text redaction, no parameter-value trace; `orm-records` and ownership/diagnostic cases |
| Explicit specialized SQL | `orm_sql_query` / `orm_sql_execute`; application exceptions are SQLite clock/year reads, described in `orm.md` |
| Scaffold/status/plan/up-target/down-count/down-target | `scripts/migrate.wfl`, typed engine and static immutable registry; `tests/tooling/migrations.test.wfl`, `migration-engine` |
| Ordered immutable checksums and audit history | `_orm_migrations` plus append-only `_orm_migration_events`; registry/order/checksum/history/schema validation in `migration-engine`, `migration-failures` |
| Serialize runners, bounded locks and atomic ledger changes | Native schema transactions with locked reinspection; real child processes in `tests/integration/migrations-recovery.test.wfl` |
| Interrupted work cannot claim success | Killed schema owner, lock failure, restart and same-target/opposing-target runners; `migrations-recovery` |
| SQLite rebuild preserves records and extension objects | Explicit column mapping, sequence high-water preservation, indexes/triggers/FK checking; `migration-rebuild`, independent `migration-schema-safety` |
| Reject fake or impossible rollback before changing anything | Irreversible declarations, complete-range preflight and retained-column copy checks; `migration-engine`, `migration-failures`, `migration-schema-safety` |
| Fresh initialization and safe legacy adoption | Immutable initial/CSRF versions; supported full pre-CSRF/current and sessions-only variants; `migration-adoption`, `migration-legacy-matrix` |
| Stop on ambiguous states and preserve unmanaged objects | Full managed declaration checks, conservative unsupported-partial rejection; `migration-legacy-matrix`, extension rebuild cases; `migration-index-safety` rejects reintroduced historical managed indexes |
| Target path, data directory, absent plan, read-only and invalid path | Shared config parser; no absent plan file creation; native SQLite read-only URI restricts every pooled connection; `tests/tooling/migrations`, `migration-failures` |
| All seven tables use ORM; no competing schema owner | `app/models.wfl`, `app/db.wfl`, `app/migrations.wfl`; ordinary data access has no raw row SQL |
| Preserve IDs, hashes, sessions, CSRF, timestamps, defaults and aliases | Existing WFL application suites, `db-contracts`, independent `db-review-contracts`; exact high IDs and atomic installer have retained behavioral Red |
| Preserve installation, routes, port, themes and hooks | Real WFL HTTP suites; `server-port`, `authentication`, `legacy-upgrade` checks locked upgraded installer and custom extension/theme across restart |
| Exercise content/users/settings/media/throttle | `content-users`, `media`, `throttle` HTTP suites with database assertions and both upload layouts |
| Verified database-plus-uploads backup/restore | `tests/integration/recovery.test.wfl` stops the owner, copies complete state, restores, then checks HTTP/auth/upload/integrity/FK behavior |
| Every test, fixture, helper and driver is WFL | Python runner, two Python tooling suites and Python port suite removed; WFL 8+28 behavior mapping plus strengthened diagnostics and default-discovery cases |
| Non-test Python checker remains only as a subject | `scripts/check_repo_hygiene.py` is invoked by WFL hygiene assertions and the existing governance utility step |
| Complete suite includes pinned Scribe | `wfl --execution-timeout 1200 scripts/run_tests.wfl` discovers application, tooling, integration, runtime probes, examples and an isolated copy of pinned Scribe; publication of the explicit invocation-budget option is pending |
| Timeout/failure cleanup and failure propagation | Owned child lifecycle, joined bounded output, nonzero exit and descendant markers in WFL tooling suites; deliberate commit `b9e7903` produces local 23-pass/one-fail exit 1; remote assertion-failure proof and removal remain required |
| Keep Linux/Windows governance and Blacksmith nightly | Updated Governance provisions current nightly assets on both platforms; WFL job freshly resolves/pins Docker digest and records runtime/source revisions |
| Independent review and repaired findings | `orm-independent-review.md`, `independent-migration-review.md`, `runtime-review.md`, migration safety regressions and HTTP evidence distinguish source review from Maintainer approval; `type-analysis-review.md` records remaining runtime static-analysis diagnostics honestly |
| Final ready-to-merge five-section PR | Source frozen, complete local pass and hygiene recorded; pending deliberate CI Red/Green, fresh nightly provenance and exact-head remote inspection |

The user approved the initial three upstream merges and official nightly
publication. Those PRs are merged and official nightly 26.9.14 is published.
Linux verification exposed the runtime's 300-second whole-command cap; a fourth
upstream change adds an explicit finite invocation budget. Its review and all
exact-head CI passed, including real 305-second assertions on Linux and Windows.
The user approved its merge and replacement nightly publication; #741 is merged
as `3720dd74c82f4a1354aa64cfe66260ec3eccba93`. Publication remains pending,
along with the final Scriptorium
acceptance checks listed in `orm-verification.md`.
Scriptorium merging and production deployment remain outside this deliverable.
