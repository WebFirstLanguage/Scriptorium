# Scriptorium Theme Guidelines

This is the contract every Scriptorium theme must satisfy. It exists so that a
theme is a *swappable* unit — you can drop in a new one without touching the
router, the data layer, or the request loop — and so that every theme, no matter
who writes it, presents the same three structural regions to a reader.

> **The one rule to remember:** every page a theme renders has a **header**, a
> **body**, and a **footer** — in that order. These three regions are
> non‑negotiable. A theme may add more (sidebars, hero mastheads, breadcrumbs,
> a sub‑nav), but it may never drop one of the three.

The `themes/base/` theme is the reference implementation of everything below.
When in doubt, read it — it is deliberately small.

---

## 1. What a theme is

A theme is a directory under `themes/<name>/`:

```
themes/<name>/
  templates/
    skeleton.html      REQUIRED  the <html> document shell
    layout.html        REQUIRED  header → body → footer, in that order
    home.html          REQUIRED  the home feed (list of posts)
    post.html          REQUIRED  a single post
    page.html          REQUIRED  a single standalone page
    notfound.html      REQUIRED  the 404 page
  partials/
    header.html        REQUIRED  the header region (see §3)
    footer.html        REQUIRED  the footer region (see §3)
```

`app/render.wfl` resolves public templates under `themes/base/templates/`. A
theme is selected by pointing `render_public` at its directory; the base theme
is the default. Keep the template **file names** above stable — the router calls
them by name (`render_public of "home.html" and ctx`, etc.). You are free to add
*more* templates and partials beyond this list.

Themes render through **Scribe** (the vendored Twig‑style engine in
`lib/scribe.wfl`). You get `{% extends %}`, `{% block %}`, `{% include %}`,
`{% for %}`, `{% if %}`, filters (`| markdown`, `| truncate`, `| default`,
`| striptags`), and auto‑escaping.

---

## 2. The three regions (non‑negotiable)

Every rendered page is composed of exactly these three regions, top to bottom:

| Region | What it is | Where it lives | Landmark |
|---|---|---|---|
| **Header** | Site identity + primary navigation. The reader's "you are here / go elsewhere". | `partials/header.html` | `<header class="site-header">` |
| **Body** | The page's own content — the *only* region that changes between page types. | `{% block content %}` inside `<main class="site-body">` | `<main class="site-body">` |
| **Footer** | Colophon, secondary links, legal/attribution. | `partials/footer.html` | `<footer class="site-footer">` |

Rules:

1. **All three are always present.** Even the 404 page has a header and footer.
2. **Order is fixed:** header, then body, then footer.
3. **One landmark each.** Exactly one `<header>`, one `<main>`, one `<footer>`
   per page — this is what keeps the theme accessible to screen readers and
   keyboard users (`<main>` is the "skip to content" target).
4. **The header and footer are partials**, included by `layout.html`. They do
   not vary by page type, so they are defined once and reused. Only the **body**
   differs per template — that is the whole point of the split.

### Why partials, not one big layout

Putting the header and footer in `partials/` (rather than inline in
`layout.html`) is what makes them *regions* rather than markup. It means:

- a page template can never accidentally ship without one of them;
- restyling the header touches one file, not every layout;
- a second theme can reuse the base header by including it, or replace it by
  supplying its own `partials/header.html`.

---

## 3. The composition contract

The three templates that wire the regions together. Copy these verbatim into a
new theme and you already satisfy the contract; then style with your own CSS.

**`templates/skeleton.html`** — the document shell. Owns `<head>`, links the two
required stylesheets (Design System first, theme second), and exposes a single
`{% block body %}`.

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

**`templates/layout.html`** — the region shell. This is where the
header → body → footer order is enforced. Every content template extends it.

```html
{% extends "themes/base/templates/skeleton.html" %}
{% block body %}
{% include "themes/base/partials/header.html" %}   {# REGION 1: header #}
<main class="site-body wrap">                        {# REGION 2: body   #}
{% block content %}{% endblock %}
</main>
{% include "themes/base/partials/footer.html" %}   {# REGION 3: footer #}
{% endblock %}
```

**Content templates** (`home.html`, `post.html`, `page.html`, `notfound.html`)
extend `layout.html` and fill *only* the body:

```html
{% extends "themes/base/templates/layout.html" %}
{% block title %}{{ post.title }} · {{ site.title }}{% endblock %}
{% block content %}
  … page-specific markup only; no header, no footer …
{% endblock %}
```

A content template that renders its own `<header>` or `<footer>`, or that skips
`{% extends "…/layout.html" %}`, is **not conformant** — it has broken the
region contract.

---

## 4. Context every template can rely on

`app/render.wfl` injects a `site` map into every public render. A conformant
theme may read these and nothing else from global scope:

| Variable | Type | Meaning |
|---|---|---|
| `site.title` | text | Site title (from settings) |
| `site.tagline` | text | Site tagline |
| `site.nav` | list | Published pages for the nav; each has `.slug` and `.title` |
| `site.user` | map / nothing | The signed‑in user, or absent for anonymous visitors |
| `site.is_admin` | bool | Whether the current user is an admin |
| `site.year` | text | Current year (for the footer colophon) |
| `site.asset_base` | text | Base URL for static assets — always `/assets` |

Per‑template content is passed in the render call: `posts` + `pagination` for
`home.html`, `post` for `post.html`, `page` for `page.html`. Use
`site.asset_base` for **every** asset URL — never hard‑code `/assets`, so a
theme keeps working if the mount point moves.

---

## 5. Styling: use the Design System, add a theme layer

Two stylesheets, in this order:

1. **`ds/styles.css`** — the **WFL Design System**. Brand tokens only: the color
   ramps, spacing scale, typography, radii, shadows, motion. Do **not** edit the
   files under `static/ds/` from a theme — they are shared with the admin panel
   and with `wfl-web`.
2. **`theme.css`** — *your* theme. Consume the tokens; never hard‑code a hex,
   a pixel gap, or a font stack that a token already provides.

```css
/* good — speaks in tokens */
.site-header { background: var(--surface-base); border-bottom: 1px solid var(--border-subtle); }
.post-card  { border-radius: var(--radius-xl); padding: var(--space-5) var(--space-6); }

/* bad — bakes in values the Design System already owns */
.site-header { background: #10221F; border-bottom: 1px solid #ffffff14; }
```

Key token families (full set in `static/ds/tokens/*.css`): `--surface-*`,
`--text-*`, `--border-*`, `--accent*`, `--space-*`, `--radius-*`, `--font-*`,
`--text-*` (sizes), `--leading-*`.

### The sticky‑footer requirement

Because the footer is non‑negotiable, it must sit at the **bottom of the
viewport even on short pages** — a lone header floating over a blank screen is a
broken footer. Achieve it with a flex column on `<body>` and a growing body
region (the base theme already does this):

```css
body        { display: flex; flex-direction: column; min-height: 100vh; }
.site-body  { flex: 1 0 auto; }   /* body grows to fill the gap  */
.site-footer{ flex-shrink: 0; }   /* footer keeps its height     */
```

---

## 6. Authoring a new theme — checklist

1. Copy `themes/base/` to `themes/<name>/`.
2. Keep the required file names (§1). Update the `{% extends %}` /
   `{% include %}` paths to point at `themes/<name>/…`.
3. Confirm the three regions render, in order, on **every** template — including
   `notfound.html`. Exactly one `<header>`, one `<main class="site-body">`, one
   `<footer>` per page.
4. Style in `theme.css` using Design System tokens only. Keep the sticky footer.
5. Read only from the `site.*` context in §4 plus each template's own content
   variable.
6. Check it in a browser at a narrow width — the header nav and footer columns
   must degrade gracefully (see the `@media` blocks in the base theme).

If all six hold, the theme is conformant. Ship it.

---

## 7. Relationship to `wfl-web`

The public marketing site, [`wfl-web`](https://github.com/WebFirstLanguage/wfl-web),
runs the same Scribe engine and the same WFL Design System, and it follows this
same three‑region contract — its `templates/base.html` composes
`partials/header.html` → `<main class="site-body">` → `partials/footer.html`.
It is a second, hand‑styled conformant "theme" living in its own repo. Any change
to what a region *means* here should stay in step with `wfl-web`.
