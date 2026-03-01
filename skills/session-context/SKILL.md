---
name: session-context
description: Track user session context across multi-turn interactions using browser sessionStorage and server-side KV caching with TTL. Use when implementing "session tracking", "conversation context", "multi-turn sessions", or "user journey tracking".
---

# Session Context

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| patterns | "session tracking", "conversation context", "multi-turn sessions", "user journey tracking" | Medium | 4 projects |

Manage user session context across multi-turn interactions by combining client-side sessionStorage for immediate state and server-side KV storage for persistence and cross-page sharing. Enables journey-stage tracking, query history, and context propagation without traditional databases.

## When to Use
- Building a conversational interface that needs to remember previous queries within a session
- Implementing journey stage tracking (exploring, comparing, deciding, supporting)
- Passing context between pages without a backend session store
- Creating recommendation engines that improve with each interaction

## Instructions

### Step 1: Client-Side SessionContextManager

Create a class wrapping `sessionStorage` with structured context management:

```javascript
class SessionContextManager {
  static STORAGE_KEY = 'session-context'
  static MAX_QUERIES = 10

  static getContext() {
    const stored = sessionStorage.getItem(this.STORAGE_KEY)
    return stored ? JSON.parse(stored) : {
      queries: [], sessionStart: Date.now(),
      lastUpdated: Date.now(), sessionId: crypto.randomUUID()
    }
  }

  static addQuery(entry) {
    const context = this.getContext()
    context.queries.push({ ...entry, timestamp: Date.now() })
    if (context.queries.length > this.MAX_QUERIES) {
      context.queries = context.queries.slice(-this.MAX_QUERIES)
    }
    context.lastUpdated = Date.now()
    sessionStorage.setItem(this.STORAGE_KEY, JSON.stringify(context))
    return context
  }
}
```

Key rules:
- Cap query history with `MAX_QUERIES` (default 10). SessionStorage has a 5MB limit and unbounded growth silently fails.
- Use `crypto.randomUUID()` for session IDs, never sequential counters.
- Always update `lastUpdated` on every write for staleness checks.

### Step 2: Query History Entry Structure

Each entry in the `queries` array:

```javascript
{
  query: "What's the best laptop for video editing?",
  intent: "product_comparison",
  timestamp: 1709123456789,
  entities: ["laptop", "video editing"],
  journeyStage: "comparing",
  recommendedProducts: ["macbook-pro-m3", "dell-xps"],
  confidence: 0.87,
  nextBestAction: "show_comparison_table"
}
```

At minimum include `query`, `timestamp`, and `journeyStage`. The remaining fields are populated by your classification pipeline and consumed by recommendation logic.

### Step 3: Journey Stage Tracking

Stages form a linear progression:

```
exploring → comparing → deciding → supporting
```

| Stage | User Behavior | System Behavior |
|-------|--------------|-----------------|
| **exploring** | Broad questions, browsing | Show categories, discovery content |
| **comparing** | Feature questions, "vs" queries | Comparison tables, differentiators |
| **deciding** | Price, availability, "should I" | CTAs, pricing, reviews, social proof |
| **supporting** | How-to, troubleshooting | Documentation, tutorials, support |

Simple heuristic classification:

```javascript
function classifyJourneyStage(query, previousStage) {
  if (/\bhow to|setup|install|fix|error|help\b/i.test(query)) return 'supporting'
  if (/\bprice|cost|buy|order|worth|should i\b/i.test(query)) return 'deciding'
  if (/\bvs\b|compare|difference|better|which/i.test(query)) return 'comparing'
  return previousStage || 'exploring'
}
```

Stages should only advance forward or stay. Never regress within a single session unless the user explicitly starts a new topic.

### Step 4: Server-Side KV Storage

Use KV (Cloudflare KV, Redis, DynamoDB) for context that must survive across page navigations.

**Key format:** `ctx_{shortId}` where short IDs are generated as:

```javascript
const contextId = 'ctx_' + crypto.randomUUID().replace(/-/g, '').slice(0, 12)
```

**Store with TTL (1 hour):**

```javascript
await kv.put(contextId, JSON.stringify(context), { expirationTtl: 3600 })
```

**Retrieve:**

```javascript
const stored = await kv.get(contextId, { type: 'json' })
if (!stored) return null  // Expired or missing
```

TTL rules:
- Default: 3600s (1 hour), covering a typical browsing session.
- Never exceed 24 hours -- session context is ephemeral. Use a database for persistent user data.
- Always handle `null` returns: entries may expire between URL generation and click.

### Step 5: Context Propagation Between Pages

**Method A -- Inline (context under 2KB):**

```javascript
// Build URL with encoded context
const encoded = btoa(JSON.stringify(context))
const url = `${baseUrl}?ctx=${encodeURIComponent(encoded)}`

// Read on receiving page
const ctx = JSON.parse(atob(decodeURIComponent(params.get('ctx'))))
```

**Method B -- Context ID (context over 2KB):**

```javascript
// Store in KV, pass ID in URL
const contextId = await storeContext(kv, context)
const url = `${baseUrl}?ctx=${contextId}`

// Read on receiving page: detect by prefix
const ctx = params.get('ctx')
if (ctx.startsWith('ctx_')) {
  return await kv.get(ctx, { type: 'json' })
}
```

The `ctx_` prefix acts as a discriminator so the receiving page auto-detects which method was used.

### Step 6: Page Load Initialization

Establish context from all sources with priority ordering:

```javascript
async function initializeContext(kv) {
  // 1. URL-propagated context (highest priority)
  const urlContext = await readContextFromUrl(window.location.href, kv)
  if (urlContext) {
    SessionContextManager.saveContext(urlContext)
    window.history.replaceState({}, '', window.location.pathname)
    return urlContext
  }
  // 2. Existing sessionStorage context
  const existing = SessionContextManager.getContext()
  if (existing.queries.length > 0) return existing
  // 3. Fresh context
  return SessionContextManager.getContext()
}
```

On each interaction, update both tiers -- client synchronously, server asynchronously:

```javascript
async function recordInteraction(kv, entry) {
  const context = SessionContextManager.addQuery(entry)  // sync
  storeContext(kv, context).catch(console.warn)           // async, non-blocking
  return context
}
```

Always treat KV sync as non-blocking. The client store is the source of truth; KV is the durability layer.

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `setItem` silently fails | Storage quota exceeded (5MB) | Reduce `MAX_QUERIES` or strip large fields before storing |
| Context lost on navigation | Different origin or wrong storage type | Verify same origin; use KV + URL for cross-origin |
| KV returns `null` for valid ID | TTL expired | Handle null gracefully; re-initialize from sessionStorage |
| Context URL truncated | Inline method with large context | Switch to Context ID method (Method B) for contexts over 2KB |
| Journey stage regresses | Classifier ignores previous stage | Always pass `previousStage` and only advance forward |

### Cross-References
- **cloudflare-fullstack** -- KV binding setup and Cloudflare Workers integration
- **multi-model-orchestrator** -- Intent classification and entity extraction for query entries
- **generative-page-pipeline** -- Consuming session context to personalize generated pages
