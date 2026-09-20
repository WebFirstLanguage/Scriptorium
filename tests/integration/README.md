# Real HTTP integration suites

Run from the repository root with the candidate executable as the first WFL
program argument, for example:

```text
wfl --test tests/integration/server-port.test.wfl /absolute/path/to/wfl
wfl --test tests/integration/authentication.test.wfl /absolute/path/to/wfl
wfl --test tests/integration/content-users.test.wfl /absolute/path/to/wfl
wfl --test tests/integration/media.test.wfl /absolute/path/to/wfl
wfl --test tests/integration/throttle.test.wfl /absolute/path/to/wfl
wfl --test tests/integration/recovery.test.wfl /absolute/path/to/wfl
```

The runtime must support native per-child working directories, owned process
completion results, `current_executable`, explicit application errors, and per-request redirect
control. The suite driver and all children use the supplied executable. Without
the argument, the helper uses `current_executable` to retain its own runtime.
Run sequentially; the two
default-port cases require loopback port 8080 to be available. A bind failure is
a failed prerequisite; no existing process is stopped or reused.

An optional second program argument selects an extracted application source
baseline for before/after characterization. Artifacts and the WFL request helper
still belong to this checkout; the source baseline supplies only application
code/templates. The pinned Scribe entry is copied from this checkout, so record
and verify its unchanged revision when comparing an older application baseline.

All fixture creation, HTTP requests, assertions, SQL inspection, process
ownership, and cleanup are WFL. Each site has a UUID directory beneath
`target/test-artifacts/http`. It copies application/library WFL and theme/admin
HTML plus the pinned Scribe entry point. It never copies checkout databases,
uploads, local configuration, Git metadata, or another site's state. The absent
configuration case inherits a loopback-only runtime configuration from its
disposable parent. The generated site runs in its own working directory.

The helper owns the direct site process, waits up to 20 seconds for its startup
message, captures early-exit stdout/stderr, and closes it in `finally`. Each
request uses a separate WFL helper with a five-second runtime budget and a
six-second owned-process deadline. It returns the actual redirect response and
all response-header values. Tests manage synthetic cookies explicitly.

| Suite | Real boundaries asserted |
|---|---|
| `server-port.test.wfl` | Original Python cases: configured ephemeral port, missing setting, absent config; exact startup URLs, installer status/content type/form/CSRF. |
| `authentication.test.wfl` | Installer CSRF and input rejection without mutation, first admin/session creation, setup locking, login response cookie flags, invalid credentials, CSRF, logout methods, and expired sessions. |
| `content-users.test.wfl` | Draft/publication, escaped title and rendered Markdown, pagination, page navigation/update/delete, mutation methods, CSRF, author ownership, admin user/settings boundaries, password update, account removal and revoked access. |
| `media.test.wfl` | Configured and legacy storage, generated safe names, byte retrieval, missing/wrong CSRF, extension/empty/malformed/oversized rejection, author denial, method enforcement, database/file consistency on deletion. |
| `throttle.test.wfl` | Exactly ten failed credentials, next request blocked, persistence across restart, expired-window recovery and successful-login clearing. |
| `recovery.test.wfl` | Stopped-site database-plus-upload backup, restart, actual restore after a later change, HTTP content/media and login, SQLite integrity and foreign-key checks. |

SQL reads inspect the synthetic site independently; installation, account and
content creation use the real HTTP routes. SQL writes only simulate expired
sessions and elapsed throttle windows. Upload payloads are synthetic text with
image extensions because the current CMS validates extensions, not image
decoding. These checks do not claim browser accessibility or image-content
inspection. Migration upgrade/crash-recovery coverage belongs to the migration
suites; this HTTP recovery test restores a matching stopped-site data backup.

The three original Python port cases have passed through their WFL replacements,
and the Python file has been removed. Its original source remains in Git at
`4ec5c88d9e4ae27041599ad8293a28130b56fbf2`. Before/after evidence is recorded in
[EVIDENCE.md](EVIDENCE.md); parsing alone is not passing integration proof.
