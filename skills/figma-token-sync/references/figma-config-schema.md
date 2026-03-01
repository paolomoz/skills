---
title: figma-config.json Schema Reference
---

# figma-config.json Schema

Complete schema documentation for the Figma Token Sync configuration file.

## Location

The configuration file must be named `figma-config.json` and placed in the project root, or specified via the `--config` flag.

## Full Schema

```json
{
  "fileKey": "string (required)",
  "collections": [
    {
      "name": "string (required)",
      "modes": {
        "desktop": "string (required)",
        "991": "string (optional)",
        "767": "string (optional)",
        "479": "string (optional)"
      }
    }
  ],
  "tokenPrefix": "string (default: '--')",
  "excludeTokens": ["string (glob patterns)"],
  "aliasTokens": {
    "cssTokenName": "figmaAliasTarget"
  },
  "unitOverrides": {
    "tokenName": "unit"
  },
  "figmaTypes": {
    "tokenName": "COLOR | FLOAT | STRING"
  }
}
```

## Field Reference

### `fileKey` (required)

The Figma file key, extracted from the Figma file URL.

```
https://www.figma.com/design/abc123DEF456/My-Design-File
                              ^^^^^^^^^^^^^^
                              This is the fileKey
```

Type: `string`

### `collections` (required)

Array of Figma variable collection configurations. Each collection maps to a Figma Variable Collection in the file.

Type: `Array<CollectionConfig>`

#### `collections[].name` (required)

The display name of the variable collection in Figma. This must match exactly (case-sensitive) if updating an existing collection.

Type: `string`
Example: `"Brand Tokens"`, `"Spacing"`, `"Typography"`

#### `collections[].modes` (required)

Maps CSS breakpoint keys to Figma mode names. The `desktop` key is required; others are optional.

Type: `Record<string, string>`

| Key | CSS Source | Figma Mode Name |
|-----|-----------|-----------------|
| `desktop` | `:root { }` | User-defined (e.g., "Desktop") |
| `991` | `@media (max-width: 991px) { :root { } }` | User-defined (e.g., "Tablet") |
| `767` | `@media (max-width: 767px) { :root { } }` | User-defined (e.g., "Mobile") |
| `479` | `@media (max-width: 479px) { :root { } }` | User-defined (e.g., "Small Mobile") |

If a breakpoint key is omitted, tokens at that breakpoint are ignored during PUSH and not generated during PULL.

### `tokenPrefix` (optional)

The prefix to strip from CSS custom property names before creating Figma variable names. Defaults to `"--"`.

Type: `string`
Default: `"--"`

Example: With `tokenPrefix: "--brand-"`, the CSS token `--brand-color-primary` becomes the Figma variable `color/primary`.

### `excludeTokens` (optional)

Array of glob patterns for tokens to exclude from sync. Useful for filtering out framework-generated tokens (Tailwind, Webkit, etc.).

Type: `string[]`
Default: `[]`

Example:
```json
{
  "excludeTokens": [
    "--tw-*",
    "--webkit-*",
    "--chakra-*",
    "--internal-*"
  ]
}
```

### `aliasTokens` (optional)

Map of CSS token names to their alias targets in Figma. When a token is listed here, it will be created as a Figma variable alias pointing to the target variable instead of a literal value.

Type: `Record<string, string>`
Default: `{}`

Example:
```json
{
  "aliasTokens": {
    "--color-primary": "--brand-primary",
    "--color-cta-bg": "--color-primary",
    "--button-color": "--color-primary"
  }
}
```

This creates Figma alias variables: `color/primary` references `brand/primary`, `color/cta-bg` references `color/primary`, etc.

### `unitOverrides` (optional)

Force specific tokens to use a particular CSS unit during PULL (Figma to CSS conversion). By default, FLOAT values are converted to `px`. Use this to specify `rem`, `em`, `%`, or unitless.

Type: `Record<string, string>`
Default: `{}`

Example:
```json
{
  "unitOverrides": {
    "--font-size-*": "rem",
    "--line-height-*": "",
    "--space-*": "rem",
    "--opacity-*": "",
    "--container-max": "px",
    "--border-radius*": "px"
  }
}
```

Glob patterns are supported in the key. The empty string `""` means unitless.

### `figmaTypes` (optional)

Force specific tokens to a Figma variable type, overriding the automatic classification. Useful when the auto-classifier gets it wrong (e.g., a string that looks like a number).

Type: `Record<string, "COLOR" | "FLOAT" | "STRING">`
Default: `{}`

Example:
```json
{
  "figmaTypes": {
    "--z-index-modal": "FLOAT",
    "--font-family-heading": "STRING",
    "--grid-columns": "FLOAT"
  }
}
```

## Complete Example

```json
{
  "fileKey": "abc123DEF456",
  "collections": [
    {
      "name": "Brand Colors",
      "modes": {
        "desktop": "Default"
      }
    },
    {
      "name": "Responsive Tokens",
      "modes": {
        "desktop": "Desktop",
        "991": "Tablet",
        "767": "Mobile",
        "479": "Small Mobile"
      }
    }
  ],
  "tokenPrefix": "--",
  "excludeTokens": [
    "--tw-*",
    "--webkit-*",
    "--internal-*"
  ],
  "aliasTokens": {
    "--color-cta-bg": "--color-primary",
    "--color-cta-text": "--color-background"
  },
  "unitOverrides": {
    "--font-size-*": "rem",
    "--line-height-*": "",
    "--space-*": "rem",
    "--container-max": "px",
    "--border-radius*": "px"
  },
  "figmaTypes": {
    "--z-index-modal": "FLOAT",
    "--grid-columns": "FLOAT"
  }
}
```

## Validation Rules

1. `fileKey` must be a non-empty string matching the pattern from a valid Figma URL
2. `collections` must have at least one entry
3. Every collection must have a `name` and a `modes` object with at least the `desktop` key
4. `excludeTokens` patterns must be valid glob patterns
5. `aliasTokens` targets must reference tokens that exist in the CSS source
6. `unitOverrides` keys support glob patterns; values must be valid CSS units or empty string
7. `figmaTypes` values must be one of: `COLOR`, `FLOAT`, `STRING`
