---
name: generative-page-pipeline
description: Build multi-stage AI pipelines that transform user queries into complete web pages through intent classification, reasoning-driven block selection, parallel content generation, and DA persistence. Use when building "page generation", "AI website builder", "content generation pipeline", or "generative web pages".
---

# Generative Page Pipeline

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| page-generation | "page generation", "AI website builder", "content generation pipeline", "generative web pages" | High | 6 projects |

Transform a user's natural language query into a fully rendered, DA-persisted web page by orchestrating multiple AI models through a five-stage pipeline. Each stage is designed for a specific latency and quality profile: fast classification up front, deep reasoning in the middle, and parallel content generation at scale.

## When to Use

- Building a generative AI website builder that creates pages from user prompts
- Implementing a multi-model pipeline where different models handle classification, reasoning, and content generation
- Creating web pages that must conform to a block-based CMS structure (EDS / Document Authoring)
- Generating pages that need RAG-augmented context from existing site content
- Building a system that streams progress events to the client during page generation
- Any pipeline that requires intent classification followed by structured content generation

## Instructions

### Pipeline Architecture

The pipeline executes five stages sequentially, with parallelism within stages 3 and 4:

```
User Query
  -> Stage 1: Intent Classification       (Cerebras 8B,    ~200ms)
  -> Stage 2: Deep Reasoning + Block Plan  (Claude Opus,    ~5-15s)
  -> Stage 3: Parallel Content Generation  (Cerebras 120B,  ~2-5s)
  -> Stage 4: Parallel Image Generation    (fal.ai/Imagen,  ~3-8s)
  -> Stage 5: HTML Assembly + DA Persist   (deterministic,  ~1-2s)
```

Total end-to-end latency target: 12-30 seconds for a full page.

---

### Stage 1: Intent Classification

Use a fast, small model (Cerebras Llama 8B) to classify the user's intent and extract entities. This stage must complete in under 300ms to keep the pipeline responsive.

```typescript
interface ClassificationResult {
  intentType: 'new_page' | 'edit_page' | 'add_section' | 'change_style' | 'question'
  entities: string[]           // Extracted nouns, topics, product names
  journeyStage: 'exploring' | 'comparing' | 'deciding' | 'supporting'
  confidence: number           // 0-1 confidence score
  suggestedPageType?: string   // e.g., "product-landing", "faq", "comparison"
}

async function classifyIntent(
  query: string,
  modelFactory: ModelFactory,
  env: Env,
  sessionContext?: SessionContext
): Promise<ClassificationResult> {
  const model = modelFactory.getModel('cerebras-8b')
  const systemPrompt = `You are an intent classifier for a web page generation system.
Classify the user's query and extract structured data.
Return valid JSON matching the ClassificationResult schema.
${sessionContext ? `Previous queries: ${JSON.stringify(sessionContext.queries.slice(-3))}` : ''}`

  const response = await model.generate({
    system: systemPrompt,
    prompt: query,
    temperature: 0,
    maxTokens: 256,
    responseFormat: 'json'
  })

  return JSON.parse(response.text)
}
```

Key rules:
- Always set `temperature: 0` for classification -- determinism matters more than creativity here.
- Pass the last 3 queries from session context (if available) so the classifier can detect follow-up intents like "now add a testimonials section" without re-explaining the full context.
- If `confidence < 0.6`, fall back to a clarification response instead of generating a page.

---

### Stage 2: Deep Reasoning + Block Selection

Use Claude Opus with extended thinking to analyze the query deeply, select appropriate blocks, and plan the page structure. This is the "brain" of the pipeline.

```typescript
interface BlockPlan {
  pageTitle: string
  pageDescription: string
  blocks: BlockSelection[]
  brandVoiceNotes: string
  targetAudience: string
}

interface BlockSelection {
  blockType: string           // Must match a BlockCatalogEntry.name
  purpose: string             // Why this block was chosen
  contentBrief: string        // What content to generate for this block
  dataRequirements: string[]  // What data/entities to include
  imageNeeded: boolean        // Whether this block needs a generated image
  imagePrompt?: string        // Prompt for image generation if needed
}
```

Provide the full block catalog to Claude as structured context:

```typescript
interface BlockCatalogEntry {
  name: string
  category: 'hero' | 'content' | 'social-proof' | 'conversion' | 'navigation'
  whenToUse: string
  dataRequirements: string[]
  guardrails: string[]
}
```

**Default Block Catalog:**

| Block | Category | When to Use |
|-------|----------|-------------|
| `hero` | hero | Opening section with headline, subheadline, CTA, and optional background image |
| `cards` | content | Presenting 3-6 related items (features, products, services) in a grid |
| `columns` | content | Side-by-side content comparison or multi-column layout (2-4 columns) |
| `accordion` | content | FAQ sections or content that benefits from progressive disclosure |
| `tabs` | content | Organizing related content into switchable views (pricing tiers, categories) |
| `table` | content | Structured data comparison, specifications, pricing matrices |
| `testimonials` | social-proof | Customer quotes, reviews, case study excerpts |
| `cta` | conversion | Call-to-action sections with headline, description, and button |

Send the block catalog, classification result, RAG context, and brand voice to Claude Opus:

```typescript
const blockPlan = await claudeOpus.generate({
  system: `You are a web page architect. Given the user's intent, available blocks,
and brand context, plan a complete page structure.
Select 4-8 blocks. Order them for optimal user journey.
Write detailed content briefs for each block.`,
  prompt: `Intent: ${JSON.stringify(classification)}
Block Catalog: ${JSON.stringify(blockCatalog)}
Brand Voice: ${brandVoice}
RAG Context: ${ragContext}
User Query: ${query}`,
  thinking: { enabled: true, budgetTokens: 4096 },
  maxTokens: 4096,
  responseFormat: 'json'
})
```

Key rules:
- Always enable extended thinking with at least 4096 token budget. Block selection benefits enormously from chain-of-thought reasoning about page flow and user journey.
- Limit blocks to 4-8 per page. Fewer than 4 feels sparse; more than 8 creates scroll fatigue.
- The content brief for each block should be 2-4 sentences describing the specific content, not generic instructions. Bad: "Write compelling copy." Good: "Highlight the three core differentiators mentioned in the RAG context: zero-downtime deployment, automatic scaling, and SOC2 compliance."

---

### Stage 3: Parallel Content Generation

Generate content for all blocks in parallel using Cerebras 120B for speed. Each block gets its own generation call.

```typescript
async function generateBlockContent(
  block: BlockSelection,
  brandVoice: BrandVoice,
  modelFactory: ModelFactory
): Promise<BlockContent> {
  const model = modelFactory.getModel('cerebras-120b')
  const schema = BLOCK_CONTENT_SCHEMAS[block.blockType]

  const response = await model.generate({
    system: `You are a web content writer. Generate content for a ${block.blockType} block.
Brand voice: ${brandVoice.tone}. Target audience: ${brandVoice.audience}.
Return valid JSON matching the provided schema exactly.`,
    prompt: `Content Brief: ${block.contentBrief}
Required Data: ${block.dataRequirements.join(', ')}
Output Schema: ${JSON.stringify(schema)}`,
    temperature: 0.7,
    maxTokens: 2048,
    responseFormat: 'json'
  })

  return JSON.parse(response.text)
}

// Generate all blocks in parallel
const blockContents = await Promise.all(
  blockPlan.blocks.map(block => generateBlockContent(block, brandVoice, modelFactory))
)
```

See `references/block-schemas.md` for the complete content schema for each block type.

Key rules:
- Use `temperature: 0.7` for content generation. This balances creativity with coherence.
- Always validate the returned JSON against the block schema before proceeding. If validation fails, retry once with `temperature: 0.3` and an explicit error message appended to the prompt.
- Set a per-block timeout of 10 seconds. If a single block times out, substitute a placeholder and continue -- do not block the entire pipeline.

---

### Stage 4: Parallel Image Generation

For blocks that require images (`imageNeeded: true`), generate them in parallel using fal.ai or Vertex AI Imagen.

```typescript
const imagePromises = blockPlan.blocks
  .filter(block => block.imageNeeded && block.imagePrompt)
  .map(async block => {
    const size = IMAGE_SIZES[block.blockType] || IMAGE_SIZES.default
    return {
      blockType: block.blockType,
      image: await generateImage({
        prompt: block.imagePrompt,
        width: size.width,
        height: size.height,
        provider: 'fal-schnell'  // fastest provider
      })
    }
  })

const images = await Promise.all(imagePromises)
```

Image generation runs in parallel with any remaining content generation that has not yet resolved. See the `ai-image-generator` skill for provider selection, fallback strategies, and caching.

---

### Stage 5: HTML Assembly + DA Persistence

Assemble the generated content into EDS-compliant HTML and persist to DA.

**EDS-compliant HTML structure:**

```html
<main>
  <div>
    <!-- Default content / section break -->
  </div>
  <div class="hero">
    <div>
      <div>
        <h1>Headline</h1>
        <p>Subheadline</p>
        <p><a href="/cta-link">CTA Text</a></p>
      </div>
      <div>
        <picture><img src="/generated/hero.webp" alt="Alt text" /></picture>
      </div>
    </div>
  </div>
  <hr/>
  <div class="cards">
    <div>
      <div><picture><img src="/generated/card1.webp" alt="" /></picture></div>
      <div>
        <h3>Card Title</h3>
        <p>Card description text.</p>
      </div>
    </div>
    <!-- More card rows -->
  </div>
  <hr/>
  <!-- More blocks separated by <hr/> -->
</main>
```

**Hybrid mode for existing scaffolds:**

When generating content for an existing page that already has a `.plain.html` scaffold, merge generated blocks into the existing structure rather than replacing the entire page. Parse the existing HTML, identify blocks by class name, and replace only the blocks that were regenerated.

```typescript
function assembleHtml(blocks: BlockContent[], images: ImageResult[]): string {
  const sections = blocks.map(block => {
    const renderer = BLOCK_RENDERERS[block.type]
    const blockImages = images.filter(img => img.blockType === block.type)
    return renderer(block, blockImages)
  })

  return `<main>\n${sections.join('\n<hr/>\n')}\n</main>`
}
```

**DA Persistence:**

Upload the assembled HTML to DA using a FormData POST:

```typescript
async function persistToDA(html: string, path: string, env: Env): Promise<void> {
  const formData = new FormData()
  formData.append('data', new Blob([html], { type: 'text/html' }), `${path}.html`)

  await fetch(`https://admin.da.live/source/${env.DA_ORG}/${env.DA_REPO}/${path}.html`, {
    method: 'PUT',
    headers: { Authorization: `Bearer ${env.DA_TOKEN}` },
    body: formData
  })
}
```

After persistence, trigger a preview:

```typescript
await fetch(`https://admin.hlx.page/preview/${env.DA_ORG}/${env.DA_REPO}/main/${path}`, {
  method: 'POST'
})
```

---

### RAG Context Retrieval

Before Stage 2, retrieve relevant existing content to inform block selection and content generation.

```typescript
async function retrieveRAGContext(
  query: string,
  env: Env
): Promise<RAGResult[]> {
  const embedding = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
    text: [query]
  })

  const vectorResults = await env.VECTORIZE.query(embedding.data[0], {
    topK: 5,
    returnMetadata: true
  })

  // Filter by score threshold
  return vectorResults.matches
    .filter(match => match.score > 0.5)
    .map(match => ({
      content: match.metadata.content,
      path: match.metadata.path,
      score: match.score
    }))
}
```

Set a 3-second timeout on RAG retrieval. If it times out or returns no results, proceed without RAG context -- the pipeline should never block on missing context. Pass retrieved content into the Stage 2 prompt as supplementary information, not as a hard constraint.

---

### Brand Voice Integration

Load brand voice settings from D1 and inject into content generation prompts:

```typescript
interface BrandVoice {
  tone: string            // e.g., "professional but approachable"
  audience: string        // e.g., "enterprise IT decision makers"
  vocabulary: string[]    // preferred terms
  avoidTerms: string[]    // terms to never use
  exampleCopy: string     // reference copy sample
}

async function loadBrandVoice(siteId: string, env: Env): Promise<BrandVoice> {
  const result = await env.DB.prepare(
    'SELECT * FROM brand_voice WHERE site_id = ? LIMIT 1'
  ).bind(siteId).first()

  if (!result) return DEFAULT_BRAND_VOICE
  return {
    tone: result.tone,
    audience: result.audience,
    vocabulary: JSON.parse(result.vocabulary),
    avoidTerms: JSON.parse(result.avoid_terms),
    exampleCopy: result.example_copy
  }
}
```

Inject brand voice into every content generation prompt. The tone and vocabulary fields are the most impactful -- include them in the system prompt. The `avoidTerms` list should be injected as a hard constraint: "Never use these words: ${avoidTerms.join(', ')}."

---

### SSE Event Types

Stream progress events to the client throughout the pipeline:

| Event Type | Payload | When Emitted |
|------------|---------|-------------|
| `generation-start` | `{ query, intentType }` | Pipeline begins |
| `reasoning-start` | `{}` | Stage 2 begins |
| `reasoning-step` | `{ thinking }` | Each reasoning token (streamed) |
| `reasoning-complete` | `{ blockCount }` | Stage 2 completes |
| `block-start` | `{ blockType, index, total }` | Each block begins generation |
| `block-content` | `{ blockType, content }` | Block content ready |
| `block-complete` | `{ blockType, index }` | Block fully rendered |
| `image-start` | `{ blockType, prompt }` | Image generation begins |
| `image-complete` | `{ blockType, url }` | Image uploaded to R2 |
| `persist-start` | `{ path }` | DA upload begins |
| `persist-complete` | `{ path, previewUrl }` | DA upload and preview done |
| `generation-complete` | `{ totalTime, blockCount, pageUrl }` | Pipeline complete |
| `error` | `{ stage, message, recoverable }` | Error at any stage |

Emit events using the standard SSE format:

```typescript
function emitEvent(stream: WritableStream, type: string, data: any) {
  const encoder = new TextEncoder()
  stream.write(encoder.encode(`event: ${type}\ndata: ${JSON.stringify(data)}\n\n`))
}
```

---

### Model Factory Presets

Configure model selection based on deployment environment:

**Production preset (quality-optimized):**

| Stage | Model | Provider | Purpose |
|-------|-------|----------|---------|
| Classification | Llama 3.1 8B | Cerebras | Fast intent classification |
| Reasoning | Claude Opus | Anthropic | Deep reasoning + block planning |
| Content | Llama 3.3 120B | Cerebras | Fast, high-quality content |
| Images | FLUX Schnell | fal.ai | Ultra-fast image generation |

**Fast preset (speed-optimized):**

| Stage | Model | Provider | Purpose |
|-------|-------|----------|---------|
| Classification | Llama 3.1 8B | Cerebras | Same as production |
| Reasoning | Claude Sonnet | Anthropic | Faster reasoning, slightly less depth |
| Content | Llama 3.3 120B | Cerebras | Same as production |
| Images | FLUX Schnell | fal.ai | Same as production |

```typescript
const MODEL_PRESETS = {
  production: {
    classification: { provider: 'cerebras', model: 'llama-3.1-8b' },
    reasoning: { provider: 'anthropic', model: 'claude-opus-4-20250514' },
    content: { provider: 'cerebras', model: 'llama-3.3-120b' },
    images: { provider: 'fal', model: 'fal-ai/flux/schnell' }
  },
  fast: {
    classification: { provider: 'cerebras', model: 'llama-3.1-8b' },
    reasoning: { provider: 'anthropic', model: 'claude-sonnet-4-20250514' },
    content: { provider: 'cerebras', model: 'llama-3.3-120b' },
    images: { provider: 'fal', model: 'fal-ai/flux/schnell' }
  }
}
```

---

### Error Handling and Recovery

Each stage should catch errors independently and decide whether to abort or continue with degraded output:

| Stage | Error | Recovery |
|-------|-------|----------|
| Classification | Model timeout | Retry once, then default to `new_page` intent |
| Reasoning | Token limit exceeded | Truncate RAG context by 50%, retry |
| Content Gen | Single block fails | Use placeholder content, mark block as draft |
| Image Gen | Provider down | Fall back to next provider (see `ai-image-generator`) |
| DA Persist | Auth failure | Refresh IMS token, retry once |
| DA Persist | Upload 413 | Compress images, strip unnecessary markup, retry |

Never let a single block failure abort the entire pipeline. Emit an `error` event with `recoverable: true` and continue with remaining blocks.

---

### Cross-References

- **sse-streaming** -- SSE connection management and client-side event handling patterns
- **multi-model-orchestrator** -- Model factory implementation and provider abstraction layer
- **session-context** -- Session context propagation for multi-turn page generation
- **da-content-pipeline** -- DA format conversion and upload mechanics used in Stage 5
- **ai-image-generator** -- Image generation providers and fallback strategies for Stage 4
