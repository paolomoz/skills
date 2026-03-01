# Tool Definitions Reference

Complete reference for all Claude agent tools used in the conversational page builder. Each tool definition includes the schema, implementation notes, and usage examples.

---

## Page Management Tools

### read_page_content

Read the current HTML content of a specific page. The agent should always call this before making edits to understand current page structure.

**Schema:**
```json
{
  "name": "read_page_content",
  "description": "Read the current HTML content of a specific page",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Page path relative to site root, e.g., '/index' or '/about'"
      }
    },
    "required": ["path"]
  }
}
```

**Return value:**
```json
{
  "content": "<main><div class=\"hero\">...</div><hr/>...</main>",
  "lastModified": "2025-01-15T10:30:00Z",
  "title": "Home Page"
}
```

**Implementation notes:**
- Reads from the current feature branch, not main
- Returns `.plain.html` format (EDS block structure with `<div class="blockname">` and `<hr/>` separators)
- If the page does not exist, returns `{ "error": "Page not found", "path": "/requested-path" }`

---

### update_page_content

Replace the full content of a page. Use this for complete page rewrites. For targeted edits, prefer `update_block_content`.

**Schema:**
```json
{
  "name": "update_page_content",
  "description": "Replace the full content of a page with new HTML",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Page path"
      },
      "content": {
        "type": "string",
        "description": "Full HTML content for the page in EDS block format"
      },
      "commitMessage": {
        "type": "string",
        "description": "Descriptive commit message for this change"
      }
    },
    "required": ["path", "content", "commitMessage"]
  }
}
```

**Return value:**
```json
{
  "success": true,
  "commitSha": "abc123f",
  "previewUrl": "https://main--repo--org.aem.page/path"
}
```

**Implementation notes:**
- Creates an atomic commit on the feature branch
- Content must be valid EDS HTML with blocks separated by `<hr/>`
- Automatically triggers preview refresh after successful update
- Maximum content size: 1MB

---

### create_new_page

Create a new page at the specified path. Fails if a page already exists at that path.

**Schema:**
```json
{
  "name": "create_new_page",
  "description": "Create a new page at the specified path",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Page path for the new page"
      },
      "content": {
        "type": "string",
        "description": "Initial HTML content"
      },
      "title": {
        "type": "string",
        "description": "Page title for metadata"
      },
      "commitMessage": {
        "type": "string",
        "description": "Commit message"
      }
    },
    "required": ["path", "content", "title", "commitMessage"]
  }
}
```

**Return value:**
```json
{
  "success": true,
  "commitSha": "def456a",
  "path": "/pricing",
  "previewUrl": "https://main--repo--org.aem.page/pricing"
}
```

**Implementation notes:**
- Path should not include `.html` extension (the system adds it)
- Creates both the content file and any necessary metadata
- If the page already exists, returns `{ "error": "Page already exists", "path": "/pricing" }`
- The agent should use `update_page_content` for existing pages

---

## Styling Tools

### read_css

Read current CSS stylesheet content.

**Schema:**
```json
{
  "name": "read_css",
  "description": "Read current CSS stylesheet content",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "CSS file path, e.g., '/styles/styles.css'"
      }
    },
    "required": ["path"]
  }
}
```

**Return value:**
```json
{
  "content": ":root { --color-primary: #0066cc; ... }",
  "lastModified": "2025-01-15T10:30:00Z"
}
```

### update_css

Update CSS stylesheet with new content.

**Schema:**
```json
{
  "name": "update_css",
  "description": "Update CSS stylesheet with new content",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "CSS file path"
      },
      "content": {
        "type": "string",
        "description": "Full CSS content"
      },
      "commitMessage": {
        "type": "string",
        "description": "Commit message"
      }
    },
    "required": ["path", "content", "commitMessage"]
  }
}
```

**Implementation notes:**
- The agent should always `read_css` first to avoid overwriting existing styles
- Prefer appending new rules rather than replacing the entire stylesheet
- Design token changes (CSS custom properties) should use `update_design_tokens` instead

---

## Navigation Tools

### read_nav_content

Read the current site navigation structure.

**Schema:**
```json
{
  "name": "read_nav_content",
  "description": "Read the current site navigation structure",
  "input_schema": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

**Return value:**
```json
{
  "content": "<ul><li><a href='/'>Home</a></li><li><a href='/about'>About</a></li></ul>",
  "format": "html"
}
```

### update_nav_content

Update site navigation.

**Schema:**
```json
{
  "name": "update_nav_content",
  "description": "Update site navigation with new structure",
  "input_schema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Navigation HTML content"
      },
      "commitMessage": {
        "type": "string",
        "description": "Commit message"
      }
    },
    "required": ["content", "commitMessage"]
  }
}
```

**Implementation notes:**
- Navigation updates should be done after all pages are created, so the nav includes links to all new pages
- Keep navigation structure flat (max 2 levels of nesting)

---

## Design Token Tools

### read_design_tokens

Read current design token values (CSS custom properties).

**Schema:**
```json
{
  "name": "read_design_tokens",
  "description": "Read current design token values (colors, typography, spacing)",
  "input_schema": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

**Return value:**
```json
{
  "tokens": {
    "--color-primary": "#0066cc",
    "--color-secondary": "#004499",
    "--color-accent": "#ff6600",
    "--font-heading": "'Helvetica Neue', sans-serif",
    "--font-body": "'Georgia', serif",
    "--spacing-unit": "8px"
  }
}
```

### update_design_tokens

Update individual design tokens without replacing the entire CSS.

**Schema:**
```json
{
  "name": "update_design_tokens",
  "description": "Update design tokens (CSS custom properties)",
  "input_schema": {
    "type": "object",
    "properties": {
      "tokens": {
        "type": "object",
        "description": "Key-value map of CSS custom property names to values",
        "additionalProperties": { "type": "string" }
      },
      "commitMessage": {
        "type": "string",
        "description": "Commit message"
      }
    },
    "required": ["tokens", "commitMessage"]
  }
}
```

**Implementation notes:**
- Only updates the specified tokens; unspecified tokens remain unchanged
- Token names must include the `--` prefix
- This is the preferred way to change colors and typography (not `update_css`)

### apply_brand_override

Apply a complete brand override from a predefined brand brief.

**Schema:**
```json
{
  "name": "apply_brand_override",
  "description": "Apply a complete brand override from a predefined brand brief",
  "input_schema": {
    "type": "object",
    "properties": {
      "brandBriefId": {
        "type": "string",
        "description": "ID of the brand brief to apply"
      },
      "commitMessage": {
        "type": "string",
        "description": "Commit message"
      }
    },
    "required": ["brandBriefId", "commitMessage"]
  }
}
```

**Implementation notes:**
- A brand brief includes a complete set of design tokens, CSS overrides, and font imports
- Applying a brand brief replaces all existing design tokens and appends brand-specific CSS
- The agent should call `trigger_preview` after applying a brand override

---

## Content Tools

### list_page_content

List all pages in the site.

**Schema:**
```json
{
  "name": "list_page_content",
  "description": "List all pages in the site with their paths and titles",
  "input_schema": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

**Return value:**
```json
{
  "pages": [
    { "path": "/index", "title": "Home", "lastModified": "2025-01-15T10:30:00Z" },
    { "path": "/about", "title": "About Us", "lastModified": "2025-01-14T08:00:00Z" }
  ]
}
```

### search_content

Search across all site content for a text pattern.

**Schema:**
```json
{
  "name": "search_content",
  "description": "Search across all site content for a text pattern",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query (searches page titles and body content)"
      }
    },
    "required": ["query"]
  }
}
```

### update_block_content

Update a specific block within a page. This is the preferred tool for targeted edits when the user says things like "change the hero headline" or "update the pricing table."

**Schema:**
```json
{
  "name": "update_block_content",
  "description": "Update a specific block within a page without replacing the entire page",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Page path"
      },
      "blockType": {
        "type": "string",
        "description": "Block type to update (e.g., 'hero', 'cards', 'cta')"
      },
      "blockIndex": {
        "type": "number",
        "description": "Zero-based index if multiple blocks of same type exist on the page (default: 0)"
      },
      "content": {
        "type": "string",
        "description": "New HTML content for just this block"
      },
      "commitMessage": {
        "type": "string",
        "description": "Commit message"
      }
    },
    "required": ["path", "blockType", "content", "commitMessage"]
  }
}
```

**Implementation notes:**
- Parses the page HTML, locates the block by type and index, replaces only that block's content
- Preserves all other blocks and the overall page structure
- If the block type is not found, returns an error listing the available block types on the page
- The agent should always `read_page_content` first to see the current block structure

---

## Preview Tools

### publish_page

Publish a page to make it live.

**Schema:**
```json
{
  "name": "publish_page",
  "description": "Publish a page to make it live on the production site",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Page path to publish"
      }
    },
    "required": ["path"]
  }
}
```

**Implementation notes:**
- The agent should only publish after the user explicitly approves
- Publishing triggers both preview and live cache invalidation

### get_page_preview

Get the preview URL for a page.

**Schema:**
```json
{
  "name": "get_page_preview",
  "description": "Get the preview URL for a page",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Page path"
      }
    },
    "required": ["path"]
  }
}
```

**Return value:**
```json
{
  "previewUrl": "https://main--repo--org.aem.page/path",
  "liveUrl": "https://main--repo--org.aem.live/path"
}
```

### trigger_preview

Force a preview refresh for a page that has been updated.

**Schema:**
```json
{
  "name": "trigger_preview",
  "description": "Force a preview refresh for a page that has been updated",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Page path to refresh"
      }
    },
    "required": ["path"]
  }
}
```

**Implementation notes:**
- Call this after any content or style update so the user sees fresh content
- Preview refresh typically takes 1-3 seconds
- The agent should emit a `preview-ready` SSE event after calling this tool
