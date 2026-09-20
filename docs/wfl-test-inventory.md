# WFL test conversion inventory and runtime gates

Status: conversion inventory and executable evidence, 2026-09-20. The WFL runner
and both tooling replacements pass against the reviewed source-built process
runtime; published-nightly/final-revision acceptance is tracked separately.
The original Python runner/tooling files were removed after all mapped WFL
cases passed and independent source review accepted the mapping. The user explicitly authorized their conversion;
this document does not request a separate layout migration.

The acceptance basis is `testing.md`, the binding root policies, the attached
task, and the complete local `G:/repos/wfl/Docs/wfl-foundation.md` Version 2.
The task's quoted No-Unlearning Invariant matches that reference. No separate
foundation attachment was supplied to this task beyond the task text's local
reference. The replacement must keep one readable WFL testing path from a
single suite to the complete run, with real assertions, actionable diagnostics,
bounded child ownership, and no Python implementation of test behavior.

## Existing executable coverage

| Existing entry point | Scenarios and limits | Conversion obligation |
|---|---|---|
| `TestPrograms/util.test.wfl` | 25 tests: slug normalization; number/default and field helpers; form and cookie parsing; truncation; extension/stem parsing; config parsing; valid, missing, empty, malformed, fractional and out-of-range ports; installation input validation. | Preserve and discover it. |
| `TestPrograms/db.test.wfl` | 16 tests: schema repeat initialization, users/settings/posts/pages/sessions/media/login-attempt helpers, expiry, legacy CSRF-column upgrade, installation state/application. Uses memory SQLite. | Preserve while adding file-backed ORM/migration/recovery coverage. |
| `TestPrograms/auth.test.wfl` | 3 tests: own CSRF token, missing token, session token binding. | Preserve; does not replace real login/authorization tests. |
| `TestPrograms/scribe.test.wfl` | 10 tests: Markdown blockquotes/code fences, safe-marker filters, escaping, suffix escaping, nested blockquotes. | Preserve and keep upstream ownership. |
| `TestPrograms/render.test.wfl` | 6 tests: theme default, configured and external roots, traversal rejection. | Preserve; does not prove HTTP rendering journeys. |
| `lib/scribe/tests/scribe.test.wfl` | 83 pinned upstream tests; writes `build/` fixtures. | Copy the pinned source without `.git`, existing `build`, or caches; run from the copy with a fresh `build/`; remove the copy. Never patch the submodule in place. |
| `tests/tooling/test_run_tests.py` | 8 regression methods, mapped below. | All fixtures, assertions, and driver logic must become WFL. |
| `tests/tooling/test_repo_hygiene.py` | 28 regression methods, mapped below. | WFL may invoke the unchanged Python hygiene checker as its implementation subject; Python must not own test behavior. |
| `tests/integration/test_server_port.py` | 3 real HTTP startup tests, mapped below. | Preserve all existing cases and cleanup, then extend actual CMS journeys. |

The original `scripts/run_tests.py` recursively discovers and lexically sorts regular
`TestPrograms/**/*.test.wfl` files, resolves its own repository root independent
of the caller's directory, resolves the selected interpreter, and runs suites
sequentially with repository cwd. Default suite timeout is 120 seconds. It
continues after failures and timeouts, preserves interpreter stdout/stderr,
reports every result and the total, and exits 1 on suite failure. Empty
discovery, bad interpreter, bad timeout, and missing requested Scribe sources
fail before running tests. Setup/cleanup failures exit 2; interruption exits
130. There are no retries. This is the historical contract inventory.

`scripts/run_tests.wfl` now discovers every maintained group by default,
including pinned Scribe. Focused commands use `--group application`, `tooling`,
`integration`, `runtime`, `examples`, or `scribe`; `--include-scribe` remains compatible
when adding Scribe to a focused run. The same-runtime default uses
`current_executable`; native launch resolves a bare `--wfl` name, then the runner
passes that exact resolved runtime to every suite as `args[0]`. Suite failures
and timeouts exit 1; setup/cleanup failures exit 2. Captured stdout and stderr
contents are preserved in the runner's output, with stderr explicitly labeled.
WFL owns interruption handling; exact Python KeyboardInterrupt formatting and
exit 130 are not a promised cross-runtime CLI contract. Child-tree ownership
and bounded cleanup remain required. Timeout arguments are finite positive JSON
numbers up to one year; spell `.5` and `+1` as `0.5` and `1`.

## Runner regression mapping

The first eight tests in `tests/tooling/runner.test.wfl` implement the eight
requirements below in the same order. The ninth verifies the complete default
discovers all maintained groups plus Scribe and excludes helper files.
They passed 9/9 on Windows with process runtime commit `a32c74f1`.
Direct argument lists avoid shell quoting; no fake Python interpreter remains
in the replacement fixtures.

| Python test method | Equivalent WFL test and required observation |
|---|---|
| `test_discovers_nested_suites_in_order_and_uses_repository_cwd` | WFL creates nested `a.test.wfl`, `z.test.wfl`, and ignored `example.wfl`; launches the copied WFL runner from outside its fixture root; asserts exactly `a`, then `z`, and the fixture root as each suite's cwd. Requires child cwd support. |
| `test_failing_suite_preserves_diagnostics_and_later_suite_runs` | A real WFL child fails intentionally with recognizable diagnostics; a second suite succeeds. Assert runner exit 1, both executions, failed suite name, and preserved stderr as well as stdout. |
| `test_timeout_fails_and_later_suite_still_runs` | WFL child waits longer than `--timeout 1`; next child writes a completion marker. Assert timeout diagnostic, both starts, second completion, runner failure, and absence of owned child processes afterward. |
| `test_empty_suite_set_is_an_error` | Empty fixture `TestPrograms/`; assert nonzero exit and empty-suite diagnostic. |
| `test_missing_interpreter_is_an_error` | Supply a nonexistent executable; assert nonzero exit and no fixture starts. |
| `test_nonpositive_and_nonfinite_timeout_are_rejected` | Parameterize `0`, `-1`, `nan`, and `inf`; each fails before any child. Retain every case. |
| `test_missing_scribe_source_is_an_error` | Request Scribe with missing source/test files; assert nonzero exit and Scribe diagnostic before running suites. |
| `test_upstream_suite_runs_in_disposable_copy_with_build_directory` | WFL creates minimal Scribe source/test and an original `build/existing.txt`. Assert the upstream fixture runs after local suites, has cwd distinct from original Scribe, sees fresh `build/`, its copy is removed, and original file bytes remain unchanged. |

The old fake interpreter is Python and uses an OS-specific shell launcher.
Neither fixture is eligible to survive this conversion. Real WFL fixture
programs can supply success, failure, delay, cwd, and marker behavior; a narrow
WFL fixture protocol can provide controlled runner observations without an
executable shell test implementation.

## Hygiene regression mapping

`tests/tooling/hygiene.test.wfl` implements the 28 rows below, in the same order,
and passed 28/28 on Windows. Common setup is WFL: make a unique disposable directory, run `git init`,
write every profile-required file and synthetic sources, stage them, and add
the approved Scribe gitlink with `git update-index --cacheinfo`. The checker
receives `--root` explicitly, so these tests do not require changing the parent
process directory. Capture its exit code and both output streams. WFL must
generate binary fixtures, edit profiles, inspect results, and clean up even
when an assertion fails. No real repository index is a fixture.

| Python test method | Equivalent WFL fixture and assertion |
|---|---|
| `test_clean_checkout_and_uninitialized_submodule_pass` | Baseline synthetic index with opaque Scribe gitlink; exit 0 and success text. |
| `test_new_untracked_root_file_is_checked_before_staging` | Add unstaged `scratch.md`; exit 1 and exact root-path diagnostic. |
| `test_new_untracked_root_directory_is_rejected` | Add `notes/design.md`; exit 1 and root diagnostic. |
| `test_legitimate_new_docs_and_binary_source_assets_pass` | Add maintained docs, synthetic WOFF2 bytes, PNG bytes under docs; exit 0. |
| `test_ignored_untracked_runtime_data_is_left_alone` | Write ignored `.db` and `.env`; exit 0 and unchanged database bytes. |
| `test_force_tracked_ignored_database_is_rejected` | Force-stage `app/fixture.db`; exit 1 and artifact diagnostic. |
| `test_repository_ignores_sqlite_databases_and_sidecars` | Copy actual `.gitignore`; create all 12 `.db`/`.sqlite`/`.sqlite3` combinations with empty, `-journal`, `-wal`, `-shm` suffixes; exit 0. |
| `test_case_variants_and_nested_cache_are_rejected` | Disable fixture ignores; separately test `app/site.SQLITE3-WAL`, `docs/server.LOG`, and `scripts/__PyCache__/bad.txt`; exact artifact diagnostic for each. |
| `test_secret_names_are_rejected_at_any_depth` | Separately test `.env.production`, `id_rsa`, and uppercase `.KEY` at the original depths; exit 1 for each. |
| `test_upload_image_cannot_use_source_asset_exception` | PNG under `static/uploads/`; exit 1 and runtime-state diagnostic. |
| `test_only_empty_declared_upload_placeholder_is_allowed` | Nonempty `static/uploads/.gitkeep`; exit 1. |
| `test_removed_and_empty_required_policy_fail` | Delete then recreate empty `GOVERNANCE.md`; both fail with their specific required/empty diagnostic. |
| `test_ignored_required_policy_cannot_pass_by_existing_locally` | Remove the policy from fixture index and ignore it; local existence still fails required-file check. |
| `test_worktree_link_changes_are_checked_without_staging` | Unstaged README link to nonexistent doc; exit 1 for candidate-tree link. |
| `test_link_to_ignored_local_file_cannot_hide_broken_clone` | Link to ignored local `.private` file; exit 1 even though it exists locally. |
| `test_links_to_new_candidates_directories_and_encoded_paths_pass` | New spaced-name doc; percent-encoded/fragment, directory, angle-bracket, and reference links all pass. |
| `test_reference_and_image_link_destinations_are_checked` | Missing image and reference-link definitions; assert both diagnostics in one failing result. |
| `test_anchors_urls_fences_and_submodule_links_are_skipped` | Anchor, HTTPS, mailto, uninitialized submodule destination, backtick fence and tilde fence examples all pass. |
| `test_links_cannot_escape_checkout` | README `../outside.md`; exit 1 for checkout escape. |
| `test_submodule_contents_are_not_recursively_inspected` | Synthetic `.db` and `.env` within Scribe gitlink directory; exit 0. |
| `test_scribe_cannot_be_replaced_with_copied_files` | Remove gitlink, create copied source; exit 1 for missing required gitlink. |
| `test_another_gitlink_cannot_bypass_artifact_inspection` | Add opaque `lib/other` gitlink; exit 1 for unapproved gitlink. |
| `test_indexed_symlink_is_rejected_even_when_checked_out_as_text` | `git hash-object -w` fixture content; index mode `120000` via cacheinfo while physical file is text; exit 1 for file type. Works without Windows symlink privileges. |
| `test_malformed_profile_fails_closed` | Invalid TOML `schema = [`; exit 2 and `HYGIENE-ERROR`. |
| `test_missing_profile_fails_closed` | Remove profile; exit 2 and profile-read error. |
| `test_unknown_profile_key_fails_closed` | Replace `allowed-dirs` with `allowed-directories`; exit 2 for unknown/missing keys. |
| `test_profile_cannot_use_escape_paths` | Replace a required architecture path with `../ARCHITECTURE.md`; exit 2 for nonrelative path. |
| `test_git_failure_fails_closed` | Move only fixture `.git` away; exit 2 and Git diagnostic. |

## HTTP port regression mapping

WFL setup must copy only application code, pinned Scribe source and installer
template into a disposable site; never copy database, uploads, config or Git
metadata. It creates a parent `.wflcfg` restricting the runtime to loopback,
including for the absent site-config case. A site config adds a disposable
`data_dir`. It owns the direct server child and its diagnostics, checks early
exit, polls `/install` for at most 20 seconds, uses bounded individual HTTP
requests, and cleans up on success, assertions, errors and timeouts. It must
refuse occupied ports without stopping an existing service. The original
driver requests an OS-assigned port for the configured case and checks that
8080 is also free, so a hardcoded-port regression produces useful output.

| Python test method | Equivalent WFL case |
|---|---|
| `test_configured_port_serves_installer_and_updates_startup_urls` | Explicit non-8080 available port; GET installer on it and assert both startup URL messages use it. |
| `test_missing_port_setting_defaults_to_8080` | Site config exists but port setting omitted; installer and both startup URLs use 8080. |
| `test_missing_config_file_defaults_to_8080` | Site `.wflcfg` absent; inherited runtime loopback config still protects fixture; app falls back to 8080. |

Every case asserts HTTP 200, `Content-Type` containing `text/html`, body text
`Set up your site` and `Scriptorium`, form action `/install`, and a named
`csrf_token` input. It asserts the exact configured `Scriptorium is running`
and `First run` URLs in the actual child log. Unit tests already cover invalid
port values; new HTTP cases should extend this coverage, not reduce it.

## Runtime evidence and upstream remedies

The following table preserves the initial Red findings, before the upstream
remedies; it is not the current source-built candidate's capability status.
Source inspected: WFL revision `cb1dadaad96939a4450a6eb2b3a6a51678035b7f`.
Executable probes were run on Windows with official nightly WFL `26.9.12`
from the locally extracted release, with that binary's directory first on
`PATH` so child runtimes match. These are native Windows results; the
Blacksmith Linux nightly results and resolved Docker digest must be recorded
separately. All fixtures contain synthetic data only.

| Capability | Verified result and effect |
|---|---|
| Filesystem | WFL creates parent directories, writes/reads/copies files, recursively lists paths, and deletes its own tree. `call remove_dir with path and yes` works. `list files recursively` is not sorted; the runner must sort explicitly. |
| Arguments and locations | `args`, `script_path`, `script_directory`, `current_directory` work. Runtime config is located from source directory; process cwd stays inherited. |
| Foreground process | `execute command` with argv returns `output`, `error`, `exit_code`, `success`. It preserves controlled child stdout/stderr and failures. Current source applies the overall runtime deadline, not an independent configurable timeout for each child. |
| Background lifecycle | Direct `spawn command`, `process ... is running`, `kill process`, and exit retrieval work. `finally` kills the owned child after both a runtime error and a failed assertion. |
| Async diagnostics | Confirmed blocker: `read output from process` exposes only stdout, although stderr is buffered internally. Waiting removes the handle and makes final output inaccessible. Capture tasks are not joined by that wait. A runner needs a complete outcome with both streams after reaping, without races or lost errors. |
| Child cwd | Confirmed missing primitive: neither spawn/execute grammar nor runtime implementation accepts a working directory, and there is no process chdir API. Launching an absolute WFL fixture path still uses the parent cwd. This prevents the existing disposable Scribe and real application fixtures from running unchanged with their required relative paths. Add a native per-launch cwd option; retain direct ownership of the actual child. |
| HTTP requests | Native POST with request headers/body returns status, body, headers, `ok`; ordinary response cookies are observable. |
| Redirect handling | Confirmed blocker: client follows redirects automatically and returns only the final response. A synthetic login POST giving 302 plus a session cookie becomes 200 with neither intermediate status nor cookie. Add explicit no-follow behavior or an equally complete redirect-chain result; preserve multiple header values. |
| Assertions/failure exit | `wfl --test` returns 1 for a genuine failed expectation. `expect` outside test mode errors instead of asserting. Documentation's `exit with code 1` does not parse as a supported exit-code construct; only successful `exit program` is implemented. A test-mode runner is possible, but exact ordinary-script exit-code compatibility needs a runtime remedy. This syntax mismatch is not behavioral Red evidence. |
| Error handling | `try`/`when error` expose `error_message`; `finally` runs cleanup and the original failure still propagates. No intentional failure is swallowed into a pass. |

The accepted foundation path cannot require people to learn shell quoting,
synthetic division-by-zero as a normal error API, or modified copies of Scribe
and the application just to run their tests. Absolute include paths do not
repair Scribe's relative `build/` or the app's cwd-based configuration/data
resolution. Shell wrappers would also change which process WFL owns and kills
on Windows. Neither is an accepted replacement for the missing primitive.

The original `a81ecf9` capability gates under `tests/runtime/` deliberately
exposed missing runtime behavior:

```sh
wfl --test tests/runtime/process-capabilities.test.wfl
wfl --test tests/runtime/http-redirect-capability.test.wfl
```

The process gate has four valid scenarios: cwd isolation, output after reaping,
stderr preservation, and error-path cleanup. On Windows 26.9.12 it reports
**1 passed / 3 failed, exit 1**; error-path cleanup passes. The HTTP gate reports
**0 passed / 1 failed, exit 1**, specifically `Expected 200 to equal 302`.
The HTTP probe requires free loopback port 41868 and checks occupancy before
starting its own server. These are historical upstream capability failures,
not application defects or replacements for the existing suites. The reviewed
upstream remedies make the current capability suites pass on the combined
candidate, and the complete runner now includes them by default. See
[the verification record](orm-verification.md) for published-runtime results.

Relevant runtime source locations: `src/parser/stmt/processes.rs` (launch
grammar), `src/interpreter/mod.rs` (`spawn_process`, `read_process_output`,
`wait_for_process`, `kill_process`, `http_client`), and
`src/parser/stmt/actions.rs` (`parse_exit_statement`). Remedies need upstream
regression tests, a published runtime, and reruns against an immutable nightly
image before the complete WFL-only runner can be claimed verified.

## CI and documentation conversion checklist

The converted Governance workflow provisions WFL on Blacksmith Ubuntu and GitHub
Windows, records the published release URL/asset/SHA256/version, runs
`wfl scripts/run_tests.wfl --group tooling`, and retains the hygiene checker.
Python remains only for that non-test checker implementation.

The WFL tests workflow pulls `bsbyrdwfl/wfl:nightly`, resolves its digest,
records runtime/Scriptorium/Scribe versions, and runs `wfl scripts/run_tests.wfl`
in that resolved container. A read-only source mount is copied into a disposable
writable checkout. Suite, Scribe-copy and HTTP orchestration are WFL. The Update
Scribe generated PR checklist uses these same commands. Final remote runtime
acceptance is pending until a published nightly contains the upstream remedies.

The hygiene profile now requires the WFL runner/helpers/config and both tooling
suites. Guidance uses the same complete/focused commands. The examples directory
houses the explicitly requested executable ORM/migration progression; the
application and test include layouts are retained.

The unchanged original Python tooling tests passed **36/36** before removal;
the replacement focused command passed **2 suites, 37/37 tests**. Its intentional
WFL assertion fixture returns runner exit 1, preserves diagnostics, and allows
later suites to complete. Its owned child/grandchild timeout fixture proves no
late marker survives cleanup. Fixture parser mistakes encountered during
development are not counted as behavioral Red evidence. Full candidate and
remote deliberate-failure evidence remain separate final acceptance steps.

Before removing Python versions, check every row above against executable WFL
scenarios. Then run the complete suite including pinned Scribe, file-backed
ORM/migrations/recovery and HTTP workflows, run repository hygiene, prove a
deliberate real WFL assertion failure reaches both runner and GitHub Actions,
remove the deliberate failure, and verify all final-revision required jobs.
