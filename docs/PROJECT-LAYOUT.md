# Project Layout — the standard shape of a WFL/Scriptorium project

**Status:** policy. Applies to **new projects**.
**Scriptorium itself is grandfathered** — this repo predates the policy and does
not follow it (`main.wfl` is one 51 KB file, themes use `sections/` +
`templates/`, tests live in `TestPrograms/`). Do not "fix" this repo to match
the doc as a drive-by; that is a separate, deliberate migration.

Every rule below states **what** and **why**. If the why no longer holds, the
rule is up for renegotiation — but change the doc, don't quietly ignore it.

**Read §8 first.** The module rules in §1 are designed against WFL's *documented*
behavior and have not been proven on a live runtime. §8 lists exactly what needs
testing before this document is binding.

---

## 0. The shape

```
<project>/
  README.md                  what this is, how to run it, where it deploys
  .wflcfg                    runtime config (read from CWD — see §5)
  main.wfl                   THE COMPOSITION ROOT — the only file that includes

  src/                       one concern per file, each exposing containers
    fileio.wfl                 file & path I/O
    data.wfl                   parsing, transforming, validating
    net.wfl                    HTTP, sockets, external calls
    store.wfl                  persistence (SQLite)
    render.wfl                 templating
    <concern>.wfl              …one file per concern, no "misc.wfl"

  plugins/                   optional containers implementing declared interfaces
    <plugin>.wfl

  themes/                    presentation (see §2)
    <name>/
      skeleton.html            the <html> document shell
      layout.html              THE ASSEMBLER — header → body → footer
      header/                  header region
      body/                    body region (one file per page kind)
      footer/                  footer region
      static/
        css/                   stylesheets
        js/                    external .js files only — never inline
        fonts/                 self-hosted woff2
        img/

  docs/                      all documentation (see §3)
  tests/                     all tests (see §4)
    unit/                      mirrors src/ one-to-one
    integration/

  data/                      GITIGNORED — data_dir: the database + uploads
```

Nothing lives at the project root except `README.md`, `.wflcfg`, `main.wfl`, and
ordinary repo furniture (`LICENSE`, `.gitignore`, CI config). If you are about to
add a loose file to the root, it belongs in one of the directories above.

---

## 1. WFL code — containers as modules

### 1.1 One concern per file

Each file in `src/` owns exactly one kind of work: file I/O, data processing,
network, persistence, rendering. The filename **is** the concern. There is no
`utils.wfl`, no `helpers.wfl`, no `misc.wfl` — those names are where concerns go
to hide.

*Why:* you should be able to answer "where does this belong?" without reading
any code, and "what will break if I change this?" without a search.

### 1.2 A module is a container, not a pile of actions

A file in `src/` defines one or more **containers** and nothing else at top
level. Consumers receive an *instance*; they never reach for a free-floating
action.

```wfl
create container FileStore:
    property root_dir: Text

    action read_text needs rel_path: Text:
        store full_path as root_dir with "/" with rel_path
        open file at full_path for reading as fh
        wait for store the_text as read content from fh
        close file fh
        return the_text
    end

    action write_text needs rel_path: Text, body_text: Text:
        store full_path as root_dir with "/" with rel_path
        open file at full_path for writing as fh
        wait for write content body_text into fh
        close file fh
    end
end
```

### 1.3 `main.wfl` is the composition root — and the only file that includes

**`main.wfl` is the only file in the project permitted to use `include from`.**
It includes each module once, instantiates the containers, wires them together,
and starts the program. Modules do not include each other. A module that needs
another module's capability receives an instance as a **parameter**.

```wfl
// main.wfl — the composition root
include from "src/fileio.wfl"
include from "src/data.wfl"
include from "src/store.wfl"
include from "src/net.wfl"

create new FileStore as files:
    root_dir is "./data"
end

create new SqliteStore as records:
    db_path is "./data/app.db"
end

// dependencies travel in as properties, never as a second include
create new HttpService as server:
    file_store is files
    record_store is records
end

server.start()
```

*Why — this is the load-bearing rule.* WFL's includes form a **tree, not a flat
namespace**, and an include that was already pulled in elsewhere is skipped: a
file only sees definitions from files *it* includes, transitively. So if
`net.wfl` and `store.wfl` both include `data.wfl`, one of them loses its
definitions. That is a **diamond**, and diamonds break.

"One file per concern" is a diamond generator — shared concerns are the whole
point of splitting them out. A star-shaped include graph with `main.wfl` at the
center makes diamonds structurally impossible: there is only ever one path to
any definition. Dependency injection is the escape hatch that lets the files
split without the includes colliding.

Scriptorium's own `main.wfl` is 51 KB partly for this reason — the router and
every handler share one scope. Note it was not the only reason: constraint #1 in
`ARCHITECTURE.md` (request values resolving only in the top-level loop) pushed
the same way, and *that* one was lifted in WFL 26.7.26.

> **Open question — verify before relying on this.** A module that declares a
> dependency as a typed property (`property file_store: FileStore`) has to know
> the name `FileStore`, which may mean including `fileio.wfl` — reintroducing the
> exact diamond this rule exists to prevent. Two candidate escapes, neither yet
> tested: declare the property untyped, or pass the dependency as an **action
> parameter** using the untyped `with parameters a and b` form instead of a
> declared property. See §8.

### 1.4 Plugins are containers behind an interface

A plugin contract is a `create interface`; a plugin is a container that
`implements` it. `main.wfl` chooses which implementation to instantiate.

```wfl
create interface Publisher

create container FilePublisher implements Publisher:
    property out_dir: Text

    action publish needs slug: Text, doc_body: Text:
        store out_path as out_dir with "/" with slug with ".html"
        open file at out_path for writing as fh
        wait for write content doc_body into fh
        close file fh
    end
end
```

*Why:* swapping an implementation becomes a one-line change in the composition
root, and a test can inject a fake without touching the module under test.

### 1.5 Naming

Avoid WFL reserved words in identifiers — `store`, `count`, `data`, `content`,
`status`, `header`, `file`, `port`, `error`, `find`, `one`, and friends are
keywords. Qualify them instead: `the_status`, `media_row`, `doc_content`,
`file_store`, `db_path`.

**Filenames are not identifiers**, so `src/data.wfl` and `src/store.wfl` are
fine even though `data` and `store` are keywords. But the container inside must
still be named legally — `RecordStore`, not `Store`; `DataPipeline`, not `Data`.
Name the file for the concern and the container for the thing.

---

## 2. Themes — header, body, footer

### 2.1 One theme per site, and the three regions are real directories

```
themes/<name>/
  skeleton.html      the <html> shell: <head>, asset links, <body> open/close
  layout.html        THE ASSEMBLER — includes header → drops body → includes footer
  header/
    header.html      REQUIRED — site identity + navbar (one bar, one <header>)
    …                additional header parts (masthead.html, nav.html …)
  body/
    home.html        REQUIRED — the feed
    post.html        REQUIRED — a single post
    page.html        REQUIRED — a single page
    notfound.html    REQUIRED — the 404
    …                more page kinds as the site grows
  footer/
    footer.html      REQUIRED — colophon + links
  static/
    css/<name>.css
    js/*.js
    fonts/*.woff2
    img/
```

**A page = header + body + footer, in that order.** All three are mandatory on
every page. A theme may add regions (a hero, a breadcrumb strip, a sidebar); it
may never drop one of the three.

`layout.html` is the **only** place the page is assembled. Body templates
describe a body and nothing else — they never emit a `<header>` or `<footer>` of
their own.

*Why:* the split is not cosmetic. Header and footer are written once and reused
on every page; the body is the only part that varies. Making the three regions
actual directories means the boundary is enforced by the filesystem instead of
by discipline, and a new page kind is obviously "a file in `body/`."

### 2.2 The four body template names are a contract

`home.html`, `post.html`, `page.html`, and `notfound.html` are named as string
literals by the request handlers, so a theme that renames or omits one breaks.
Keep those four stable.

Adding a *new* body template is not free: it needs a handler that names it. Body
templates are a fixed contract with the application, not a directory the theme
can extend on its own.

### 2.3 JavaScript lives in files

- **No inline `<script>` blocks.** JS goes in `static/js/*.js` and is loaded with
  `<script src>`.
- **No CDN.** Self-host everything — scripts, fonts, icons. A homelab site must
  not depend on unpkg or Google Fonts being reachable.
- **The site must work with JavaScript disabled.** Server-rendered HTML is the
  product; JS is progressive enhancement only. (`news.starnet` ships with zero
  `<script>` tags and nine self-hosted woff2 fonts — that is the bar.)

*Why:* inline script can't be cached, can't be linted, can't be
content-security-policied, and can't be diffed usefully. A CDN is an outage you
don't control. And a server-rendered CMS that white-screens without JS has
thrown away its main advantage.

### 2.4 Static assets are namespaced

Theme assets live under `themes/<name>/static/` and are served under a path that
includes the theme name (`/assets/<name>/…`). Nothing goes in a shared static
root.

*Why:* two themes coexisting during a redesign must not fight over `theme.css`,
and rollback should never mean "restore the right version of a shared file."

---

## 3. Documentation — `docs/`

All documentation lives in `docs/`. The only Markdown at the project root is
`README.md`, which stays short and points into `docs/`.

Required for any project that will be deployed:

| File | Answers |
|---|---|
| `ARCHITECTURE.md` | How the pieces fit, and which language constraints shaped them |
| `OPERATIONS.md` | How it deploys, where it runs, how to restart, how to roll back |
| `THEMING.md` | Theme contract — required for anything with a `themes/` directory |

Record **constraints and their consequences**, not just descriptions. The most
valuable paragraph in Scriptorium's `ARCHITECTURE.md` is the list of WFL
limitations that forced the design — it turns "this is weird" into "this is
deliberate."

---

## 4. Tests — `tests/`

```
tests/
  unit/          one file per src/ module, same name + _test
  integration/   boot, routing, auth, end-to-end behavior
  fixtures/      sample data (optional)
```

**`tests/unit/` mirrors `src/` one-to-one.**

| Module | Test |
|---|---|
| `src/fileio.wfl` | `tests/unit/fileio_test.wfl` |
| `src/data.wfl` | `tests/unit/data_test.wfl` |
| `src/net.wfl` | `tests/unit/net_test.wfl` |
| `src/store.wfl` | `tests/unit/store_test.wfl` |

Rules:

- A module without a test file is not done.
- No test code in `src/`. No production code in `tests/`.
- Use WFL's built-in `describe` / `test` / `expect`.
- Unit tests inject fakes through the container constructor (§1.4) — they do not
  touch the real filesystem, database, or network.
- Integration tests may use real resources, but only ephemeral ones
  (`sqlite::memory:`, a temp directory).
- CI must **fail on a failing test**, not merely on a non-zero exit code. A test
  program that prints "FAIL" and exits 0 is a false green.

*Why the mirror:* coverage gaps become visible by `ls` instead of by tooling, and
"which tests do I run after changing `net.wfl`?" has one obvious answer.

---

## 5. Configuration and state

- **`.wflcfg` at the project root.** It is read from the **current working
  directory**, so the service must be started with the project root as its CWD.
  Say so explicitly in the systemd unit (`WorkingDirectory=`).
- **All mutable state under `data/`**, reached through a `data_dir` key in
  `.wflcfg`. The database and uploads never live in the application tree.

  ⚠️ **`data_dir` is an application convention, not a WFL runtime feature.** The
  runtime reads its own keys from `.wflcfg` (`timeout_seconds`,
  `web_server_bind_address`, …) and ignores this one. Scriptorium implements it
  by reading `.wflcfg` itself at boot and parsing the key. A new project inherits
  nothing here — it must do the same read, in its config module, at startup.
- **`data/` is gitignored.** The repo holds the application; the data directory
  holds the site. A redeploy must not be able to destroy content.
- **Secrets never enter the repo.** They live in vault (`secret/<project>/…`),
  with the workspace `.env` as the documented fallback.

*Why:* this is the line between *replaceable* and *precious*. If it's in git it
can be rebuilt from scratch; if it's in `data/` it must be backed up. Anything
that blurs that line eventually eats someone's content on a redeploy.

---

## 6. Engine dependencies — pin, never patch

If the project builds on an upstream engine (Scriptorium, Scribe, a shared
library):

- **Pin it.** Use a git submodule or a recorded commit/version. Write the version
  down in `docs/OPERATIONS.md`.
- **Never patch a deployed clone.** A local edit to a vendored engine is erased
  by the next `git pull`, and the ritual of re-applying it after every update is
  a bug waiting for the one time someone forgets.
- **Needed behavior goes upstream.** If the engine can't do what the project
  needs, fix the engine and bump the pin.

*Why — this is not hypothetical.* `news.starnet` runs a hand-patched clone of
Scriptorium because upstream `render_public` hardcodes
`themes/base/templates/`. The documented update procedure literally reads
"`git pull` … then RE-APPLY the render.wfl theme patch, or the theme reverts to
base." The patch has outlived two theme generations and has never actually been
re-applied — because the clone has never been refreshed. It is a loaded gun, not
a proven ritual: the first routine `git pull` silently reverts the live site to
the base theme.

### 6.1 What the engine owes this layout

Good news — this is **one change, not three**. Scribe's `{% extends %}` and
`{% include %}` already accept arbitrary repo-relative paths, and the base theme
already splits `sections/` from `templates/`, so region directories (`header/`,
`body/`, `footer/`) work today for every template except the **entry** template.
That one is pinned by a single hardcoded prefix in `render_public`.

So the engine needs exactly one thing:

> **Make the entry-template prefix configurable** — resolve
> `<theme_root>/<theme>/body/<name>.html` from the `theme` setting and a
> configurable theme root, instead of the literal `themes/base/templates/`.

That single change delivers theme selection, region-aware paths, and
out-of-tree themes together, and retires the `news.starnet` patch.

Until it lands, a new project either carries the engine as a fork with the change
committed (so an update is a merge, not a re-applied patch), or defines its own
render module in `src/render.wfl` per §1.

---

## 7. Checklist for a new project

- [ ] Root holds only `README.md`, `.wflcfg`, `main.wfl`, repo furniture
- [ ] `main.wfl` is the only file with `include from`
- [ ] Every `src/` file is one concern and exposes containers
- [ ] Dependencies are passed as parameters, never re-included
- [ ] Plugin points are declared as interfaces
- [ ] Theme has `header/`, `body/`, `footer/`, plus `skeleton.html` + `layout.html`
- [ ] Zero inline `<script>`, zero CDN references, site works with JS off
- [ ] `docs/` has `ARCHITECTURE.md`, `OPERATIONS.md`, and `THEMING.md`
- [ ] `tests/unit/` mirrors `src/` with no gaps; CI fails on a failing test
- [ ] `data_dir` read at startup; `data/` gitignored; no secrets in the repo
- [ ] Engine pinned and unpatched; version recorded

---

## 8. Unproven — verify before treating this as binding

This policy is designed against WFL's documented behavior, not against a working
reference implementation. The following are **open**, and §1 does not stand until
they are settled on a live runtime. Resolve them, then delete this section.

1. **Do diamond includes still break?** `ARCHITECTURE.md` catalogues that
   constraint against **WFL 26.7.25** and explicitly marks three of its siblings
   as lifted in 26.7.26. The include constraint carries no such note, but nothing
   has retested it. The fleet now runs 26.7.46–26.7.52. **All of §1.3 rests on
   this.** If diamonds now work, the composition-root rule becomes a style
   preference rather than a necessity.

2. **Does dependency injection actually escape the diamond?** A container-typed
   property (`property file_store: FileStore`) may force the consuming module to
   include the provider, recreating the diamond. Test whether an untyped
   property, or passing the instance as an untyped action parameter, avoids it.

3. **Is the container system real enough to build on?** `create container`,
   `create interface`, `implements`, and `needs`-style typed parameters appear
   **zero times** across Scriptorium and Scribe — every line of production WFL in
   house uses `define action called X with parameters a and b`. This policy
   prescribes a module system with no production mileage. Build one small module
   plus its unit test end-to-end before committing the fleet to it.

4. **Can an interface declare its members?** `create interface Publisher`
   declares no actions, and no documented syntax adds any. If `implements` is an
   unchecked marker, a "plugin contract" is a naming convention — still useful,
   but say so honestly rather than implying enforcement.

5. **Does `wfl` exit non-zero on a failing test?** §4 requires CI to fail on a
   failing test. Nothing documents the test runner's exit codes, and Scriptorium
   has no test workflow to copy. If exit codes are unreliable, CI must assert on
   output instead.

6. **Does the runtime read `.wflcfg` from CWD, or relative to the entry file?**
   Confirmed for the application-level `data_dir` read; unconfirmed for the keys
   the `wfl` binary consumes. `WorkingDirectory=` is correct either way, but the
   §5 wording depends on it.
