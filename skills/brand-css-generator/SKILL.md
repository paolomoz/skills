---
name: brand-css-generator
description: Generate CSS custom property overrides and complete design branches from brand profiles, ensuring WCAG AA compliance and design coherence. Use when "generating brand CSS", "creating design tokens", "brand theming", or "CSS from brand profile".
---

# Brand CSS Generator

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| brand-design | "brand CSS", "design tokens", "brand theme", "CSS overrides" | High | 5 projects |

Generate production-ready CSS from a BrandProfile — either as a lightweight custom property override sheet or as a full design branch with atomic file generation, responsive breakpoints, and WCAG AA contrast enforcement. The skill bridges the gap between brand identity and implementable design code.

## When to Use
- A BrandProfile has been extracted (via brand-extractor) and needs to become CSS
- User wants to theme an existing site/template with a new brand's colors, fonts, and spacing
- User needs a complete design branch with per-block CSS files
- Design tokens need to be generated for a design system
- User wants to preview multiple design options with CSS-only variation

## Instructions

### Step 1: Gather Inputs

You need two inputs to generate brand CSS:

1. **BrandProfile** — the structured brand identity (from brand-extractor or user-provided)
2. **Design context** — one of:
   - A design option object with `cssTokenHints` (from a design pipeline)
   - A brief or description of the target design
   - An existing CSS file to override/extend
   - A template or site to theme

If no BrandProfile exists, run brand-extractor first. Do not attempt to generate CSS from vague descriptions — the profile ensures consistency across all generated files.

### Step 2: Choose Generation Mode

#### Mode A: CSS Custom Property Overrides (Lightweight)

Use this mode when theming an existing site or generating design tokens. The output is a single CSS string with `:root { }` custom properties.

**Function signature:**
```typescript
generateBrandCssOverrides(
  profile: BrandProfile,
  briefContent: string,
  design: DesignOption
): Promise<string>
```

**Output format** — a `:root` block organized into named sections:
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  /* Brand Colors: primary, dark, light, secondary, accent, background, surface, text, text-muted */
  --color-primary: #635BFF;
  --color-secondary: #0A2540;
  --color-accent: #00D4AA;
  /* Typography: font families (heading, body, mono), sizes (base through 3xl), line-heights */
  --font-heading: 'Inter', system-ui, sans-serif;
  --font-size-base: 1rem;
  /* Spacing: xs (0.25rem) through 2xl (8rem) */
  /* Layout: container-max, border-radius, border-radius-lg */
  /* Shadows: sm, md, lg */
}
```

**Rules for Mode A:**
- The `@import` for Google Fonts (if used) MUST appear BEFORE the `:root` block — browsers ignore `@import` after any other rules
- Every color must pass WCAG AA contrast ratio (4.5:1 for normal text, 3:1 for large text) against its intended background
- Include both light and dark variants of the primary color for hover states
- Use `system-ui` as the final fallback in all font stacks
- Token names must follow the existing site's naming convention if one exists

#### Mode B: Full Design Branch Generation (Enterprise)

Use this mode when generating a complete themed version of a site with per-block CSS files, responsive breakpoints, and a design critique pass.

**Step 2B-1: Generate atomic CSS files**

Create the following file structure:
```
design-branch/
  styles.css          # Global overrides and custom properties
  fonts.css           # @import rules for web fonts
  hero.css            # Hero/banner block styles
  features.css        # Feature grid/list block styles
  testimonials.css    # Testimonial block styles
  cta.css             # Call-to-action block styles
  footer.css          # Footer block styles
  [block-name].css    # One file per content block
```

**Step 2B-2: Maintain reference integrity**

This is critical — the generated CSS must work as an override layer, not a replacement.

- Preserve ALL existing class names and selectors from the base template
- Never rename classes — only add properties or override values
- If the base uses `.hero-title`, your override targets `.hero-title`, not a new `.brand-hero-title`
- Comment any selector that is purely additive (not overriding an existing rule)

**Step 2B-3: Responsive breakpoints**

All block CSS files must include three mobile-first breakpoint tiers: default (< 600px), tablet (600px+), and desktop (900px+). Each tier adjusts font sizes, padding, and grid columns. Use `var()` references to spacing and typography tokens rather than hardcoded values.

### Step 3: WCAG AA Contrast Enforcement

For every text-color / background-color pair, compute the contrast ratio using relative luminance: `(L1 + 0.05) / (L2 + 0.05)`. Required ratios: normal text >= 4.5:1, large text (>= 18px or >= 14px bold) >= 3.0:1, UI components >= 3.0:1. If a pair fails, adjust the text color darker or the background lighter until it passes. Document every adjustment in a CSS comment showing the original ratio, the adjusted value, and the passing ratio.

### Step 4: Safety Sanitization Rules

After generating CSS, apply these mandatory sanitization rules. These address recurring production issues discovered across multiple projects.

| Rule | What to do | Why |
|------|-----------|-----|
| Strip `@font-face` from fonts.css | Keep only `@import` rules in fonts.css — remove any `@font-face` declarations | `@font-face` with local paths breaks on deploy; `@import` from Google Fonts/CDN is reliable |
| Remove vertical margin on sections | Delete `margin-top` and `margin-bottom` from any section-level container | Section spacing is controlled by the layout system, not individual sections — adding margin causes double-spacing |
| Fix `z-index: -1` on hero images | Change to `z-index: 0` | Negative z-index pushes images behind the page background, making them invisible |
| Remove `opacity: 0` on lazy images | Delete any `opacity: 0` rule on `img` or `picture` elements | Lazy-load libraries manage opacity transitions; a CSS `opacity: 0` permanently hides images if JS fails |
| No layout property animations | Never use `transition` or `animation` on `width`, `height`, `top`, `left`, `margin`, `padding` | Layout animations cause reflow jank; use `transform` and `opacity` only |
| No bounce/elastic easing | Never use `cubic-bezier` curves that overshoot (values > 1.0 in p2/p4) | Bounce easing causes elements to visually overlap neighbors during animation |
| No `!important` | Never use `!important` in generated CSS | Specificity wars are unsustainable; use proper selector specificity instead |
| Google Fonts import position | `@import` must be the very first rule in the file, before any selectors | Browsers silently ignore `@import` after other rules |

### Step 5: Design Critique Pass

After generating all files, review the complete output for these common design coherence issues:

**CTA Hierarchy**: There should be exactly one primary CTA style and one secondary. If three or more button styles exist with similar visual weight, the hierarchy is broken. Fix by increasing contrast between primary and secondary.

**Spacing Monotony**: If more than 3 consecutive sections use the same padding value, the rhythm is monotonous. Alternate between at least 2 spacing values (e.g., `--space-lg` and `--space-xl`).

**Color Overuse**: If the primary brand color appears in more than 40% of elements, the design lacks hierarchy. Reserve primary color for CTAs and key headings; use neutrals and the surface color for everything else.

**Typography Hierarchy**: There must be clear visual distinction between at least 4 levels: page title, section heading, body text, and caption/meta. If any two adjacent levels are within 2px of each other, increase the size difference.

**Whitespace Ratio**: At least 30% of the viewport should be whitespace (background color showing through). If content is wall-to-wall, increase padding and reduce element widths.

### Step 6: Output and File Delivery

For Mode A, return the CSS string directly. For Mode B, write all files to the target directory and provide a summary listing each file, the number of custom properties, breakpoints used, WCAG AA pass/fail status, and which sanitization rules were applied.

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Fonts not loading | `@import` placed after `:root` block | Move all `@import` rules to the very top of the file |
| Colors look washed out | WCAG adjustment pushed colors too far toward neutral | Use a darker background instead of lightening the text color |
| Hero image invisible | `z-index: -1` in generated CSS | Sanitization rule should catch this; verify it was applied |
| Buttons all look the same | Missing CTA hierarchy pass | Ensure primary uses brand color fill and secondary uses outline/ghost variant |
| Double spacing between sections | Vertical margin on section containers | Sanitization rule should strip these; verify |
| Animations are janky | Animating layout properties | Replace with `transform: translateX()` / `opacity` transitions |

## Cross-References

- **brand-extractor**: Produces the BrandProfile input required by this skill
- **design-system-extractor**: Extracts existing tokens from a live site to use as a base for overrides
- **figma-token-sync**: Pushes generated CSS tokens to Figma variables for designer handoff
