---
name: figma-token-sync
description: Bidirectionally sync CSS custom properties with Figma variables — push local tokens to Figma, pull Figma changes to CSS, and diff for CI drift detection. Use when "syncing Figma tokens", "Figma variables", "design token sync", or "CSS to Figma".
---

# Figma Token Sync

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| brand-design | "Figma sync", "Figma tokens", "design tokens", "CSS to Figma" | High | 4 projects |

Bidirectional synchronization between CSS custom properties and Figma variables. Supports three operations: PUSH (CSS to Figma), PULL (Figma to CSS), and DIFF (compare for drift). Handles responsive breakpoints as Figma modes, maps CSS token types to Figma variable types, and maintains a lock file for CI-friendly drift detection.

## When to Use
- Design tokens have been updated in CSS and need to propagate to Figma
- A designer has updated variables in Figma and the CSS needs to catch up
- CI pipeline needs to verify that Figma and CSS tokens are in sync
- A new brand profile has been converted to CSS tokens (via brand-css-generator) and needs to be reflected in Figma
- Responsive breakpoint tokens need to map to Figma variable modes

## Prerequisites

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FIGMA_ACCESS_TOKEN` | Yes | Personal access token or OAuth token from Figma (Settings > Account > Personal Access Tokens) |
| `FIGMA_FILE_KEY` | Yes | The file key from the Figma URL: `figma.com/design/{FILE_KEY}/...` |

### Configuration File: `figma-config.json`

This file drives all sync behavior. It must exist in the project root (or be specified via `--config` flag). See `references/figma-config-schema.md` for the full schema documentation.

Minimal example:
```json
{
  "fileKey": "abc123DEF456",
  "collections": [
    {
      "name": "Brand Tokens",
      "modes": {
        "desktop": "Desktop",
        "991": "Tablet",
        "767": "Mobile",
        "479": "Small Mobile"
      }
    }
  ],
  "tokenPrefix": "--",
  "excludeTokens": ["--tw-*", "--webkit-*"],
  "aliasTokens": {
    "--color-primary": "--brand-primary",
    "--color-secondary": "--brand-secondary"
  }
}
```

## Instructions

### Operation 1: PUSH (CSS to Figma)

Push local CSS custom properties to Figma as variables. This is the most common operation after generating brand CSS.

#### Step 1: Parse CSS tokens

Extract all custom properties from the CSS source. The parser handles four breakpoint tiers:

```javascript
// Parsed token structure
{
  desktop: {
    "--color-primary": "#635BFF",
    "--font-size-base": "1rem",
    "--space-md": "1rem"
  },
  991: {
    "--font-size-base": "0.9375rem",
    "--space-md": "0.875rem"
  },
  767: {
    "--font-size-base": "0.875rem",
    "--space-md": "0.75rem"
  },
  479: {
    "--font-size-base": "0.8125rem",
    "--space-md": "0.625rem"
  }
}
```

The parser extracts tokens from:
- `:root { }` blocks (mapped to `desktop`)
- `@media (max-width: 991px) { :root { } }` blocks (mapped to `991`)
- `@media (max-width: 767px) { :root { } }` blocks (mapped to `767`)
- `@media (max-width: 479px) { :root { } }` blocks (mapped to `479`)

Use `parseCSSTokens(cssString)` to extract and return the four-tier object.

#### Step 2: Classify tokens by Figma type

Each CSS token maps to a Figma variable type:

| CSS Pattern | Figma Type | Examples |
|-------------|-----------|----------|
| Hex color (`#RRGGBB`, `#RGB`) | `COLOR` | `--color-primary: #635BFF` |
| RGB/RGBA function | `COLOR` | `--color-overlay: rgba(0,0,0,0.5)` |
| HSL/HSLA function | `COLOR` | `--color-accent: hsl(160, 100%, 42%)` |
| Numeric with unit (`px`, `rem`, `em`, `%`) | `FLOAT` | `--font-size-base: 1rem` |
| Unitless number | `FLOAT` | `--line-height-body: 1.6` |
| Everything else | `STRING` | `--font-heading: 'Inter', sans-serif` |

Use `classifyToken(name, value)` to determine the type. The `figma-config.json` `unitOverrides` field can force specific tokens to a different type.

#### Step 3: Convert colors to Figma format

Figma's API uses RGBA floats (0-1 range), not hex strings:

```javascript
// hexToFigmaColor("#635BFF") returns:
{ r: 0.388, g: 0.357, b: 1.0, a: 1.0 }

// hexToFigmaColor("#635BFF80") returns (with alpha):
{ r: 0.388, g: 0.357, b: 1.0, a: 0.502 }
```

For `rem`/`em` values, convert to pixels using the base font size (default 16px) before sending to Figma as FLOAT. For percentage values, send as FLOAT divided by 100.

#### Step 4: Push to Figma API

Use the Figma Variables API to create or update variables:

```
POST https://api.figma.com/v1/files/{fileKey}/variables
Authorization: Bearer {FIGMA_ACCESS_TOKEN}
Content-Type: application/json
```

The request body contains `variableCollections` (with `action`, `name`, and `modes` array) and `variables` (with `action`, `name`, `variableCollectionId`, `resolvedType`, and `valuesByMode` keyed by mode ID). Use temporary IDs (e.g., `temp-collection-1`, `temp-var-1`) for CREATE actions — Figma assigns real IDs in the response.

**Rate Limiting**: Implement exponential backoff on 429 responses (1s, 2s, 4s, max 5 retries).

**Naming Convention**: Convert CSS token names to Figma `/`-separated paths: `--color-primary` becomes `color/primary`, `--font-size-base` becomes `font-size/base`.

#### Step 5: Update the lock file

After a successful push, write `figma-lock.json`:
```json
{
  "lastSync": "2026-02-28T14:30:00Z",
  "direction": "push",
  "tokenCount": 42,
  "fileKey": "abc123DEF456",
  "checksums": {
    "css": "sha256:abc123...",
    "figma": "sha256:def456..."
  }
}
```

---

### Operation 2: PULL (Figma to CSS)

Fetch Figma variables and reconstruct CSS custom properties.

#### Step 1: Fetch variables from Figma

```
GET https://api.figma.com/v1/files/{fileKey}/variables/local
Authorization: Bearer {FIGMA_ACCESS_TOKEN}
```

The response contains variable collections, modes, and values. Parse the response to extract all variables with their mode values.

#### Step 2: Resolve aliases

Figma variables can reference other variables (aliases). Resolve the alias chain before converting to CSS:
- If a variable's value is `{ type: "VARIABLE_ALIAS", id: "VariableID:123" }`, look up the referenced variable and use its resolved value
- Follow alias chains up to 10 levels deep (guard against circular references)

#### Step 3: Convert Figma values to CSS

Reverse the PUSH conversions: `figmaColorToHex()` converts RGBA floats back to hex (or `rgba()` if alpha < 1). For FLOAT values, convert back to `rem` using the `unitOverrides` in `figma-config.json`, defaulting to `px` if no override is specified.

#### Step 4: Reconstruct CSS

Generate `:root { }` with desktop values, then `@media (max-width: Npx) { :root { } }` blocks for each breakpoint in the config. Only include breakpoint blocks for tokens that actually change at that breakpoint — do not repeat identical values across breakpoints.

#### Step 5: Update the lock file (same as PUSH, with `direction: "pull"`)

---

### Operation 3: DIFF (Compare for Drift)

Compare CSS tokens against Figma variables and report discrepancies. This is designed for CI pipelines.

#### Step 1: Run both PARSE (CSS) and FETCH (Figma) in parallel

#### Step 2: Compare token-by-token and classify each as:

| Status | Meaning |
|--------|---------|
| `IN_SYNC` | Same value in both CSS and Figma |
| `VALUE_CHANGED` | Token exists in both but values differ |
| `CSS_ONLY` | Token exists in CSS but not in Figma |
| `FIGMA_ONLY` | Token exists in Figma but not in CSS |

#### Step 3: Output the diff report

The output JSON contains a `summary` (counts per status) and `changes` array (each with `token`, `status`, `cssValue`, `figmaValue`, `breakpoint`). For CI usage, exit with code 0 if all tokens are `IN_SYNC`, exit with code 1 if any drift is detected.

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| 403 Forbidden from Figma API | Token lacks variable permissions | Regenerate token with "File content" and "Variables" scopes in Figma Settings |
| 429 Too Many Requests | Rate limited | Exponential backoff should handle this; if persistent, batch variables into fewer API calls |
| Variables created in wrong collection | `figma-config.json` collection name doesn't match | Verify the collection name matches exactly (case-sensitive) |
| Modes not mapping correctly | Breakpoint keys in config don't match CSS media queries | Ensure `modes` keys (`desktop`, `991`, `767`, `479`) match the parsed breakpoints |
| Color values slightly off | Floating-point precision loss in conversion | Round to 3 decimal places in `hexToFigmaColor`; accept 1/255 tolerance in DIFF |
| Alias chain not resolving | Circular reference in Figma variables | PULL follows up to 10 levels; log a warning if depth exceeded |
| Lock file conflicts in CI | Multiple branches syncing simultaneously | Use branch-specific lock files or merge lock file changes automatically |

## Cross-References

- **brand-css-generator**: Generates the CSS custom properties that this skill syncs to Figma
- **design-system-extractor**: Extracts tokens from live sites as an alternative CSS source
