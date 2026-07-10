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
   ├─ /, /post/:slug, /page/:slug → dispatch_public → Scribe → HTML  │
   └─ /admin/*    → dispatch_admin (session + role gate) → Scribe    │
                                     │                                │
                                     ▼                                │
                              SQLite (scriptorium.db) ◄───────────────┘
                        users · sessions · posts · pages · settings
```

Library layers, each pulled in with `include from` (see the include rule below):

```
render.wfl ── auth.wfl ── db.wfl ── util.wfl
     └──────── lib/scribe.wfl
main.wfl ── render.wfl   (+ defines the router and every request handler)
```

- **util.wfl** — `slugify`, `to_int`, `field_or`, `truncate_text`. Form/cookie
  parsing is *not* here: WFL's stdlib already ships `parse_form_urlencoded` and
  `parse_cookies` (both percent-decode), so we use those.
- **db.wfl** — the SQLite schema (idempotent `CREATE TABLE IF NOT EXISTS`) and
  every `query`/`execute` the app runs. Helpers take the connection handle as a
  parameter, so the data layer is testable against `sqlite::memory:`.
- **auth.wfl** — `hash_password`/`verify_password`, session create/lookup/delete,
  and the `is_admin` / `can_edit` role checks.
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
store req_method as method          # request globals are only readable here…
store req_path   as path
store req_body   as body
store cookie_hdr as header "Cookie" of req
call dispatch with db and req and req_method and req_path and req_body and cookie_hdr
```

`dispatch` resolves the current user from the cookie, then routes with WFL's
`route` construct and `path_params`. Handlers are ordinary actions that call
`respond to req …`.

## WFL constraints that shaped the design

These are real properties of WFL v26.7 that the structure works within:

1. **`header`, `path`, and `method` only resolve in the top-level request loop.**
   Inside an action the analyzer rejects them. → The loop reads them once and
   passes them into handlers as parameters. `respond to req` *does* work inside
   an action, so handlers can render and reply.
2. **Includes form a tree, not a flat namespace — diamonds break.** A file only
   sees definitions from files *it* includes (transitively), and an include that
   was already pulled in elsewhere is skipped. → The libraries form a strict
   chain `util ← db ← auth ← render`, `main` includes only `render`, and the
   router + handlers live in `main.wfl` (so they share one scope). Scribe is
   included exactly once (by `render.wfl`).
3. **No query strings.** WFL's server drops the query string entirely. → All
   state is in the path (`/blog/page/2`, `/admin/posts/7/edit`) or in POST bodies.
4. **No transactions / no migration engine.** → Schema is idempotent DDL run at
   boot; every write is a single statement.
5. **No CSRF/session helpers.** → Sessions are a random `secure_random_bytes` id
   in an `HttpOnly; SameSite=Lax` cookie, stored in a `sessions` table with a
   SQL-checked expiry.
6. **Reserved words.** `found`, `missing`, `undefined`, `data`, `content`,
   `status`, `count`, `header`, … are keywords, so identifiers avoid them
   (`the_status`, `password_hash`, `svalue`, …).

## Data model

| Table | Columns |
|---|---|
| `users` | id, username (unique), password_hash, role (`admin`/`author`), created_at |
| `sessions` | id (random hex), user_id, created_at, expires_at |
| `posts` | id, slug (unique), title, body_markdown, status (`draft`/`published`), author_id, created_at, updated_at |
| `pages` | id, slug (unique), title, body_markdown, status, author_id, created_at, updated_at |
| `settings` | skey (PK), svalue |

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
- **CSRF** = add a token column to `sessions`, embed it as a hidden field, and
  compare with `constant_time_equals` in the POST handlers.
