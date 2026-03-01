---
name: cloudflare-fullstack
description: Build full-stack applications on Cloudflare Workers with KV, D1, R2, Vectorize, and Workers AI bindings. Use when building "Cloudflare Workers apps", "serverless full-stack", "Workers + D1", or "Cloudflare edge applications".
---

# Cloudflare Full-Stack

## Quick Reference

| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| patterns | "Cloudflare Workers apps", "serverless full-stack", "Workers + D1", "edge applications" | Medium | 5 projects |

Builds full-stack applications on Cloudflare's edge platform using Workers for compute, KV for caching, D1 for relational data, R2 for file storage, Vectorize for vector search, and Workers AI for inference. Covers project structure, wrangler.toml configuration, TypeScript Env typing, request routing, CORS, storage selection, multi-worker architecture, and deployment.

## When to Use

- Building a new API or full-stack app on Cloudflare Workers
- Adding storage bindings (KV, D1, R2) to an existing Worker
- Setting up Vectorize for RAG/semantic search
- Deploying a multi-worker architecture with internal communication
- Migrating from Node.js/Express to Cloudflare Workers

## Instructions

### Step 1: Project Structure

Each worker gets its own directory with its own `wrangler.toml`.

**Single worker:**
```
project/
├── src/
│   ├── index.ts          # Worker entry point
│   ├── routes/            # Route handlers
│   ├── services/          # Storage/AI abstractions
│   └── types.ts           # Env type definition
├── wrangler.toml
└── package.json
```

**Multi-worker (recommended for complex apps):**
```
project/
├── workers/
│   ├── api-worker/
│   │   ├── src/index.ts
│   │   └── wrangler.toml
│   └── gen-worker/
│       ├── src/index.ts
│       └── wrangler.toml
├── packages/
│   └── shared/            # Shared types, utilities
├── scripts/
└── package.json           # Root workspace
```

**Why separate workers:** Each has independent resource limits (CPU, memory), independent scaling, and independent deployment. A gen-worker running 30s should not share limits with an API worker responding in 50ms.

### Step 2: wrangler.toml Configuration

The `wrangler.toml` is the single source of truth for bindings and deployment config. Every binding declared here becomes available on the `env` object.

```toml
name = "my-api-worker"
main = "src/index.ts"
compatibility_date = "2024-12-01"
compatibility_flags = ["nodejs_compat"]

[vars]
ENVIRONMENT = "production"
CORS_ORIGIN = "https://myapp.example.com"

[ai]
binding = "AI"

[[vectorize]]
binding = "VECTORIZE_INDEX"
index_name = "content-embeddings"

[[r2_buckets]]
binding = "ASSETS_BUCKET"
bucket_name = "my-app-assets"

[[kv_namespaces]]
binding = "CONTENT_KV"
id = "abcdef1234567890abcdef1234567890"

[[d1_databases]]
binding = "DB"
database_name = "my-app-db"
database_id = "12345678-1234-1234-1234-123456789012"

[[services]]
binding = "GEN_WORKER"
service = "my-gen-worker"
```

**Critical settings:**
- `compatibility_flags = ["nodejs_compat"]`: Enables Node.js built-ins (crypto, Buffer, streams). Required for most npm packages.
- KV `id` comes from `npx wrangler kv namespace create CONTENT_KV`
- D1 `database_id` comes from `npx wrangler d1 create my-app-db`
- `[[services]]` enables zero-latency worker-to-worker calls (no HTTP overhead)

### Step 3: Env Type Definition

The most important type in the project. Every handler receives `env: Env`.

```typescript
interface Env {
  AI: Ai;
  VECTORIZE_INDEX: VectorizeIndex;
  ASSETS_BUCKET: R2Bucket;
  CONTENT_KV: KVNamespace;
  DB: D1Database;
  GEN_WORKER: Fetcher;

  ENVIRONMENT: string;
  CORS_ORIGIN: string;
  ANTHROPIC_API_KEY: string;   // Set via wrangler secret
}
```

Types come from `@cloudflare/workers-types`. Install with `npm install -D @cloudflare/workers-types` and add to tsconfig:

```json
{ "compilerOptions": { "types": ["@cloudflare/workers-types"] } }
```

### Step 4: Request Routing

Workers use a single `fetch` handler. Route by pathname and method.

```typescript
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') return handleCORS(request, env);

    try {
      switch (url.pathname) {
        case '/api/generate':
          if (request.method !== 'POST') return methodNotAllowed();
          return handleGenerate(request, env, ctx);
        case '/api/content':
          if (request.method === 'GET') return handleGetContent(request, env);
          if (request.method === 'POST') return handleCreateContent(request, env);
          return methodNotAllowed();
        case '/api/search':
          return handleSearch(request, env);
        case '/api/health':
          return Response.json({ status: 'ok' });
        default:
          return new Response('Not Found', { status: 404 });
      }
    } catch (error) {
      console.error('Unhandled error:', error);
      return Response.json({ error: 'Internal Server Error' }, {
        status: 500, headers: corsHeaders(env),
      });
    }
  },
} satisfies ExportedHandler<Env>;
```

For 10+ routes, use **Hono** (`npm install hono`) or **itty-router** instead of manual switching.

### Step 5: CORS Middleware

```typescript
function corsHeaders(env: Env): Record<string, string> {
  return {
    'Access-Control-Allow-Origin': env.CORS_ORIGIN || '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, Cache-Control, Last-Event-ID',
    'Access-Control-Max-Age': '86400',
  };
}

function handleCORS(request: Request, env: Env): Response {
  return new Response(null, { status: 204, headers: corsHeaders(env) });
}

function jsonResponse(data: unknown, env: Env, status = 200): Response {
  return Response.json(data, { status, headers: corsHeaders(env) });
}
```

Include `Last-Event-ID` in allowed headers if any endpoint uses SSE streaming.

### Step 6: Storage Selection Guide

| Storage | Best For | Latency | Consistency | Size Limit |
|---------|----------|---------|-------------|------------|
| **KV** | Cached reads, config, sessions | <10ms read | Eventually consistent | 25MB/value |
| **D1** | Relational data, queries, joins | 5-50ms | Strong (per-region) | 10GB/db |
| **R2** | Files, images, large objects | 50-200ms | Strong | 5TB/object |
| **Vectorize** | Semantic search, RAG | 20-100ms | Eventually consistent | Varies |

**Decision rules:**
1. Read 100x more than write? **KV.** Globally cached, near-instant reads, but writes take up to 60s to propagate.
2. Need SQL queries, joins, transactions? **D1.** Only relational option.
3. File larger than 1MB? **R2.** Large blobs in KV/D1 hit size limits.
4. Need similarity search? **Vectorize.** Purpose-built for vector queries.

**Common patterns:**

```typescript
// KV: Cache with TTL
await env.CONTENT_KV.put(`page:${slug}`, html, { expirationTtl: 3600 });
const cached = await env.CONTENT_KV.get(`page:${slug}`);

// D1: Parameterized queries (never string interpolation)
const row = await env.DB.prepare(
  'SELECT * FROM pages WHERE slug = ? AND status = ?'
).bind(slug, 'published').first();

// R2: Store and retrieve files
await env.ASSETS_BUCKET.put(`images/${id}.png`, imageBuffer, {
  httpMetadata: { contentType: 'image/png' },
});
const object = await env.ASSETS_BUCKET.get(`images/${id}.png`);

// Vectorize: Query for similar content
const matches = await env.VECTORIZE_INDEX.query(embedding, { topK: 10, returnMetadata: 'all' });
```

### Step 7: Workers AI Integration

Workers AI runs on the same edge with no API keys and no network hops.

```typescript
async function generateEmbedding(env: Env, text: string): Promise<number[]> {
  const result = await env.AI.run('@cf/baai/bge-base-en-v1.5', { text: [text] });
  return result.data[0]; // 768-dimensional vector
}

async function generateText(env: Env, prompt: string, system?: string): Promise<string> {
  const messages = [];
  if (system) messages.push({ role: 'system', content: system });
  messages.push({ role: 'user', content: prompt });
  const result = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', { messages, max_tokens: 2048 });
  return result.response;
}
```

Use Workers AI for embeddings and lightweight inference. Use external APIs (Anthropic, OpenAI) for high-quality generation.

### Step 8: Multi-Worker Communication

Workers communicate via service bindings — zero-latency, no DNS/TCP/TLS overhead.

```typescript
// In api-worker: forward to gen-worker via service binding
async function handleGenerate(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
  const genResponse = await env.GEN_WORKER.fetch(
    new Request('https://gen-worker/generate', {
      method: 'POST', headers: request.headers, body: request.body,
    })
  );
  // Stream SSE response back to client
  return new Response(genResponse.body, { headers: genResponse.headers });
}
```

The URL in `new Request()` is ignored for routing — the binding determines the target. Each worker has independent CPU time limits.

### Step 9: D1 Schema Management

```bash
npx wrangler d1 migrations create my-app-db "create_pages_table"
```

```sql
-- migrations/0001_create_pages_table.sql
CREATE TABLE IF NOT EXISTS pages (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  html TEXT NOT NULL,
  status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'published', 'archived')),
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX idx_pages_slug ON pages(slug);
```

```bash
npx wrangler d1 migrations apply my-app-db --remote
```

**D1/SQLite gotchas:** No `BOOLEAN` (use INTEGER 0/1), no `AUTO_INCREMENT` (use randomblob UUIDs), `datetime('now')` returns UTC, JSON stored as TEXT.

### Step 10: Deployment and Secrets

```bash
npx wrangler deploy                           # Deploy worker
npx wrangler secret put ANTHROPIC_API_KEY     # Set encrypted secret
npx wrangler secret list                      # Verify secrets exist
npx wrangler deploy --env staging             # Deploy to staging
```

**Secrets vs vars:** `[vars]` in wrangler.toml for non-sensitive config (visible in dashboard). `wrangler secret put` for credentials (encrypted, never visible after setting).

**Staging overrides:**
```toml
[env.staging]
name = "my-api-worker-staging"
[env.staging.vars]
ENVIRONMENT = "staging"
CORS_ORIGIN = "https://staging.myapp.example.com"
```

### Step 11: Local Development

```bash
npx wrangler dev              # Local with emulated bindings
npx wrangler dev --remote     # Local with real KV/D1/R2
npx wrangler dev --port 8787  # Custom port
```

KV/D1/R2 are emulated locally in `.wrangler/state/`. Vectorize and Workers AI are NOT available locally — use `--remote` or mock them.

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `Binding not found: CONTENT_KV` | Wrong ID in wrangler.toml | Run `npx wrangler kv namespace list` and verify |
| `D1_ERROR: no such table` | Migrations not applied | `npx wrangler d1 migrations apply DB_NAME --remote` |
| `script startup exceeded CPU time limit` | Heavy top-level imports | Lazy-import inside handlers, not at top level |
| `env.AI.run is not a function` | Missing `[ai]` binding | Add `[ai]\nbinding = "AI"` to wrangler.toml |
| `process is not defined` | Node.js API without compat | Add `compatibility_flags = ["nodejs_compat"]` |
| CORS errors in browser | Missing headers or wrong origin | Verify `Access-Control-Allow-Origin` matches |
| Deploy succeeds but 500s | Secret not set | `npx wrangler secret list` to verify |
| R2 returns null | Wrong key path | Include full path e.g. `images/foo.png` |
| Service binding Error 1042 | Target worker runtime error | Check with `npx wrangler tail --service gen-worker` |
| Vectorize empty results | Dimension mismatch | Verify embedding model matches index config |

## Cross-References

- **sse-streaming** — SSE endpoints implemented as Worker routes; see for ReadableStream patterns
- **multi-model-orchestrator** — AI pipelines run inside Workers using Vectorize and KV bindings
- **session-context** — Session management patterns using KV with TTL
