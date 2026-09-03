# Install wizard — design

Replace Scriptorium's console-seeded first-run admin with a one-page in-browser
installer. First boot no longer prints a random password. The operator opens the
site, fills in site title, tagline, admin username, and password (plus confirm),
and lands in `/admin` already signed in.

This repository stays on its existing layout. Handlers remain in `main.wfl`.
Includes still form a tree (`util ← db ← auth ← render`). This work must not
retrofit the repo to `docs/PROJECT-LAYOUT.md`.

## Goal

A fresh database has no users and no `installed` setting. Every public and
admin URL except static assets redirects to `/install` until setup finishes.
Completing the form creates the first admin, writes site title and tagline,
sets `installed` to `yes`, starts a session, and 303s to `/admin`.

Existing sites that already have users never see the wizard: boot backfills
`installed=yes` when users exist and the flag is missing (live upgrades, and
recovery if the process crashed after `user_create` but before the flag write).

## One-page installer

`GET /install` renders `admin/templates/install.html` through `render_admin`.
The page clones the login card (`body.admin.admin--auth`, `auth-card` plus
`auth-card--wide` so the extra fields fit), brand mark, title “Set up your
site”, short subcopy, optional flash, and a POST form to `/install`.

Fields:

| Name | Notes |
|---|---|
| `site_title` | Required after trim |
| `site_tagline` | Optional; not validated |
| `username` | Required after trim; autocomplete `username` |
| `password` | Required; not trimmed; autocomplete `new-password` |
| `password_confirm` | Must equal `password`; not trimmed; autocomplete `new-password` |
| `csrf_token` | Hidden; double-submit cookie (see Security) |

Validation errors re-render the form with a flash. Title, tagline, and
username are preserved. Passwords are never echoed.

On success the new admin is signed in and sent to `/admin`.

## `installed` setting

A `settings` row `installed` / `yes` is the lock. Absence or any other value
means the wizard is still open.

Helpers in `app/db.wfl`:

- `install_is_done(conn)` — `setting_get` of `"installed"` equals `"yes"`
- `install_mark_done(conn)` — `setting_set` `"installed"` / `"yes"`
- `install_apply(conn, title, tagline, username, password_hash)` — `user_create`
  as role `admin`, then `setting_set` title and tagline, then
  `install_mark_done`. Returns `yes` / `no`. Unique-username failure is caught
  with `try` the same way `handle_user_create` does; settings and the flag are
  not written in that case.

Pure validation lives in `app/util.wfl` (`install_validate`). Trim title and
username with WFL `trim`; do not trim passwords.

| Condition | Message |
|---|---|
| Empty title (after trim) | `Site title is required.` |
| Empty username (after trim) | `Username is required.` |
| Empty password (not trimmed) | `Password is required.` |
| Password ≠ confirm | `Passwords do not match.` |
| Otherwise | `""` |

## Boot backfill

After migrate and `setting_default`s, **instead of** the random-admin seed: if
not `install_is_done` and `user_count > 0`, call `install_mark_done`. First run
with zero users leaves the flag unset so the dispatch lock engages.

## Dispatch lock

In `dispatch`, before the existing `route`:

1. Always serve `/assets/*` (the installer needs CSS, fonts, and the brand mark).
2. If **not** installed: `/install` → GET/POST handlers; every other path →
   303 `/install`.
3. If installed: `/install` (GET or POST) → 303 `/` without processing a late
   POST; otherwise the existing public and admin routes.

Handlers stay in `main.wfl` next to login. They share one scope with the
router; splitting them out would break the include tree.

## Security

Same pattern as `/admin/login`:

- **CSRF.** GET mints a token, sets
  `csrf=…; HttpOnly; Path=/install; SameSite=Lax; Max-Age=600`, and embeds it
  as `csrf_token`. POST compares `login_csrf_from_cookie` against the form
  field with `constant_time_equals`.
- **Rate limit.** Existing `login_attempts_*` (10 failures / 15 minutes from
  one IP → 429) before credentials are applied. A successful install clears
  the counter for that IP.
- **Re-check.** POST re-reads `install_is_done` so a late or double submit
  does not create a second admin.

After `install_apply` succeeds: `login_attempts_clear`, `session_start` for
the new user, 303 `/admin` with the session cookie. Apply failure (taken
username) re-renders with `That username is already taken.`

## Out of scope

`.wflcfg` (bind, TLS, `data_dir`), theme picker, first welcome post, password
minimum length, an HTTP integration suite, and splitting `main.wfl` or
otherwise migrating this repo onto `docs/PROJECT-LAYOUT.md`.
