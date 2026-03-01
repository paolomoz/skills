---
name: multi-model-orchestrator
description: Orchestrate multi-stage AI pipelines that route tasks to optimal models by role — fast models for classification, reasoning models for planning, content models for generation. Use when building "multi-model pipelines", "AI orchestration", "model routing", or "LLM orchestration".
---

# Multi-Model Orchestrator

## Quick Reference

| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| patterns | "multi-model pipeline", "AI orchestration", "model routing", "LLM orchestration" | High | 3 projects |

Architects multi-stage AI pipelines where each stage routes to the optimal model for its role: fast models for classification, reasoning models for planning, high-throughput models for parallel content generation, and specialized models for images. Each stage emits SSE progress events and includes timeout protection and fallback routing.

## When to Use

- Building AI pipelines with 3+ stages that have different latency/quality tradeoffs
- Routing classification to fast/cheap models and reasoning to capable/expensive models
- Running parallel content generation across multiple blocks
- Combining text generation, image generation, and retrieval (RAG) in a single pipeline
- Multi-agent analysis where the same prompt runs across Claude, Gemini, and GPT

## Instructions

### Step 1: Define Pipeline Stages

Map your workflow into discrete stages with role assignments and latency budgets.

**Standard 5-stage pipeline:**

```
Stage 1: Intent Classification (fast, ~200ms)
  → Stage 2: Deep Reasoning (reasoning, ~3-5s)
    → Stage 3: Content Generation (content, parallel, ~1-2s each)
    → Stage 4: Image Generation (image, parallel, ~2-10s each)
      → Stage 5: Persistence (storage)
```

| Role | Purpose | Latency Target | Model Characteristics |
|------|---------|---------------|----------------------|
| `classification` | Triage, routing, intent detection | <500ms | Fast inference, small model, structured output |
| `reasoning` | Planning, analysis, architecture | 3-8s | High capability, chain-of-thought, large context |
| `content` | Text/HTML generation | 1-3s per block | High throughput, good instruction following |
| `image` | Image generation | 2-10s per image | Specialized vision model |
| `embedding` | Vector embeddings for RAG | <500ms | Embedding-specific model |

### Step 2: Configure Model Presets

Define named presets that map roles to providers and models.

```typescript
interface ModelConfig {
  provider: 'anthropic' | 'cerebras' | 'openai' | 'google' | 'fal';
  model: string;
  maxTokens: number;
  temperature?: number;
  timeout?: number;
}

const PRESETS: Record<string, Record<string, ModelConfig>> = {
  production: {
    reasoning: {
      provider: 'anthropic', model: 'claude-opus-4-6',
      maxTokens: 4096, temperature: 0.3, timeout: 30_000,
    },
    content: {
      provider: 'cerebras', model: 'gpt-oss-120b',
      maxTokens: 4096, temperature: 0.7, timeout: 15_000,
    },
    classification: {
      provider: 'cerebras', model: 'llama-3.1-8b',
      maxTokens: 500, temperature: 0.0, timeout: 5_000,
    },
    image: {
      provider: 'fal', model: 'fal-ai/flux-pro/v1.1',
      maxTokens: 0, timeout: 60_000,
    },
  },
  fast: {
    reasoning: {
      provider: 'cerebras', model: 'llama-3.3-70b',
      maxTokens: 4096, temperature: 0.3, timeout: 10_000,
    },
    content: {
      provider: 'cerebras', model: 'llama-3.1-8b',
      maxTokens: 2048, temperature: 0.7, timeout: 5_000,
    },
    classification: {
      provider: 'cerebras', model: 'llama-3.1-8b',
      maxTokens: 500, temperature: 0.0, timeout: 3_000,
    },
  },
};
```

Use `production` for user-facing generation, `fast` for development and testing.

### Step 3: Implement ModelFactory

Abstract provider differences behind a unified interface with per-role timeout protection.

```typescript
class ModelFactory {
  private env: Env;
  private preset: Record<string, ModelConfig>;

  constructor(env: Env, presetName = 'production') {
    this.env = env;
    this.preset = PRESETS[presetName];
  }

  async generate(role: string, prompt: string, systemPrompt?: string): Promise<string> {
    const config = this.preset[role];
    if (!config) throw new Error(`No model configured for role: ${role}`);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.timeout ?? 30_000);

    try {
      switch (config.provider) {
        case 'anthropic': return await this.callAnthropic(config, prompt, systemPrompt, controller.signal);
        case 'cerebras': return await this.callCerebras(config, prompt, systemPrompt, controller.signal);
        case 'openai':   return await this.callOpenAI(config, prompt, systemPrompt, controller.signal);
        default: throw new Error(`Unknown provider: ${config.provider}`);
      }
    } finally {
      clearTimeout(timeoutId);
    }
  }

  private async callAnthropic(config: ModelConfig, prompt: string, system: string | undefined, signal: AbortSignal): Promise<string> {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: config.model, max_tokens: config.maxTokens,
        temperature: config.temperature ?? 0.7, system,
        messages: [{ role: 'user', content: prompt }],
      }),
      signal,
    });
    if (!response.ok) throw new Error(`Anthropic ${response.status}: ${await response.text()}`);
    const data = await response.json() as any;
    return data.content[0].text;
  }
  // Similar implementations for callCerebras, callOpenAI...
}
```

### Step 4: Parallel Execution

Independent stages (content blocks, images) run in parallel. This is where the biggest latency savings come from.

```typescript
async function generateContentBlocks(
  factory: ModelFactory, blocks: BlockPlan[], write: SSEWriter,
): Promise<string[]> {
  return Promise.all(
    blocks.map(async (block, index) => {
      await write('block-start', { blockIndex: index, title: block.title });
      const content = await factory.generate('content', block.prompt, block.systemPrompt);
      await write('block-content', { blockIndex: index, html: content });
      await write('block-complete', { blockIndex: index });
      return content;
    })
  );
}
```

**Rules:** Use `Promise.allSettled` when partial failure is acceptable. Limit concurrency for rate-limited APIs:

```typescript
async function withConcurrencyLimit<T>(tasks: (() => Promise<T>)[], limit: number): Promise<T[]> {
  const results: T[] = [];
  const executing: Promise<void>[] = [];
  for (const task of tasks) {
    const p = task().then(r => { results.push(r); });
    executing.push(p);
    if (executing.length >= limit) {
      await Promise.race(executing);
      executing.splice(executing.findIndex(e => e === p), 1);
    }
  }
  await Promise.all(executing);
  return results;
}
```

### Step 5: SSE Progress Streaming

Emit events at each stage boundary. The `write` function from sse-streaming is threaded through the entire pipeline.

```typescript
async function runPipeline(request: ParsedRequest, env: Env, write: SSEWriter): Promise<GenerationResult> {
  const factory = new ModelFactory(env, request.preset ?? 'production');

  // Stage 1: Classification (~200ms)
  await write('reasoning-start', { stage: 'classification' });
  const intent = JSON.parse(await factory.generate('classification', classificationPrompt));
  await write('reasoning-complete', { stage: 'classification', intent });

  // Stage 2: Deep Reasoning (~3-5s)
  await write('reasoning-start', { stage: 'planning' });
  const blockPlans = JSON.parse(await factory.generate('reasoning', planningPrompt(intent)));
  await write('reasoning-complete', { stage: 'planning', totalBlocks: blockPlans.length });

  // Stage 3: Content Generation (parallel, ~1-2s total)
  const contents = await generateContentBlocks(factory, blockPlans, write);

  // Stage 4: Image Generation (parallel, ~5-30s)
  const images = await generateImages(env, blockPlans, write);

  // Stage 5: Persistence
  await write('persist-start', { target: 'storage' });
  const url = await persistResult(env, contents, images);
  await write('persist-complete', { url });

  return { url, blockCount: contents.length, imageCount: images.length };
}
```

### Step 6: RAG Integration

Retrieve context using Cloudflare Vectorize and Voyage AI embeddings before the reasoning stage.

```typescript
async function retrieveContext(env: Env, query: string, topK = 5): Promise<string[]> {
  const embeddingResponse = await fetch('https://api.voyageai.com/v1/embeddings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${env.VOYAGE_API_KEY}` },
    body: JSON.stringify({ input: query, model: 'voyage-3' }),
  });
  const { data } = await embeddingResponse.json() as any;
  const matches = await env.VECTORIZE_INDEX.query(data[0].embedding, { topK, returnMetadata: 'all' });
  return matches.matches.map((m: any) => m.metadata?.content ?? '');
}
```

**Timeout protection:** Wrap in `Promise.race` with a 3s timeout. If Vectorize is slow, the pipeline continues without context rather than failing.

```typescript
const context = await Promise.race([
  retrieveContext(env, query),
  new Promise<string[]>(resolve => setTimeout(() => resolve([]), 3_000)),
]);
```

### Step 7: Multi-Agent Analysis

For comparative analysis, run the same prompt across multiple models and synthesize.

```typescript
async function multiAgentAnalysis(env: Env, prompt: string, synthesisPrompt: string): Promise<string> {
  const factory = new ModelFactory(env, 'production');

  const [claude, gemini, gpt] = await Promise.allSettled([
    factory.generate('reasoning', prompt),
    callGemini(env, prompt),
    callOpenAI(env, prompt),
  ]);

  const analyses = [
    { model: 'Claude', result: claude.status === 'fulfilled' ? claude.value : null },
    { model: 'Gemini', result: gemini.status === 'fulfilled' ? gemini.value : null },
    { model: 'GPT',    result: gpt.status === 'fulfilled' ? gpt.value : null },
  ].filter(a => a.result !== null);

  const combined = analyses.map(a => `## ${a.model}\n${a.result}`).join('\n\n');
  return factory.generate('reasoning', `${synthesisPrompt}\n\n${combined}`);
}
```

Use only for high-stakes analysis where diverse perspectives matter. For standard generation, a single model is faster and cheaper.

### Step 8: Error Handling and Fallbacks

Every stage needs a fallback. The pipeline degrades gracefully, not catastrophically.

```typescript
async function generateWithFallback(factory: ModelFactory, role: string, prompt: string, system?: string): Promise<string> {
  try {
    return await factory.generate(role, prompt, system);
  } catch (primaryError) {
    console.error(`Primary ${role} failed:`, primaryError);
    const fallback = new ModelFactory(factory.env, 'fast');
    try {
      return await fallback.generate(role, prompt, system);
    } catch (fallbackError) {
      throw new Error(`All models failed for ${role}: ${primaryError.message}`);
    }
  }
}
```

**Timeout protection per stage:**

| Stage | Timeout | On Timeout |
|-------|---------|-----------|
| Classification | 5s | Fall back to default intent |
| Reasoning | 30s | Fall back to fast preset |
| Content (per block) | 15s | Retry once, then placeholder |
| Image (per image) | 90s | Skip, use placeholder |
| Vectorize (RAG) | 3s | Continue without context |
| Persistence | 10s | Return content without URL |

### Step 9: Pipeline Configuration

Make pipelines configurable at the request level. Clients can skip stages and override presets.

```typescript
interface PipelineConfig {
  preset: string;
  stages: { classify: boolean; reason: boolean; generate: boolean; images: boolean; persist: boolean };
}

const config: PipelineConfig = {
  preset: url.searchParams.get('preset') ?? 'production',
  stages: {
    classify: url.searchParams.get('classify') !== 'false',
    reason:   url.searchParams.get('reason') !== 'false',
    generate: true,
    images:   url.searchParams.get('images') !== 'false',
    persist:  url.searchParams.get('persist') !== 'false',
  },
};
```

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Classification returns invalid JSON | Small model hallucinating | Add explicit JSON schema in system prompt; validate and retry once |
| Reasoning stage times out | Prompt too complex | Reduce context length; fall back to fast preset |
| Parallel blocks inconsistent style | Independent generation | Include style guide in every block's system prompt |
| Image generation fails silently | fal.ai queue timeout | Increase timeout to 90s; add retry with 10s delay |
| Rate limit errors (429) | Too many parallel requests | Add concurrency limiter (max 5); exponential backoff on 429 |
| Vectorize returns no results | Empty index or narrow query | Verify index has vectors; broaden query; fall back to keyword search |
| High costs | Reasoning model called too often | Cache classification in KV; skip reasoning for repeat intents |

## Cross-References

- **sse-streaming** — Transport layer for pipeline progress events
- **cloudflare-fullstack** — Pipeline runs as a Cloudflare Worker; see for wrangler.toml and bindings
- **multi-provider-fallback** — Detailed fallback chain patterns
- **generative-page-pipeline** — Primary consumer of this orchestration pattern
