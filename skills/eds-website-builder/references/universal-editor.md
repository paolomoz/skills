# Universal Editor (UE) Integration

## Overview

The Universal Editor enables visual in-context editing of EDS pages directly in Document Authoring (DA). Authors can click on blocks, sections, and content elements to edit them visually rather than through table structures.

UE integration requires three layers:
1. **Component definitions** — What components exist and how they're structured
2. **Component models** — What fields each component exposes for editing
3. **Component filters** — What components can be nested inside what
4. **Instrumentation scripts** — JavaScript that bridges decorated DOM back to editable structure

## Architecture

```
project-root/
├── component-definition.json    # Root-level flat definitions (required)
├── component-models.json        # Root-level flat models (required)
├── component-filters.json       # Root-level flat filters (required)
├── paths.json                   # Content path mapping (required)
└── ue/                          # Modular versions (optional, for maintainability)
    ├── scripts/
    │   ├── ue.js                # MutationObserver + event handlers
    │   └── ue-utils.js          # Attribute movement utilities
    └── models/
        ├── component-definition.json   # Modular with $ref spreads
        ├── component-models.json       # Modular with $ref spreads
        ├── component-filters.json      # Modular with $ref spreads
        ├── page.json                   # Page metadata model
        ├── section.json                # Section model
        ├── text.json                   # Default content: text
        ├── image.json                  # Default content: image
        └── blocks/
            ├── cards-teaser.json       # Block model + child model
            ├── columns-teaser.json
            ├── introduction.json
            └── title.json
```

## paths.json

Maps DA content repository paths to website routes:

```json
{
  "mappings": [
    "/content/{org}/{repo}/:/"
  ]
}
```

This tells UE that content stored at `/content/myorg/mysite/page` serves at `/page`.

## Component Definitions

The `component-definition.json` file declares all available components grouped by type:

```json
{
  "groups": [
    {
      "title": "Default Content",
      "id": "default",
      "components": [
        {
          "title": "Text",
          "id": "text",
          "plugins": {
            "xwalk": {
              "page": { "resourceType": "core/franklin/components/text", "template": {} }
            }
          }
        },
        {
          "title": "Image",
          "id": "image",
          "plugins": {
            "xwalk": {
              "page": {
                "resourceType": "core/franklin/components/image",
                "template": { "imageAlt": "" }
              }
            }
          }
        }
      ]
    },
    {
      "title": "Sections",
      "id": "sections",
      "components": [
        {
          "title": "Section",
          "id": "section",
          "plugins": {
            "xwalk": {
              "page": {
                "resourceType": "core/franklin/components/section",
                "template": { "unsafeHTML": "<div></div>" }
              }
            }
          }
        }
      ]
    },
    {
      "title": "Blocks",
      "id": "blocks",
      "components": [
        {
          "title": "Cards Teaser",
          "id": "cards-teaser",
          "plugins": {
            "xwalk": {
              "page": {
                "resourceType": "core/franklin/components/block",
                "template": {
                  "name": "Cards Teaser",
                  "rows": 1, "columns": 2
                }
              }
            }
          }
        }
      ]
    }
  ]
}
```

Key concepts:
- `resourceType` maps to AEM component types
- `template` defines default structure (rows, columns for blocks)
- `name` must match the block name as authored (Title Case)
- Default content (text, image) and sections are always needed

### DA Plugin Definitions

For blocks that need field extraction from decorated HTML, add DA plugin selectors:

```json
{
  "title": "Columns Teaser",
  "id": "columns-teaser",
  "plugins": {
    "xwalk": {
      "page": {
        "resourceType": "core/franklin/components/block",
        "template": { "name": "Columns Teaser", "model": "columns-teaser" }
      }
    },
    "da": {
      "collab": {
        "fields": [
          { "component": "richtext", "selector": "div:nth-child(1)>div" },
          { "component": "reference", "selector": "div:nth-child(2)>div:nth-child(2)>picture>img[src]" },
          { "component": "text", "selector": "div:nth-child(2)>div:nth-child(2)>picture>img[alt]" }
        ]
      }
    }
  }
}
```

The `da.collab.fields` array maps CSS selectors to editable field types:
- `richtext` — WYSIWYG text editing
- `reference` — Image/asset reference
- `text` — Plain text field

## Component Models

Define the editable fields for each component:

```json
[
  {
    "id": "page-metadata",
    "fields": [
      { "component": "text", "name": "title", "label": "Title" },
      { "component": "text", "name": "description", "label": "Description" },
      { "component": "reference", "name": "image", "label": "Image" }
    ]
  },
  {
    "id": "section",
    "fields": [
      {
        "component": "multiselect",
        "name": "style",
        "label": "Style",
        "options": [
          { "name": "Default", "value": "" },
          { "name": "Light", "value": "light" },
          { "name": "Dark", "value": "dark" },
          { "name": "Highlight", "value": "highlight" }
        ]
      }
    ]
  },
  {
    "id": "card-teaser",
    "fields": [
      { "component": "reference", "name": "image", "label": "Image" },
      { "component": "text", "name": "imageAlt", "label": "Image Alt Text" },
      { "component": "richtext", "name": "text", "label": "Text" }
    ]
  }
]
```

Field component types:
- `text` — Single-line plain text
- `richtext` — WYSIWYG rich text editor
- `reference` — Asset/image reference picker
- `multiselect` — Dropdown with options (used for section styles, block variants)

## Component Filters

Control what can be nested inside what:

```json
[
  {
    "id": "main",
    "components": ["section"]
  },
  {
    "id": "section",
    "components": [
      "text", "image",
      "title", "introduction", "hero",
      "cards", "cards-teaser",
      "columns", "columns-teaser"
    ]
  },
  {
    "id": "cards-teaser",
    "components": ["card-teaser"]
  }
]
```

This hierarchy:
- `main` can only contain `section` components
- `section` can contain default content and blocks
- Container blocks (like `cards-teaser`) define their allowed children

## UE Instrumentation Scripts

### The Problem

EDS blocks transform their DOM during decoration. For example, `cards-teaser` converts `<div>` rows into `<ul>/<li>` lists. UE needs `data-aue-*` attributes on the correct elements to enable editing, but decoration moves or replaces those elements.

### Solution: MutationObserver

The `ue.js` script watches for DOM changes and moves instrumentation attributes to the correct decorated elements:

```javascript
// ue/scripts/ue.js

import { moveInstrumentation } from './ue-utils.js';

function setupObservers() {
  // Watch for cards-teaser decoration (div→ul/li transformation)
  document.querySelectorAll('.cards-teaser').forEach((block) => {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeName === 'UL') {
            // Move block instrumentation from div wrapper to ul
            moveInstrumentation(block.firstElementChild, node);
            // Move item instrumentation from original divs to li elements
            [...node.children].forEach((li, i) => {
              const originalDiv = block.querySelectorAll(':scope > div > div')[i];
              if (originalDiv) moveInstrumentation(originalDiv, li);
            });
          }
        });
      });
    });
    observer.observe(block, { childList: true, subtree: true });
  });

  // Watch for carousel-teaser decoration
  document.querySelectorAll('.carousel-teaser').forEach((block) => {
    const observer = new MutationObserver((mutations) => {
      // Map slide indices to transformed DOM structure
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.classList?.contains('carousel-slides')) {
            [...node.children].forEach((slide, i) => {
              const original = block.querySelectorAll(':scope > div')[i];
              if (original) moveInstrumentation(original, slide);
            });
          }
        });
      });
    });
    observer.observe(block, { childList: true, subtree: true });
  });

  // Watch for accordion decoration (div→details/summary)
  document.querySelectorAll('.accordion').forEach((block) => {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeName === 'DETAILS') {
            const originalDiv = node.parentElement;
            moveInstrumentation(originalDiv, node);
          }
        });
      });
    });
    observer.observe(block, { childList: true, subtree: true });
  });
}

function setupUEEventHandlers() {
  // Handle image source updates
  document.addEventListener('aue:content-patch', (event) => {
    const { detail } = event;
    if (detail?.type === 'image') {
      const img = detail.element?.querySelector('img');
      if (img) {
        // Update all source elements in the picture
        const picture = img.closest('picture');
        if (picture) {
          picture.querySelectorAll('source').forEach((source) => {
            source.srcset = img.src;
          });
        }
      }
    }
  });

  // Handle UI select events
  document.addEventListener('aue:ui-select', (event) => {
    const { detail } = event;
    // Auto-open accordion items when selected for editing
    if (detail?.element?.closest('.accordion')) {
      const details = detail.element.closest('details');
      if (details) details.open = true;
    }
  });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    setupObservers();
    setupUEEventHandlers();
  });
} else {
  setupObservers();
  setupUEEventHandlers();
}
```

### Utility: moveInstrumentation

```javascript
// ue/scripts/ue-utils.js

export function moveAttributes(from, to, attributes) {
  attributes.forEach((attr) => {
    const value = from.getAttribute(attr);
    if (value) {
      to.setAttribute(attr, value);
      from.removeAttribute(attr);
    }
  });
}

export function moveInstrumentation(from, to) {
  // Move all data-aue-* and data-richtext-* attributes
  const attrs = [...from.attributes]
    .filter((a) => a.name.startsWith('data-aue-') || a.name.startsWith('data-richtext-'))
    .map((a) => a.name);
  moveAttributes(from, to, attrs);
}
```

## Loading UE Scripts

UE scripts should only load in the editor context. Add conditional loading in `scripts.js`:

```javascript
async function loadLazy(doc) {
  // ... existing lazy loading ...

  // Load UE instrumentation only when in editor
  if (window.location.hostname.includes('adobeaemcloud.com')
      || new URLSearchParams(window.location.search).has('aue')) {
    const { default: setupUE } = await import('../ue/scripts/ue.js');
  }
}
```

## Modular Model Organization

For larger projects, use modular JSON files with `$ref` spreads instead of one flat file:

```json
// ue/models/component-definition.json (modular)
{
  "groups": [
    {
      "title": "Default Content",
      "id": "default",
      "components": [
        "./text.json#/definitions",
        "./image.json#/definitions"
      ]
    },
    {
      "title": "Sections",
      "id": "sections",
      "components": ["./section.json#/definitions"]
    },
    {
      "title": "Blocks",
      "id": "blocks",
      "components": ["./blocks/*.json#/definitions"]
    }
  ]
}
```

Individual block model file:

```json
// ue/models/blocks/introduction.json
{
  "definitions": [
    {
      "title": "Introduction",
      "id": "introduction",
      "plugins": {
        "xwalk": {
          "page": {
            "resourceType": "core/franklin/components/block",
            "template": { "name": "Introduction", "model": "introduction" }
          }
        },
        "da": {
          "collab": {
            "fields": [
              { "component": "richtext", "selector": "" }
            ]
          }
        }
      }
    }
  ],
  "models": [
    {
      "id": "introduction",
      "fields": [
        { "component": "richtext", "name": "content", "label": "Content" }
      ]
    }
  ]
}
```

The root-level flat files are still required — they're the source of truth. The modular files in `ue/models/` are a development convenience.

## Checklist

When adding UE support to a new block:

- [ ] Add component definition (id, title, resourceType, template)
- [ ] Add DA plugin fields with CSS selectors matching decorated DOM
- [ ] Add component model with field definitions
- [ ] Update component filters if the block has child components
- [ ] Add MutationObserver in `ue.js` if the block transforms its DOM
- [ ] Test in DA visual editor — verify fields are editable
- [ ] Verify image updates propagate to all `<source>` elements
