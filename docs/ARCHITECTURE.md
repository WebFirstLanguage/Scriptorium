# Scriptorium — architecture

Scriptorium is a single WFL program. This note explains how the pieces fit and,
importantly, the **WFL constraints** that shaped the design — so the structure
reads as deliberate rather than accidental.

## The stack

```
Browser
   │  HTTP (127.0.0.1:8080)
   ▼
main.wfl ── listen on port ── main loop: wait for request ── route ──┐
   │                                                                  │
   ├─ /assets/*   → serve_asset (read binary + mime_type)            │
   │                 └─ /assets/uploads/* = media uploaded via admin │
   ├─ /, /post/:slug, /page/:slug → dispatch_public → Scribe → HTML  │
   └─ /admin/*    → dispatch_admin (session + CSRF + role gate)      │
                                     │                                │
                                     ▼                                │
                              SQLite (scriptorium.db) ◄───────────────┘
          users · sessions · posts · pages · settings · media · login_attempts
```

Library layers, each pulled in with `include from` (see the include rule below):

```
render.wfl ── auth.wfl ── db.wfl ── util.wfl
     └──────── lib/scribe.wfl
main.wfl ── render.wfl   (+ defines the router and every request handler)
```

- **util.wfl** — `slugify`, `to_int`, `field_or`, `truncate_text`, `file_ext`,
  `file_stem`. Form/cookie parsing is *not* here: WFL's stdlib already ships
  `parse_form_urlencoded` and `parse_cookies` (both percent-decode), so we use
  those.
- **db.wfl** — the SQLite schema (idempotent `CREATE TABLE IF NOT EXISTS`) and
  every `query`/`execute` the app runs. Helpers take the connection handle as a
  parameter, so the data layer is testable against `sqlite::memory:`.
- **auth.wfl** — `hash_password`/`verify_password`, session create/lookup/delete
  (each session carries a CSRF token, validated by `csrf_ok`), and the
  `is_admin` / `can_edit` role checks.
- **render.wfl** — builds the shared `site` context (title, nav, current user)
  and wraps Scribe's `scribe_render_file` with the theme/admin template dirs.
- **main.wfl** — boot (open DB, migrate, seed the first admin), the request loop,
  the `route`-based dispatcher, and all handler actions.

## Request lifecycle

WFL's web server is **pull-based and single-threaded**: the loop blocks on
`wait for request`, handles exactly one request, responds, and loops. There is
no middleware and no built-in session support, so the loop does the plumbing:

```wfl
wait for request comes in on web_server as req
store req_method as method
store req_path   as path
store req_body   as body
store req_ip     as client_ip       # feeds the login rate limiter
store cookie_hdr as header "Cookie" of req
call dispatch with db and req and req_method and req_path and req_body and cookie_hdr and req_ip
```

`dispatch` resolves the current user from the cookie, then routes with WFL's
`route` construct and `path_params`. Handlers are ordinary actions that call
`respond to req …`. Since WFL 26.7.26, `header "X" of req`, `body_bytes of req`
and friends also resolve *inside* actions from a passed request object — the
media-upload handler uses that to read the multipart body and its
`Content-Type` itself instead of having the loop thread them through.

## WFL constraints that shaped the design

These are real properties of WFL that the structure works within. The first
MVP targeted v26.7.25; WFL#597 (fixed in 26.7.26) lifted several of them —
noted inline:

1. **Request values used to resolve only in the top-level request loop.**
   *Lifted in 26.7.26:* `header "X" of req`, `path of req`, `method of req`,
   `body of req`, `body_bytes of req` and `query of req` now work inside
   actions that receive `req`. The loop still threads `method`/`path`/`body`/
   `client_ip` into handlers as plain parameters (it reads them once anyway),
   but new code — like the media-upload handler — reads what it needs straight
   from `req`.
2. **Includes form a tree, not a flat namespace — diamonds break.** A file only
   sees definitions from files *it* includes (transitively), and an include that
   was already pulled in elsewhere is skipped. → The libraries form a strict
   chain `util ← db ← auth ← render`, `main` includes only `render`, and the
   router + handlers live in `main.wfl` (so they share one scope). Scribe is
   included exactly once (by `render.wfl`).
3. **No query strings.** *Lifted in 26.7.26* (`query` / `query of req` +
   `parse_query_string`). Scriptorium's URLs still keep state in the path
   (`/blog/page/2`) — they predate the fix and are stable, shareable URLs.
4. **No transactions / no migration engine.** → Schema is idempotent DDL run at
   boot; every write is a single statement. (The one post-MVP column addition,
   `sessions.csrf_token`, is a `try`-guarded `ALTER TABLE` at boot.)
5. **No CSRF/session helpers.** → Sessions are a random `secure_random_bytes` id
   in an `HttpOnly; SameSite=Lax` cookie, stored in a `sessions` table with a
   SQL-checked expiry. CSRF tokens ride the same table — see Security below.
6. **Request bodies were capped at 1 MB with no multipart parser.** *Lifted in
   26.7.26:* `.wflcfg` sets `web_server_max_body_size = 10485760` (10 MiB) and
   the upload handler parses `multipart/form-data` with `parse_multipart`.
7. **Reserved words.** `found`, `missing`, `undefined`, `data`, `content`,
   `status`, `count`, `header`, `one`, … are keywords, so identifiers avoid
   them (`the_status`, `password_hash`, `svalue`, `media_row`, …).

## Security

- **CSRF.** Every admin `<form method="post">` carries a hidden `csrf_token`.
  For signed-in users the token is minted per session (`generate_csrf_token`
  at login, stored in `sessions.csrf_token`) and validated centrally in
  `dispatch_admin`: any admin POST whose token doesn't match the session's —
  compared with `constant_time_equals` — is rejected with 403 before any
  handler runs. The multipart upload route is the one exception: its token
  travels as a form *part* and is checked inside `handle_media_upload`. The
  login form has no session yet, so it uses a **double-submit cookie**: the
  rendered form mints a token, sets it as a short-lived `csrf` cookie and
  embeds it as the hidden field; the POST must present both, matching.
  Logout is POST-only (a GET cannot end a session) and sits behind the gate.
- **Login rate limiting.** Failed logins are recorded per client IP in
  `login_attempts` (timestamps are SQL-side, like everything else). More than
  10 failures from one address inside 15 minutes → `429` for that address,
  before credentials are even checked. A successful login clears the counter;
  stale rows are purged at boot. This is the crude in-app limiter the
  single-threaded server allows — a robust one still wants upstream
  concurrency/middleware support.
- **Media uploads.** Only `png`/`jpg`/`jpeg`/`gif`/`webp` extensions are
  accepted (no SVG — it can carry scripts). Stored names are re-derived, never
  trusted: `slugify(original stem)` + a random hex suffix + the vetted
  extension, so path separators or oddball characters in the client's filename
  never reach the filesystem. Bytes land in `static/uploads/` (served by the
  existing `/assets/*` route, which already rejects `..`), and a `media` row
  records size/type/uploader. Deleting is uploader-or-admin (`can_edit`).

## Data model

| Table | Columns |
|---|---|
| `users` | id, username (unique), password_hash, role (`admin`/`author`), created_at |
| `sessions` | id (random hex), user_id, created_at, expires_at, csrf_token |
| `posts` | id, slug (unique), title, body_markdown, status (`draft`/`published`), author_id, created_at, updated_at |
| `pages` | id, slug (unique), title, body_markdown, status, author_id, created_at, updated_at |
| `settings` | skey (PK), svalue |
| `media` | id, filename (unique, on disk under `static/uploads/`), original_name, content_type, size, uploader_id, created_at |
| `login_attempts` | id, ip, attempted_at |

Timestamps are filled by SQLite (`DEFAULT (datetime('now'))` and explicit
`datetime('now')` in updates), so the app never formats dates itself.

## Templating

Scribe is a Twig-style engine (vendored at `lib/scribe.wfl`). Template paths
resolve **relative to the process working directory**, which is why Scriptorium
must be run from the repo root and templates reference each other by root paths
(`{% extends "themes/base/templates/skeleton.html" %}`). Every `{{ … }}` is
auto-escaped; post/page bodies go through the `markdown` filter, which escapes
input first and neutralises dangerous link schemes.

## Extending it

- **A new content type** = a table + helpers in `db.wfl`, templates, handlers in
  `main.wfl`, and route arms in `dispatch_admin` / `dispatch_public`.
- **A new theme** = a second folder under `themes/` and an `active theme` setting
  (the `render_public` wrapper is the single place that maps names to paths).
- **A new protected form** = include `<input type="hidden" name="csrf_token"
  value="{{ site.csrf }}">` in the form; the POST gate in `dispatch_admin`
  validates it before your handler is reached — nothing else to do.
