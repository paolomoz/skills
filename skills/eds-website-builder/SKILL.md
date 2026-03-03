---
name: eds-website-builder
description: Build a complete website with AEM Edge Delivery Services from scratch. Guides through project setup (from aem-boilerplate), block development, styling, content authoring, and deployment. Use this skill when the user wants to create an EDS site, set up an AEM Edge Delivery project, build EDS blocks, or start a new aem.live website. Also useful for "create a website", "new EDS project", or "AEM site from scratch".
---

# EDS Website Builder

Build a complete AEM Edge Delivery Services website from project creation to production deployment. This skill captures battle-tested patterns from real EDS projects.

## When to Use

- User wants to create a new EDS / aem.live website
- User wants to set up a project from the AEM boilerplate
- User asks about EDS architecture, block development, or deployment
- User wants to migrate or build a site on Edge Delivery Services

## Quick Start

If the user already knows what they want, jump straight to the relevant section. Otherwise, walk them through the full workflow below.

## Workflow Overview

```
 1. Project Setup        → Clone boilerplate, connect to GitHub + content source
 2. Brand Analysis       → Screenshot reference site, extract brand voice + visual patterns
 3. Design Foundation    → Brand tokens, fonts, color system, block-level design tokens
 4. Content Planning     → Product briefing, page structure, block content models
 5. Block Development    → Build blocks (JS decoration + CSS styling)
 6. Image Generation     → AI-generated site images (Gemini / FLUX / Firefly)
 7. Content Authoring    → Create content in CMS or local drafts
 7b. Parallel Page Gen   → Spawn parallel agents to generate all pages concurrently
 8. DA Integration       → Programmatic content upload via service token (optional)
 9. Universal Editor     → Component definitions, models, filters, instrumentation (optional)
10. Three-Phase Loading  → Eager/lazy/delayed resource loading strategy
11. Testing & QA         → Lint, CI/CD, responsive check, accessibility, PageSpeed
12. Deployment           → Push to GitHub, preview on aem.page, go live on aem.live
```

---

## Common Pitfalls

Hard-won lessons from real site builds. Read these before starting any phase.

### DA breaks local asset paths → `about:error`

**DA cannot resolve repo-relative paths** like `/icons/logo.svg` or `/images/hero.jpeg`. When DA encounters these, it silently converts them to `src="about:error"` — producing broken images on the live site with no obvious error message.

**Every `<img>` in DA-uploaded content must use a public URL** — this includes page drafts, `nav.plain.html`, and `footer.plain.html`. The fix: deploy all assets (images, icons, logos) to a public CDN (e.g. Cloudflare Pages) first, then reference the public URL in your HTML.

```html
<!-- WRONG — DA converts this to about:error -->
<img src="/icons/logo.svg" alt="Logo">

<!-- RIGHT — DA fetches and ingests from public URL -->
<img src="https://my-site-images.pages.dev/logo.svg" alt="Logo">
```

This is especially easy to miss for **nav and footer icons** (logos, search icons, social icons) because they're authored as separate fragments — you won't see the breakage until the header/footer loads on the live site.

**Checklist**: Before every DA upload, grep your drafts for local asset paths:
```bash
grep -rn 'src="/\|src="\.\.' drafts/ --include='*.html' && echo "BLOCKED: fix local paths before uploading" || echo "OK: no local paths"
```

### Single-product sites don't need nested navigation

If your site has one product with multiple pages (efficacy, safety, dosing, etc.), put pages at the root level with a flat nav — not under a subfolder with a single dropdown. A dropdown that contains all pages adds a click with no informational benefit.

### Hero text is unreadable over background images

Hero blocks that place white text over a background image have **three layered problems** that must all be addressed:

**1. No gradient overlay** — reducing image opacity alone isn't enough for busy images. Add a directional gradient:

```css
.hero-teaser::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(to right, rgb(0 0 0 / 60%) 0%, rgb(0 0 0 / 30%) 50%, transparent 100%);
  pointer-events: none;
}
```

**2. Gradient covers the text** — if the overlay and the content row share the same `z-index`, the gradient renders on top of the text. The content row must have a higher z-index than the overlay.

**3. Image paints on top of text (the subtle one)** — in hero-teaser's DOM, the `<picture>` is a child of the content row but positioned absolutely to cover the whole hero. Because positioned elements with `z-index: 0` paint *after* non-positioned flow content in CSS stacking order, the semi-transparent image sits on top of the text — making it look permanently washed out. **The text cell must be explicitly positioned above the image**:

```css
/* Text cell must be above the absolutely-positioned picture */
.hero-teaser > div:last-child > div:last-child {
  position: relative;
  z-index: 1;
}
```

**Complete stacking order** (bottom to top):
```
z-index: 0  — <picture> (position: absolute, covers hero, opacity 0.5–0.6)
z-index: 1  — ::before gradient overlay (position: absolute)
z-index: 2  — content row container
  z-index: 0  — <picture> again (resolved within row's stacking context)
  z-index: 1  — text cell (position: relative, sits above picture)
```

All three fixes are required. Missing any one produces text that looks transparent or washed out.

---

## Phase 1: Project Setup

### 1.1 Clone the Boilerplate

```bash
# Option A: Use the GitHub template
# Go to https://github.com/adobe/aem-boilerplate and click "Use this template"

# Option B: Clone directly
git clone https://github.com/adobe/aem-boilerplate.git my-site
cd my-site
rm -rf .git
git init
git add -A && git commit -m "Initial commit from aem-boilerplate"
```

### 1.2 Connect to GitHub

```bash
gh repo create owner/my-site --public --source=. --push
```

The AEM Code Sync bot will automatically detect the new repo and start syncing.

### 1.3 Connect a Content Source

EDS supports multiple content sources:
- **Google Drive** — Shared folder with Google Docs/Sheets
- **SharePoint** — For Microsoft 365 organizations
- **Document Authoring (DA)** — Adobe's browser-based authoring at `da.live`

Configure `fstab.yaml` in the project root:

```yaml
mountpoints:
  /: https://content.da.live/org/repo/
```

Or for Google Drive:
```yaml
mountpoints:
  /: https://drive.google.com/drive/folders/YOUR_FOLDER_ID
```

### 1.4 Install & Start Development

```bash
npm install
npx @adobe/aem-cli up --no-open
# Dev server at http://localhost:3000
```

For local-only content (no CMS), create a `drafts/` folder with `.plain.html` files:
```bash
mkdir drafts
npx @adobe/aem-cli up --no-open --html-folder drafts
```

### 1.5 Understand the Project Structure

```
├── blocks/              # Reusable content blocks
│   └── {blockname}/
│       ├── {blockname}.js    # Block decoration logic
│       └── {blockname}.css   # Block styles
├── styles/
│   ├── styles.css            # Critical-path CSS (loaded eagerly for LCP)
│   ├── lazy-styles.css       # Below-fold CSS (loaded lazily)
│   └── fonts.css             # @font-face definitions
├── scripts/
│   ├── aem.js                # Core AEM library — NEVER MODIFY
│   ├── scripts.js            # Page decoration entry point
│   └── delayed.js            # Martech, analytics (loaded 3s after page)
├── icons/                    # SVG icons (referenced as :icon-name: in content)
├── fonts/                    # Web font files
├── head.html                 # Global <head> content (meta, scripts)
├── 404.html                  # Custom 404 page
└── fstab.yaml                # Content source mount configuration
```

**For detailed setup instructions and troubleshooting, read `references/project-setup.md`.**

---

## Phase 2: Brand Analysis (Reference Site → Guidelines)

Before writing code, analyze a reference site to extract structured brand guidelines. This produces two key artifacts that drive all design and content decisions.

### 2.1 Screenshot the Reference Site

Use Playwright to capture full-page screenshots of 10-20 representative pages:

```bash
mkdir -p analysis/screenshots
node tools/screenshot-reference.js
```

Capture: homepage, category pages, product/detail pages, about page, contact page.

### 2.2 Create Visual Design Analysis

Analyze screenshots systematically to document:
- **Global chrome** — header, footer, utility bars, navigation
- **Color system** — primary, secondary, text, background, product-specific accent colors (with hex values)
- **Typography** — heading font (family, weight, sizes), body font, display text, CTA text
- **Spacing & layout** — max width, section spacing, card grids, button styling
- **Component inventory** — hero variants, card types, accordions, data displays, alerts
- **Imagery style** — photography categories, illustration style, icon system

End with a **block mapping table** connecting visual patterns to EDS blocks:

| Site Pattern | EDS Block | Notes |
|---|---|---|
| Hero with image + heading | `hero-teaser` | Product-branded heroes |
| 3-column image cards | `cards-teaser` | Homepage category cards |
| Expandable sections | `accordion` | FAQ, focus areas |

### 2.3 Create Brand Voice & Imagery Skill

Extract text from reference pages and analyze for:
- **Voice attributes** — supportive, evidence-led, action-oriented, etc.
- **Voice by page type** — different registers for homepage vs. product vs. data pages
- **Sentence patterns** — opening sentences, benefit statements, CTAs
- **Vocabulary preferences** — preferred vs. avoided words
- **Regulatory language** — trademark conventions, disclaimers, required boilerplate
- **Imagery tiers** — when to use editorial vs. lifestyle vs. product photography
- **Copy templates** — fill-in-the-blank templates for hero sections, product cards, etc.
- **Writing checklist** — pre-publish verification items

### 2.4 Reference the Guidelines

Add to your project's `CLAUDE.md` or `AGENTS.md`:

```markdown
### Brand Guidelines
- Visual analysis: `analysis/visual-analysis.md`
- Brand voice & imagery: `brand-voice.md`
- Consult these when writing copy, selecting imagery, or making design decisions.
```

**For the complete brand analysis methodology, templates, and examples, read `references/brand-analysis.md`.**

---

## Phase 3: Design Foundation

### 3.1 CSS Custom Properties

Define your brand's design tokens in `styles/styles.css` under `:root`:

```css
:root {
  /* Colors */
  --background-color: #fff;
  --light-color: #f5f5f5;
  --dark-color: #1a1a2e;
  --text-color: #333;
  --link-color: #0066cc;
  --link-hover-color: #004499;

  /* Typography */
  --body-font-family: 'Inter', 'Helvetica Neue', helvetica, arial, sans-serif;
  --heading-font-family: 'Georgia', serif;
  --fixed-font-family: 'Roboto Mono', menlo, consolas, monospace;

  /* Font Sizes */
  --heading-font-size-xxl: 36px;
  --heading-font-size-xl: 28px;
  --heading-font-size-l: 24px;
  --heading-font-size-m: 20px;
  --heading-font-size-s: 18px;
  --heading-font-size-xs: 16px;
  --body-font-size-m: 16px;
  --body-font-size-s: 14px;
  --body-font-size-xs: 12px;

  /* Layout */
  --max-width-site: 1200px;
  --nav-height: 64px;
}

/* Scale up headings on desktop */
@media (width >= 900px) {
  :root {
    --heading-font-size-xxl: 48px;
    --heading-font-size-xl: 36px;
    --heading-font-size-l: 28px;
    --heading-font-size-m: 24px;
  }
}
```

### 3.2 Fonts

Define fonts in `styles/fonts.css` (loaded conditionally for performance):

```css
@font-face {
  font-family: 'MyFont';
  src: url('/fonts/myfont.woff2') format('woff2');
  font-weight: 400;
  font-display: swap;
}
```

Fonts are loaded conditionally by `scripts.js` — only on desktop (>= 900px) or when cached in `sessionStorage`. This prevents font-loading from blocking LCP on mobile.

### 3.3 Buttons

Links are auto-converted to buttons based on author formatting:
- `**[Link text](url)**` → `.button.primary` (strong wrapping)
- `*[Link text](url)*` → `.button.secondary` (em wrapping)
- `***[Link text](url)***` → `.button.accent` (strong + em wrapping)

Style all three variants in `styles/styles.css`.

### 3.4 Block-Level Design Tokens

Each block defines its own token file that centralizes all customizable values — colors, typography, spacing, borders, effects. This makes it easy to re-skin blocks without touching structural CSS.

```
blocks/{blockname}/
├── {blockname}.js              # Decoration logic
├── {blockname}.css             # Structural styles (uses tokens)
└── {blockname}-tokens.css      # Design tokens (all customizable values)
```

Token naming convention: `--{blockname}-{element}-{property}`

```css
/* cards-teaser-tokens.css */
:root {
  --cards-teaser-heading-font-size: 26px;
  --cards-teaser-heading-color: #4f0031;
  --cards-teaser-button-background: #d0006f;
  --cards-teaser-button-hover-background: #a80059;
  /* ... all visual values for the block */
}
```

Import tokens at the top of the structural CSS:
```css
/* cards-teaser.css */
@import url('./cards-teaser-tokens.css');

main .cards-teaser h2 {
  font-size: var(--cards-teaser-heading-font-size);
  color: var(--cards-teaser-heading-color);
}
```

Optionally create `{blockname}-measurements.txt` files to capture exact Figma values as a bridge between design and implementation.

**For the complete token architecture, naming conventions, and examples, read `references/design-tokens.md`.**

---

## Phase 4: Content Planning

### 4.1 Product Briefing

Before creating content, write a structured product/project briefing that defines the scope and subject matter. This becomes the single source of truth for all page content, driving page structure decisions, content for each page, brand voice application, and block selection.

The briefing should cover: product overview, clinical/technical data, key messages, and website scope (which pages to create and what each contains).

### 4.2 Content Structure

Every EDS page is composed of:
- **Sections** — Top-level divisions (separated by `---` in authoring)
- **Default content** — Text, headings, images, links (no block wrapper)
- **Blocks** — Named components with structured content (tables in authoring)

### 4.3 Markup Structure

The aem.live backend delivers clean HTML. Inspect it to understand the DOM:

```bash
# See the full decorated HTML
curl http://localhost:3000/path/to/page

# See the raw markdown
curl http://localhost:3000/path/to/page.md

# See the plain HTML before decoration
curl http://localhost:3000/path/to/page.plain.html
```

Section structure:
```html
<main>
  <div class="section">
    <div class="default-content-wrapper">
      <h1>Page Title</h1>
      <p>Introductory text</p>
    </div>
  </div>
  <div class="section">
    <div class="hero-wrapper">
      <div class="hero block" data-block-name="hero" data-block-status="loaded">
        <!-- Block content -->
      </div>
    </div>
  </div>
</main>
```

### 4.4 Content Modeling for Blocks

Before building a block, define its content model — the table structure authors will create:

| Column 1 | Column 2 |
|-----------|----------|
| Image     | Text content |
| ...       | ... |

The block name is the table header. Each row/cell maps to `block > div > div` in the DOM. Design your content model to be author-friendly and handle missing fields gracefully.

### 4.5 Block Markup Reference

Maintain a `blocks/BLOCK-REFERENCE.md` file documenting the expected `.plain.html` markup structure for every block in the project. This serves as the authoritative reference for content authoring — both for human authors and for parallel page generation agents. Include: class name, HTML snippet showing row/cell structure, and key notes per block.

**For detailed content planning patterns, read `references/content-patterns.md`.**

---

## Phase 5: Block Development

### 5.1 Block Architecture

Each block is self-contained:

```
blocks/my-block/
├── my-block.js     # Decoration logic
└── my-block.css    # Scoped styles
```

Blocks are auto-loaded when their content appears on a page — no manual imports needed.

### 5.2 JavaScript Pattern

```javascript
/**
 * loads and decorates the block
 * @param {Element} block The block element
 */
export default async function decorate(block) {
  // 1. Read the DOM structure delivered by the backend
  const rows = [...block.children];

  // 2. Transform the DOM in place
  rows.forEach((row) => {
    const [imageCell, textCell] = [...row.children];
    // ... transform cells
  });

  // 3. Add interactivity
  block.addEventListener('click', handleClick);
}
```

Key principles:
- The `decorate` function receives the block `<div>` element
- Transform DOM **in place** — don't rebuild from scratch when possible
- Re-use existing elements (`<picture>`, headings, etc.) rather than recreating
- Handle missing/optional content gracefully
- Use `console.log(block.innerHTML)` to inspect what the backend sends
- Always include `.js` extensions in imports

### 5.3 CSS Pattern

```css
/* All selectors MUST be scoped to the block */
main .my-block {
  /* Mobile-first base styles */
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

main .my-block h2 {
  font-family: var(--heading-font-family);
  font-size: var(--heading-font-size-m);
}

/* Tablet+ */
@media (width >= 600px) {
  main .my-block {
    padding: 2rem;
  }
}

/* Desktop+ */
@media (width >= 900px) {
  main .my-block {
    flex-direction: row;
    padding: 4rem;
  }
}
```

CSS rules:
- **All selectors scoped to block**: `.my-block .item`, never just `.item`
- **Mobile-first**: Base styles for mobile, `min-width` media queries for larger
- **Breakpoints**: 600px (tablet), 900px (desktop), 1200px (wide) — use only what's needed
- **CSS custom properties**: Use `var(--token)` for all colors, fonts, sizes
- **No `-container` / `-wrapper`** class names — those conflict with section wrappers
- **No Tailwind or frameworks** — vanilla CSS only

### 5.4 Variants

Block variants are CSS classes added to the block element by authors (e.g., `Hero (dark)` → `.hero.dark`):

```css
/* CSS-only variant — no JS needed */
main .hero.dark {
  background: var(--dark-color);
  color: white;
}

/* JS-variant — when DOM structure changes */
if (block.classList.contains('carousel')) {
  setupCarousel(block);
}
```

### 5.5 Auto-Blocking

Create blocks automatically from content patterns in `scripts.js`:

```javascript
function buildAutoBlocks(main) {
  // Example: auto-create hero from first H1 + picture
  const h1 = main.querySelector('h1');
  const picture = main.querySelector('picture');
  if (h1 && picture && h1.closest('div') === picture.closest('div')) {
    const section = h1.closest('div.section > div');
    const heroBlock = buildBlock('hero', { elems: [picture, h1] });
    section.prepend(heroBlock);
  }
}
```

**For complete block development patterns, read `references/block-patterns.md`.**

---

## Phase 6: AI Image Generation

Replace stock photography placeholders with AI-generated images tailored to your brand.

### 6.1 Choose a Provider

Ask the user which provider to use:

| Provider | When to Choose |
|----------|---------------|
| **Gemini 3 Pro** | Fast iteration, simple setup (single API key), good general quality |
| **FLUX 2 Pro** | Highest photorealism, explicit size control, async generation |
| **Adobe Firefly** | Brand-safe imagery, Adobe ecosystem, OAuth credentials |

### 6.2 Generate Images

1. Define a **style prefix** consistent with the brand voice document
2. Create a generation script (`tools/generate-images.sh`) with prompts for each image
3. Run the script — it saves images to `images/` directory

```bash
chmod +x tools/generate-images.sh
./tools/generate-images.sh
```

### 6.3 Deploy Images to Public URL

**CRITICAL: Never reference local paths (`/images/`, `/icons/`) in DA content.** DA converts unresolvable paths to `about:error`. See "Common Pitfalls" above.

Deploy generated images to a CDN so DA can ingest them. Cloudflare Pages is the simplest option:

```bash
# Create a Pages project (one-time)
npx wrangler pages project create my-site-images --production-branch main

# Deploy images
npx wrangler pages deploy ./images --project-name my-site-images
# → Images live at https://my-site-images.pages.dev/hero-example.jpeg
```

### 6.4 Update HTML References & Upload

Replace placeholder URLs in draft HTML with the public Cloudflare URLs, then upload to DA. DA automatically ingests images from public URLs.

```bash
# Replace all placeholder URLs with public Cloudflare URLs
find drafts -name '*.plain.html' -exec sed -i '' 's|/images/|https://my-site-images.pages.dev/|g' {} \;

# Upload to DA — DA will ingest the images automatically
./tools/upload-to-da.sh
./tools/preview-all.sh
```

**For complete API documentation, script templates, and prompt writing tips for all three providers, read `references/image-generation.md`.**

---

## Phase 7: Content Authoring

Create page content using your chosen content source:

- **Document Authoring (DA)** — Edit pages visually at `da.live`, using tables for blocks and formatted text for default content
- **Google Docs / SharePoint** — Author content in familiar document editors; tables become blocks automatically
- **Local drafts** — Create `.plain.html` files in `drafts/` for development without a CMS

For local drafts, follow the markup structure documented in `references/content-patterns.md` — sections as `<div>` children of `<main>`, blocks as `<div class="blockname">` with nested row/cell `<div>` elements.

**CRITICAL: All `<img>` tags in DA content must use public URLs, not local paths.** This applies to page images, nav logos, footer icons — everything. Local paths like `/icons/logo.svg` become `about:error` in DA. See "Common Pitfalls" above.

### 7.1 Navigation Structure

Choose navigation depth based on the site scope:

- **Single-product site** → flat top-level nav, pages at root (`/efficacy`, `/safety`, `/dosing`)
- **Multi-product portfolio** → nested dropdowns, pages in subfolders (`/product-a/efficacy`)

**Key rule**: if the nav would have only one top-level dropdown, flatten it. A single dropdown adds a click with no informational benefit.

### 7.2 Keep Navigation in Sync

**Every time you create or delete a page, update `nav.plain.html` and `footer.plain.html` to match.** Navigation is authored as a separate fragment — broken nav links (pointing to non-existent pages) are easy to miss.

Quick audit:
```bash
# Compare page inventory against nav links
find drafts -name '*.plain.html' ! -name 'nav.*' ! -name 'footer.*' | sort
grep -oP 'href="\K[^"]+' drafts/nav.plain.html | grep -v '^#' | sort
```

**For navigation structure patterns and consistency checklists, see `references/content-patterns.md`.**

---

## Phase 7b: Parallel Page Generation (Briefing-Driven Sites)

When a site has a complete briefing with final copy for every page, all pages can be generated concurrently using parallel agents. Each page is independent — same accordion, same CDN base, same block patterns — so no agent needs another agent's output.

### 7b.1 Prerequisites (Sequential)

Complete these steps sequentially before spawning parallel agents:

```
1. Generate images       → ./tools/generate-images.sh {sitename}
2. Deploy to CDN         → ./tools/deploy-images.sh {sitename}
3. Create nav + footer   → Write drafts/{sitename}/nav.plain.html & footer.plain.html
   - Extract top-bar link URLs from briefing nav section (Contact Us, Login)
   - Extract footer link URLs from briefing footer section (Privacy, Terms, Accessibility, AE reporting)
   - Extract copyright line verbatim from briefing footer section
   - Extract approval code and DOP from briefing
   - Do NOT use placeholder /{sitename}/ URLs for links that the briefing specifies as external
```

These produce the **shared context** that all pages need.

### 7b.2 Extract Shared Context Bundle

Before spawning agents, assemble a context bundle containing everything each agent needs. This avoids each agent redundantly reading the same files.

```
Shared context bundle:
├── CDN base URL          → https://{sitename}-images.pages.dev/
├── Site prefix           → /{sitename}/
├── Accordion content     → The prescribing info / AE reporting / references HTML
│                           (identical on every page — generate once from briefing
│                            sections 5/6/7, then include verbatim in every page agent's
│                            context. Do NOT let individual agents re-generate this.)
├── Metadata block        → HTML pattern for page metadata
├── Block reference       → blocks/BLOCK-REFERENCE.md (markup patterns for all blocks)
└── Image <picture> pattern → <picture><source type="image/webp" srcset="CDN_URL"><img src="CDN_URL" alt="..."></picture>
```

### 7b.3 Spawn Parallel Agents

Slice the briefing into per-page sections. Each agent receives:
- Its **page-specific briefing section** (copy, block types, image filenames, metadata)
- The **shared context bundle** (CDN URL, accordion HTML, block reference)
- The **output path** (e.g. `drafts/{sitename}/efficacy.plain.html`)

```
┌─────────────────────────────────────────────────────┐
│                   Main Agent                         │
│  1. Sequential setup (images, CDN, nav, footer)     │
│  2. Extract shared context bundle                    │
│  3. Spawn N page agents in parallel                  │
│  4. Wait for all to complete                         │
│  5. Upload to DA + preview                           │
└──────────┬──────┬──────┬──────┬──────┬──────┬───────┘
           │      │      │      │      │      │
           ▼      ▼      ▼      ▼      ▼      ▼
        Page 1  Page 2  Page 3  Page 4  Page 5  Page 6
        Agent   Agent   Agent   Agent   Agent   Agent
```

Use the Agent tool with `subagent_type: "general-purpose"` for each page. Launch all agents in a **single message** with multiple tool calls so they run concurrently:

```javascript
// Pseudocode — launch all page agents in one message
for (const page of pages) {
  Agent({
    description: `Generate ${page.name} page`,
    prompt: `
      Create the file: drafts/${sitename}/${page.filename}

      ## Shared Context
      ${sharedContextBundle}

      ## Page Content (from briefing)
      ${page.briefingSection}

      ## Block Reference
      ${blockReference}

      Write the complete .plain.html file using the exact copy from the briefing.
      Map content to the specified block types using the markup patterns from the block reference.
      Use CDN URLs for all images: https://${sitename}-images.pages.dev/${imageName}
      Do not modify any copy text — it is final approved content.
    `,
    subagent_type: "general-purpose"
  });
}
```

### 7b.4 Post-Generation: Upload, Preview, and Open (Sequential)

**IMPORTANT: Execute all of these steps automatically** once all page agents complete. Do not wait for the user to ask — the whole point of parallel generation is an end-to-end pipeline that delivers a viewable site.

**Step 1 — Verify no local image paths** (blocks upload if any are found):
```bash
grep -rn 'src="/' drafts/{sitename}/ --include='*.html' && echo "BLOCKED: fix local paths before uploading" || echo "OK: no local paths"
```

**Step 1b — Verify no placeholder links in nav/footer** (blocks upload if any are found):
```bash
grep -Pn 'href="/{sitename}/"' drafts/{sitename}/nav.plain.html drafts/{sitename}/footer.plain.html | grep -v 'img src' | grep -v 'Login' && echo "BLOCKED: placeholder links found — replace with briefing URLs" || echo "OK: no placeholder links"
```

Nav/footer links that equal `/{sitename}/` (other than the logo home link and Login CTA) are likely unfilled placeholders. Cross-reference against the briefing's nav/footer sections and replace with the specified URLs.

**Step 2 — Upload all drafts to DA** (including nav and footer):
```bash
./tools/upload-to-da.sh {sitename}
```

**Step 3 — Preview all pages on AEM CDN** (including nav and footer — they must be previewed or the header/footer won't render on the live preview):
```bash
./tools/preview-all.sh {sitename}
```

**Step 4 — Open the previewed homepage in the browser**:
```bash
open "https://main--{repo}--{owner}.aem.page/{sitename}/"
```

This closes the feedback loop — the user sees the fully rendered site with header, footer, and all blocks decorated without needing to start a local dev server or run any commands themselves.

### Key Design Decisions

- **Why parallel?** A 6-page site takes ~2 minutes sequentially per page. Parallel generation reduces wall-clock time to ~2 minutes total regardless of page count.
- **Why extract shared context?** Without it, each agent independently reads the briefing, block reference, and existing files — multiplying file reads by N and wasting tokens on redundant context.
- **Why not parallel for nav/footer?** Nav and footer reference page names and URLs. They're small files that take seconds — not worth parallelizing, and they serve as a sanity check that all page names are consistent before generation begins.
- **Copy fidelity rule**: When the briefing marks copy as final/approved, agents must use text exactly as written. Image alt text may be adapted to match generated images, but headings, body text, CTAs, and metadata must be verbatim.

---

## Phase 8: DA Integration (Programmatic Content Management)

When using Document Authoring (DA) as your content source, you can programmatically upload and manage content using Adobe IMS service tokens. This enables automated workflows: AI-generated content, bulk uploads, CI/CD pipelines.

### 8.1 Service Token Authentication

DA uses a two-step OAuth flow:
1. Exchange a long-lived **service token** (JWT) for a short-lived **access token** via Adobe IMS
2. Use the access token to call DA and Admin APIs

```bash
# Exchange service token for access token
ACCESS_TOKEN=$(curl -s -X POST "https://ims-na1.adobelogin.com/ims/token/v3" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&client_id=$DA_CLIENT_ID&client_secret=$DA_CLIENT_SECRET&code=$DA_SERVICE_TOKEN" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### 8.2 Credentials

Store in `.env` (never commit):

```env
DA_ORG=my-org
DA_REPO=my-site
DA_CLIENT_ID=my-project-da-prod
DA_CLIENT_SECRET="your-secret"
DA_SERVICE_TOKEN="eyJhbGciOiJSUzI1NiIs..."
```

### 8.3 Content Workflow

**Before uploading**: verify no local asset paths remain in drafts (DA converts these to `about:error`):
```bash
grep -rn 'src="/\|src="\.\.' drafts/ --include='*.html' && echo "BLOCKED: fix local paths" || echo "OK"
```

```bash
# 1. Create local draft content (drafts/*.plain.html)
# 2. Convert plain HTML → DA table format
python3 tools/plain-to-da.py drafts/page.plain.html > /tmp/page.html

# 3. Upload to DA
curl -X POST -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "data=@/tmp/page.html;type=text/html" \
  "https://admin.da.live/source/$DA_ORG/$DA_REPO/page.html"

# 4. Trigger CDN preview refresh
curl -X POST -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://admin.hlx.page/preview/$DA_ORG/$DA_REPO/main/page"
```

### 8.4 Bundled Tools

The skill includes ready-to-use scripts:

| Script | Purpose |
|--------|---------|
| `tools/plain-to-da.py` | Convert `.plain.html` (div-based) to DA format (table-based) |
| `tools/upload-to-da.sh` | Authenticate + bulk upload all drafts to DA |
| `tools/preview-all.sh` | Trigger CDN preview refresh for all uploaded pages |

**For complete DA integration guide including format conversion details, API reference, and troubleshooting, read `references/da-integration.md`.**

---

## Phase 9: Universal Editor Integration (Optional)

When using Document Authoring (DA), enable visual in-context editing with the Universal Editor. Authors can click on blocks and content elements to edit them directly rather than through table structures.

### 9.1 Component Definitions

Create four root-level JSON files:

| File | Purpose |
|------|---------|
| `component-definition.json` | Declares all available components (text, image, section, blocks) |
| `component-models.json` | Defines editable fields for each component |
| `component-filters.json` | Controls what can be nested inside what |
| `paths.json` | Maps DA content paths to website routes |

### 9.2 Block Instrumentation

Blocks that transform their DOM during decoration (e.g., converting `<div>` rows to `<ul>/<li>` lists) need MutationObserver scripts that move `data-aue-*` attributes to the correct decorated elements.

```javascript
// ue/scripts/ue.js — watches for DOM changes and remaps editor attributes
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    mutation.addedNodes.forEach((node) => {
      if (node.nodeName === 'UL') {
        moveInstrumentation(block.firstElementChild, node);
      }
    });
  });
});
observer.observe(block, { childList: true, subtree: true });
```

### 9.3 Loading UE Scripts

Only load UE scripts in the editor context:

```javascript
if (window.location.hostname.includes('adobeaemcloud.com')
    || new URLSearchParams(window.location.search).has('aue')) {
  await import('../ue/scripts/ue.js');
}
```

**For the complete UE integration guide including component definitions, models, filters, DA plugin fields, and instrumentation patterns, read `references/universal-editor.md`.**

---

## Phase 10: Three-Phase Page Loading

EDS uses progressive loading for maximum performance:

### Eager Phase (LCP)
- Decorates sections, blocks, buttons, icons
- Loads only the **first section** of the page
- Conditionally loads fonts (desktop only, or from cache)
- Adds `appear` class to body (reveals content)

### Lazy Phase
- Loads header and footer (as fragments)
- Loads all remaining sections
- Loads `lazy-styles.css`
- Handles hash-based navigation

### Delayed Phase (3 seconds later)
- Loads `delayed.js` for martech, analytics, third-party scripts
- Nothing here should affect perceived performance

**Never load non-critical resources in the eager phase.** This is the single most important performance rule.

---

## Phase 11: Testing & Quality

### Linting & CI/CD
```bash
npm run lint        # ESLint (Airbnb) + Stylelint
npm run lint:fix    # Auto-fix issues
```

Set up GitHub Actions to run lint on every push. Create a PR template that requires preview URLs. See `references/project-setup.md` for the CI/CD workflow and template.

### Performance
- Target PageSpeed Insights score of **100**
- Check: `https://developers.google.com/speed/pagespeed/insights/?url=YOUR_URL`
- Keep `styles.css` minimal (critical path only)
- Lazy-load images below the fold
- No JavaScript dependencies — vanilla ES6+ only
- Automatic code splitting per block

### Accessibility
- Proper heading hierarchy (H1 → H2 → H3)
- Alt text on all images
- ARIA labels on interactive elements
- Keyboard navigation support
- WCAG 2.1 AA compliance

### Content Inspection
```bash
curl http://localhost:3000/page          # Full HTML
curl http://localhost:3000/page.md       # Markdown
curl http://localhost:3000/page.plain.html  # Plain HTML
```

**For detailed testing and performance guidance, read `references/testing-performance.md`.**

---

## Phase 12: Deployment

### Environment URLs

With your GitHub `{owner}/{repo}` and `{branch}`:

| Environment | URL |
|-------------|-----|
| Local dev | `http://localhost:3000/` |
| Branch preview | `https://{branch}--{repo}--{owner}.aem.page/` |
| Production preview | `https://main--{repo}--{owner}.aem.page/` |
| Production live | `https://main--{repo}--{owner}.aem.live/` |

### Publishing Process

1. Push feature branch to GitHub
2. AEM Code Sync processes changes automatically
3. Test on `https://{branch}--{repo}--{owner}.aem.page/`
4. Run PageSpeed Insights against feature preview URL
5. Open PR to `main` — **include a link to the preview URL** showing your changes
6. After review + merge, production updates automatically

### PR Template

```bash
gh pr create --title "Add hero block" --body "$(cat <<'EOF'
## Summary
- Added hero block with image + heading + CTA layout
- Supports dark variant for inverted color scheme

## Preview
https://feat-hero--my-site--my-org.aem.page/

## Test plan
- [ ] Hero renders correctly on desktop and mobile
- [ ] Dark variant applies correct colors
- [ ] PageSpeed score remains 100
EOF
)"
```

---

## Appendix: Documentation Search

Search the full aem.live documentation:

```bash
# Search by keyword
curl -s https://www.aem.live/docpages-index.json | jq -r '.data[] | select(.content | test("KEYWORD"; "i")) | "\(.path): \(.title)"'

# Web search restricted to docs
# Use: site:www.aem.live <query>
```

Key documentation:
- [Developer Tutorial](https://www.aem.live/developer/tutorial)
- [Markup Reference](https://www.aem.live/developer/markup-reference)
- [Sections & Blocks](https://www.aem.live/developer/markup-sections-blocks)
- [Keeping it 100](https://www.aem.live/developer/keeping-it-100)
- [David's Model](https://www.aem.live/docs/davidsmodel)
- [Anatomy of a Project](https://www.aem.live/developer/anatomy-of-a-project)

---

## Reference Files

Read these for detailed guidance on specific topics:

| File | When to Read |
|------|-------------|
| `references/project-setup.md` | Setting up a new project, configuring content sources, CI/CD pipeline, troubleshooting dev server |
| `references/brand-analysis.md` | Screenshotting reference sites, extracting brand voice, visual analysis methodology |
| `references/design-tokens.md` | Block-level CSS custom properties, token naming conventions, Figma-to-tokens workflow |
| `references/block-patterns.md` | Building new blocks, JS decoration patterns, advanced DOM manipulation |
| `references/image-generation.md` | AI image generation with Gemini 3 Pro, FLUX 2 Pro, or Adobe Firefly |
| `references/content-patterns.md` | Product briefing, content modeling, section metadata, fragment patterns, draft content |
| `references/da-integration.md` | DA service token auth, programmatic content upload, format conversion, preview API |
| `references/universal-editor.md` | UE component definitions, models, filters, DA plugin fields, MutationObserver instrumentation |
| `references/testing-performance.md` | Linting, PageSpeed optimization, accessibility testing, responsive QA |
