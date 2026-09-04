# Scriptorium Theme Guidelines

A Scriptorium site is built from **sections** — self‑contained pieces of a page —
and every page is **assembled** by snapping those sections together in a fixed
order. This is the whole mental model:

> **A page = header + body + footer.**
> The **header** (site identity + navbar — they are one bar) and the **footer**
> are reusable *section* files, written once and reused on every page. The
> **body** is the one part that changes per page. An **assembler** template
> stitches the three together.

Header, body, and footer are **non‑negotiable** — every page has all three, in
that order. A theme may add more sections (a hero masthead, a breadcrumb strip,
a sidebar), but it may never drop one of the three.

The `themes/base/` theme is the reference implementation. It is deliberately
small — read it alongside this doc.

> **Two folder shapes are supported.** This doc describes Scriptorium's own
> themes: `sections/` (header + footer) plus `templates/` (assembler + bodies).
> Per [`PROJECT-LAYOUT.md`](PROJECT-LAYOUT.md), a **new** project makes the
> three regions literal directories — `header/`, `body/`, `footer/` — with
> `skeleton.html` and `layout.html` at the theme root. The mental model is
> identical; only the folders move. `render_public` resolves a body template as
> `<theme_root>/<theme>/body/<name>.html`, then
> `<theme_root>/<theme>/templates/<name>.html`, then the base theme, so either
> shape works today and a theme can override only the pages it cares about.
> Pick the theme with `theme` / `theme_root` in `.wflcfg`.

---

## 1. The parts

```
themes/<name>/
  sections/                 the reusable section library
    header.html   REQUIRED  site identity + navbar   → <header class="site-header">
    footer.html   REQUIRED  colophon + links         → <footer class="site-footer">
  templates/
    skeleton.html REQUIRED  the <html> document shell (head, asset links)
    layout.html   REQUIRED  THE ASSEMBLER — header → body → footer
    home.html     REQUIRED  body: the post feed          }
    post.html     REQUIRED  body: a single post          }  each supplies only
    page.html     REQUIRED  body: a single page          }  the body; the
    notfound.html REQUIRED  body: the 404 page           }  assembler wraps it
```

- **Sections** (`sections/*.html`) are the shared building blocks. `header.html`
  and `footer.html` are required; add more section files as your theme grows.
- **The assembler** (`templates/layout.html`) is the *only* place the page is
  put together. It includes the header section, drops in the body, and includes
  the footer section — in that order.
- **Body templates** (`home.html`, `post.html`, …) each describe *one* body.
  They extend the assembler and fill a single content slot; they never render a
  header or footer of their own.

Keep the file names above stable — the router calls the body templates by name
(`render_public of "home.html" and ctx`). You are free to add *more* sections
and templates.

Everything renders through **Scribe** (`lib/scribe.wfl`): `{% extends %}`,
`{% block %}`, `{% include %}`, `{% for %}`, `{% if %}`, filters (`| markdown`,
`| truncate`, `| default`, `| striptags`), and auto‑escaping.

### The `markdown` filter

`{{ post.body_markdown | markdown }}` renders a small, safe Markdown subset —
HTML in the source is escaped first, so authored markup can never inject tags:

- **Headings** (`# …` through `###### …`), **paragraphs**, and **unordered
  lists** (a `-` or `*` followed by a space).
- **Blockquotes** — lines beginning with `>` (followed by a space) are gathered
  into a `<blockquote>` and their contents rendered as Markdown (so `> **Note:**
  …` bolds inside the quote). Consecutive `>` lines join; a `>` on its own line
  starts a new paragraph within the quote.
- **Fenced code blocks** — text between ```` ``` ```` fences becomes
  `<pre><code>…</code></pre>` with its contents escaped and inline Markdown
  left untouched. An optional info string (```` ```rust ````) is accepted.
- **Inline**: `**bold**`, `*italic*`, `` `code` ``, and `[text](url)` links
  (dangerous URL schemes such as `javascript:` are neutralised).

The filter returns **safe** (already-escaped) HTML. Text filters that subset
that output — `striptags`, `truncate`, `trim`, `first`, `last` — preserve the
safe marker, so an excerpt chain like
`{{ post.body_markdown | markdown | striptags | truncate(180) }}` is **not**
escaped a second time (no `&#39;` → `&amp;#39;` corruption).

---

## 2. How a page is assembled

Three files do the work. Copy them into a new theme and the assembly already
works; then style with your own CSS.

**`sections/header.html`** — the header section. Site identity + the navbar
(same bar). Written once, reused everywhere.

```html
{# SECTION: header — site identity + navbar. One <header> per page. #}
<header class="site-header">
  <div class="site-header__inner">
    <a class="brand" href="/">
      <img src="{{ site.asset_base }}/ds/assets/wfl-mark.svg" alt="">
      <span class="brand__name">{{ site.title }}</span>
    </a>
    <nav class="site-nav">
      <a href="/">Home</a>
      {% for p in site.nav %}<a href="/page/{{ p.slug }}">{{ p.title }}</a>{% endfor %}
    </nav>
  </div>
</header>
```

**`sections/footer.html`** — the footer section.

```html
{# SECTION: footer — colophon + links. One <footer> per page. #}
<footer class="site-footer">
  <div class="wrap">
    <span>© {{ site.year }} {{ site.title }}</span>
    <span>Built with WFL · Scriptorium</span>
  </div>
</footer>
```

**`templates/layout.html`** — the assembler. The single place the three sections
are snapped together, in order.

```html
{% extends "themes/base/templates/skeleton.html" %}
{% block body %}
{% include "themes/base/sections/header.html" %}   {# 1. header section #}
<main class="site-body wrap">                        {# 2. body           #}
{% block content %}{% endblock %}
</main>
{% include "themes/base/sections/footer.html" %}   {# 3. footer section #}
{% endblock %}
```

**A body template** just fills the body slot — no header, no footer:

```html
{% extends "themes/base/templates/layout.html" %}
{% block title %}{{ post.title }} · {{ site.title }}{% endblock %}
{% block content %}
  … this page's markup only …
{% endblock %}
```

A body template that renders its own `<header>`/`<footer>`, or that skips
`{% extends "…/layout.html" %}`, has broken the assembly — it is not conformant.

### The document shell

`templates/skeleton.html` owns `<head>` and links the two required stylesheets
(Design System first, theme second). The assembler extends it:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{{ site.title }}{% endblock %}</title>
  <link rel="icon" href="{{ site.asset_base }}/ds/assets/wfl-mark.svg">
  <link rel="stylesheet" href="{{ site.asset_base }}/ds/styles.css">   {# 1. Design System tokens #}
  <link rel="stylesheet" href="{{ site.asset_base }}/theme.css">       {# 2. this theme's styles   #}
</head>
<body>
{% block body %}{% endblock %}
</body>
</html>
```

---

## 3. Context every section can rely on

`app/render.wfl` injects a `site` map into every public render, so any section
or body template can read it:

| Variable | Type | Meaning |
|---|---|---|
| `site.title` | text | Site title (from settings) |
| `site.tagline` | text | Site tagline |
| `site.nav` | list | Published pages for the navbar; each has `.slug` and `.title` |
| `site.user` | map / nothing | The signed‑in user, or absent for anonymous visitors |
| `site.is_admin` | bool | Whether the current user is an admin |
| `site.year` | text | Current year (for the footer) |
| `site.asset_base` | text | Base URL for static assets — always `/assets` |

Per‑page content is passed in the render call: `posts` + `pagination` for
`home.html`, `post` for `post.html`, `page` for `page.html`. Always build asset
URLs from `site.asset_base` — never hard‑code `/assets`.

---

## 4. Styling: Design System first, theme second

Two stylesheets, in this order:

1. **`ds/styles.css`** — the **WFL Design System**: brand tokens only (color
   ramps, spacing scale, typography, radii, shadows, motion). Do **not** edit
   `static/ds/` from a theme — it is shared with the admin panel and `wfl-web`.
2. **`theme.css`** — *your* theme. Consume the tokens; never hard‑code a hex, a
   pixel gap, or a font stack a token already provides.

```css
/* good — speaks in tokens */
.site-header { background: var(--surface-base); border-bottom: 1px solid var(--border-subtle); }

/* bad — bakes in values the Design System already owns */
.site-header { background: #10221F; border-bottom: 1px solid #ffffff14; }
```

**Sticky footer.** Because the footer section is non‑negotiable, it must sit at
the bottom of the viewport even on short pages. The base theme does this with a
flex column on `<body>` and a growing body:

```css
body        { display: flex; flex-direction: column; min-height: 100vh; }
.site-body  { flex: 1 0 auto; }   /* body grows to fill the gap */
.site-footer{ flex-shrink: 0; }   /* footer keeps its height    */
```

---

## 5. Authoring a new theme — checklist

1. Copy `themes/base/` to `themes/<name>/`, and set `theme = <name>` in
   `.wflcfg` (plus `theme_root` if the theme lives outside `themes/`).
2. Keep the required file names (§1). Point the `{% extends %}` / `{% include %}`
   paths at `themes/<name>/…` — Scribe resolves those relative to the working
   directory, not to the including file.
3. Confirm the assembler puts the sections in order — **header → body → footer**
   — on **every** body template, including `notfound.html`. Exactly one
   `<header>`, one `<main class="site-body">`, one `<footer>` per page.
4. Put shared page furniture in `sections/`; keep body templates body‑only.
5. Style in `theme.css` with Design System tokens; keep the sticky footer.
6. Read only from the `site.*` context (§3) plus each template's own content.

If all six hold, the theme is conformant. Ship it.

---

## 6. Relationship to `wfl-web`

The public marketing site,
[`wfl-web`](https://github.com/WebFirstLanguage/wfl-web), uses the same Scribe
engine, the same WFL Design System, and this **same section‑assembly model**:
its `templates/base.html` is the assembler, and it includes
`templates/sections/header.html` → `<main class="site-body">` →
`templates/sections/footer.html`. It is a second, hand‑styled conformant theme
living in its own repo. Any change to what a section *means* here should stay in
step with `wfl-web`.
