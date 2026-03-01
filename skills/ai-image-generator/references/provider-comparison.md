# Provider Comparison

Detailed comparison of all image generation providers supported by the AI Image Generator skill.

---

## Overview Table

| Property | fal.ai FLUX Schnell | fal.ai FLUX Dev + LoRA | Vertex AI Imagen 3 | Gemini |
|----------|--------------------|-----------------------|--------------------| -------|
| **Primary Use** | High-volume batch | Brand-consistent | Fallback / GCP shops | Prompt enhancement |
| **Speed** | ~1-2s | ~3-5s | ~5-10s | ~2-3s |
| **Quality** | Good | High | High | N/A (text only) |
| **Cost per 1MP** | ~$0.003 | ~$0.025 | ~$0.020 | N/A |
| **Max Concurrency** | 20 | 10 | 5 | 20 |
| **Auth Method** | API key | API key | JWT (service account) | API key |
| **LoRA Support** | No | Yes | No | No |
| **Aspect Ratios** | Any (pixel dims) | Any (pixel dims) | 1:1, 3:4, 4:3, 9:16, 16:9 | N/A |
| **Output Format** | PNG/JPEG | PNG/JPEG | PNG | N/A |
| **Safety Filter** | Minimal | Minimal | Configurable (4 levels) | N/A |

---

## fal.ai FLUX Schnell

**When to use:** Default provider for all non-brand-critical images. Best for cards, thumbnails, and any block where speed matters more than pixel-perfect brand consistency.

**Configuration:**

```typescript
{
  model: 'fal-ai/flux/schnell',
  num_inference_steps: 4,
  image_size: { width: 1344, height: 768 },  // Or any pixel dimensions
  num_images: 1,
  enable_safety_checker: true
}
```

**API call:**

```typescript
const response = await fetch('https://fal.run/fal-ai/flux/schnell', {
  method: 'POST',
  headers: {
    'Authorization': `Key ${env.FAL_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: request.prompt,
    image_size: { width: request.width, height: request.height },
    num_inference_steps: 4,
    num_images: 1,
    enable_safety_checker: true
  })
})

const result = await response.json()
const imageUrl = result.images[0].url
```

**Strengths:**
- Extremely fast (1-2 seconds for a 1MP image)
- Cheap at scale ($0.003 per image)
- High concurrency tolerance (20 parallel requests)
- No guidance scale needed (the model is distilled for direct generation)

**Weaknesses:**
- Lower detail fidelity compared to Dev model
- No LoRA support for brand consistency
- Limited control over style (fewer inference steps means less refinement)
- Occasional artifacts in complex scenes with many subjects

---

## fal.ai FLUX Dev with LoRA

**When to use:** Hero images, brand-critical visuals, and any content where the image must match the brand's visual identity. Use when a LoRA adapter has been trained on brand assets.

**Configuration:**

```typescript
{
  model: 'fal-ai/flux-lora',
  num_inference_steps: 28,
  guidance_scale: 4.5,
  image_size: { width: 1344, height: 768 },
  num_images: 1,
  loras: [
    {
      path: 'https://storage.example.com/brand-lora.safetensors',
      scale: 0.8
    }
  ],
  enable_safety_checker: true
}
```

**API call:**

```typescript
const response = await fetch('https://fal.run/fal-ai/flux-lora', {
  method: 'POST',
  headers: {
    'Authorization': `Key ${env.FAL_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: request.prompt,
    image_size: { width: request.width, height: request.height },
    num_inference_steps: 28,
    guidance_scale: 4.5,
    num_images: 1,
    loras: request.loraPath ? [{
      path: request.loraPath,
      scale: request.loraScale || 0.8
    }] : [],
    enable_safety_checker: true,
    seed: request.seed
  })
})
```

**LoRA scale tuning:**
- `0.5-0.7`: Subtle brand influence, more creative freedom
- `0.7-0.9`: Strong brand consistency, recommended for most uses
- `0.9-1.0`: Very strong brand adherence, may reduce prompt responsiveness

**Strengths:**
- High-quality output with fine detail
- LoRA support for brand-trained models
- Controllable via guidance scale and inference steps
- Deterministic output with seed parameter

**Weaknesses:**
- 3-5x slower than Schnell
- 8x more expensive per image
- Lower concurrency tolerance (10 max)
- LoRA model must be hosted and accessible via URL

---

## Vertex AI Imagen 3

**When to use:** Fallback when fal.ai is unavailable, or in GCP-native environments where Vertex AI is already integrated. Also preferred when Google's content safety filtering is required.

**Authentication:**

Imagen 3 requires GCP service account authentication via JWT:

```typescript
async function getVertexAccessToken(env: Env): Promise<string> {
  const serviceAccount = JSON.parse(env.GCP_SERVICE_ACCOUNT_JSON)

  const jwt = await createJWT({
    iss: serviceAccount.client_email,
    scope: 'https://www.googleapis.com/auth/cloud-platform',
    aud: 'https://oauth2.googleapis.com/token',
    exp: Math.floor(Date.now() / 1000) + 3600,
    iat: Math.floor(Date.now() / 1000)
  }, serviceAccount.private_key)

  const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`
  })

  const { access_token } = await tokenResponse.json()
  return access_token
}
```

**API call:**

```typescript
const accessToken = await getVertexAccessToken(env)

const response = await fetch(
  `https://${env.GCP_REGION}-aiplatform.googleapis.com/v1/projects/${env.GCP_PROJECT}/locations/${env.GCP_REGION}/publishers/google/models/imagen-3.0-generate-002:predict`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      instances: [{
        prompt: request.prompt
      }],
      parameters: {
        sampleCount: 1,
        aspectRatio: mapToImagenAspectRatio(request.width, request.height),
        negativePrompt: request.negativePrompt || 'blurry, low quality, watermark',
        safetyFilterLevel: 'block_some'
      }
    })
  }
)

const result = await response.json()
const imageBase64 = result.predictions[0].bytesBase64Encoded
const imageBuffer = base64ToArrayBuffer(imageBase64)
```

**Aspect ratio mapping:**

```typescript
function mapToImagenAspectRatio(width: number, height: number): string {
  const ratio = width / height
  if (ratio > 1.5) return '16:9'
  if (ratio > 1.1) return '4:3'
  if (ratio < 0.67) return '9:16'
  if (ratio < 0.9) return '3:4'
  return '1:1'
}
```

**Safety filter levels:**
- `block_none`: No filtering (not recommended for production)
- `block_few`: Block only clearly harmful content
- `block_some`: Moderate filtering (recommended default)
- `block_most`: Aggressive filtering

**Strengths:**
- High-quality output from Google's latest model
- Configurable safety filtering with fine-grained control
- Native GCP integration (no additional vendor)
- Supports negative prompts natively

**Weaknesses:**
- Complex JWT authentication setup
- Limited aspect ratio options (5 fixed ratios, no arbitrary dimensions)
- Slower than fal.ai (5-10 seconds typical)
- Lower concurrency limit (5 max before rate limiting)
- Returns base64-encoded images (additional decode step)

---

## Gemini (Prompt Enhancement Only)

**When to use:** Not for direct image generation. Use Gemini to analyze page content and enhance image prompts before sending them to fal.ai or Imagen.

**Prompt enhancement workflow:**

```
Raw prompt from block plan
  -> Gemini analyzes content context + brand + block type
  -> Returns enhanced prompt with visual details
  -> Enhanced prompt sent to image generation provider
```

**Example transformation:**

Raw: `"A team collaborating in a modern office"`

Enhanced: `"A diverse team of four professionals collaborating around a large touchscreen display in a bright, modern office space with floor-to-ceiling windows. Natural daylight illuminates the scene from the left. Clean, minimalist interior with plants and warm wood accents. Shot from a slight low angle to convey dynamism. Shallow depth of field focusing on the interaction between team members. Corporate photography style, warm color temperature."`

**Strengths:**
- Dramatically improves image quality by adding visual specificity
- Can incorporate brand context and block-specific requirements
- Fast (2-3 seconds for prompt enhancement)

**Weaknesses:**
- Adds latency to the generation pipeline (must run before image generation)
- Additional API cost for the text generation call
- Occasionally over-specifies prompts, reducing the model's creative freedom

---

## Provider Selection Decision Tree

```
Is a LoRA model available for this brand?
  Yes -> Is this a hero or primary image?
    Yes -> fal.ai FLUX Dev + LoRA
    No  -> fal.ai FLUX Schnell (faster, LoRA not needed for secondary images)
  No  -> Is fal.ai available?
    Yes -> Is this a hero or primary image?
      Yes -> fal.ai FLUX Dev (no LoRA, but higher quality)
      No  -> fal.ai FLUX Schnell
    No  -> Is GCP configured?
      Yes -> Vertex AI Imagen 3
      No  -> Hash-based fallback placeholder
```

---

## Cost Estimation

For a typical page with 1 hero + 4 cards + 1 CTA = 6 images:

| Provider | Cost per page | Time (parallel) |
|----------|--------------|-----------------|
| All Schnell | ~$0.018 | ~2s |
| Hero Dev + rest Schnell | ~$0.040 | ~5s |
| All Dev + LoRA | ~$0.150 | ~5s |
| All Imagen 3 | ~$0.120 | ~10s |

For a 20-page site with ~120 images total:
- Schnell only: ~$0.36
- Mixed (Dev hero + Schnell rest): ~$0.80
- With 50% cache hit rate: roughly half the above costs
