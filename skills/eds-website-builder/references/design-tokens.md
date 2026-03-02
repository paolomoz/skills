# Token-Driven Design System

## Overview

EDS projects use CSS custom properties (design tokens) to maintain visual consistency across blocks. Each block defines its own token file that centralizes all customizable values — colors, typography, spacing, borders, effects. This makes it easy to re-skin blocks by changing token values without touching structural CSS.

## Architecture

```
blocks/
└── {blockname}/
    ├── {blockname}.js              # Decoration logic
    ├── {blockname}.css             # Structural styles (uses tokens)
    ├── {blockname}-tokens.css      # Design tokens (all customizable values)
    └── {blockname}-measurements.txt # Figma measurements reference (optional)
```

The token file is imported at the top of the block's CSS:

```css
/* cards-teaser.css */
@import url('./cards-teaser-tokens.css');

main .cards-teaser {
  max-width: var(--cards-teaser-max-width);
  background: var(--cards-teaser-background);
  /* ... structural layout using token values ... */
}
```

## Token Naming Convention

All tokens follow a strict naming pattern:

```
--{blockname}-{element}-{property}
```

Examples:
```css
--cards-teaser-max-width              /* Block-level property */
--cards-teaser-heading-font-size      /* Element + property */
--cards-teaser-heading-color          /* Element + property */
--cards-teaser-button-background      /* Element + property */
--cards-teaser-button-hover-background /* Element + state + property */
--cards-teaser-card-border-radius     /* Sub-element + property */
```

## Token Categories

Every block token file should cover these categories:

### 1. Layout & Dimensions

```css
:root {
  /* Container */
  --{block}-max-width: 1180px;
  --{block}-padding-top: 40px;
  --{block}-padding-bottom: 40px;
  --{block}-padding-left: 20px;
  --{block}-padding-right: 20px;

  /* Grid/flex layout */
  --{block}-columns: 4;
  --{block}-gap: 10px;
  --{block}-min-width: 248px;      /* Grid item min-width */
}
```

### 2. Colors

```css
:root {
  /* Backgrounds */
  --{block}-background: #ebefee;
  --{block}-card-background: #ffffff;

  /* Text colors */
  --{block}-heading-color: #830051;
  --{block}-body-color: #363b3b;

  /* Interactive colors */
  --{block}-button-background: #d0006f;
  --{block}-button-hover-background: #a80059;
  --{block}-button-color: #ffffff;

  /* Borders */
  --{block}-border-color: #ebefee;
}
```

### 3. Typography

```css
:root {
  /* Headings */
  --{block}-heading-font-family: "Lexia VF", Georgia, serif;
  --{block}-heading-font-size: 26px;
  --{block}-heading-font-weight: 400;
  --{block}-heading-line-height: 34px;

  /* Body text */
  --{block}-body-font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
  --{block}-body-font-size: 18px;
  --{block}-body-font-weight: 400;
  --{block}-body-line-height: 28px;

  /* Buttons */
  --{block}-button-font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
  --{block}-button-font-size: 16px;
  --{block}-button-font-weight: 600;
  --{block}-button-line-height: 24px;
}
```

### 4. Spacing

```css
:root {
  --{block}-content-padding: 24px;
  --{block}-heading-padding-top: 20px;
  --{block}-body-padding-top: 16px;
  --{block}-button-padding: 8px 16px;
  --{block}-button-min-height: 42px;
}
```

### 5. Borders & Radius

```css
:root {
  --{block}-border-width: 0px;
  --{block}-border-style: none;
  --{block}-border-radius: 8px;           /* Cards, images */
  --{block}-button-border-radius: 4px;    /* Buttons */
}
```

### 6. Effects & Transitions

```css
:root {
  --{block}-transition-duration: 200ms;
  --{block}-transition-timing: ease;
  --{block}-image-aspect-ratio: 4/3;      /* Or 16/9 */
  --{block}-image-object-fit: cover;
}
```

## Complete Token File Example

```css
/* cards-teaser-tokens.css */
:root {
  /* Layout */
  --cards-teaser-max-width: 1180px;
  --cards-teaser-padding-top: 40px;
  --cards-teaser-padding-bottom: 40px;
  --cards-teaser-padding-left: 20px;
  --cards-teaser-padding-right: 20px;
  --cards-teaser-columns: 4;
  --cards-teaser-gap: 10px;
  --cards-teaser-min-width: 248px;

  /* Container */
  --cards-teaser-background: #ebefee;
  --cards-teaser-card-background: #ffffff;
  --cards-teaser-card-border-radius: 8px;
  --cards-teaser-card-border-width: 0px;
  --cards-teaser-card-border-style: none;
  --cards-teaser-content-padding: 24px;

  /* Image */
  --cards-teaser-image-aspect-ratio: 4/3;
  --cards-teaser-image-object-fit: cover;

  /* Heading */
  --cards-teaser-heading-font-family: "Lexia VF", Georgia, serif;
  --cards-teaser-heading-font-size: 26px;
  --cards-teaser-heading-font-weight: 400;
  --cards-teaser-heading-line-height: 34px;
  --cards-teaser-heading-color: #4f0031;

  /* Body */
  --cards-teaser-body-font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
  --cards-teaser-body-font-size: 18px;
  --cards-teaser-body-font-weight: 400;
  --cards-teaser-body-line-height: 28px;
  --cards-teaser-body-color: #363b3b;

  /* Button */
  --cards-teaser-button-font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
  --cards-teaser-button-font-size: 16px;
  --cards-teaser-button-font-weight: 600;
  --cards-teaser-button-line-height: 24px;
  --cards-teaser-button-background: #d0006f;
  --cards-teaser-button-hover-background: #a80059;
  --cards-teaser-button-color: #ffffff;
  --cards-teaser-button-border-radius: 4px;
  --cards-teaser-button-padding: 8px 16px;
  --cards-teaser-button-min-height: 42px;

  /* Transitions */
  --cards-teaser-transition-duration: 200ms;
  --cards-teaser-transition-timing: ease;
}
```

## Measurement Files

When implementing blocks from a design system (e.g., Figma), create measurement reference files that capture exact values from the design:

```
# cards-teaser-measurements.txt

## Container
- Max width: 1180px
- Background: #EBEFEE
- Padding: 40px 20px

## Card
- Background: #FFFFFF
- Border radius: 8px
- Content padding: 24px
- Gap between cards: 10px
- Min card width: 248px
- Columns: 4 (desktop), 2 (tablet), 1 (mobile)

## Image
- Aspect ratio: 4:3
- Object fit: cover
- Border radius: 8px 8px 0 0 (top corners only)

## Typography
- Heading: Lexia VF, 26px, weight 400, line-height 34px, color #4F0031
- Body: Inter, 18px, weight 400, line-height 28px, color #363B3B
- Button: Inter, 16px, weight 600, line-height 24px, color #FFFFFF

## Button
- Background: #D0006F
- Hover: #A80059
- Padding: 8px 16px
- Min height: 42px
- Border radius: 4px
- Transition: 200ms ease
```

These files serve as a bridge between the designer's Figma measurements and the developer's CSS tokens. Keep them as plain text checklists for easy reference.

## Typography Scale

A consistent typography hierarchy across all blocks:

| Role | Font Family | Size | Weight | Line Height | Color |
|------|------------|------|--------|-------------|-------|
| Hero heading | Lexia VF | 56px | 400 | 62px | #ffffff (on dark bg) |
| Intro heading | Lexia VF | 46px | 400 | 52px | #830051 |
| Section heading | Lexia VF | 36px | 400 | 44px | #830051 |
| Card heading | Lexia VF | 26px | 400 | 34px | #4f0031 |
| Body text | Inter | 16-18px | 400 | 24-28px | #363b3b |
| Button text | Inter | 16px | 600 | 24px | #ffffff |

## Color Palette

Brand colors applied consistently via tokens:

| Name | Hex | Usage |
|------|-----|-------|
| AZ Magenta | #830051 | Section headings, primary brand |
| Dark Magenta | #4f0031 | Card headings |
| CTA Pink | #d0006f | Buttons, interactive elements |
| CTA Hover | #a80059 | Button hover state |
| Dark Gray | #363b3b | Body text |
| Light Gray | #ebefee | Section backgrounds, borders |
| Off-White | #f8f8f8 | Alternate section backgrounds |
| Dark | #2e3232 | Dark section backgrounds |
| White | #ffffff | Card backgrounds, button text |

## Button System

Consistent button tokens across all blocks:

```css
/* Standard filled button (primary) */
--button-background: #d0006f;
--button-hover-background: #a80059;
--button-color: #ffffff;
--button-border: 1px solid #d0006f;

/* Ghost/outlined button (secondary) */
--button-background: transparent;
--button-hover-background: #d0006f;
--button-color: #d0006f;
--button-hover-color: #ffffff;
--button-border: 2px solid #d0006f;

/* Shared */
--button-padding: 8px 16px;
--button-min-height: 42px;
--button-border-radius: 4px;
--button-font-size: 16px;
--button-font-weight: 600;
--button-transition: 200ms ease;
```

## Standard Layout

All blocks share a consistent max-width:

```css
--max-width: 1180px;  /* Block content area */
```

With a standard vertical rhythm:
- `40px` — Between sections
- `20px` — Between section heading and content
- `16px` — Between content elements
- `8px` — Small gaps (title block, inline elements)
- `10px` — Card grid gaps
- `30px` — Carousel slide gaps

## Workflow: From Figma to Tokens

1. **Export measurements** from Figma (use Figma's inspect panel)
2. **Create `{block}-measurements.txt`** with raw values organized by element
3. **Create `{block}-tokens.css`** translating measurements to CSS custom properties
4. **Import tokens** at the top of `{block}.css`
5. **Use `var(--token)` everywhere** in the structural CSS — never hardcode values
6. **Test responsive** — tokens should work across breakpoints, add media queries in the structural CSS (not the token file) for responsive overrides

## Tips

- **Token files contain only `:root` declarations** — no selectors, no structural CSS
- **One token file per block** — keeps customization isolated
- **All visual values come from tokens** — if you're hardcoding a color or size in the structural CSS, it should be a token
- **Measurement files are optional but valuable** — they document the designer's intent and make it easy to verify accuracy
- **Keep the naming hierarchy flat** — `--block-element-property`, not deeply nested
- **Responsive adjustments go in the structural CSS** via media queries, not in the token file
