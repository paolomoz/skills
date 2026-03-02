# Content Patterns

## Product Briefing

Before creating content, write a structured product/project briefing that defines the scope and subject matter. This becomes the single source of truth for all page content.

### Briefing Template

```markdown
# [PRODUCT NAME] — Product Briefing

## Product Overview
- Generic name: [generic]
- Class: [drug class / product category]
- Regulatory status: [approved / pending / investigational]
- Approval date: [date]

## Clinical Data
### [Trial Name 1] (Phase III)
- Population: [N patients, demographics]
- Primary endpoint: [endpoint + result]
- Key statistic: [HR/RR, 95% CI, p-value]
- Comparator: [vs. what]

### [Trial Name 2]
- ...

## Safety Profile
- Common adverse events: [list with percentages]
- Contraindications: [list]
- Key warnings: [list]

## Dosing & Administration
- Starting dose: [dose]
- Route: [oral / IV / SC / inhaled]
- Frequency: [once daily / twice daily]
- Adjustments: [renal, hepatic, dose reduction criteria]

## Mechanism of Action
- [2-3 sentence description of how the product works]

## Website Scope
- Page 1: Home — [description]
- Page 2: Efficacy — [description]
- Page 3: Safety — [description]
- Page 4: Dosing — [description]
- Page 5: Mechanism of Action — [description]
- Page 6: Resources — [description]

## Key Messages
1. [Primary message / tagline]
2. [Secondary message]
3. [Tertiary message]
```

This briefing drives:
- Page structure decisions (which pages to create)
- Content for each page (clinical data, safety info, dosing)
- Brand voice application (how to present the data)
- Block selection (which blocks best present each content type)

## Page Structure

Every EDS page follows a consistent structure when delivered from the backend:

```html
<body>
  <header></header>
  <main>
    <div><!-- Section 1: default content or blocks --></div>
    <div><!-- Section 2 --></div>
    <!-- ... more sections ... -->
  </main>
  <footer></footer>
</body>
```

After decoration by `aem.js`, sections get wrapped:

```html
<main>
  <div class="section" data-section-status="loaded">
    <div class="default-content-wrapper">
      <h1>Heading</h1>
      <p>Paragraph text</p>
    </div>
  </div>
  <div class="section" data-section-status="loaded">
    <div class="hero-wrapper">
      <div class="hero block" data-block-name="hero" data-block-status="loaded">
        <!-- Block content -->
      </div>
    </div>
  </div>
</main>
```

## Section Metadata

Authors can apply styles to sections using a special "Section Metadata" table at the end of a section:

| Section Metadata | |
|---|---|
| Style | dark |

This adds CSS classes to the section: `<div class="section dark">`

Common section styles:
- `light` / `highlight` — Light background
- `dark` — Dark background with light text
- Custom classes — Any value becomes a CSS class

## Default Content

Content that isn't inside a block gets wrapped in `.default-content-wrapper`:

- Headings (H1-H6)
- Paragraphs
- Lists (ul, ol)
- Images (`<picture>` elements)
- Links (plain or buttonized)
- Horizontal rules (`<hr>`)

## Block Content Models

### Single-Column Block

Author creates a table with one column:

| Blockname |
|-----------|
| Content row 1 |
| Content row 2 |

DOM:
```html
<div class="blockname">
  <div><div>Content row 1</div></div>
  <div><div>Content row 2</div></div>
</div>
```

### Two-Column Block

| Blockname | |
|-----------|------|
| Image | Text |
| Image | Text |

DOM:
```html
<div class="blockname">
  <div>
    <div><picture>...</picture></div>
    <div><p>Text</p></div>
  </div>
  <div>
    <div><picture>...</picture></div>
    <div><p>Text</p></div>
  </div>
</div>
```

### Block with Variants

Author names the block with variants in parentheses:

| Cards (three-up, dark) | |
|---|---|
| ... | ... |

Results in: `<div class="cards three-up dark">`

### Rich Cell Content

Cells can contain complex content:

```
| Hero | |
|------|------|
| [image] | # Heading |
|          | Paragraph text |
|          | **[CTA Button](url)** |
```

The image becomes a `<picture>`, the heading becomes `<h1>`, the bold link becomes `<a class="button primary">`.

## Icons

Authors reference icons with the `:icon-name:` syntax. The icon file must exist at `/icons/icon-name.svg`.

After decoration, icons become inline SVGs wrapped in `<span class="icon icon-name">`.

## Links and Buttons

### Plain links
`[Link text](url)` → `<a href="url">Link text</a>`

### Button links (wrapped in formatting)
- `**[Text](url)**` → Primary button (`.button.primary`)
- `*[Text](url)*` → Secondary button (`.button.secondary`)
- `***[Text](url)***` → Accent button (`.button.accent`)

After decoration:
```html
<p class="button-wrapper">
  <a href="url" class="button primary">Text</a>
</p>
```

## Images

### Author-uploaded images
Automatically optimized by aem.live — delivered as `<picture>` with WebP and fallback `<img>`.

### Images in Git
Must be manually optimized. Place in a logical directory (e.g., `/images/`, `/icons/`).

### Responsive images
Use `createOptimizedPicture()` from `aem.js` when programmatically creating images:
```javascript
import { createOptimizedPicture } from '../../scripts/aem.js';
const picture = createOptimizedPicture('/path/to/image.jpg', 'Alt text', false, [
  { media: '(min-width: 600px)', width: '800' },
  { width: '400' },
]);
```

## Metadata

### Page Metadata
Authors set page metadata via a "Metadata" table (typically at the bottom of the page):

| Metadata | |
|---|---|
| Title | My Page Title |
| Description | A brief description |
| Image | [hero image] |

Access in JavaScript:
```javascript
import { getMetadata } from '../../scripts/aem.js';
const title = getMetadata('title');
const description = getMetadata('description');
```

### Nav and Footer Fragments
Header and footer content lives in separate pages (`/nav` and `/footer`) loaded as fragments during the lazy phase. Authors edit these pages independently.

## Creating Draft Content

### File Format

Draft files in the `drafts/` folder follow `.plain.html` structure:

```html
<body>
  <header></header>
  <main>
    <div>
      <!-- Section 1 -->
      <h1>Page Title</h1>
      <p>Introduction paragraph.</p>
    </div>
    <div>
      <!-- Section 2: a block -->
      <div class="columns">
        <div>
          <div>
            <picture><img src="https://placehold.co/600x400" alt="Column 1"></picture>
          </div>
          <div>
            <h2>Column Heading</h2>
            <p>Column description.</p>
          </div>
        </div>
      </div>
    </div>
    <div>
      <!-- Section 3: with section metadata -->
      <h2>Another Section</h2>
      <p>Content here.</p>
      <div class="section-metadata">
        <div>
          <div>Style</div>
          <div>dark</div>
        </div>
      </div>
    </div>
  </main>
  <footer></footer>
</body>
```

### Navigation Draft

Create `drafts/nav.plain.html` for the header:

```html
<body>
  <header></header>
  <main>
    <div>
      <p><a href="/">Brand Name</a></p>
      <ul>
        <li><a href="/about">About</a></li>
        <li><a href="/products">Products</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>
    </div>
  </main>
  <footer></footer>
</body>
```

### Footer Draft

Create `drafts/footer.plain.html`:

```html
<body>
  <header></header>
  <main>
    <div>
      <p>&copy; 2025 Brand Name. All rights reserved.</p>
      <ul>
        <li><a href="/privacy">Privacy</a></li>
        <li><a href="/terms">Terms</a></li>
      </ul>
    </div>
  </main>
  <footer></footer>
</body>
```

## Navigation Structure

### Single-Product vs Multi-Product Sites

Choose navigation depth based on the site's scope:

**Single-product site** (e.g. one drug/product brand site):
- Use **flat top-level navigation** — every page is a direct nav link
- The homepage IS the product page
- No subfolders or dropdowns needed

```
/              ← homepage (product landing)
/efficacy      ← top-level nav item
/safety        ← top-level nav item
/dosing        ← top-level nav item
/resources     ← top-level nav item
```

Nav markup (flat `<ul>`, no nesting):
```html
<ul>
  <li><a href="/efficacy">Efficacy</a></li>
  <li><a href="/safety">Safety</a></li>
  <li><a href="/dosing">Dosing</a></li>
  <li><a href="/resources">Resources</a></li>
</ul>
```

**Multi-product portfolio** (e.g. corporate site with multiple brands):
- Use **nested navigation** with dropdowns per product
- Products live in subfolders (`/product-a/efficacy`, `/product-b/safety`)

```
/              ← corporate homepage
/product-a     ← product A landing
/product-a/efficacy
/product-b     ← product B landing
/product-b/efficacy
```

Nav markup (nested `<ul>` for dropdowns):
```html
<ul>
  <li><a href="/product-a">Product A</a>
    <ul>
      <li><a href="/product-a/efficacy">Efficacy</a></li>
      <li><a href="/product-a/safety">Safety</a></li>
    </ul>
  </li>
  <li><a href="/product-b">Product B</a>
    <ul>
      <li><a href="/product-b/efficacy">Efficacy</a></li>
    </ul>
  </li>
</ul>
```

**Key principle**: if the nav would have only one top-level dropdown, flatten it. A single dropdown wrapping all pages adds a click with no informational benefit.

## Images in DA Content

**DA cannot resolve local paths like `/icons/logo.svg` or `/images/photo.jpeg`.** When DA encounters these paths, it converts them to `about:error` — resulting in broken images on the live site.

All images referenced in DA-authored content (including nav and footer fragments) must use **public URLs** that DA can fetch and ingest:

```html
<!-- WRONG — DA can't resolve local paths -->
<img src="/icons/logo.svg" alt="Logo">

<!-- RIGHT — DA fetches and ingests from public URL -->
<img src="https://my-cdn.pages.dev/logo.svg" alt="Logo">
```

After DA ingests the image, it serves it through its own media CDN (`./media_xxxxx.svg`), automatically optimizing and caching it.

This applies to all content uploaded to DA: page drafts, nav fragments, footer fragments. Deploy icons and images to a public CDN (e.g. Cloudflare Pages) before referencing them in DA content.

## Navigation & Footer Consistency

**CRITICAL: Every time you create or delete a page, verify that `nav.plain.html` and `footer.plain.html` still have correct links.**

Navigation links that point to non-existent pages create a broken user experience — dropdown menus leading to 404s. This is easy to miss because the nav is authored separately as a fragment.

### Checklist: After Creating a New Page

1. Open `drafts/nav.plain.html` (or the CMS nav page)
2. Add a link to the new page in the appropriate menu section
3. If the page belongs under an existing dropdown, add it as a nested `<li>` inside the parent `<ul>`
4. Verify the nav renders correctly in the dev server

### Checklist: After Deleting a Page

1. Open `drafts/nav.plain.html` and `drafts/footer.plain.html`
2. Remove or update any links pointing to the deleted page
3. If the deleted page was the only item in a dropdown, consider removing the dropdown parent too

### Checklist: After Restructuring Pages

1. Audit all nav links against the current page inventory
2. Compare the list of draft files with the list of nav links
3. Fix any mismatches — every nav link should resolve to a real page

### Quick Audit Command

```bash
# List all pages in drafts (excluding nav/footer fragments)
find drafts -name '*.plain.html' ! -name 'nav.*' ! -name 'footer.*' | sed 's|^drafts||;s|\.plain\.html$||;s|/index$|/|' | sort

# Extract all links from nav
grep -oP 'href="\K[^"]+' drafts/nav.plain.html | grep -v '^#' | sort

# Compare (links in nav not matching any page = broken)
```

## Plain HTML Section Separators

**CRITICAL: `plain-to-da.py` splits sections by `<hr>` tags.** Without `<hr>` between top-level `<div>` elements, all content merges into one section during DA upload. This causes:
- Section-metadata text appearing visibly on the page ("Style / highlight")
- Section styles applied incorrectly
- Only the first section-metadata being consumed

```html
<!-- BAD — no separators, everything merges into one section -->
<div>
  <div class="hero-teaser">...</div>
</div>
<div>
  <div class="introduction">...</div>
  <div class="section-metadata">...</div>
</div>

<!-- GOOD — <hr> separates sections for DA processing -->
<div>
  <div class="hero-teaser">...</div>
</div>
<hr>
<div>
  <div class="introduction">...</div>
  <div class="section-metadata">...</div>
</div>
```

Verify before upload: every top-level `<div>` in a `.plain.html` file must be separated by `<hr>`.

## Local Dev Server: getSiteRoot() Returns /drafts

When running with `--html-folder drafts`, the AEM CLI serves pages at `/drafts/{sitename}/` not `/{sitename}/`. The `getSiteRoot()` function returns the first URL path segment, so it returns `/drafts` instead of `/{sitename}`.

This means nav loads from `/drafts/nav` and footer from `/drafts/footer`. For local dev to work, you must also place copies of `nav.plain.html` and `footer.plain.html` at the `drafts/` root level:

```
drafts/
├── nav.plain.html          ← copy for local dev (getSiteRoot = /drafts)
├── footer.plain.html       ← copy for local dev
└── {sitename}/
    ├── nav.plain.html      ← canonical version
    ├── footer.plain.html   ← canonical version
    ├── index.plain.html
    └── *.plain.html
```

## Footer 4-Section Structure

The footer block CSS expects exactly **4 sections** in a 3-column grid layout:

1. **Brand column**: Logo (p1), hidden ID (p2, hidden by CSS), copyright/trademark text (p3)
2. **Site nav links**: Each link as a separate `<p>` (vertically stacked)
3. **Utility links**: External/legal links, each as a separate `<p>`
4. **Bottom row**: Full-width with border-top separator, right-aligned (e.g. approval code, date)

```html
<div>
  <p><a href="/{site}/"><img src="https://cdn/logo.svg" alt="Brand"></a></p>
  <p>APPROVAL-CODE</p>
  <p>Trademark notice. &copy; Company 2026. All rights reserved.</p>
</div>
<hr>
<div>
  <p><a href="/{site}/efficacy">Efficacy</a></p>
  <p><a href="/{site}/safety">Safety</a></p>
  <p><a href="/{site}/dosing">Dosing</a></p>
</div>
<hr>
<div>
  <p><a href="https://external.com">Report Adverse Event</a></p>
  <p><a href="/{site}/">Privacy Policy</a></p>
  <p><a href="/{site}/">Terms of Use</a></p>
</div>
<hr>
<div>
  <p>Date of Preparation: March 2026</p>
</div>
```

**Do not** use pipe-separated links in a single `<p>` — each link must be its own `<p>` for the CSS vertical stacking to work.

## Tips

- **Sections are separated by `---`** (horizontal rule) in the authoring tool
- **Block names are case-insensitive** in authoring but become lowercase CSS classes
- **Empty cells are valid** — your code must handle them
- **Multiple blocks per section** — a section can contain default content and multiple blocks
- **Content order matters** — the DOM order matches the authoring order
- **Keep nav in sync with pages** — every nav link must point to a real page; audit after every page change
