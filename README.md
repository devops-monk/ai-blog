# AI Blog

> How AI systems actually work in production — models, retrieval, agents, evaluation, inference.

Source for **[ai.devops-monk.com](https://ai.devops-monk.com/)**.

This is a working template, not an empty scaffold: the layouts, CSS, tooling and CI are the ones running [system-design.devops-monk.com](https://system-design.devops-monk.com/), rebranded and stripped of that site's content. Everything below already works — the first article is the only thing missing.

---

## What is already built

| | |
|---|---|
| **Diagrams** | Mermaid 11, client-side, themed to match the site in light and dark. Click any diagram to open it full screen with wheel/pinch zoom and drag to pan. |
| **Listen to this article** | Browser text-to-speech with a segmented speed control, section progress and paragraph highlighting. Skips code blocks and interactive widgets. |
| **Series navigation** | Previous/next chapter and a "Part 1 · Chapter 3 of 9" badge, driven by explicit front matter rather than publication date. |
| **Social cards** | `og:image`, Twitter card, canonical link and JSON-LD, all resolving to a generated 1200×630 JPEG per article. |
| **Search** | Fuse.js over a `index.json` built by Hugo. |
| **Dark mode** | Token-based, remembered in `localStorage`, and diagrams re-render when it flips. |
| **RSS** | Posts only, hand-written descriptions, cover images attached. |
| **Cover art** | `tools/gen_covers.py` — a shared template with a hand-drawn SVG motif per article. |

`content/posts/2026/hello-transformers.md` is a `draft: true` reference article that demonstrates every one of these. Read it first, then copy it.

---

## Tech stack

| Layer | Tool |
|---|---|
| Static site generator | [Hugo](https://gohugo.io/) **0.160.1 extended** |
| Theme | Wellington, heavily customised via `layouts/` |
| Diagrams | [Mermaid 11](https://mermaid.js.org/), rendered client-side |
| Hosting | GitHub Pages (`gh-pages` branch) |
| DNS | Porkbun (CNAME → `devops-monk.github.io`) |
| CI/CD | GitHub Actions, auto-deploy on push to `main` |

> **The Hugo version matters.** `layouts/partials/post-cover.html` uses `hash.FNV32a`, which requires Hugo ≥ 0.129. An older version fails with `function "hash" not defined`. `.github/workflows/deploy.yml` pins it — keep it in sync with local.

---

## Local development

```bash
brew install hugo          # macOS — must be the extended build
hugo server -D             # http://localhost:1313, -D includes drafts
hugo --minify              # production build into public/
```

---

## Writing an article

```bash
hugo new posts/2026/my-topic.md
```

The archetype fills in the front matter:

```markdown
---
title: "How a Transformer Actually Predicts"
image: /images/articles/hello-transformers.webp
toc: true
date: 2026-01-01T10:00:00+00:00
description: "One sentence that sells the article."
tags: ["llm", "transformers", "inference"]
categories: ["Fundamentals"]
url: /2026/01/hello-transformers/
series: "Part 1 — Foundations"
series_order: 1
draft: true
---
```

`description` is not decoration — the RSS feed, the search index, the OpenGraph card and the JSON-LD all read it. Write it deliberately.

**Categories:** `Fundamentals` for concepts and building blocks, `Deep Dives` for full system walkthroughs.

**`series` / `series_order`** drive the previous/next chapter links. The parts are chained into one continuous reading order by `params.series_sequence` in `config.toml`, so the last chapter of one part leads into the first of the next. Inserting a chapter means renumbering the ones after it — the order is explicit on purpose, because date-based `.PrevInSection` wanders. Keep `series_order` in step with the `PART n · CH n` badge baked into the cover.

### Diagrams

Fenced ` ```mermaid ` blocks are rendered by `layouts/partials/head.html`.

> **Gotcha: a semicolon inside a mermaid label silently kills the whole diagram.** Mermaid treats `;` as a statement separator, so `A-->>B: joined; you are the leader` truncates the line and the diagram renders nothing — with no error on the page. Use a dash or comma.
>
> Because a failed diagram is invisible, always check the **rendered count against the source count**:
> ```bash
> grep -c '^```mermaid' content/posts/2026/my-post.md   # source blocks
> # rendered: count the ids mermaid assigns, NOT `<pre class="mermaid"...><svg`.
> # The <pre> carries the source in data-src, and that source contains `-->`,
> # so any regex ending the tag at the first `>` matches nothing.
> chrome --headless --dump-dom "$URL" | grep -c 'id="mermaid-svg-'
> ```

### Interactive widgets

Self-contained HTML + CSS + JS in the article. Styles go in `static/assets/css/custom-styles.css` under a short per-widget class prefix (`tok-` in the example article).

> **Gotcha: no blank lines inside a raw HTML block.** Goldmark ends an HTML block at the first blank line, so anything after it is parsed as Markdown and the widget breaks apart.

Every widget must style its dark variant under `[data-theme="dark"]` and collapse to one column under `@media (max-width: 40em)`. Class names ending in `-demo`, `-calc`, `-sim`, `-explorer` or `-check` are excluded from the text-to-speech narration.

### Cover images

```bash
python3 tools/gen_covers.py                    # rebuild all
python3 tools/gen_covers.py hello-transformers # rebuild one
python3 tools/gen_social.py                    # then regenerate share cards
```

Write an `art_*()` function returning a 640×420 SVG, add an entry to `COVERS`. Three motifs ship as examples: `art_tokens`, `art_embedding`, `art_attention`.

Requires headless Chrome and `cwebp` (`brew install webp`).

**Always run `gen_social.py` after a cover change.** The covers are 1600×640 WebP; networks want 1.91:1 JPEG, and LinkedIn has never reliably rendered WebP. `gen_social.py` scales each cover to 1200×480 on a 1200×630 canvas and fills the bands with a blurred copy so there is no seam.

---

## Custom layouts

| File | Purpose |
|---|---|
| `index.html` | Home page — `all-posts.html`, cover cards and pagination |
| `page/single.html` | Clean layout for `type: page` (About, Contact, Guide) — no post chrome |
| `_default/single.html` | Article layout — hero cover, TOC, share, TTS, series nav, related |
| `_default/rss.xml` | Feed: posts only, front-matter descriptions, cover images attached |
| `index.json` | Search index for the Fuse.js client-side search |
| `partials/social-meta.html` | `og:image` + Twitter card + canonical — Hugo's internal OpenGraph template reads `.Params.images`, which this site never sets |
| `partials/social-image.html` | Resolves the share card URL; one source of truth for the meta tags and the JSON-LD |
| `partials/site-schema.html` | JSON-LD, built with `dict`/`jsonify` so a quote in a title cannot break it |
| `partials/series-badge.html` | "Part 1 · Chapter 3 of 9" under the title |
| `partials/series-nav.html` | Previous/next chapter, from `series_order` rather than date |
| `partials/text-to-speech.html` | The listen-to-article player |
| `partials/post-cover.html` | Resolves `image:` → `images:` → a generated gradient fallback |
| `partials/head.html` | Mermaid bootstrap, theme-aware, re-renders on dark-mode toggle |
| `_default/_markup/render-codeblock-mermaid.html` | Turns ` ```mermaid ` fences into `<pre class="mermaid">` |

---

## CI/CD

Every push to `main` runs `.github/workflows/deploy.yml`:

```
push to main → checkout → setup Hugo 0.160.1 extended
             → hugo --minify --buildFuture → peaceiris/actions-gh-pages
             → pushes public/ to the gh-pages branch
             → GitHub Pages serves ai.devops-monk.com
```

`--buildFuture` matters: articles dated ahead of today still build. The workflow also fails the build if `public/CNAME` is missing — Hugo copies `static/CNAME` into `public/`, and a CNAME at the repo root would never reach the published branch, silently unsetting the custom domain on every deploy.

`.gitlab-ci.yml` is the same pipeline for GitLab Pages. The live site deploys from GitHub Actions; that file only does anything if the repo is mirrored to GitLab, and is kept in step so either host can build.

GitHub Pages and the CDN cache aggressively — **hard-refresh (Cmd+Shift+R) before concluding a change didn't ship**, or append a cache-busting query string when checking with `curl`.

### One-time setup

1. Repo **Settings → Pages** → source `gh-pages`, root `/`
2. Custom domain `ai.devops-monk.com`
3. Porkbun DNS: `CNAME  ai → devops-monk.github.io`

---

## Project structure

```
ai-blog/
├── .github/workflows/deploy.yml    # CI/CD
├── CNAME                           # ai.devops-monk.com
├── archetypes/default.md           # front matter for `hugo new`
├── content/
│   ├── about.md
│   ├── pages/guide.md              # the reading index
│   └── posts/2026/*.md             # articles
├── layouts/                        # theme overrides — see table above
├── static/
│   ├── assets/css/custom-styles.css   # design tokens + all widget styles
│   ├── assets/js/enhancements.js      # dark mode, copy buttons, diagram zoom
│   ├── images/articles/*.webp         # covers, generated by tools/
│   └── images/social/*.jpg            # share cards, generated by tools/
├── tools/
│   ├── gen_covers.py
│   └── gen_social.py
├── themes/wellington/              # base theme
└── config.toml
```

---

## Author

**Abhay Pratap Singh** — Principal Software Engineer

- AI blog: [ai.devops-monk.com](https://ai.devops-monk.com/)
- System design: [system-design.devops-monk.com](https://system-design.devops-monk.com/)
- DevOps: [blog.devops-monk.com](https://blog.devops-monk.com/)
- GitHub: [@abhi15sep](https://github.com/abhi15sep)
- LinkedIn: [abhay-singh-831997b5](https://www.linkedin.com/in/abhay-singh-831997b5/)
