# Independent migration and schema review

Technical review on 2026-09-20, independent of the migration implementation
owner. This is not Maintainer approval or final remote CI acceptance.

The review covers historical schema declarations, migration fingerprints and
history replay, legacy adoption, explicit rebuild copy maps, native transaction
ownership, reversible-range checks, CLI scaffolding and target selection, and
concurrent migration execution. ORM record and application compatibility review
is recorded separately in [orm-independent-review.md](orm-independent-review.md).

## Findings and remedies

| Finding | Executable evidence and reviewed remedy |
| --- | --- |
| SQL normalization erased meaningful quoted identifier whitespace | A table containing `"ti tle"` was accepted as the declared `title` column. The unchanged WFL assertion is retained in `TestPrograms/migration-schema-safety.test.wfl`. Normalization now tokenizes SQL, preserves literal bytes and identifier content, and only removes ordinary identifier quoting. |
| An incomplete rebuild copy map silently lost a retained nullable field | A same-schema rebuild copying only `id` changed an existing title to NULL and reported success. The retained WFL regression now requires refusal and the original value. Rebuilds require unique source/destination mappings and explicit same-name copies for every retained field. Removed or renamed fields remain explicit; unrecoverable data loss requires an irreversible declaration in either direction. |
| Tables appearing only in a historical before-schema escaped drift checks | A declared dropped table could remain present without detection. The retained WFL regression now requires refusal. The managed table universe includes both before and after declarations. |
| A concurrent runner could move beyond the requested target while the waiting runner reported success | Source review found the old greater-than/less-than completion conditions. Up and down now finish only at equality, reject movement beyond the target or opposite to their observed direction, and re-read history and schema under each native write lock. Status and plan use one read snapshot. Real process coverage is in `tests/integration/migrations-recovery.test.wfl`. |
| A historical managed index recreated after rollback escaped drift checks | A real version-two to version-one rollback followed by recreating `idx_items_title` still allowed status to succeed. `TestPrograms/migration-index-safety.test.wfl` preserves the independently confirmed failing assertion. The required remedy is to track historical managed index names from both before and after declarations and reject their unexpected presence, without claiming unknown extension indexes. This remedy is pending at this Red checkpoint. |

The first three assertions ran as meaningful behavioral failures before the
remedies: the initial local probe reported **0/3**, including an observed title
value of NULL after the unsafe rebuild. The unchanged assertions then passed
**3/3**, with the original title retained. Local logs are
`target/migration-review-red.txt` and `target/migration-review-green.txt`.
The scenarios were promoted to `TestPrograms/migration-schema-safety.test.wfl`.
Parser or static-analysis diagnostics are not counted as the behavioral Red.

The index regression independently reported **0/1**, exit 1, against Scriptorium
`9de5c72` and the combined runtime below. The failure is the actual assertion
that status should refuse the incompatible schema. Local log:
`target/migration-index-review-red.txt`. It is retained unchanged apart from its
include path when moving from the ignored probe directory to `TestPrograms`.

## Review boundaries

Schema checks deliberately compare conservative SQL tokens rather than claiming
a complete SQLite SQL equivalence parser. Unsupported declarations are refused.
The reviewed rebuild performs its row copy inside SQLite, retains sequence
values as exact decimal text, recreates extension indexes and triggers, and
refuses ambiguous column removal in the presence of extension triggers. Native
schema transactions perform foreign-key checks before commit and restore
connection settings; their implementation and cancellation review is recorded
in [runtime-review.md](runtime-review.md).

The write lock covers one version, not an entire multi-version command. A later
failure can leave earlier successfully committed versions applied. The concurrent
target test accepts either an initial-plan target refusal or a locked recheck
concurrency refusal, depending on scheduling; it does not claim to prove one
particular lock position with a fixed delay. Both must return a nonzero result.

The local combined runtime is WFL source `df6ad9a2`, executable SHA-256
`b96c06f6013a9a64d4d042c9b379a30af1c8d274d7855b5ebe9d7fe14a750d1c`.
It is an integration candidate, not evidence that the published nightly already
contains the upstream remedies. Final focused Green results, the complete suite,
and exact-revision remote Linux/Windows and resolved-image evidence remain
separate acceptance requirements.
