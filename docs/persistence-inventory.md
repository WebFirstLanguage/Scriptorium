# Persistence compatibility inventory

This is the pre-ORM compatibility baseline at Scriptorium revision
`4ec5c88d9e4ae27041599ad8293a28130b56fbf2`, inspected on 2026-09-20. It records
actual source behavior, including distinctions omitted by the older architecture
summary. It is an input to implementation and acceptance testing, not a claim
that the requested ORM or migration lifecycle has shipped.

## Sources and ownership

The complete application include path is
`main → site_ext → render → auth → db → util`; `render` also includes the pinned
Scribe root. Preserve this tree, wrapper signatures, and the raw database handle
passed to `site_ext_boot` and `site_ext_dispatch`. Scribe stays upstream-owned.

`app/db.wfl` owns seven application tables and one explicit index. Most data
access is there, but `auth.session_start` directly queries SQLite for seven-day
expiry, and `render.site_context` directly queries SQLite for the year.
`main.wfl` has no direct SQL. Extensions may own other tables, indexes, triggers,
and SQL through the same connection; core schema inspection must not reject,
rewrite, drop, or adopt those objects.

## Exact legacy schema

The baseline creates these statements with `IF NOT EXISTS`. No table has foreign
keys, cascade behavior, enum checks, custom collation, generated columns, or a
`STRICT`/`WITHOUT ROWID` declaration. `role` and `status` values shown in UI docs
are application conventions, not database constraints.

```sql
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'author', created_at TEXT DEFAULT (datetime('now')));
CREATE TABLE sessions (id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, created_at TEXT DEFAULT (datetime('now')), expires_at TEXT NOT NULL, csrf_token TEXT NOT NULL DEFAULT '');
CREATE TABLE posts (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT UNIQUE NOT NULL, title TEXT NOT NULL, body_markdown TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'draft', author_id INTEGER, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')));
CREATE TABLE pages (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT UNIQUE NOT NULL, title TEXT NOT NULL, body_markdown TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'draft', author_id INTEGER, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')));
CREATE TABLE settings (skey TEXT PRIMARY KEY, svalue TEXT NOT NULL DEFAULT '');
CREATE TABLE media (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT UNIQUE NOT NULL, original_name TEXT NOT NULL DEFAULT '', content_type TEXT NOT NULL DEFAULT '', size INTEGER NOT NULL DEFAULT 0, uploader_id INTEGER, created_at TEXT DEFAULT (datetime('now')));
CREATE TABLE login_attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT NOT NULL, attempted_at TEXT DEFAULT (datetime('now')));
CREATE INDEX idx_login_attempts_ip_time ON login_attempts (ip, attempted_at);
```

Five integer primary keys use `AUTOINCREMENT`: users, posts, pages, media, and
login_attempts. A rebuild must preserve `sqlite_sequence`, including a high-water
mark above the current maximum row ID. The implicit unique indexes for username,
slugs, filename, and text primary keys are significant even though the app names
only the rate-limit index.

All timestamp columns and the author/uploader references are nullable. The text
primary keys have no explicit `NOT NULL` clause. Do not strengthen those legacy
constraints during adoption. Existing orphans and nulls are valid legacy state;
deleting a user does not delete content, media, sessions, or attempts.

The older supported sessions definition is identical except it lacks
`csrf_token`. The old upgrader checks
`pragma_table_info('sessions')` and adds
`csrf_token TEXT NOT NULL DEFAULT ''` only when missing. Existing session IDs,
users, timestamps, and expirations are untouched. Its tests also construct a
database containing only this old sessions table; all remaining tables are
then created by `db_migrate`.

## Value and result contracts

- Single-row wrappers return a row map or WFL `nothing` when no row matches.
  Collection wrappers return a list, including an empty list. Counts return the
  numeric `n` value of `count(*)`; no count wrapper returns the SQL row map.
- SQL NULL maps to `nothing`; empty text remains empty text. `first_row` tests
  list length, not row truthiness. Defaults apply when INSERT omits a field;
  they must not silently replace explicit NULL or empty text.
- User, session, post, page, media, and attempt mutation wrappers return the
  native `execute` result, not an inserted ID or an ORM record. Current WFL
  source defines it as a map with `affected_rows` and `last_insert_id`. Keep that
  wrapper contract even if the reusable ORM offers record-returning methods.
- `setting_get` returns its fallback only when the key has no row. An existing
  empty setting is returned unchanged. `setting_set`, `setting_default`,
  `install_mark_done`, and successful `db_migrate` return `yes`.
- `field_or` treats missing keys and `nothing` as absent, but preserves empty
  text, `no`, and zero. `map_has` also treats a present `nothing` as absent; it
  is therefore unsuitable for ORM missing-versus-NULL validation.
- Query projections below are contracts. In particular, list rows intentionally
  omit password hashes and several content fields; changing every result to a
  full model record would change those contracts.

## Wrapper inventory

All predicates containing caller values use bound parameters. Quoted constants
such as `published`, time expressions, and sort keys are static source SQL.
No wrapper interpolates caller text into an identifier or SQL fragment.

### Settings and installer

| Action | Behavior | Application callers |
|---|---|---|
| `setting_get(conn, key, fallback)` | Select `svalue` by `skey`; fallback only for no row | `site_context`, home pagination, installer form, settings form, `install_is_done` |
| `setting_set(conn, key, value)` | `INSERT … ON CONFLICT(skey) DO UPDATE SET svalue = ?`; returns yes | Settings save, installation title/tagline, installed flag |
| `setting_default(conn, key, value)` | `INSERT OR IGNORE`; existing value wins | Boot defaults |
| `install_is_done(conn)` | True only for setting `installed` exactly `yes` | Dispatch gate, installer POST guard, boot backfill and startup message |
| `install_mark_done(conn)` | Upsert `installed=yes` | Installation and boot backfill |
| `install_apply(conn, title, tagline, username, hash)` | Create admin, then set title/tagline/installed; catches user-create failure and returns no | Installer POST |

The old `install_apply` is not atomic. Its promised compatibility is that an
initial username failure leaves settings untouched; an error after user creation
can leave a partially installed site, whose next boot locks the installer because
a user exists. The new transaction implementation should make installation
atomic while retaining successful results and the duplicate-username no result.
Do not weaken the boot backfill for pre-wizard installations.

### Users

| Action | Result or mutation | Application callers |
|---|---|---|
| `user_count(conn)` | Numeric count of all users | Boot backfill, dashboard |
| `user_create(conn, username, hash, role)` | Insert three named values; DB generates ID/time | Installer, admin user create |
| `user_by_username(conn, username)` | `id, username, password_hash, role, created_at` | Login verification, installer session creation |
| `user_by_id(conn, id)` | Same projection | Admin edit/update |
| `user_list(conn)` | `id, username, role, created_at`; `ORDER BY id ASC` | Admin users list |
| `user_set_role(conn, id, role)` | Update only role by ID | Admin user update |
| `user_set_password(conn, id, hash)` | Update only hash by ID | Admin user update when password nonempty |
| `user_delete(conn, id)` | Delete only user row by ID | Admin delete after self-delete guard |

Passwords are already hashes when passed to persistence; never hash them again
during adoption or mapping. `role` and `password_hash` need explicit trusted
assignment paths, while the generic ORM must reject unchecked mass assignment.
Username update is not offered by the existing wrapper. User deletion leaves
references intact; surviving sessions cease resolving because their user join
no longer matches.

### Sessions and login attempts

| Action | Result or predicate | Application callers |
|---|---|---|
| `session_create(conn, sid, user_id, expires_at, csrf)` | Insert supplied session ID/user/expiry/token; SQLite generates created time | `auth.session_start` |
| `session_user(conn, sid)` | Inner join users; `u.id AS id, u.username AS username, u.role AS role, s.csrf_token AS csrf_token`; `s.id=? AND expires_at > datetime('now')` | `current_user`, request dispatch |
| `session_delete(conn, sid)` | Delete only matching session | Logout |
| `session_purge_expired(conn)` | Delete where expiry `<= datetime('now')` | Boot |
| `login_attempt_record(conn, ip)` | Insert IP; SQLite generates ID/time | Invalid credentials and invalid/failed installer inputs |
| `login_attempts_recent(conn, ip)` | Count matching IP with `attempted_at > datetime('now', '-15 minutes')` | Login and installer POST |
| `login_attempts_clear(conn, ip)` | Delete all attempts for that IP | Successful login/install |
| `login_attempts_purge(conn)` | Delete attempts `<= datetime('now', '-15 minutes')` | Boot |

`session_start` generates a 32-byte random hex ID and a separate CSRF token,
obtains expiry with `SELECT datetime('now', '+7 days') AS exp`, then calls
`session_create`. Preserve SQLite UTC text values and strict time boundaries.
Legacy sessions gaining an empty CSRF token remain identifiable; `csrf_ok`
rejects an empty token and does not invent one during lookup or upgrade.

The HTTP limiter refuses requests once the recent count is **at least 10**,
before credentials or CSRF are checked. Login CSRF failure does not add an
attempt; bad credentials do. Installer field-validation and apply failures add
attempts; successful authentication clears only the requesting IP.

### Posts

`post_create` inserts slug, title, Markdown body, status, and author ID.
`post_update` updates slug/title/body/status and sets `updated_at=datetime('now')`
for one ID; it preserves author and creation time. `post_delete` deletes one ID.
Their callers are the corresponding create/update/delete HTTP handlers, which
enforce CSRF and author/admin ownership outside the wrapper.

| Read action | Exact projection | Filter and order |
|---|---|---|
| `post_by_id` | `id, slug, title, body_markdown, status, author_id, created_at, updated_at, author_name` | ID; left join username as author_name |
| `post_by_slug` | Same | Slug only, including drafts; left join username |
| `post_list_published` | `id, slug, title, body_markdown, status, created_at, author_name` | Published; created_at DESC, id DESC; bound LIMIT/OFFSET |
| `post_list_all` | `id, slug, title, status, author_id, updated_at, author_name` | updated_at DESC, id DESC |
| `post_list_by_author` | Same list projection | author_id; updated_at DESC, id DESC |
| `post_count_published` | Numeric count | Published only |
| `posts_total` | Numeric count | All rows |

The author join is LEFT JOIN in every post read, so null and dangling authors
retain the post with `author_name=nothing`. The public post handler separately
rejects drafts; moving its filter into `post_by_slug` would change that public
wrapper. Public home uses published count/list and `posts_per_page`, falling
back to 5 if parsed value is below 1. Admin dashboard/list calls all/by-author
according to role. Edit/update/delete first call `post_by_id` for existence and
ownership. Duplicate slug creation is caught by the handler; other database
constraints remain authoritative.

### Pages

Page create/update/delete mirror posts, including updated time and preserving
author/created time. There is no user join in any page wrapper.

| Read action | Exact projection | Filter and order |
|---|---|---|
| `page_by_id` | `id, slug, title, body_markdown, status, author_id, updated_at` | ID |
| `page_by_slug` | Same | Slug AND published |
| `page_list_all` | `id, slug, title, status, updated_at` | title ASC |
| `page_list_by_author` | Same list projection | author_id; title ASC |
| `page_list_published` | `id, slug, title` | Published; title ASC |
| `pages_total` | Numeric count | All rows |

Page ordering has no explicit secondary key. Do not silently promise or impose
an ID tie-breaker as a compatibility assumption. Public rendering uses the slug
lookup; `site_context` builds navigation with the published list; admin list
chooses all/by-author; edit/update/delete use ID lookup and ownership checks.

### Media

`media_create` inserts filename, original_name, content_type, size, uploader_id;
SQLite creates ID/time. `media_by_id` returns
`id, filename, original_name, content_type, size, uploader_id, created_at` or
nothing. `media_list_all` returns those fields plus left-joined username as
`uploader_name`, ordered `created_at DESC, id DESC`. `media_delete` removes only
the row by ID. Null/dangling uploaders do not remove a media list row.

The upload handler writes bytes first, then inserts metadata; an insertion
failure attempts to delete the just-written file. Delete checks uploader/admin
ownership, deletes the row, then attempts file deletion. ORM migration must not
introduce cascades or rewrite filenames. Preserve `/assets/uploads/` URLs and
the storage path chosen at boot. Database transactions alone cannot make a
filesystem write/delete atomic.

## Startup and extension contract

Current boot performs these operations in order:

1. Read optional `.wflcfg` from process CWD. `config_value_from` trims lines,
   ignores whole-line `#` comments, uses the first exact key, and retains inline
   `#` text. Missing config reads as empty text.
2. Resolve HTTP port through `config_port_from`: numeric integer 1–65535 or
   fallback 8080. Resolve `data_dir`; create it if nonempty and absent. Defaults
   are `scriptorium.db` and `static/uploads`; configured paths are
   `<data_dir>/scriptorium.db` and `<data_dir>/uploads`.
3. Configure the public theme and issue existing missing/refused-theme notices.
4. Open `sqlite://` plus resolved database path and run `db_migrate`.
5. Insert only absent settings: site_title=Scriptorium,
   site_tagline=Words, well kept., posts_per_page=5.
6. If any user exists and installed is not exactly yes, upsert installed=yes.
7. Call `site_ext_boot(db)` once with the open database handle.
8. Purge expired sessions and old attempts; create uploads directory if absent.
9. Listen on the resolved port; print matching startup/installer URLs; dispatch
   requests using the same open connection until shutdown.

Administrative migration commands must resolve the same path and visibly name
it. Read-only status/plan must not accidentally initialize an absent database.
Startup must stop before serving if migration/adoption fails. It may perform
supported forward upgrades; it must never roll back destructively. Preserve the
extension's place after successful schema/default/backfill and before listening.

At request dispatch, assets are served before the installation lock. An
uninstalled site sends every other route to `/install`; an installed site's
late installer GET or POST redirects without applying setup. Public extension
dispatch precedes stock public routes, returns yes only after responding, and
otherwise falls through. Its signature is
`site_ext_dispatch(db, req, req_method, req_path, req_body, user)`.

## Adoption and ORM acceptance decisions

These concrete requirements follow from the inventory:

1. Validate the core table structure, defaults, uniqueness, primary keys, and
   owned index before recording any baseline. Recognize fresh, exact current,
   and supported pre-CSRF schemas explicitly. Recognize safe partial legacy
   creation only when each present managed object matches its historical
   definition. Stop on incompatible or ambiguous objects without a successful
   ledger row. Preserve every extension-owned object and row.
2. Use immutable migration-specific definitions, independent of current model
   metadata. Adoption is an inspected history event, never permission to claim
   that unexecuted arbitrary migrations ran. Preserve passwords, IDs, nullable
   values, defaults, sessions, CSRF tokens, timestamps, and sequence state.
3. Keep existing wrappers as projection/return adapters over one reusable ORM.
   Model metadata can describe logical relationships without adding physical
   foreign keys to legacy tables. Explicit relationship loading must preserve
   nullable/dangling links and avoid one-query-per-row collection loading.
4. Preserve existing native connection ownership for callers and extensions.
   ORM-owned connections need explicit close semantics; borrowed handles must
   not be closed unexpectedly. Transaction scope must use verified native WFL
   behavior and documented nested semantics, never catch-and-report-success.
5. Parameterize every value, validate metadata identifiers and sort directions,
   distinguish missing/null/empty/default/not-found, reject unknown fields, and
   require explicit authority for sensitive assignment and unfiltered bulk
   mutation. Keep counts and generated SQL inspectable without parameter values.
6. Keep the seven-day expiry, fifteen-minute attempt window, setting upsert,
   SQLite timestamp defaults/updates, and year lookup as explicit, named uses
   of a parameterized SQL escape hatch if the generic query API cannot express
   them naturally. Exceptions must not become a second persistence layer.
7. Characterize these exact wrapper projections, ordering, empty results,
   return maps, duplicate errors, null/orphan relationships, installation lock,
   and SQL time boundaries before refactoring. Exercise file-backed adoption,
   restart, and HTTP callers afterward; existing memory tests alone are not
   recovery evidence.

The WFL foundations were read in full from
`G:\repos\wfl\Docs\wfl-foundation.md`. The supplied task attachment includes the
same No-Unlearning Invariant: “For every feature, the beginner form and the expert
form must be the same form, or connected by a smooth path with nothing to
unlearn.” No separate foundations attachment was present in the supplied
references, so there is no second full text to compare. The implementation must
use explicit versioned migrations in the first executable example and extend
the same model/record/query vocabulary through filters, relationships,
transactions, and schema evolution. Avoid opaque encoded metadata strings,
disposable automatic synchronization, and silently swallowed errors. Readable
WFL actions, strict validation, actionable safe diagnostics, native standard
library integration, and bounded/query-visible relationship loading make the
foundations measurable acceptance conditions.

## Documentation corrections identified

- `docs/ARCHITECTURE.md` constraint 2 says main includes render directly; actual
  main includes site_ext. Its diagram already shows the correct tree.
- Constraint 4 says csrf ALTER is guarded by try; source now inspects schema
  and propagates ALTER errors. Its no-transactions claim must be rechecked
  against the required current nightly, not copied as a runtime limitation.
- The database-layer description and README layout say all queries live in
  db.wfl; auth expiry and render year queries are counterexamples.
- Architecture's theme extension recipe mentions an active-theme setting;
  current implementation selects `theme`/`theme_root` from `.wflcfg`.
- Architecture and README prose say more than 10 failures; actual HTTP
  threshold is at least 10 recent failures.
- `main.wfl` header and `auth.sid_from_cookie` comment claim request values
  only resolve in the main loop, although architecture already records that
  limitation as lifted and media upload reads request values in an action.
- Existing docs correctly describe no general migration lifecycle at the
  baseline. README, CLAUDE, SECURITY, testing, CONTRIBUTING, hygiene policy,
  and workflow commands must describe actual shipped WFL migration/testing
  behavior when integration is complete.
