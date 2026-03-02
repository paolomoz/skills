# Brand Analysis & Guidelines

## Overview

Before building an EDS site, analyze an existing reference site (client's current site, competitor, or brand guidelines) to extract a structured brand guide. This ensures every block, page, and content piece is visually and tonally consistent.

The output is two documents:
1. **Visual Design Analysis** — Layout patterns, typography, colors, spacing, imagery style, component inventory
2. **Brand Voice & Imagery Skill** — Copy patterns, tone, vocabulary, regulatory language, imagery tiers, templates

These become the authoritative reference for all content and design decisions.

## Phase 1: Screenshot the Reference Site

### Tool: Playwright Screenshot Script

Create a script to capture full-page screenshots of key pages:

```javascript
// tools/screenshot-reference.js
const { chromium } = require('playwright');

const PAGES = [
  { name: 'homepage', url: 'https://example.com/' },
  { name: 'about', url: 'https://example.com/about' },
  { name: 'product-1', url: 'https://example.com/product-1' },
  { name: 'product-2', url: 'https://example.com/product-2' },
  // Add all representative pages
];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  for (const { name, url } of PAGES) {
    console.log(`Capturing ${name}...`);
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.screenshot({
      path: `analysis/screenshots/${name}.png`,
      fullPage: true,
    });
  }

  await browser.close();
  console.log(`Done. ${PAGES.length} screenshots saved to analysis/screenshots/`);
})();
```

```bash
mkdir -p analysis/screenshots
npx playwright install chromium
node tools/screenshot-reference.js
```

### Advanced: Removing Overlays

Real-world sites often have cookie banners, HCP gates, or modal overlays. Add overlay removal:

```javascript
async function nukeOverlays(page) {
  await page.evaluate(() => {
    // Accept cookie consent
    document.querySelector('[id*="onetrust"] button.accept, .cookie-accept')?.click();

    // Remove fixed/sticky overlays
    document.querySelectorAll('*').forEach((el) => {
      const style = getComputedStyle(el);
      if (style.position === 'fixed' || style.position === 'sticky') {
        if (el.tagName !== 'HEADER' && el.tagName !== 'NAV') {
          el.remove();
        }
      }
    });

    // Remove modal backdrops
    document.querySelectorAll('[class*="overlay"], [class*="modal"], [class*="backdrop"]')
      .forEach((el) => el.remove());

    // Restore scrolling
    document.body.style.overflow = 'auto';
    document.documentElement.style.overflow = 'auto';
  });
}

// Usage in screenshot loop:
await page.goto(url, { waitUntil: 'networkidle' });
await nukeOverlays(page);
await page.waitForTimeout(1000);
await page.screenshot({ path: `analysis/screenshots/${name}.png`, fullPage: true });
```

### Project QA Screenshots

Create a second script for capturing your own site's pages for QA:

```javascript
// tools/screenshot-project.js
const PAGES = [
  { name: 'home', path: '/' },
  { name: 'product', path: '/product' },
  { name: 'product-efficacy', path: '/product/efficacy' },
  // ... all key pages
];
const BASE_URL = 'https://main--{repo}--{owner}.aem.page';
```

This gives you before/after comparison screenshots during development.

### What to Capture

Aim for 10-20 pages covering:
- **Homepage** — overall brand impression, navigation, card patterns
- **Category/listing pages** — information architecture, content grouping
- **Detail pages** — content depth, data presentation, CTAs
- **About/corporate pages** — brand voice at its most authentic
- **Contact/form pages** — interaction patterns, form design

### Supplementary: Text Extraction

Also extract raw text from each page for copy analysis:

```bash
# Use WebFetch or curl to grab page content
curl -s "https://example.com/page" | python3 -c "
import sys
from html.parser import HTMLParser
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'):
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'):
            self.skip = False
    def handle_data(self, data):
        if not self.skip and data.strip():
            self.text.append(data.strip())
p = TextExtractor()
p.feed(sys.stdin.read())
print('\n'.join(p.text))
" > analysis/text/page.txt
```

## Phase 2: Visual Design Analysis

Analyze the screenshots systematically. Create a markdown document covering:

### 2.1 Global Chrome

| Element | Details to Capture |
|---------|-------------------|
| **Header** | Logo placement, nav items, mobile behavior, background color |
| **Footer** | Column layout, links, social icons, legal text |
| **Utility bars** | Top bars (disclaimers, PI links), height, colors |
| **Breadcrumb** | Format, separator character, positioning |

### 2.2 Color System

Extract and document:
- **Primary brand color** (logo, CTAs, active states)
- **Secondary colors** (accents, highlights)
- **Text colors** (headings, body, muted)
- **Background colors** (sections, cards, alternating)
- **Product-specific accent colors** (if multi-product site)

Use browser dev tools or a color picker to get exact hex values.

### 2.3 Typography

| Property | What to Capture |
|----------|----------------|
| **Heading font** | Family, weight, style (serif/sans), approximate sizes |
| **Body font** | Family, weight, line-height, color |
| **Display text** | Large statistics, hero text, special treatments |
| **CTA text** | Size, weight, case (sentence/title/upper) |

### 2.4 Spacing & Layout

- **Max content width** (usually 1200px, 1400px, or full-width)
- **Section spacing** (vertical padding between major sections)
- **Card grid** (columns, gutter width, responsive behavior)
- **Card styling** (borders, shadows, border-radius, padding)
- **Button styling** (border-radius, padding, colors)

### 2.5 Component Inventory

Document each reusable component pattern:
- **Hero variants** (image left, image right, full-bleed, text-only)
- **Card variants** (image card, icon card, data card, CTA card)
- **Accordion/FAQ** patterns
- **Data display** (statistics, charts, callouts)
- **Alert/callout boxes**
- **Contact sections**
- **Resource/download sections**

### 2.6 Imagery Style

Categorize the types of imagery used:
- **Photography style** (editorial, lifestyle, clinical, abstract)
- **Illustration style** (flat, detailed, iconographic)
- **Icon system** (shape, style, colors, sizes)
- **Image treatment** (rounded corners, overlays, borders)

### Output Template

```markdown
# [Site Name] — Visual Design & Layout Analysis

> Based on browser screenshots of [N] pages taken [date]

## 1. Global Chrome (Header, Footer, Utility Bars)
### 1.1 Header
### 1.2 Footer

## 2. Page Types Observed
### 2.1 Homepage
### 2.2 Category Pages
### 2.3 Detail Pages

## 3. Visual Design System
### 3.1 Color Usage
### 3.2 Typography
### 3.3 Imagery Style
### 3.4 Spacing & Layout

## 4. Component Patterns
### 4.1 Card Patterns
### 4.2 Data Display Patterns
### 4.3 Accordion Pattern
### 4.4 Alert/Callout Box

## 5. Mapping to EDS Block Library
| Site Pattern | EDS Block | Notes |
|---|---|---|
| ... | ... | ... |
```

The block mapping table (Section 5) is critical — it connects the visual analysis to your EDS implementation, telling you which blocks to use or build for each pattern.

## Phase 3: Brand Voice & Imagery Skill

Analyze the extracted text to create a comprehensive copy guide.

### 3.1 Voice Overview

Define the core voice attributes:

| Attribute | Description | Example |
|-----------|-------------|---------|
| Supportive | ... | "How can we help?" |
| Evidence-led | ... | "56% reduction (P<0.001)" |
| Action-oriented | ... | "Explore the data" |

Also define what the voice is NOT (anti-patterns).

### 3.2 Voice by Page Type

Different page types often have different registers:
- **Homepage**: Warm, invitational, broad
- **Category pages**: Authoritative, evidence-driven
- **Product pages**: Clinical, precise, benefit-led
- **Data pages**: Bold, assertive, data-forward

Document heading patterns, body copy patterns, and CTA patterns for each type.

### 3.3 Sentence-Level Patterns

Extract actual patterns from the reference site:
- **Opening sentences** — how pages begin
- **Benefit statements** — how outcomes are framed
- **CTAs** — exact phrasing used for call-to-action text
- **Vocabulary preferences** — preferred vs. avoided words

### 3.4 Regulatory/Legal Language (if applicable)

For regulated industries (pharma, finance, insurance):
- Trademark conventions (®, ™, first/subsequent mention)
- Required disclaimers and their exact wording
- Approval/compliance codes
- Adverse event reporting language
- Prescribing information format
- Reference/citation format

### 3.5 Imagery Guidelines

Create tiered imagery guidance:
- **Tier 1**: Hero/signature imagery — style, subjects, mood
- **Tier 2**: Lifestyle/secondary imagery — settings, diversity, lighting
- **Tier 3**: Product/technical imagery — angles, backgrounds
- **Tier 4**: Abstract/dramatic imagery — when and where to use

For each tier, include:
- Where it's used on the site
- Visual characteristics
- Emotional tone
- AI image generation prompt guidance
- Do's and don'ts

### 3.6 Product/Sub-Brand Colors

If the site has multiple products or sections with their own identity:

| Product | Brand Color | Hex | Imagery Warmth |
|---------|------------|-----|----------------|
| Product A | Amber | #E88A00 | Warm golden |
| Product B | Teal | #00827F | Cool medical |

### 3.7 Copy Templates

Create fill-in-the-blank templates for common page sections:

```
[H1] [Benefit-led headline]
[Paragraph] [Product] is indicated for [indication language].
[CTA] [Verb] [object]
```

### Output Template

```markdown
# [Brand Name] — Brand Voice & Imagery Skill

> Derived from analysis of [N] pages, [date]
> Use this file as the authoritative guide when writing copy or selecting imagery.

## 1. Brand Voice Overview
### Core Voice Attributes
### What the Voice Is NOT

## 2. Voice by Page Type
### 2.1 Homepage
### 2.2 Category Pages
### 2.3 Product Pages

## 3. Sentence-Level Patterns
### 3.1 Sentence Structure
### 3.2 Vocabulary Preferences
### 3.3 Trademark & Regulatory Conventions

## 4. Imagery Guidelines
### 4.1 Imagery Tiers
### 4.2 Icon System
### 4.3 Imagery Do's and Don'ts

## 5. Product Brand Colors

## 6. Copy Templates
### 6.1 Hero Section Template
### 6.2 Category Introduction Template
### 6.3 Product Card Template

## 7. Quick Reference: Writing Checklist
```

## Phase 4: Using the Guidelines

### In AGENTS.md / CLAUDE.md

Reference the brand documents so Claude uses them automatically:

```markdown
## Brand Guidelines
- Visual analysis: `analysis/visual-analysis.md`
- Brand voice & imagery: `brand-voice.md`
- Always consult these when writing copy or making design decisions.
```

### In Block Development

When building blocks, cross-reference:
1. The **component patterns** from the visual analysis — "what does this look like?"
2. The **copy templates** from the brand voice guide — "what goes in this block?"
3. The **EDS block mapping** — "which block do I use?"

### In Content Creation

When writing draft content for pages:
1. Check the **voice by page type** section — match the register
2. Use the **copy templates** — fill in the blanks
3. Apply the **writing checklist** — verify compliance
4. Select imagery following the **imagery tiers** guidance

## Tips

- **Start with screenshots, not assumptions** — the visual analysis grounds everything in reality
- **Extract actual copy, don't paraphrase** — real examples are more useful than descriptions
- **Map everything to EDS blocks** — the bridge from analysis to implementation
- **Update guidelines as the project evolves** — they're living documents, not one-time artifacts
- **The brand voice guide is the single most valuable artifact** — it ensures every piece of content feels consistent, even when different people (or AI agents) create it
- **Include AI image generation prompts** — if the project uses AI imagery, bake guidance into the brand doc
