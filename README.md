# Scriptorium

A small, WordPress-style **content management system written entirely in
[WFL](https://github.com/WebFirstLanguage/wfl)** — the WebFirst Language, where
programs read like plain English. Scriptorium serves a public blog/site and a
login-protected admin panel, persists everything in **SQLite**, renders pages
with the **[Scribe](https://github.com/WebFirstLanguage/scribe)** templating
engine, and is styled with the **WFL Design System** (dark, teal-on-Ink).

![Public home](docs/screenshots/public-home.png)

## Features (MVP)

- **Public site** with a base theme: home feed with pagination, single-post
  pages, standalone pages, and a site nav — all server-rendered.
- **Admin panel** (`/admin`): dashboard, and full CRUD for **posts**, **pages**,
  **users**, and **site settings**.
- **Markdown** authoring — post/page bodies are written in Markdown and rendered
  with Scribe's safe `markdown` filter (HTML-escaped, dangerous links neutralised).
- **Media uploads** — a media library (`/admin/media`) with image uploads
  (multipart, up to 10 MiB), served from `/assets/uploads/`, plus an upload
  panel right in the post/page editors.
- **Multiple users with roles**:
  - **admin** — manages users, settings, and *all* content.
  - **author** — creates and edits *their own* posts and pages.
- **Sessions & auth** rolled on WFL's Argon2id password hashing
  (`hash_password` / `verify_password`), a random session id in an `HttpOnly`
  cookie, and a server-side `sessions` table.
- **CSRF protection** on every admin form (per-session tokens, compared in
  constant time; the login form uses a double-submit cookie), and **per-IP
  login rate limiting** (10 failures / 15 minutes → 429).
- **WFL routing** — dispatch uses WFL's `route` construct plus `path_params`
  for `/post/:slug`, `/admin/posts/:id/edit`, and friends.
- **Design system** — every screen uses the WFL Design System tokens
  (Alegreya display serif, Verdant Teal accent, Ink surfaces, pill buttons,
  20px card radius).
- **Swappable themes** — the public site is built from reusable **sections** and
  assembled into pages: every page is a **header** + a **body** + a **footer**,
  in that order (`themes/base/`). See [`docs/THEMING.md`](docs/THEMING.md).

| Admin dashboard | Post editor | Sign in |
|---|---|---|
| ![Dashboard](docs/screenshots/admin-dashboard.png) | ![Editor](docs/screenshots/admin-post-edit.png) | ![Login](docs/screenshots/admin-login.png) |

## Quick start

You need the WFL interpreter (`wfl`) on your PATH. Then, **from the repository
root** (template and asset paths resolve relative to the working directory):

```sh
wfl main.wfl
```

On first run Scriptorium creates `scriptorium.db`, seeds default settings, and
prints a **one-time admin password**:

```text
==================================================
 Scriptorium — first run: seeded an admin account
   username:  admin
   password:  d1194faad562283922
   (shown once — sign in and add users under Users)
==================================================
Scriptorium is running at http://127.0.0.1:8080  (admin: /admin)
```

Open <http://127.0.0.1:8080/> for the site and <http://127.0.0.1:8080/admin> to
sign in. Add more users (admins or authors) under **Users**.

> Bind address and TLS are set in `.wflcfg`. The server listens on
> `127.0.0.1:8080` by default; set `web_server_bind_address = 0.0.0.0` to expose
> it behind a reverse proxy.

## Routes

All state lives in the **path** (or in POST bodies) — stable, shareable URLs.

| Method | Path | What |
|---|---|---|
| GET | `/` · `/blog/page/:n` | Home feed (paginated) |
| GET | `/post/:slug` | A published post |
| GET | `/page/:slug` | A published page |
| GET | `/assets/*` | Static files (CSS, fonts, logo, uploads) |
| GET/POST | `/admin/login` · `/admin/logout` | Auth (logout is POST-only) |
| GET | `/admin` | Dashboard |
| GET/POST | `/admin/posts` · `/admin/posts/new` · `/admin/posts/:id/edit` · `/admin/posts/:id` · `/admin/posts/:id/delete` | Posts CRUD |
| GET/POST | `/admin/pages…` | Pages CRUD (same shape) |
| GET/POST | `/admin/media` · `/admin/media/upload` · `/admin/media/:id/delete` | Media library + uploads |
| GET/POST | `/admin/users…` | Users CRUD *(admin only)* |
| GET/POST | `/admin/settings` | Site settings *(admin only)* |

Every admin POST must carry the session's CSRF token (rendered into each form
as a hidden `csrf_token` field) — requests without it get a 403.

## Project layout

```text
main.wfl              Boot (open DB, migrate, seed) + request loop + router + handlers
.wflcfg               WFL runtime config (bind address, TLS, body-size cap)
app/
  util.wfl            slugify, to_int, field_or, truncate, file_ext/stem (parsing is stdlib)
  db.wfl              SQLite schema + every query/execute helper
  auth.wfl            passwords, sessions, CSRF tokens, role checks
  render.wfl          shared "site" context + Scribe wrappers
lib/scribe.wfl        vendored Scribe template engine
themes/base/          Default theme: sections/ (header, footer) + templates (skeleton, assembler, bodies)
themes/README.md      Theme layout at a glance
admin/templates       Admin panel templates
static/               WFL Design System (ds/) + theme.css + admin.css
static/uploads/       Uploaded media (runtime; served as /assets/uploads/*)
TestPrograms/         WFL test suites (wfl --test)
docs/                 Architecture notes + THEMING.md + screenshots
```

## Tests

```sh
wfl --test TestPrograms/util.test.wfl   # helpers (slugify, file_ext, parsing, …)
wfl --test TestPrograms/db.test.wfl     # data layer against sqlite::memory:
wfl --test TestPrograms/auth.test.wfl   # sessions + CSRF token checks
```

## Security notes

- Passwords are stored only as Argon2id hashes; login uses `verify_password`.
- Every SQL statement is **parameterised** — user input is never spliced into SQL.
- Output is **auto-escaped** by Scribe; Markdown is rendered through a safe subset.
- Session cookies are `HttpOnly` + `SameSite=Lax`; static serving rejects `..`.
- **CSRF**: every admin POST form carries a per-session token (hidden
  `csrf_token` field), validated with `constant_time_equals` before anything
  mutates; the login form uses a double-submit cookie since no session exists
  yet. Every mutating route (update, delete, logout) is POST-only — a GET
  returns 405 so nothing can slip past the token check.
- **Rate limiting**: more than 10 failed logins from one IP within 15 minutes
  → `429` on `/admin/login` until the window passes. (A crude in-app limiter —
  see `docs/ARCHITECTURE.md` for why a robust one wants upstream support.)
- **Uploads**: images only (`png/jpg/jpeg/gif/webp`; no SVG — it can script),
  stored under a server-generated name, capped by `web_server_max_body_size`
  (10 MiB in `.wflcfg`).

## Built on

- **WFL** — the language, runtime, built-in web server, SQLite, and crypto.
- **Scribe** — Twig-style templating (vendored at `lib/scribe.wfl`).
- **WFL Design System** — brand tokens, fonts, and the logo mark (`static/ds/`).

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for how the pieces fit and the
WFL constraints that shaped the design.

## License

Apache-2.0. See [LICENSE](LICENSE).
