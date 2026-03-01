# DA HTML Format Specification

Complete specification for the Document Authoring (DA) HTML format used by AEM Edge Delivery Services. This document covers the structure, rules, and examples for converting content to DA-compatible HTML.

---

## Document Structure

Every DA document follows this top-level structure:

```html
<body>
  <header></header>
  <main>
    <!-- Content goes here -->
  </main>
  <footer></footer>
</body>
```

- `<header>` and `<footer>` are always present, even if empty. They serve as placeholders for header/footer fragments loaded by the EDS framework.
- All page content lives inside `<main>`.
- The `<body>` tag is the root element. Do not include `<html>`, `<head>`, or `<!DOCTYPE>` -- DA strips them.

---

## Content Types

DA content consists of two types: **default content** and **blocks**.

### Default Content

Default content is any HTML that is not inside a block table. It appears directly inside `<main>` wrapped in a `<div>`:

```html
<main>
  <div>
    <h1>Page Title</h1>
    <p>Introductory paragraph that appears before any blocks.</p>
  </div>
</main>
```

Default content supports all standard HTML elements: headings, paragraphs, lists, links, images, and inline formatting.

### Blocks

Blocks are structured content components represented as HTML tables. Each block has:

1. A `<thead>` with a single row containing the block name
2. A `<tbody>` with one or more rows containing the block's data

```html
<table>
  <thead>
    <tr><th colspan="2">block-name</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>Cell 1 content</td>
      <td>Cell 2 content</td>
    </tr>
  </tbody>
</table>
```

---

## Block Name Convention

The block name in `<thead>` determines which EDS block component renders the content:

- Block names are **lowercase kebab-case**: `hero`, `cards`, `columns`, `call-to-action`
- Block **variants** are specified with parentheses: `columns (highlight)`, `cards (3-up)`
- Multiple variants can be combined: `hero (centered, dark)`
- The block name maps directly to a folder in the EDS project: `blocks/hero/hero.js` and `blocks/hero/hero.css`

```html
<!-- Standard block -->
<table>
  <thead>
    <tr><th colspan="2">hero</th></tr>
  </thead>
  ...
</table>

<!-- Block with variant -->
<table>
  <thead>
    <tr><th colspan="2">columns (highlight)</th></tr>
  </thead>
  ...
</table>
```

---

## Section Separators

Sections within a page are separated by `<hr/>` (horizontal rule) elements. Each section becomes a `<div>` with a `section` class in the rendered page.

```html
<main>
  <div>
    <h1>Section 1 Content</h1>
  </div>

  <table>
    <thead><tr><th>hero</th></tr></thead>
    <tbody>...</tbody>
  </table>

  <hr/>  <!-- Section break -->

  <table>
    <thead><tr><th>cards</th></tr></thead>
    <tbody>...</tbody>
  </table>

  <hr/>  <!-- Another section break -->

  <div>
    <h2>Final Section</h2>
    <p>Closing content.</p>
  </div>
</main>
```

Key rules:
- `<hr/>` creates a new section in the rendered page
- Content before the first `<hr/>` is the first section
- Empty sections (two consecutive `<hr/>` tags) are valid but render as empty `<div>` containers
- Section separators are siblings of blocks and default content, never nested inside them

---

## Cell Content Rules

Table cells (`<td>`) in block tables can contain rich HTML:

### Text Content

```html
<td>
  <h1>Heading</h1>
  <h2>Subheading</h2>
  <p>Paragraph text with <strong>bold</strong> and <em>italic</em>.</p>
  <ul>
    <li>List item one</li>
    <li>List item two</li>
  </ul>
</td>
```

### Links

```html
<td>
  <p><a href="/path/to/page">Link Text</a></p>
  <p><strong><a href="/cta-path">Primary CTA</a></strong></p>
</td>
```

- Links wrapped in `<strong>` render as primary buttons in most EDS themes
- Links wrapped in `<em>` render as secondary/outline buttons
- Plain links render as text links

### Images

```html
<td>
  <picture>
    <source type="image/webp" srcset="/media/image.webp?width=2000&amp;format=webply&amp;optimize=medium" media="(min-width: 600px)" />
    <source type="image/webp" srcset="/media/image.webp?width=750&amp;format=webply&amp;optimize=medium" />
    <img src="/media/image.webp" alt="Descriptive alt text" loading="lazy" width="1200" height="800" />
  </picture>
</td>
```

- Always use `<picture>` with `<img>` for images
- Include `alt` text on every image
- `loading="lazy"` is recommended for below-the-fold images
- Width and height attributes should match the source image dimensions for CLS prevention
- For DA uploads, a simple `<picture><img src="..." alt="..." /></picture>` is sufficient -- the EDS framework adds responsive source sets automatically

### Icons

```html
<td>
  <span class="icon icon-checkmark"></span>
</td>
```

Icons are rendered via `<span>` elements with the `icon` class and a specific icon name class.

---

## Colspan Rules

The `<th>` in the `<thead>` must have a `colspan` attribute matching the maximum number of columns in any `<tbody>` row:

```html
<!-- 2-column block -->
<table>
  <thead>
    <tr><th colspan="2">columns</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>Column 1 content</td>
      <td>Column 2 content</td>
    </tr>
  </tbody>
</table>

<!-- Single-column block (colspan not needed or set to 1) -->
<table>
  <thead>
    <tr><th>accordion</th></tr>
  </thead>
  <tbody>
    <tr><td>Item content</td></tr>
  </tbody>
</table>
```

If rows have different numbers of cells, use the maximum:

```html
<table>
  <thead>
    <tr><th colspan="3">mixed-block</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>One cell</td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>Cell 1</td>
      <td>Cell 2</td>
      <td>Cell 3</td>
    </tr>
  </tbody>
</table>
```

---

## Block Examples

### Hero Block

```html
<table>
  <thead>
    <tr><th colspan="2">hero</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <h1>Transform Your Business</h1>
        <p>AI-powered solutions that scale with your growth.</p>
        <p><strong><a href="/get-started">Get Started Free</a></strong></p>
        <p><a href="/demo">Watch Demo</a></p>
      </td>
      <td>
        <picture><img src="/media/hero-image.webp" alt="Platform dashboard showing analytics" /></picture>
      </td>
    </tr>
  </tbody>
</table>
```

### Cards Block

```html
<table>
  <thead>
    <tr><th colspan="2">cards</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <picture><img src="/media/feature-1.webp" alt="Automated workflows" /></picture>
      </td>
      <td>
        <h3>Automated Workflows</h3>
        <p>Set up complex automation in minutes, not months.</p>
      </td>
    </tr>
    <tr>
      <td>
        <picture><img src="/media/feature-2.webp" alt="Real-time analytics" /></picture>
      </td>
      <td>
        <h3>Real-Time Analytics</h3>
        <p>Monitor performance metrics as they happen.</p>
      </td>
    </tr>
    <tr>
      <td>
        <picture><img src="/media/feature-3.webp" alt="Team collaboration" /></picture>
      </td>
      <td>
        <h3>Team Collaboration</h3>
        <p>Work together seamlessly across time zones.</p>
      </td>
    </tr>
  </tbody>
</table>
```

### Accordion Block

```html
<table>
  <thead>
    <tr><th colspan="2">accordion</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><p><strong>What is Document Authoring?</strong></p></td>
      <td><p>Document Authoring (DA) is a lightweight content management system for AEM Edge Delivery Services that uses a simple HTML table format for content structure.</p></td>
    </tr>
    <tr>
      <td><p><strong>How do I upload content?</strong></p></td>
      <td><p>Use the DA Admin API to PUT content to <code>admin.da.live/source/{org}/{repo}/{path}</code> with a valid IMS bearer token.</p></td>
    </tr>
  </tbody>
</table>
```

### Columns Block with Variant

```html
<table>
  <thead>
    <tr><th colspan="3">columns (highlight)</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <h3>Enterprise Plan</h3>
        <p>Everything you need at scale.</p>
        <p><strong><a href="/contact">Contact Sales</a></strong></p>
      </td>
      <td>
        <h3>Professional Plan</h3>
        <p>For growing teams.</p>
        <p><strong><a href="/signup?plan=pro">Start Free Trial</a></strong></p>
      </td>
      <td>
        <h3>Starter Plan</h3>
        <p>Get started quickly.</p>
        <p><strong><a href="/signup?plan=starter">Sign Up Free</a></strong></p>
      </td>
    </tr>
  </tbody>
</table>
```

---

## Metadata Block

Page metadata is stored in a special `metadata` block at the end of the page:

```html
<table>
  <thead>
    <tr><th colspan="2">metadata</th></tr>
  </thead>
  <tbody>
    <tr>
      <td>title</td>
      <td>Page Title for SEO</td>
    </tr>
    <tr>
      <td>description</td>
      <td>Meta description for search engines, 150-160 characters.</td>
    </tr>
    <tr>
      <td>image</td>
      <td><picture><img src="/media/og-image.webp" alt="" /></picture></td>
    </tr>
    <tr>
      <td>template</td>
      <td>default</td>
    </tr>
  </tbody>
</table>
```

Common metadata keys:
- `title`: Page title (used in `<title>` tag and Open Graph)
- `description`: Meta description
- `image`: Open Graph image
- `template`: Page template name
- `theme`: Color theme variant
- `robots`: Search engine directives (e.g., `noindex, nofollow`)

The metadata block should always be the last block on the page.

---

## Conversion Checklist

When converting `.plain.html` to DA format, verify:

1. Document is wrapped in `<body><header/><main>...</main><footer/></body>`
2. Every `<div class="blockname">` is converted to a `<table>` with proper `<thead>`
3. Block names in `<thead>` match the original class names exactly
4. `colspan` on `<th>` matches maximum cells in any row
5. Section separators (`<hr/>`) are preserved between blocks
6. Default content (not in a block) is wrapped in `<div>`
7. Images use `<picture><img/></picture>` format
8. Links for CTAs are wrapped in `<strong>` for primary or `<em>` for secondary
9. All inner HTML within cells is preserved (no stripping or sanitizing)
10. Metadata block is present and positioned last
