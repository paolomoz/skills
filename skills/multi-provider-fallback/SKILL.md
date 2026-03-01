---
name: multi-provider-fallback
description: Abstract AI model providers behind a unified interface with automatic fallback, parallel execution, and result synthesis. Use when implementing "provider fallback", "multi-provider AI", "model abstraction", or "AI client switching".
---

# Multi-Provider Fallback

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| patterns | "provider fallback", "multi-provider AI", "model abstraction", "AI client switching" | Medium | 5 projects |

Abstract multiple AI providers (Anthropic, Bedrock, OpenAI, Gemini, image generators) behind a unified interface so your application can switch providers via configuration, fall back on failure, run providers in parallel for consensus, and synthesize results. Eliminates hard provider dependencies and builds resilience against outages and rate limits.

## When to Use
- Your application calls AI APIs and needs resilience against any single provider going down
- Switching between Anthropic direct API and AWS Bedrock without changing application code
- Comparing or combining results from multiple models for quality or consensus
- Building an image pipeline that routes between providers (fal, Imagen, LoRA)
- Different tasks need different model configurations (reasoning vs classification vs content)

## Instructions

### Step 1: Provider Client Factory

Create a factory returning a unified client type. Consuming code never knows which provider is active.

```typescript
import Anthropic from '@anthropic-ai/sdk'
import AnthropicBedrock from '@anthropic-ai/bedrock-sdk'

type AIClient = Anthropic | AnthropicBedrock

export function createAnthropicClient(): AIClient {
  if (process.env.USE_BEDROCK === '1') {
    return new AnthropicBedrock({ awsRegion: process.env.AWS_REGION || 'us-east-1' })
  }
  return new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
}

// Bedrock uses its own model ID format
function toBedrockModel(model: string): string {
  if (model.startsWith('anthropic.') || model.startsWith('us.')) return model
  return `us.anthropic.${model}-v1:0`
}
```

The factory must be the **only place** checking provider flags. If provider logic leaks into business code, you lose the abstraction.

### Step 2: Model Preset Registry

Map task roles to provider + model + parameter combinations instead of hardcoding model names:

```typescript
const MODEL_PRESETS: Record<string, {
  provider: string; model: string; maxTokens: number; temperature: number
}> = {
  reasoning:      { provider: 'anthropic', model: 'claude-sonnet-4-20250514', maxTokens: 8192, temperature: 0.3 },
  content:        { provider: 'anthropic', model: 'claude-sonnet-4-20250514', maxTokens: 4096, temperature: 0.7 },
  classification: { provider: 'anthropic', model: 'claude-haiku-4-20250414',  maxTokens: 1024, temperature: 0.0 },
  embedding:      { provider: 'openai',    model: 'text-embedding-3-small',   maxTokens: 0,    temperature: 0   },
}
```

Application code calls `MODEL_PRESETS['reasoning']` instead of hardcoding IDs. When upgrading models or switching providers, change one entry.

### Step 3: Fallback Chains

Try providers in order, falling back on failure:

```typescript
interface ProviderCall {
  name: string
  execute: (prompt: string) => Promise<string>
}

async function callWithFallback(prompt: string, providers: ProviderCall[]) {
  const errors: string[] = []
  for (const p of providers) {
    try {
      return { result: await p.execute(prompt), provider: p.name }
    } catch (e) {
      errors.push(`${p.name}: ${(e as Error).message}`)
    }
  }
  throw new Error(`All providers failed: ${errors.join('; ')}`)
}
```

Ordering: highest quality first (not cheapest), most reliable second. Max 3 providers -- after 3 failures the issue is likely your prompt, not providers.

### Step 4: Parallel Execution and Result Synthesis

For consensus or best-of-N, execute in parallel with `Promise.allSettled` (not `Promise.all` -- one failure would cancel successful in-flight responses):

```typescript
async function callParallel(prompt: string, providers: ProviderCall[]) {
  const results = await Promise.allSettled(
    providers.map(async (p) => ({ result: await p.execute(prompt), provider: p.name }))
  )
  const successes = results
    .filter((r): r is PromiseFulfilledResult<{ result: string; provider: string }> =>
      r.status === 'fulfilled')
    .map(r => r.value)
  if (!successes.length) throw new Error('All parallel providers failed')
  return successes
}
```

Synthesize multiple results: if only one succeeds, return it directly. If multiple succeed, use Claude to merge them:

```typescript
async function synthesizeResults(results: Array<{ result: string; provider: string }>, prompt: string) {
  if (results.length === 1) return results[0].result
  const client = createAnthropicClient()
  const response = await client.messages.create({
    model: MODEL_PRESETS.reasoning.model,
    max_tokens: MODEL_PRESETS.reasoning.maxTokens,
    messages: [{ role: 'user', content:
      `Synthesize these ${results.length} AI responses for "${prompt}":\n\n` +
      results.map(r => `--- ${r.provider} ---\n${r.result}`).join('\n\n') +
      `\n\nTake strongest elements. Prefer responses with specific evidence on factual disagreements.`
    }]
  })
  return response.content[0].type === 'text' ? response.content[0].text : ''
}
```

### Step 5: Image Provider Routing and JSON Extraction

Route image generation by task type: `product-photo` to Imagen, `illustration`/`infographic` to fal, `brand-asset` to LoRA. Fall back to `IMAGE_PROVIDER` env var or `fal` as default.

For JSON extraction from provider responses, use progressive parsing:

```typescript
function extractJSON(response: string): unknown {
  try { return JSON.parse(response) } catch {}
  const stripped = response.replace(/```json\s*/g, '').replace(/```\s*/g, '').trim()
  try { return JSON.parse(stripped) } catch {}
  const start = Math.min(
    ...[stripped.indexOf('{'), stripped.indexOf('[')].filter(i => i !== -1)
  )
  if (start === Infinity) throw new Error('No JSON found')
  const close = stripped[start] === '[' ? ']' : '}'
  return JSON.parse(stripped.slice(start, stripped.lastIndexOf(close) + 1))
}
```

Apply this before parsing any provider response. Handles raw JSON, markdown-fenced JSON, and JSON embedded in text.

### Step 6: Environment Variables

```bash
USE_BEDROCK=0                    # 1 for Bedrock instead of direct Anthropic
ANTHROPIC_API_KEY=sk-ant-...     # Direct Anthropic
AWS_REGION=us-east-1             # Bedrock
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
OPENAI_API_KEY=sk-...            # Fallback / embeddings
GOOGLE_API_KEY=AIza...           # Gemini / Imagen
FAL_KEY=...                      # Image generation
IMAGE_PROVIDER=fal               # fal | imagen | lora
```

Never hardcode API keys. Never commit `.env` files. Use a secrets manager in production.

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Bedrock "access denied" | Missing IAM permissions | Add `bedrock:InvokeModel` to IAM policy for the model ARN |
| Model ID not found on Bedrock | Standard ID not transformed | Apply `toBedrockModel()` to convert to Bedrock format |
| Fallback chain too slow | Each timeout adds latency | Set aggressive per-provider timeouts (10-15s) |
| Parallel results inconsistent | Models interpret prompt differently | Add explicit output format instructions; use JSON schema |
| JSON extraction fails | Provider wrapped JSON in explanation | Use `extractJSON` with progressive parsing |
| Rate limits from all providers | Traffic spike exceeds all quotas | Add request queuing with backpressure and per-provider circuit breakers |

### Cross-References
- **multi-model-orchestrator** -- Higher-level orchestration using this as execution layer
- **ai-image-generator** -- Image pipeline using provider routing for different image types
- **incremental-processor** -- Uses the AI client abstraction for API calls with pacing and retry
