---
name: block-detector
description: Detect and catalog content blocks on web pages using Puppeteer browser automation with semantic analysis, bounding box capture, and CSS selector generation. Use when "detecting page blocks", "block analysis", "content block extraction", or "page structure detection".
---

# Block Detector

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| audit | "detecting page blocks", "block analysis", "content block extraction", "page structure detection" | Medium | 5 projects |

Analyze the visual and semantic structure of a web page to detect discrete content blocks (hero sections, feature grids, testimonial carousels, CTAs, etc.) using Puppeteer browser automation. For each detected block, the skill captures bounding box coordinates, generates a stable CSS selector, extracts content metadata, and produces a visual position map. The output feeds into design-system-extractor for pattern cataloging and generative-page-pipeline for block-aware page generation.

## When to Use
- User wants to understand the block structure of a live web page
- User needs to extract individual content blocks for reuse or migration
- User is building a design system and needs to catalog all block types on a site
- User wants to compare block structure across pages to find patterns
- A downstream skill (design-system-extractor, generative-page-pipeline) needs a block inventory as input
- User is reverse-engineering a competitor or reference site's page structure

## Instructions

### Step 1: Launch Puppeteer and Navigate to the Target URL

Launch a headless Chromium instance with a consistent viewport to ensure reproducible block detection.

```javascript
const browser = await puppeteer.launch({
  headless: 'new',
  args: ['--no-sandbox', '--disable-setuid-sandbox']
})
const page = await browser.newPage()
await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 })
await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 30000 })
```

Key settings:
- **Viewport**: 1440x900 is the standard desktop analysis viewport. This provides a consistent baseline for bounding box calculations.
- **Wait condition**: `networkidle2` waits until there are no more than 2 active network connections for 500ms. This ensures lazy-loaded content and async components have rendered.
- **Timeout**: 30 seconds is generous enough for most pages. Increase to 60 seconds for heavy SPAs.

After navigation, wait an additional 1 second for CSS animations and JavaScript-driven layout shifts to settle:

```javascript
await new Promise(resolve => setTimeout(resolve, 1000))
```

---

### Step 2: Detect Content Blocks Using the Priority Strategy

Run block detection in the browser context using `page.evaluate()`. The detection strategy follows a priority order, with each subsequent strategy catching blocks missed by the previous ones.

#### Strategy 1: Semantic HTML Elements (Highest Priority)

Query for semantic sectioning elements that browsers and assistive technologies already recognize as discrete content regions:

```javascript
const semanticSelectors = [
  'main > section',
  'main > article',
  'main > aside',
  'main > div[class]',     // Direct children of main with a class
  'section[class]',
  'article[class]',
  'aside[class]'
]
```

Prioritize elements that are direct children of `<main>` -- these are the most likely top-level content blocks. Deeper nesting produces component-level blocks, which are handled separately.

#### Strategy 2: Class-Based Patterns

Scan for elements whose class names match common block/section naming conventions:

```javascript
const classPatterns = [
  /\bblock\b/i,
  /\bsection\b/i,
  /\bcomponent\b/i,
  /\bmodule\b/i,
  /\bwidget\b/i,
  /\bpanel\b/i,
  /\bcard-group\b/i,
  /\bgrid\b/i,
  /\bhero\b/i,
  /\bbanner\b/i,
  /\bcta\b/i,
  /\bfooter-content\b/i
]
```

Match against the full class list of each element. Select only elements that are not already captured by Strategy 1.

#### Strategy 3: CMS Data Attributes

Many content management systems annotate blocks with data attributes:

```javascript
const cmsSelectors = [
  '[data-block-name]',
  '[data-block-type]',
  '[data-component]',
  '[data-component-name]',
  '[data-module]',
  '[data-section-type]',
  '[data-aue-type]',         // Adobe Universal Editor
  '[data-testid*="block"]',  // Testing IDs that include "block"
  '[data-testid*="section"]'
]
```

These selectors are highly reliable because the CMS explicitly marks block boundaries. When a CMS attribute is found, use it as the canonical block identifier.

#### Strategy 4: Layout-Based Detection (Fallback)

If the previous strategies find fewer than 3 blocks, fall back to layout analysis. Query for all elements that are direct children of the main content area and apply size heuristics (see Step 3).

---

### Step 3: Apply Content Block Heuristics

Filter all candidate elements through these heuristics to eliminate noise:

#### Minimum Size Requirements

```javascript
function meetsMinSize(rect) {
  return rect.width >= 200 && rect.height >= 80
}
```

Elements smaller than 200x80 pixels are unlikely to be standalone content blocks. They are more likely individual components within a block (buttons, icons, labels).

#### Exclusion Rules

Exclude elements that match any of these conditions:

| Condition | Reason |
|-----------|--------|
| `tagName` is `NAV`, `HEADER`, or `FOOTER` | Navigation and chrome, not content blocks |
| `height > 2 * viewportHeight` | Full-page wrappers, not individual blocks |
| `width < 0.5 * viewportWidth` and not inside a grid | Sidebar elements or narrow components, not primary blocks |
| `display: none` or `visibility: hidden` | Not visible to users |
| `position: fixed` or `position: sticky` | Floating UI elements (headers, chat widgets), not content blocks |

#### Meaningful Content Requirements

A valid content block must have at least one of:
- Text content >= 20 characters (excluding whitespace)
- At least one heading element (`h1`-`h6`)
- At least one image element (`img`, `picture`, `svg`)
- At least one link element (`a[href]`)

Elements that are purely structural wrappers with no meaningful content of their own are excluded.

```javascript
function hasMeaningfulContent(el) {
  const textLen = el.textContent.trim().length
  const hasHeadings = el.querySelector('h1, h2, h3, h4, h5, h6') !== null
  const hasImages = el.querySelector('img, picture, svg') !== null
  const hasLinks = el.querySelector('a[href]') !== null
  return textLen >= 20 || hasHeadings || hasImages || hasLinks
}
```

---

### Step 4: Handle Nested Blocks

When blocks are nested (a parent section containing child blocks), apply deduplication to avoid reporting redundant entries:

#### Rule 1: Child Coverage Deduplication

If a child block covers more than 80% of its parent block's area, remove the parent. The child is the meaningful content unit.

```javascript
function childCoversParent(parent, child) {
  const parentArea = parent.width * parent.height
  const childArea = child.width * child.height
  return childArea / parentArea > 0.8
}
```

#### Rule 2: Container Deduplication

If a container element has 2 or more detected children, remove the container from the results. The children are the meaningful blocks.

#### Rule 3: Visual Position Sorting

After deduplication, sort remaining blocks by visual position: top to bottom (by `boundingBox.y`), then left to right (by `boundingBox.x`) for blocks at the same vertical position.

#### Rule 4: Maximum Block Limit

Cap the result at 10 blocks per page. If more than 10 blocks pass all heuristics, keep the 10 largest by area. This prevents noise from highly modular pages (e.g., dashboards with 30+ small widgets).

If the page genuinely has more than 10 major content sections, note the truncation in the output and suggest the user increase the limit for that specific page.

---

### Step 5: Generate CSS Selectors

For each detected block, generate a stable CSS selector that can reliably re-select the element in future page loads. Follow this priority order:

#### Priority 1: ID Selector
If the element has a unique `id` attribute, use it directly.

```javascript
// #hero-section
if (el.id) return `#${CSS.escape(el.id)}`
```

#### Priority 2: Unique Class Combination
Find the smallest combination of classes that uniquely identifies the element on the page.

```javascript
// .hero-banner.full-width
const classes = Array.from(el.classList)
for (const cls of classes) {
  if (document.querySelectorAll(`.${CSS.escape(cls)}`).length === 1) {
    return `.${CSS.escape(cls)}`
  }
}
// Try pairs if singles are not unique
for (let i = 0; i < classes.length; i++) {
  for (let j = i + 1; j < classes.length; j++) {
    const selector = `.${CSS.escape(classes[i])}.${CSS.escape(classes[j])}`
    if (document.querySelectorAll(selector).length === 1) return selector
  }
}
```

#### Priority 3: Tag + Classes
Combine the tag name with classes for additional specificity.

```javascript
// section.hero-banner
const tagSelector = `${el.tagName.toLowerCase()}.${classes.map(c => CSS.escape(c)).join('.')}`
if (document.querySelectorAll(tagSelector).length === 1) return tagSelector
```

#### Priority 4: Parent Context + nth-of-type
Use the parent element's selector combined with `:nth-of-type()`.

```javascript
// main > section:nth-of-type(3)
const parent = el.parentElement
const siblings = Array.from(parent.children).filter(s => s.tagName === el.tagName)
const index = siblings.indexOf(el) + 1
return `${parentSelector} > ${el.tagName.toLowerCase()}:nth-of-type(${index})`
```

#### Priority 5: Data Attributes
If the element has CMS data attributes, use them as selectors.

```javascript
// [data-block-name="hero"]
if (el.dataset.blockName) return `[data-block-name="${CSS.escape(el.dataset.blockName)}"]`
if (el.dataset.component) return `[data-component="${CSS.escape(el.dataset.component)}"]`
```

#### Priority 6: Fallback — null
If no stable selector can be generated (highly dynamic content with no classes, IDs, or data attributes), set the selector to `null` and include the element's XPath as a debug reference. Do not include blocks with null selectors in the primary output -- move them to a separate `unstableBlocks` array.

---

### Step 6: Build the DetectedBlock Output

For each detected block, capture this data:

```typescript
interface DetectedBlock {
  index: number                    // Visual position index (0-based, top to bottom)
  selector: string | null          // CSS selector (null if unstable)
  tagName: string                  // HTML tag (SECTION, DIV, ARTICLE, etc.)
  classes: string[]                // All CSS classes on the element
  id: string | null                // Element ID if present
  dataAttributes: Record<string, string>  // All data-* attributes
  htmlSnippet: string              // First 500 chars of outerHTML
  textContent: string              // First 200 chars of textContent (trimmed)
  hasImages: boolean               // Contains img, picture, or svg
  hasHeadings: boolean             // Contains h1-h6
  hasLinks: boolean                // Contains a[href]
  childCount: number               // Number of direct child elements
  boundingBox: {
    x: number                      // Left edge in pixels
    y: number                      // Top edge in pixels
    width: number                  // Width in pixels
    height: number                 // Height in pixels
  }
  blockType: string                // Inferred type: 'hero', 'features', 'testimonials', 'cta', 'content', 'gallery', 'form', 'unknown'
}
```

#### Block Type Inference

Infer the block type from content signals:

| Block Type | Detection Signals |
|------------|------------------|
| `hero` | First major block, large image or video, single heading, CTA button |
| `features` | Grid/flex layout with 3-4 equal children, icon + heading + text pattern |
| `testimonials` | Contains quotation marks, cite/blockquote elements, person images |
| `cta` | Contains a form or prominent button, short text, contrasting background |
| `content` | Long-form text (> 500 chars), multiple paragraphs, few interactive elements |
| `gallery` | Multiple images in a grid/carousel, minimal text |
| `form` | Contains `<form>` element with inputs |
| `pricing` | Contains price-formatted text ($, /mo, /yr), comparison table |
| `navigation` | Multiple links in a list, category-like structure (not top nav) |
| `unknown` | Does not match any pattern |

---

### Step 7: Generate the Output

Write results to `data/blocks/{sanitized-path}.json`:

```json
{
  "meta": {
    "url": "https://example.com/landing-page",
    "viewport": { "width": 1440, "height": 900 },
    "detectedAt": "2024-12-15T10:30:00Z",
    "strategiesUsed": ["semantic", "class-patterns", "cms-attributes"],
    "totalCandidates": 24,
    "afterFiltering": 8
  },
  "blocks": [
    {
      "index": 0,
      "selector": ".hero-banner",
      "tagName": "SECTION",
      "classes": ["hero-banner", "full-width"],
      "id": null,
      "dataAttributes": { "block-name": "hero" },
      "htmlSnippet": "<section class=\"hero-banner full-width\"><div class=\"hero-content\"><h1>...",
      "textContent": "Welcome to Our Platform. Build faster with modern tools...",
      "hasImages": true,
      "hasHeadings": true,
      "hasLinks": true,
      "childCount": 2,
      "boundingBox": { "x": 0, "y": 0, "width": 1440, "height": 680 },
      "blockType": "hero"
    }
  ],
  "unstableBlocks": [],
  "pageHeight": 4200,
  "blockCoverage": 0.87
}
```

The `blockCoverage` field indicates what percentage of the page height is covered by detected blocks. Coverage below 0.6 suggests the detection missed significant content areas -- consider running with relaxed heuristics.

---

### Step 8: Clean Up

Always close the browser instance after detection, even if an error occurs:

```javascript
try {
  // ... detection logic
} finally {
  await browser.close()
}
```

---

## Workflow: Detecting Blocks on a Live Page

1. **User provides a URL** (e.g., "detect blocks on https://example.com/landing")
2. Launch Puppeteer, navigate to the URL, wait for rendering
3. Run the four detection strategies in priority order
4. Apply size, exclusion, and content heuristics
5. Deduplicate nested blocks
6. Generate CSS selectors for each block
7. Infer block types from content signals
8. Write results to `data/blocks/`
9. Present a summary: block count, types detected, coverage, and any blocks with unstable selectors
10. Close the browser

For multi-page analysis, repeat steps 2-9 for each URL and produce an aggregate summary showing which block types appear on which pages.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| No blocks detected | Page uses heavy JavaScript rendering that has not completed | Increase the post-navigation wait time to 3-5 seconds, or use `waitForSelector` on a known element |
| Too many blocks detected (> 20) | Page is highly modular (dashboard, admin panel) | Increase minimum size thresholds or restrict detection to `main > *` children only |
| Selectors break on subsequent loads | Page uses dynamic class names (CSS modules, styled-components) | Fall back to data attribute selectors or parent context + nth-of-type |
| Bounding boxes are wrong | Page has horizontal scroll or CSS transforms | Capture `getBoundingClientRect()` after scrolling the element into view |
| Block type inference is wrong | Content signals are ambiguous | Allow the user to override inferred types; store overrides in a separate config file |
| Puppeteer fails to launch | Missing system dependencies | Install Chromium dependencies: `npx puppeteer browsers install chrome` |

## Cross-References

- **design-system-extractor**: Consumes detected blocks to catalog block patterns and extract design tokens
- **site-auditor**: Provides the page inventory that determines which URLs to analyze for blocks
- **generative-page-pipeline**: Uses the block inventory to generate new pages with matching block structures
- **screenshot-capture**: Captures visual screenshots of individual blocks using the generated CSS selectors
