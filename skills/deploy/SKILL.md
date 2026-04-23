---
name: deploy
description: Use when porting a hand-coded bespoke HTML page (art-directed landing, campaign site, keynote companion, one-off microsite, designer-generated "snowflake") to Adobe Edge Delivery Services with pixel-perfect fidelity, where forcing the design into EDS's standard block library would compromise the visual intent. Also use when the source is static HTML/CSS/JS with no CMS, time-boxed to hours/days, and authoring will be done by an AI agent rather than humans in Docs/SharePoint.
---

# Snowflake CMS: Deploy a Bespoke Page to EDS

## Overview

Some pages shouldn't be block-composed — they're fully art-directed, high-design, short-lived, and the design *is* the message. EDS's default decoration pipeline (auto-blocking, button decoration, section wrapping) actively fights this class of page.

**Bespoke-page mode** is the escape hatch: each page opts out of decoration and opts into (a) a per-page CSS file (verbatim lift of the source's inline `<style>`), (b) an optional per-page JS file for bespoke interactive devices, and (c) semantic HTML as direct content. All other EDS primitives — tokens, shared blocks, three-phase load, edge delivery, preview/publish — still apply.

**Core principle: don't decompose. Lift verbatim, then isolate per page.** Pixel fidelity beats reuse for this class of page.

## When to Use

- Hand-coded source (static HTML/CSS/JS, no framework, no CMS).
- Design fidelity is mandatory — no "close enough."
- Short-lived or campaign-driven (Summit, keynote, PR moment, product launch).
- Authoring via AI agent (Claude Code) or a designer-developer pair, not via Docs/SharePoint.

## When NOT to Use

- Design is already composed from reusable patterns → use the standard EDS block model.
- Authored by humans in Docs/SharePoint → block model gives them the right authoring UX.
- Site-wide design system that will be reused across many pages → extract into blocks, not per-page CSS.

## The Convention

```
site-root/
├── index.html                    # Full HTML doc (DOCTYPE, head inline, body content)
├── {slug}.html                   # Same structure per page
├── head.html                     # Shared head (unused locally; used once aem.page remote exists)
├── nav.plain.html                # Nav content (logo + links)
├── footer.plain.html             # Footer content
├── styles/
│   ├── styles.css                # Tokens + universal base ONLY (:root, *, body, shared utilities)
│   ├── page-{slug}.css           # Per-page styles — near-verbatim lift from source inline <style>
│   └── fonts.css                 # Self-hosted @font-face (or empty if using Google Fonts CDN)
├── scripts/
│   ├── scripts.js                # Bespoke-mode loader (see below)
│   ├── page-{slug}.js            # Per-page JS (animations, etc.) — stub if unused
│   └── aem.js  delayed.js        # Boilerplate, unchanged
└── blocks/
    ├── header/  footer/          # Thin: fetch .plain.html, set .active on nav, no button decoration
    ├── {shared-widget}/          # Only for things genuinely shared across pages (e.g., modal)
    └── {marker-class}/           # No-op stub for any `<div class="foo">` in content — see Mistake #4
```

## Port Workflow

1. **Bootstrap from aem-boilerplate.** `git clone https://github.com/adobe/aem-boilerplate.git && npm install`.
2. **Extract tokens to `styles/styles.css`.** Lift `:root { --color-*, --heading-*, --spacing-* … }` + universal `*` reset + `body` base + any genuinely-shared utilities (`.section-divider`, `.bg-lifted`). Keep `body { display: none }` + `body.appear { display: block }` from boilerplate.
3. **Per-page CSS.** For each page, copy the source's inline `<style>` into `styles/page-{slug}.css`, verbatim minus `:root` and the shared base. Do **not** decompose into per-block sheets.
4. **Per-page content.** Create `{slug}.html` as a **full HTML document** — inline the contents of `head.html` in `<head>` (see Mistake #5), then `<body>` contains `<header></header><main><div>…sections…</div></main><footer></footer>`. Preserve every authored class and `data-*` attribute.
5. **Shared nav + footer.** Put content in `nav.plain.html` and `footer.plain.html`. Rewrite `blocks/header/header.js` to: fetch `/nav.plain.html`, add `.site-header` class to the `<header>` element, inject nav contents, and set `.active` on the link whose path matches `window.location.pathname`. **Disable the default button decoration.** Do the equivalent for `footer`.
6. **Rewrite `scripts/scripts.js` for bespoke mode.** See the Loader Contract below.
7. **Static assets.** Copy favicon, OG image, poster, video, etc. to the repo root. Flag media > 5 MB for external hosting (R2/YouTube) rather than git.
8. **Pixel-diff.** Start dev server (`aem up --no-open`). Screenshot with Puppeteer/Playwright at 375/768/1440, pixel-diff against the source. Gate: <0.01% diff.
9. **AI-edit smoke test.** Verify Claude can reliably change 5 representative pieces of copy (hero headline, CTA text, footer line, a nested italic accent, a section label) via prompt without touching CSS.

## Loader Contract (`scripts/scripts.js`)

Replace the boilerplate `loadEager`/`loadLazy`/`decorateMain` with the code below.

**What stays on** (do NOT strip these — the loader depends on them):
- `decorateSections` — tags the top-level `<div>` in `<main>` as `.section` so `loadSection` can find it.
- `decorateBlocks` — mounts any marker-style `<div class="foo">` (header, footer, interest-modal, etc.).
- `decorateIcons` — cheap, no-op on pages with no `.icon` spans.

**What comes off** (these mutate content in ways that break pixel fidelity):
- `buildAutoBlocks` — auto-builds a hero from `h1 + picture`; tries to load `/fragments/` refs.
- `decorateButtons` — wraps `<p> <a>` in `.button-container`; overrides your CTA styling.

```js
export function decorateMain(main) {
  decorateIcons(main);
  decorateSections(main);
  decorateBlocks(main);
}

function pageSlug() {
  const p = window.location.pathname;
  if (p === '/' || p === '') return 'landing';
  return p.replace(/^\//, '').replace(/\.html$/, '').replace(/\/$/, '');
}

async function loadEager(doc) {
  document.documentElement.lang = 'en';
  decorateTemplateAndTheme();
  const slug = pageSlug();
  document.body.dataset.page = slug;

  // Page CSS is critical — wait for it before revealing body. Log (not swallow)
  // failures so a missing page-{slug}.css doesn't silently degrade to FOUC.
  const pageCss = loadCSS(`${window.hlx.codeBasePath}/styles/page-${slug}.css`)
    .catch((e) => console.error(`[bespoke] page CSS load failed: ${e.message}`));
  const main = doc.querySelector('main');
  if (main) {
    decorateMain(main);
    await pageCss;
    document.body.classList.add('appear');
    await loadSection(main.querySelector('.section'), waitForFirstImage);
  }
  // Fixed header w/ backdrop-blur must be in DOM before first paint.
  const header = doc.querySelector('header');
  if (header) loadHeader(header);
}

async function loadLazy(doc) {
  const main = doc.querySelector('main');
  await loadSections(main);
  loadFooter(doc.querySelector('footer'));
  loadCSS(`${window.hlx.codeBasePath}/styles/lazy-styles.css`);
  const slug = document.body.dataset.page;
  if (slug) import(`${window.hlx.codeBasePath}/scripts/page-${slug}.js`).catch(() => {});
}
```

## Common Mistakes

| Mistake | What happens | Fix |
|---|---|---|
| 1. Decomposing into blocks | Inline CSS spreads across 10+ block sheets; design coherence shatters | Lift verbatim into one `page-{slug}.css` |
| 2. Leaving `buildAutoBlocks` + `decorateButtons` on | Links get wrapped in `<p class="button-container">`; hero auto-built from h1+picture; pixel diff explodes | Skip them in your `decorateMain` |
| 3. Loading page CSS lazily | FOUC: body paints before page styles apply | Use `await loadCSS(...)` before `body.classList.add('appear')` |
| 4. `<div class="foo">` marker with no block stub | `decorateBlocks` 404s on `/blocks/foo/foo.{js,css}` | **Preferred: create a 3-line no-op block stub** (see below). Alternative: change the authored tag to `<hr>`/`<aside>`/`<section>` so `decorateBlocks`'s `div.foo` selector doesn't match — but this mutates authored markup, so prefer the stub. |
| 5. Writing content as body-only HTML | `aem up` doesn't wrap local files with `head.html`; page renders unstyled | Write each page as a full HTML doc with `<head>` inlined. **Deployment note**: once the `aem.page` remote is configured (via `aem up --url https://main--{repo}--{owner}.aem.page`), the backend injects `head.html` and you can strip the inline `<head>` contents from each page. Until then, maintain head duplication — it's short and AI-maintainable. |
| 6. Header in lazy phase | Fixed header pops in after LCP; visible flash | Move `loadHeader` to `loadEager` for fixed/blurred headers |
| 7. Inline `onclick="…"` handlers | CSP blocks them silently — the button just doesn't respond, no console error | Use `data-*` attributes + JS binding in a block or page JS. **CSP scope**: `nonce-aem 'strict-dynamic'` is set by both `head.html` (production) and the `aem up` dev server. Test locally; what works locally works in prod for this. |
| 8. Shared widget: inline stub vs. injected block — pick one | Mixing patterns leaves orphan markers or duplicate DOM | **Pattern A (inline)**: markup lives in page HTML, `blocks/widget/widget.js` is a no-op stub just to silence `decorateBlocks`. **Pattern B (injected)**: authored marker is `<div class="widget"></div>`, block's `decorate()` removes the marker and injects markup at `document.body`. Use A for page-specific widgets, B for ones on 2+ pages. Don't do both. |
| 9. Missing per-page JS stub | 404 in network tab even with `.catch()` | Create `scripts/page-{slug}.js` as an empty file for pages without bespoke JS |
| 10. Forgetting favicon / OG / fonts | 404s, missing meta, system font fallback | Copy favicon, OG image; add Google Fonts preconnect + stylesheet or self-host in `styles/fonts.css` |

## No-op Block Stub Template

For any `<div class="foo">` in authored content that isn't backed by a real block, drop in this stub at `blocks/foo/`:

```js
// blocks/foo/foo.js
export default function decorate() {}
```

```css
/* blocks/foo/foo.css — intentionally empty; real styles live in page-{slug}.css */
```

Three lines. Prevents 404s on `/blocks/foo/foo.{js,css}` without mutating authored markup.

## Pixel-diff Setup

Reference gate values (`<0.01%`) come from: Puppeteer `page.screenshot({ fullPage: true, deviceScaleFactor: 2 })` at widths 375/768/1440, compared with `pixelmatch` at `threshold: 0.1`. Different tools/configs produce different baselines. If you use Playwright `odiff`, recalibrate against the source rendered in the same tool before gating.

## Reference Implementation

`github.com/paolomoz/of1-eds` — the of1.live site (3 marketing pages) ported to EDS using this convention. Source site: `github.com/paolomoz/of1`. Spike achieved 0.0014% pixel diff at desktop, 0.0058% at mobile.

## Red Flags — STOP and reconsider

- "I'll make a block for the hero / manifesto / pipeline animation" → you're decomposing. Stop. One `page-{slug}.css` per page.
- "The diff is 3% — good enough" → it's not. Bespoke-page mode targets <0.01%. Find the rule that's missing or extra.
- "I'll put the nav links directly in the header block's JS" → no, put them in `nav.plain.html` so copy changes don't need code edits.
- "Let me add a `<meta name="page">` in each file" → overkill. Derive slug from `window.location.pathname`.
- "I'll keep the inline `<style>` block in each HTML page" → works, but breaks EDS caching. Move to `styles/page-{slug}.css`.
