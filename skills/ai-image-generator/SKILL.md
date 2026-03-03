---
name: ai-image-generator
description: Generate images for web pages using multiple AI providers (fal.ai FLUX, Vertex AI Imagen, Gemini) with smart fallbacks, embedding-based caching, and R2 storage. Use when "generating AI images", "image generation", "creating hero images", or "AI-powered visuals".
---

# AI Image Generator

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| page-generation | "generating AI images", "image generation", "creating hero images", "AI-powered visuals" | High | 5 projects |

Generate images for web page blocks using multiple AI providers with automatic fallback chains, embedding-based cache lookup, and R2 storage for persistence. This skill handles provider selection, prompt enhancement, size configuration per block type, batch generation with concurrency limits, and resumable generation for large page sets.

## When to Use

- Generating images during page creation (hero banners, card thumbnails, column illustrations)
- Building a system that needs to generate multiple images in parallel with different sizes
- Implementing an image generation service with provider fallback (fal.ai down? fall back to Vertex AI)
- Caching generated images by semantic similarity to avoid regenerating similar images
- Generating brand-consistent images using LoRA-trained models
- Any pipeline that needs to produce web-optimized images from text prompts

## Instructions

### Providers and Models

The system supports four image generation providers, each with different speed, quality, and cost characteristics:

**fal.ai FLUX Schnell (Primary -- Fast)**

Ultra-fast generation (~1s per image). Best for high-volume batch generation where speed matters more than fine detail.

```typescript
const schnellConfig = {
  provider: 'fal',
  model: 'fal-ai/flux/schnell',
  inferenceSteps: 4,
  guidanceScale: 0,       // Schnell does not use guidance
  maxConcurrency: 20,
  costPer1MP: 0.003,      // ~$0.003 per 1-megapixel image
  avgLatency: '1-2s'
}
```

**fal.ai FLUX Dev with LoRA (Brand-Consistent)**

Higher quality with support for LoRA adapters trained on brand assets. Use when visual consistency with existing brand imagery matters.

```typescript
const devLoRAConfig = {
  provider: 'fal',
  model: 'fal-ai/flux-lora',
  inferenceSteps: 28,
  guidanceScale: 4.5,
  maxConcurrency: 10,     // Lower concurrency due to higher compute
  costPer1MP: 0.025,
  avgLatency: '3-5s',
  loraConfig: {
    path: 'https://storage.example.com/brand-lora.safetensors',
    scale: 0.8             // 0.0-1.0, how strongly to apply the LoRA
  }
}
```

**Vertex AI Imagen 3 (Google)**

Google's image generation model. Requires GCP service account with JWT authentication. Good alternative when fal.ai is unavailable.

```typescript
const imagenConfig = {
  provider: 'vertex',
  model: 'imagen-3.0-generate-002',
  sampleCount: 1,
  aspectRatio: '16:9',    // Supports: 1:1, 3:4, 4:3, 9:16, 16:9
  negativePrompt: 'blurry, low quality, watermark, text overlay',
  safetyFilterLevel: 'block_some',
  authMethod: 'jwt',
  avgLatency: '5-10s'
}
```

**Gemini (Prompt Enhancement)**

Not used for direct image generation in production. Instead, use Gemini to analyze content and enhance image prompts before sending them to fal.ai or Imagen.

```typescript
async function enhancePrompt(
  rawPrompt: string,
  blockType: string,
  brandContext: string
): Promise<string> {
  const response = await gemini.generate({
    prompt: `Enhance this image generation prompt for a ${blockType} block.
Raw prompt: "${rawPrompt}"
Brand context: ${brandContext}

Return an enhanced prompt that:
1. Adds specific visual details (lighting, composition, color palette)
2. Specifies photographic or illustration style
3. Includes negative prompt elements to avoid
4. Is optimized for FLUX model generation

Return only the enhanced prompt text, no explanation.`,
    temperature: 0.3
  })
  return response.text
}
```

See `references/provider-comparison.md` for a detailed comparison table of all providers.

---

### Size Configurations

Each block type has an optimal image size based on its layout and typical viewport:

```typescript
const IMAGE_SIZES: Record<string, { width: number; height: number; aspect: string }> = {
  hero:      { width: 1344, height: 768,  aspect: '16:9' },
  card:      { width: 768,  height: 576,  aspect: '4:3'  },
  column:    { width: 576,  height: 768,  aspect: '3:4'  },
  thumbnail: { width: 384,  height: 288,  aspect: '4:3'  },
  default:   { width: 768,  height: 768,  aspect: '1:1'  }
}
```

These sizes are chosen to produce images that are:
- Large enough to look sharp on 2x retina displays when displayed at their typical CSS size
- Small enough to keep file sizes reasonable (typically 100-400KB as WebP)
- Aspect-ratio-matched to the block layout to avoid cropping

When using Vertex AI Imagen (which accepts aspect ratio strings rather than pixel dimensions), map from the size config to the nearest supported aspect ratio.

---

### Request and Response Interfaces

```typescript
interface ImageRequest {
  prompt: string              // Text prompt describing the desired image
  blockType: string           // Block type for size selection
  blockId: string             // Unique identifier for this block instance
  provider?: string           // Override provider selection
  width?: number              // Override width from size config
  height?: number             // Override height from size config
  loraPath?: string           // Optional LoRA model path
  loraScale?: number          // LoRA strength (0.0-1.0)
  seed?: number               // Deterministic seed for reproducibility
  negativePrompt?: string     // What to avoid in the image
}

interface GeneratedImage {
  url: string                 // R2 public URL of the stored image
  r2Key: string               // R2 object key for direct access
  provider: string            // Which provider generated this image
  prompt: string              // The prompt used (may be enhanced)
  width: number
  height: number
  generationTime: number      // Milliseconds to generate
  blockId: string             // Which block this image belongs to
  seed?: number               // Seed used (for reproducibility)
  cached: boolean             // Whether this was a cache hit
}
```

---

### Smart Fallback Strategy

When generating images for a page with multiple blocks, use a three-tier fallback strategy:

**Tier 1: Partition by type**

Group image requests by block type and assign providers based on priority:

```typescript
function assignProvider(request: ImageRequest): string {
  // LoRA requests must go to fal-dev
  if (request.loraPath) return 'fal-dev-lora'

  // Hero images benefit from higher quality
  if (request.blockType === 'hero') return 'fal-dev-lora'

  // Everything else uses Schnell for speed
  return 'fal-schnell'
}
```

**Tier 2: Reuse siblings**

If multiple cards need images and one card's image generation fails, check if a sibling card's image can be reused with a different crop or if a semantically similar cached image exists.

```typescript
async function findSiblingFallback(
  failedRequest: ImageRequest,
  successfulResults: GeneratedImage[]
): Promise<GeneratedImage | null> {
  // Look for a successfully generated image from the same block type
  const sibling = successfulResults.find(
    r => r.blockType === failedRequest.blockType && r.blockId !== failedRequest.blockId
  )
  return sibling || null
}
```

**Tier 3: Deterministic hash-based fallback**

As a last resort, generate a deterministic color gradient or pattern based on the prompt hash:

```typescript
function generateFallbackImage(request: ImageRequest): GeneratedImage {
  // Hash the prompt to get deterministic colors
  const hash = hashString(request.prompt)
  const hue = hash % 360
  const size = IMAGE_SIZES[request.blockType] || IMAGE_SIZES.default

  // Generate a gradient SVG placeholder
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size.width}" height="${size.height}">
    <defs>
      <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:hsl(${hue},60%,70%)" />
        <stop offset="100%" style="stop-color:hsl(${(hue + 40) % 360},60%,50%)" />
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#g)" />
  </svg>`

  return {
    url: `data:image/svg+xml;base64,${btoa(svg)}`,
    provider: 'fallback',
    cached: false,
    // ... other fields
  }
}
```

The full fallback chain: Primary provider -> Alternate provider -> Sibling reuse -> Hash-based placeholder.

---

### Embedding-Based Caching

Before generating a new image, check if a semantically similar image already exists in the cache. This uses vector embeddings of the prompt text to find near-matches.

**D1 schema:**

```sql
CREATE TABLE image_library (
  id TEXT PRIMARY KEY,
  prompt TEXT NOT NULL,
  prompt_embedding BLOB,          -- 768-dim float32 embedding
  r2_key TEXT NOT NULL,
  provider TEXT NOT NULL,
  width INTEGER NOT NULL,
  height INTEGER NOT NULL,
  aspect_ratio REAL NOT NULL,     -- width/height as decimal
  block_type TEXT,
  generation_time_ms INTEGER,
  created_at TEXT DEFAULT (datetime('now')),
  site_id TEXT
);
```

**Cache lookup:**

```typescript
async function findCachedImage(
  prompt: string,
  targetAspect: number,
  env: Env
): Promise<GeneratedImage | null> {
  // Generate embedding for the prompt
  const embedding = await env.AI.run('@cf/baai/bge-base-en-v1.5', {
    text: [prompt]
  })

  // Query Vectorize for similar prompts
  const results = await env.VECTORIZE.query(embedding.data[0], {
    topK: 5,
    returnMetadata: true,
    filter: { site_id: env.SITE_ID }
  })

  // Filter by similarity threshold and aspect ratio tolerance
  for (const match of results.matches) {
    if (match.score < 0.85) continue

    const cachedAspect = match.metadata.aspect_ratio as number
    if (Math.abs(cachedAspect - targetAspect) > 0.1) continue

    // Cache hit
    return {
      url: `${env.R2_PUBLIC_URL}/${match.metadata.r2_key}`,
      r2Key: match.metadata.r2_key as string,
      provider: match.metadata.provider as string,
      prompt: match.metadata.prompt as string,
      width: match.metadata.width as number,
      height: match.metadata.height as number,
      generationTime: 0,
      blockId: '',
      cached: true
    }
  }

  return null
}
```

Key rules:
- Similarity threshold: `0.85`. Lower values return too many false positives (visually different images). Higher values miss valid cache hits.
- Aspect ratio tolerance: `0.1`. A 16:9 image (1.78) will not match a 4:3 request (1.33), but a 1344x768 image will match a 1280x720 request.
- Always check the cache before generating. Cache hits save both money and latency.
- Store every generated image in the cache after generation, even fallback images.

---

### Batch Generation

When generating images for an entire page, use controlled concurrency to avoid provider rate limits:

```typescript
async function generateBatch(
  requests: ImageRequest[],
  env: Env
): Promise<GeneratedImage[]> {
  const results: GeneratedImage[] = []
  const concurrencyLimit = requests.some(r => r.loraPath)
    ? 10   // LoRA requests are heavier
    : 20   // Schnell can handle more concurrency

  // Process in batches
  for (let i = 0; i < requests.length; i += concurrencyLimit) {
    const batch = requests.slice(i, i + concurrencyLimit)
    const batchResults = await Promise.allSettled(
      batch.map(async request => {
        // Check cache first
        const targetAspect = (request.width || IMAGE_SIZES[request.blockType].width) /
                             (request.height || IMAGE_SIZES[request.blockType].height)
        const cached = await findCachedImage(request.prompt, targetAspect, env)
        if (cached) return { ...cached, blockId: request.blockId }

        // Generate
        return await generateSingleImage(request, env)
      })
    )

    for (const result of batchResults) {
      if (result.status === 'fulfilled') {
        results.push(result.value)
      } else {
        console.error('Image generation failed:', result.reason)
        // Use fallback strategy
      }
    }
  }

  return results
}
```

Key rules:
- Use `Promise.allSettled`, not `Promise.all`. Individual failures should not abort the entire batch.
- Concurrency limits: 10 for LoRA, 20 for Schnell. These are empirically tested against fal.ai rate limits.
- Process batches sequentially (one batch at a time) to avoid overwhelming the provider.

---

### R2 Storage

Store all generated images in Cloudflare R2 with structured metadata:

```typescript
async function storeImage(
  imageBuffer: ArrayBuffer,
  request: ImageRequest,
  provider: string,
  generationTime: number,
  env: Env
): Promise<string> {
  const key = `images/${env.SITE_ID}/${request.blockType}/${request.blockId}.webp`

  await env.R2_BUCKET.put(key, imageBuffer, {
    httpMetadata: {
      contentType: 'image/webp',
      cacheControl: 'public, max-age=31536000'  // 1 year cache
    },
    customMetadata: {
      prompt: request.prompt,
      blockId: request.blockId,
      blockType: request.blockType,
      provider: provider,
      generationTime: String(generationTime),
      width: String(request.width || IMAGE_SIZES[request.blockType].width),
      height: String(request.height || IMAGE_SIZES[request.blockType].height),
      generatedAt: new Date().toISOString()
    }
  })

  return key
}
```

Key rules:
- Always store as WebP format. Convert from PNG/JPEG if the provider returns a different format.
- Set `Cache-Control: public, max-age=31536000` (1 year). Images are addressed by content-based keys and are effectively immutable.
- Key structure: `images/{siteId}/{blockType}/{blockId}.webp`. This allows easy listing of all images for a specific block type or site.
- Store the original prompt in custom metadata for debugging and cache indexing.

---

### Brand Color Injection

When generating images for a branded site, inject the brand's color palette into the generation prompt:

```typescript
function injectBrandColors(
  prompt: string,
  brandColors: { primary: string; secondary: string; accent: string }
): string {
  return `${prompt}. Use a color palette featuring ${brandColors.primary} as the dominant color, with ${brandColors.secondary} as secondary and ${brandColors.accent} as accent highlights. Maintain visual consistency with this color scheme.`
}
```

Key rules:
- Only inject brand colors when the prompt does not already specify colors.
- For photographic images, use brand colors subtly (lighting tint, background elements). For illustrations and graphics, use them prominently.
- Never inject brand colors into prompts for product photography or realistic portraits -- it produces unnatural results.

---

### Resumable Generation

For large page sets (e.g., generating images for 20+ pages in a batch), support resumable generation by checking which images already exist:

```typescript
async function generateWithResume(
  requests: ImageRequest[],
  env: Env
): Promise<GeneratedImage[]> {
  const results: GeneratedImage[] = []

  for (const request of requests) {
    const key = `images/${env.SITE_ID}/${request.blockType}/${request.blockId}.webp`

    // Check if image already exists in R2
    const existing = await env.R2_BUCKET.head(key)
    if (existing) {
      results.push({
        url: `${env.R2_PUBLIC_URL}/${key}`,
        r2Key: key,
        provider: existing.customMetadata?.provider || 'unknown',
        prompt: existing.customMetadata?.prompt || request.prompt,
        width: parseInt(existing.customMetadata?.width || '768'),
        height: parseInt(existing.customMetadata?.height || '768'),
        generationTime: 0,
        blockId: request.blockId,
        cached: true
      })
      continue  // Skip generation
    }

    // Generate new image
    const generated = await generateSingleImage(request, env)
    results.push(generated)
  }

  return results
}
```

This is critical for recovery scenarios: if a page generation pipeline fails at Stage 5 (assembly) after all images have been generated, resumable generation avoids regenerating (and paying for) all images on retry.

---

### Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Provider 429 (rate limited) | Too many concurrent requests | Reduce concurrency, retry with exponential backoff |
| Provider 500 (server error) | Provider outage | Switch to fallback provider |
| NSFW content filter | Prompt triggered safety filter | Rephrase prompt to remove potentially flagged terms, retry |
| Timeout (>30s) | Provider overloaded | Retry once, then use fallback provider |
| R2 upload failure | R2 outage or quota | Retry with backoff; return image URL directly from provider as temporary fallback |
| Embedding generation failure | Workers AI overloaded | Skip cache lookup, generate directly |

---

### Brand Style Brief Integration

When a project includes a `brand/*-style-brief.md` or `brand/*-style-config.sh`, use the tier system to select appropriate style prefixes and negative prompts per image.

**Tier System** (4 tiers + generic fallback):

| Tier | Name | Use Case | Style |
|------|------|----------|-------|
| tier1 | Double-Exposure Artistic | Homepage heroes, therapy area cards | Human silhouette filled with scientific/natural imagery |
| tier2 | Warm Lifestyle Photography | Product heroes, patient benefit sections | Natural-light photos of patients in everyday settings |
| tier3 | Product & Device Photography | Dosing pages, device guides | Clean product shots on white/light backgrounds |
| tier4 | Dramatic/Abstract Hero | Oncology heroes, severe disease products | Bold CGI, aurora borealis, dramatic landscapes |
| (none) | Generic | Backwards-compatible default | Photorealistic pharmaceutical style |

**How to apply tiers:**

1. Check if `brand/az-image-style-config.sh` (or equivalent) exists in the project
2. Each tier provides a `TIER{N}_PREFIX` (style instruction prepended to the prompt) and `TIER{N}_NEGATIVE` (appended as "Avoid: ..." clause)
3. When generating image prompts, assign a tier based on block type and content:
   - Hero blocks on homepage / therapy pages → tier1
   - Hero blocks on product pages → tier2
   - Product/device images → tier3
   - Oncology / severe disease heroes → tier4
   - Everything else → omit tier for generic fallback
4. Include the tier as a parameter in the generation call (e.g., the 3rd arg to `generate_image` in bash scripts)

**For TypeScript/Workers implementations**, read the style config and map tiers to prompt enhancement:

```typescript
interface TierConfig {
  prefix: string
  negative: string
}

function applyTier(prompt: string, tier: string, config: Record<string, TierConfig>): string {
  const tierConfig = config[tier] || config.generic
  let enhanced = `${tierConfig.prefix} ${prompt}`
  if (tierConfig.negative) {
    enhanced += `. Avoid: ${tierConfig.negative}.`
  }
  return enhanced
}
```

---

### Reference Image Grounding

When `brand/reference-images/tier{1,2,3,4}/` directories exist with curated reference images, use them as multi-modal style references to improve brand alignment of generated images.

**How it works:**

1. For each generation request with a tier, check if `brand/reference-images/{tier}/` contains any images
2. Randomly select one reference image from the tier directory (style grounding, not content matching — any image in the tier is valid for any prompt in that tier)
3. Base64-encode the reference image and include it as an `inlineData` part in the multi-modal API payload
4. Prepend "Generate an image matching the visual style of this reference." to the text prompt

**For Gemini API (bash `generate-images.sh`):**

The reference image is sent as the first part in the `contents` array:
```json
{
  "contents": [{
    "parts": [
      {"inlineData": {"mimeType": "image/jpeg", "data": "<base64>"}},
      {"text": "Generate an image matching the visual style of this reference. <tier prefix> <user prompt>"}
    ]
  }],
  "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}
```

**For fal.ai FLUX / Imagen (TypeScript):**

These providers don't support multi-modal reference input directly. Instead:
- Use the reference image to enhance the text prompt via Gemini vision: send the reference + "Describe the visual style of this image in detail for an image generation prompt" → append the style description to the generation prompt
- Alternatively, if using FLUX with LoRA, train on the reference images for stronger style consistency

**Populating reference images:**

Run `node tools/crawl-az-references.mjs` to crawl the brand website and auto-classify images into tiers. Then review `brand/reference-images/manifest.json` and reclassify as needed. Target: 3-5 images per tier.

**Key rules:**
- Reference images ground style, not content. A cardiovascular tier2 photo is valid for a respiratory tier2 generation
- Random selection per generation call ensures variety while maintaining tier-consistent style
- Always log which reference image was used (for debugging and reproducibility)
- Reference images should be real brand photography, not AI-generated

---

### Cross-References

- **multi-provider-fallback** -- General multi-provider fallback patterns and health checking
- **generative-page-pipeline** -- Stage 4 consumes this skill for parallel image generation during page creation
- **cloudflare-fullstack** -- R2 bucket bindings, Workers AI configuration, and Vectorize setup
- **brand-extractor** -- Extract brand profiles that can inform tier selection and colour injection
