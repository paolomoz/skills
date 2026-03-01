---
name: conversational-page-builder
description: Build interactive AI agent loops that iteratively create and refine web pages through multi-turn conversations with Claude tool calling, design selection, and real-time preview. Use when building "conversational website builder", "chat-based page editor", "AI agent builder", or "interactive page generation".
---

# Conversational Page Builder

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| page-generation | "conversational website builder", "chat-based page editor", "AI agent builder", "interactive page generation" | High | 5 projects |

Build an interactive AI agent that creates and refines web pages through multi-turn conversations. Unlike the one-shot generative pipeline, the conversational builder uses Claude's tool calling capability to iterate on pages in a loop: analyzing requirements, presenting design options, generating content, and refining based on user feedback -- all streamed as real-time SSE events to the client.

## When to Use

- Building a chat-based website builder where users describe what they want and the AI creates it iteratively
- Implementing a Claude-powered agent loop with tool calling for page creation and editing
- Creating a system where users choose from brand briefs and design options before generation
- Building a multi-phase creation flow: requirements analysis, design selection, page generation, refinement
- Any interactive builder where the user should be able to say "make the hero bigger" or "change the color scheme" and see updates in real time
- Implementing a website creation wizard that uses conversation instead of forms

## Instructions

### Multi-Phase Architecture

The conversational builder operates in three phases, each ending with a user decision point:

```
Phase 1: Analyze Requirements
  User describes what they want
  -> Agent analyzes, extracts requirements
  -> Presents brand brief options
  -> User selects brand direction

Phase 2: Design Selection
  -> Agent generates design options based on brand
  -> Presents 2-3 visual design options with preview
  -> User selects design

Phase 3: Page Generation + Refinement
  -> Agent generates full page using selected brand + design
  -> User reviews live preview
  -> User requests changes ("make the hero more bold", "add a pricing section")
  -> Agent uses tools to read and update specific sections
  -> Loop until user is satisfied
```

Each phase transition is driven by user input. The agent never advances to the next phase without explicit user confirmation.

---

### Requirements Analysis

When the user provides their initial description, extract structured requirements:

```typescript
interface Requirements {
  businessType: string         // e.g., "SaaS startup", "restaurant", "portfolio"
  audience: string             // Target audience description
  tone: string                 // e.g., "professional", "playful", "minimalist"
  pages: PageRequirement[]     // Pages to generate
  designNotes: string          // Any specific design preferences mentioned
}

interface PageRequirement {
  name: string                 // e.g., "Home", "About", "Pricing"
  path: string                 // e.g., "/", "/about", "/pricing"
  sections: string[]           // e.g., ["hero", "features", "testimonials", "cta"]
  priority: 'primary' | 'secondary'
}
```

The agent should infer unstated requirements from the business type. For example, a restaurant site implicitly needs a menu page and hours/location, even if the user only says "I need a website for my restaurant."

Prompt the requirements extraction as follows:

```typescript
const requirementsPrompt = `Analyze this website request and extract structured requirements.
Infer any unstated but obviously needed pages and sections based on the business type.
Do NOT ask the user for more information -- make reasonable assumptions and note them.

User request: "${userMessage}"

Return JSON matching the Requirements schema.`
```

Key rules:
- Never ask the user to fill out a form. Extract everything from natural language.
- Make assumptions and state them explicitly: "I'm assuming you'll want a contact form since you mentioned client inquiries."
- If the request is too vague to act on (e.g., "make me a website"), generate requirements for a generic business site and let the user refine from there. Do not ask clarifying questions that block progress.

---

### Tool Definitions

The Claude agent is configured with tools that let it read and modify page content, styling, navigation, and design tokens. These tools are the mechanism by which the agent takes action.

**Page Management Tools:**

```typescript
const pageTools = [
  {
    name: 'read_page_content',
    description: 'Read the current HTML content of a specific page',
    input_schema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Page path, e.g., "/index" or "/about"' }
      },
      required: ['path']
    }
  },
  {
    name: 'update_page_content',
    description: 'Replace the full content of a page with new HTML',
    input_schema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Page path' },
        content: { type: 'string', description: 'Full HTML content for the page' },
        commitMessage: { type: 'string', description: 'Descriptive commit message for this change' }
      },
      required: ['path', 'content', 'commitMessage']
    }
  },
  {
    name: 'create_new_page',
    description: 'Create a new page at the specified path',
    input_schema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Page path for the new page' },
        content: { type: 'string', description: 'Initial HTML content' },
        title: { type: 'string', description: 'Page title for metadata' },
        commitMessage: { type: 'string', description: 'Commit message' }
      },
      required: ['path', 'content', 'title', 'commitMessage']
    }
  }
]
```

**Styling Tools:**

```typescript
const stylingTools = [
  {
    name: 'read_css',
    description: 'Read current CSS stylesheet content',
    input_schema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'CSS file path, e.g., "/styles/styles.css"' }
      },
      required: ['path']
    }
  },
  {
    name: 'update_css',
    description: 'Update CSS stylesheet with new content',
    input_schema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'CSS file path' },
        content: { type: 'string', description: 'Full CSS content' },
        commitMessage: { type: 'string', description: 'Commit message' }
      },
      required: ['path', 'content', 'commitMessage']
    }
  }
]
```

**Navigation Tools:**

```typescript
const navTools = [
  {
    name: 'read_nav_content',
    description: 'Read the current site navigation structure',
    input_schema: {
      type: 'object',
      properties: {},
      required: []
    }
  },
  {
    name: 'update_nav_content',
    description: 'Update site navigation with new structure',
    input_schema: {
      type: 'object',
      properties: {
        content: { type: 'string', description: 'Navigation HTML content' },
        commitMessage: { type: 'string', description: 'Commit message' }
      },
      required: ['content', 'commitMessage']
    }
  }
]
```

**Design Token Tools:**

```typescript
const designTools = [
  {
    name: 'read_design_tokens',
    description: 'Read current design token values (colors, typography, spacing)',
    input_schema: {
      type: 'object',
      properties: {},
      required: []
    }
  },
  {
    name: 'update_design_tokens',
    description: 'Update design tokens (CSS custom properties)',
    input_schema: {
      type: 'object',
      properties: {
        tokens: {
          type: 'object',
          description: 'Key-value map of CSS custom property names to values',
          additionalProperties: { type: 'string' }
        },
        commitMessage: { type: 'string', description: 'Commit message' }
      },
      required: ['tokens', 'commitMessage']
    }
  },
  {
    name: 'apply_brand_override',
    description: 'Apply a complete brand override from a predefined brand brief',
    input_schema: {
      type: 'object',
      properties: {
        brandBriefId: { type: 'string', description: 'ID of the brand brief to apply' },
        commitMessage: { type: 'string', description: 'Commit message' }
      },
      required: ['brandBriefId', 'commitMessage']
    }
  }
]
```

**Content Search and Update Tools:**

```typescript
const contentTools = [
  {
    name: 'list_page_content',
    description: 'List all pages in the site with their paths and titles',
    input_schema: {
      type: 'object',
      properties: {},
      required: []
    }
  },
  {
    name: 'search_content',
    description: 'Search across all site content for a text pattern',
    input_schema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query' }
      },
      required: ['query']
    }
  },
  {
    name: 'update_block_content',
    description: 'Update a specific block within a page without replacing the entire page',
    input_schema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Page path' },
        blockType: { type: 'string', description: 'Block type to update (e.g., "hero", "cards")' },
        blockIndex: { type: 'number', description: 'Zero-based index if multiple blocks of same type' },
        content: { type: 'string', description: 'New HTML content for just this block' },
        commitMessage: { type: 'string', description: 'Commit message' }
      },
      required: ['path', 'blockType', 'content', 'commitMessage']
    }
  }
]
```

**Preview Tools:**

```typescript
const previewTools = [
  {
    name: 'publish_page',
    description: 'Publish a page to make it live',
    input_schema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Page path to publish' }
      },
      required: ['path']
    }
  },
  {
    name: 'get_page_preview',
    description: 'Get the preview URL for a page',
    input_schema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Page path' }
      },
      required: ['path']
    }
  },
  {
    name: 'trigger_preview',
    description: 'Force a preview refresh for a page that has been updated',
    input_schema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'Page path to refresh' }
      },
      required: ['path']
    }
  }
]
```

See `references/tool-definitions.md` for the complete tool schema reference with examples and implementation notes.

---

### Agent Loop Structure

The core agent loop sends messages to Claude with tools enabled and iterates until Claude produces a final text response (stop_reason: `end_turn`) or the iteration limit is reached.

```typescript
const MAX_ITERATIONS = 10

async function runAgentLoop(
  messages: Message[],
  tools: Tool[],
  env: Env,
  emitEvent: (type: string, data: any) => void
): Promise<string> {
  let iterations = 0

  while (iterations < MAX_ITERATIONS) {
    iterations++

    const response = await anthropic.messages.create({
      model: 'claude-opus-4-20250514',
      max_tokens: 8192,
      system: AGENT_SYSTEM_PROMPT,
      messages,
      tools
    })

    // Stream text content to the client
    for (const block of response.content) {
      if (block.type === 'text') {
        emitEvent('text', { content: block.text })
      }
    }

    // Check if agent wants to use tools
    const toolUseBlocks = response.content.filter(b => b.type === 'tool_use')

    if (response.stop_reason === 'end_turn' || toolUseBlocks.length === 0) {
      // Agent is done -- return final text
      const textBlocks = response.content.filter(b => b.type === 'text')
      return textBlocks.map(b => b.text).join('\n')
    }

    // Execute tool calls and add results to conversation
    messages.push({ role: 'assistant', content: response.content })

    const toolResults = await Promise.all(
      toolUseBlocks.map(async toolUse => {
        emitEvent('step', { tool: toolUse.name, input: toolUse.input })

        try {
          const result = await executeToolCall(toolUse.name, toolUse.input, env)
          return {
            type: 'tool_result' as const,
            tool_use_id: toolUse.id,
            content: JSON.stringify(result)
          }
        } catch (error) {
          return {
            type: 'tool_result' as const,
            tool_use_id: toolUse.id,
            content: JSON.stringify({ error: error.message }),
            is_error: true
          }
        }
      })
    )

    messages.push({ role: 'user', content: toolResults })
  }

  return 'Reached maximum iterations. Please provide more specific instructions.'
}
```

Key rules:
- Set `MAX_ITERATIONS = 10`. This prevents runaway agent loops while allowing enough iterations for multi-step page creation (typically 3-6 tool calls for a full page).
- Always execute tool calls returned by Claude. Never skip or filter tool calls.
- Include both text and tool_use blocks in the assistant message pushed to the conversation. Claude needs to see its own tool calls to maintain coherent state.
- Stream text events to the client as they arrive so the user sees the agent "thinking out loud."

---

### SSE Event Types

| Event Type | Payload | When Emitted |
|------------|---------|-------------|
| `step` | `{ tool, input }` | Agent calls a tool |
| `text` | `{ content }` | Agent produces text (streamed) |
| `brand-brief-options` | `{ options: BrandBrief[] }` | Phase 1 complete, presenting brand options |
| `design-options` | `{ options: DesignOption[] }` | Phase 2, presenting design choices |
| `progress` | `{ phase, step, total }` | Progress update within a phase |
| `preview-ready` | `{ url, path }` | Page preview is available |
| `error` | `{ message, recoverable }` | Error occurred |
| `complete` | `{ pages[], previewUrl }` | All generation complete |

---

### Design Options Pattern

After the user selects a brand brief, generate 2-3 design options that apply different visual treatments:

```typescript
interface DesignOption {
  id: string                    // e.g., "design-modern", "design-classic"
  name: string                  // Human-readable name
  description: string           // 1-2 sentence description of the visual style
  cssOverridesPath: string      // Path to CSS overrides file
  colorPalette: {
    primary: string             // Hex color
    secondary: string
    accent: string
    background: string
    text: string
  }
  typography: {
    headingFont: string         // Font family name
    bodyFont: string
    headingWeight: string       // e.g., "700", "900"
  }
  previewThumbnail?: string     // URL to a generated preview thumbnail
}
```

Present design options to the user via the `design-options` SSE event. The client renders selectable cards with color swatches and typography samples. When the user selects a design, the agent applies it using `update_design_tokens` and `apply_brand_override` tools, then proceeds to page generation.

Key rules:
- Always generate at least 2 options. Three is ideal.
- Options should be meaningfully different (not just "blue vs slightly different blue"). Vary layout density, typography weight, and color warmth.
- Include a "safe" option that is conventional for the business type and a "bold" option that is more distinctive.

---

### GitHub Branch Management

All changes made by the agent are committed to a feature branch, never directly to main:

```typescript
async function setupBranch(
  owner: string,
  repo: string,
  branchName: string,
  env: Env
): Promise<void> {
  // Get main branch SHA
  const mainRef = await githubAPI(`/repos/${owner}/${repo}/git/ref/heads/main`, env)
  const sha = mainRef.object.sha

  // Create feature branch
  await githubAPI(`/repos/${owner}/${repo}/git/refs`, env, {
    method: 'POST',
    body: JSON.stringify({
      ref: `refs/heads/${branchName}`,
      sha
    })
  })
}
```

Branch naming convention: `ai-builder/${timestamp}-${slugified-business-type}`

Each tool call that modifies content (`update_page_content`, `create_new_page`, `update_css`, etc.) creates an atomic commit on the feature branch. This gives the user a complete change history and the ability to revert individual changes.

Key rules:
- Never commit directly to `main`. Always use a feature branch.
- Each commit should have a descriptive message generated by the agent (passed via the tool's `commitMessage` parameter).
- After all pages are generated, provide the user with a link to create a PR from the feature branch to main.

---

### System Prompt Structure

The agent system prompt should establish the agent's persona, capabilities, and constraints:

```typescript
const AGENT_SYSTEM_PROMPT = `You are a website builder agent. You create and edit web pages
by using the tools provided. You work in three phases:

Phase 1: Analyze the user's requirements and present brand brief options.
Phase 2: Present design options based on the selected brand.
Phase 3: Generate pages and refine based on feedback.

Rules:
- Always read existing content before updating it.
- Make targeted edits using update_block_content when the user requests small changes.
- Use update_page_content only for full page rewrites.
- Trigger preview after every content update so the user sees changes immediately.
- Explain what you're doing at each step.
- When generating HTML, follow EDS block structure conventions.
- Never ask the user for information you can reasonably infer from context.`
```

---

### Error Handling

| Error | Recovery |
|-------|----------|
| Tool execution fails | Return error as tool_result with `is_error: true`. Claude will retry or adapt. |
| Claude returns malformed tool input | Log and return validation error as tool_result. Claude self-corrects. |
| MAX_ITERATIONS reached | Return graceful message asking user to be more specific. |
| GitHub API rate limited | Wait and retry with exponential backoff (max 3 retries). |
| Preview generation fails | Emit `error` event with `recoverable: true`, continue without preview. |

---

### Cross-References

- **generative-page-pipeline** -- One-shot page generation used within Phase 3 for initial page creation
- **brand-extractor** -- Extracting brand identity from existing websites to seed brand brief options
- **brand-css-generator** -- Generating CSS overrides from brand briefs for design options
- **da-content-pipeline** -- DA format conversion and upload for EDS-based sites
- **session-context** -- Maintaining conversation state across agent loop iterations
