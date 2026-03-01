---
name: design-system-extractor
description: Extract design tokens and component styles from live websites using Puppeteer browser automation to capture computed styles, typography, colors, and button variants. Use when "extracting design systems", "reverse-engineering CSS", "design token extraction", or "capturing website styles".
---

# Design System Extractor

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| brand-design | "extract design system", "reverse-engineer CSS", "capture styles", "design tokens from site" | High | 5 projects |

Extract a complete design token set from a live website by launching a headless browser, navigating to the target URL, and capturing computed styles from the DOM. The output is a structured token object covering colors, typography, spacing, buttons, layout, and shadows — ready to feed into brand-css-generator or figma-token-sync.

## When to Use
- User wants to replicate or build upon an existing website's design system
- A live site needs to be reverse-engineered into CSS custom properties
- Brand colors, fonts, and spacing need to be extracted from a competitor or inspiration site
- An existing site is being migrated to a new platform and tokens need to be preserved
- A designer needs a token inventory from a site that has no documented design system

## Prerequisites

- **Puppeteer** must be installed: `npm install puppeteer` (or use the system-installed Chromium)
- The target URL must be publicly accessible (no authentication required) or you must provide cookies/headers for authenticated access

## Instructions

### Step 1: Launch the Browser and Navigate

Launch a headless Chromium instance via Puppeteer and navigate to the target URL. Wait for the page to be fully loaded including web fonts.

Launch with `headless: 'new'` and `args: ['--no-sandbox', '--disable-setuid-sandbox']`. Set viewport to 1440x900 (desktop). Navigate with `waitUntil: 'networkidle0'` and `timeout: 30000`. After navigation, await `document.fonts.ready` to ensure web fonts are rendered.

**Important**: Use `networkidle0` (zero outstanding requests for 500ms) rather than `domcontentloaded` — the latter fires before CSS and fonts are loaded, producing incorrect computed styles.

### Step 2: Extract Base Styles

Capture foundational styles from the `<body>` element via `getComputedStyle`: `fontFamily`, `fontSize`, `lineHeight`, `color`, `backgroundColor`. This establishes the baseline that all other extractions are relative to.

### Step 3: Extract Heading Hierarchy

Query `h1` through `h6` and capture computed styles for each present level: `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `color`, `letterSpacing`, `textTransform`. Not every page has all six levels — extract only those in the DOM.

### Step 4: Extract Link Styles

Capture link `color`, `textDecoration`, and `fontWeight` from the first `<a>` element. For hover states, use `page.hover()` to trigger the pseudo-class, then re-capture. Some sites use JS-based hover effects that may not trigger from synthetic events.

### Step 5: Extract Button Variants

Buttons are the highest-value extraction target because they have the most visual variation. Use an extended selector strategy to find all button variants:

Use extended selector arrays to find each variant. Try selectors in order and use the first match:

| Variant | Selectors (try in order) |
|---------|-------------------------|
| **Primary** | `.primary`, `.btn-primary`, `button[type="submit"]`, `.cta`, `.cta-button`, `[class*="btn-primary"]`, `[class*="button-primary"]`, `.hero button`, `.hero .btn` |
| **Secondary** | `.secondary`, `.btn-secondary`, `.btn-outline`, `[class*="btn-secondary"]`, `[class*="btn-ghost"]`, `[class*="button-outline"]` |
| **Link** | `.link-button`, `.text-link`, `.btn-link`, `a[class*="arrow"]`, `a[class*="link-btn"]`, `[class*="btn-text"]` |

For each matched element, extract the full visual profile via `getComputedStyle`: `backgroundColor`, `color`, `borderColor`, `borderWidth`, `borderStyle`, `borderRadius`, `padding`, `fontSize`, `fontWeight`, `fontFamily`, `textTransform`, `letterSpacing`, `boxShadow`, `transition`.

### Step 6: Extract Layout Tokens

Query container elements (`.container`, `.wrapper`, `[class*="container"]`, `main`, `.content`) and capture `maxWidth` values. For grid systems, find elements with `display: grid` and extract `gridTemplateColumns`, `gridTemplateRows`, and `gap`.

### Step 7: Extract Color Palette

Scan all DOM elements and collect unique values from `color`, `backgroundColor`, `borderColor`, and `outlineColor`. Filter out `transparent` and `rgba(0,0,0,0)`.

**Post-processing**: Convert all `rgb()`/`rgba()` values to hex codes, deduplicate near-identical colors (within 5 units per channel), and sort by frequency. The most frequently used colors are the primary palette; rarely-used colors are accents or one-offs. Limit to the first 500 elements on very large pages to avoid timeouts.

### Step 8: Extract Spacing Patterns

Collect `paddingTop/Bottom/Left/Right` and `marginTop/Bottom/Left/Right` from structural elements (`section`, `div`, `article`, `header`, `footer`, `main`, `aside`). Count frequency of each value.

Sort by frequency and identify the spacing scale (e.g., 4px, 8px, 16px, 24px, 32px, 48px, 64px). Most design systems use a base-4 or base-8 scale.

### Step 9: Extract Shadow Tokens

Collect all unique `boxShadow` values (excluding `none`) from the DOM. Classify into `sm`, `md`, `lg` tiers based on blur radius: sm (0-4px blur), md (5-12px), lg (13px+).

### Step 10: Detect and Download Web Fonts (Optional)

If extracted `fontFamily` values include custom fonts, iterate through `document.styleSheets` and find `CSSFontFaceRule` instances. Extract `fontFamily`, `src`, `fontWeight`, and `fontStyle`. Cross-origin stylesheets will throw `SecurityError` — skip those silently.

For Google Fonts, reconstruct the import URL from detected families (e.g., `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap`). For Typekit (Adobe Fonts), the `@import` URL contains the kit ID — extract and preserve it.

### Step 11: Assemble the Output

Combine all extracted data into the two output types:

#### ComputedDesign (raw extraction)

Contains the raw `getComputedStyle` values organized by category:
- `body` — fontFamily, fontSize, lineHeight, color, backgroundColor
- `headings` — Record of h1-h6, each with fontFamily, fontSize, fontWeight, lineHeight, color
- `links` — color, textDecoration
- `buttons` — primary/secondary/link, each with the full button style properties (or null if not found)

#### ExtractedDesign (processed tokens)

The processed, design-system-ready output:

```typescript
interface ExtractedDesign {
  colors: {
    primary: string;       // Most used non-black/white color
    secondary: string;     // Second most used
    accent: string;        // Third most used
    background: string;    surface: string;
    text: string;          textMuted: string;
    palette: string[];     // Full deduplicated palette (hex)
  };
  typography: {
    headingFamily: string; bodyFamily: string;
    monoFamily: string | null;
    baseFontSize: string;
    scaleRatio: number;    // From heading size progression
    weights: number[];
  };
  buttons: { primary: ButtonTokens; secondary: ButtonTokens; borderRadius: string; };
  layout: { containerMax: string; gridColumns: number; gridGap: string; breakpoints: string[]; };
  spacing: {
    scale: string[];       // e.g., ["4px", "8px", "16px", ...]
    baseUnit: number;      // Detected base (4 or 8)
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
  };
  fonts: {
    sources: FontSource[];
    googleFontsUrl: string | null;
    typekitId: string | null;
  };
}
```

### Step 12: Close the Browser

Always wrap extraction in a `try/finally` block and call `browser.close()` in the finally. Leaving headless Chromium processes running consumes significant memory and can crash the system.

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| All fonts show as system defaults | Page fonts haven't loaded when styles are captured | Ensure `document.fonts.ready` completes before extraction; increase `networkidle0` timeout |
| Colors are all `rgba(0,0,0,0)` | Elements have transparent backgrounds inheriting from parent | Walk up the DOM tree to find the nearest non-transparent ancestor |
| No buttons found | Site uses non-standard class names | Add site-specific selectors to the button selector arrays; inspect the DOM first |
| Cross-origin stylesheet error | CSS loaded from a CDN with restrictive CORS | These rules are inaccessible via `cssRules`; fetch the stylesheet URL directly and parse it |
| Computed styles differ from visual appearance | CSS animations or transitions in mid-flight | Add a 2-second delay after navigation before capturing styles |
| Missing hover/active states | Synthetic events don't trigger all CSS pseudo-classes | Use `page.hover()` for hover; for active/focus, use `CDP` session to force pseudo-class state |
| Extraction takes > 30 seconds | `querySelectorAll('*')` on a massive DOM | Limit color/spacing extraction to the first 500 elements; sample rather than exhaustively scan |
| Headless Chromium crashes | Out of memory on large pages | Use `--disable-dev-shm-usage` flag and limit viewport to reduce rendering memory |

## Cross-References

- **brand-extractor**: For when you need brand identity analysis beyond visual tokens (tone, values, positioning)
- **brand-css-generator**: Consumes ExtractedDesign to generate CSS custom property sheets and full design branches
- **figma-token-sync**: Pushes extracted tokens to Figma variables for designer handoff
