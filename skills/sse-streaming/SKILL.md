---
name: sse-streaming
description: Implement Server-Sent Events streaming from Cloudflare Workers to browser clients with reconnection, state persistence, and progress tracking. Use when building "SSE streaming", "real-time updates", "server push", or "event streaming".
---

# SSE Streaming

## Quick Reference

| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| patterns | "SSE streaming", "real-time updates", "server push", "event streaming" | Medium | 4 projects |

Implements the Server-Sent Events pattern for streaming structured progress events from a Cloudflare Workers backend to a browser client. Covers server-side emission with ReadableStream, client-side EventSource consumption with skeleton placeholders, state management with sessionStorage persistence, and reconnection with exponential backoff.

## When to Use

- Streaming AI generation progress to a browser (block-by-block content arrival)
- Long-running server tasks where the client needs real-time status updates
- Multi-stage pipelines that emit progress at each stage boundary
- Any scenario where the server pushes data and the client only listens (no bidirectional needed)

## Instructions

### Step 1: Server-Side SSE Endpoint (Cloudflare Workers)

Create a streaming endpoint using the TransformStream pattern.

```typescript
export async function handleGenerate(request: Request, env: Env): Promise<Response> {
  const { readable, writable } = new TransformStream();
  const writer = writable.getWriter();
  const encoder = new TextEncoder();

  const write = async (event: string, data: object, id?: string) => {
    let message = '';
    if (id) message += `id: ${id}\n`;
    message += `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
    await writer.write(encoder.encode(message));
  };

  // Start async pipeline — do NOT await (that would block the response)
  (async () => {
    try {
      await write('generation-start', { sessionId, totalBlocks: 6 });
      await runPipeline(request, env, write);
      await write('generation-complete', { success: true });
    } catch (error) {
      await write('error', { message: error.message });
    } finally {
      await writer.close();
    }
  })();

  return new Response(readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
      'Access-Control-Allow-Origin': '*',
    },
  });
}
```

**Critical details:**
- The async pipeline runs in an un-awaited IIFE. The Response returns immediately with the readable side.
- `X-Accel-Buffering: no` is essential behind nginx/Cloudflare — without it, the entire response is buffered and delivered at once.
- Every SSE message ends with `\n\n`. A single `\n` separates fields within a message.
- The `id` field enables reconnection — the client sends `Last-Event-ID` on reconnect.

### Step 2: Event Types Catalog

Define a consistent event vocabulary across the pipeline lifecycle.

| Event | Payload | When Emitted |
|-------|---------|-------------|
| `generation-start` | `{ sessionId, totalBlocks, model }` | Pipeline begins |
| `reasoning-start` | `{ model }` | Reasoning stage begins |
| `reasoning-step` | `{ step, content }` | Each reasoning substep |
| `reasoning-complete` | `{ duration }` | Reasoning stage done |
| `block-start` | `{ blockIndex, blockId, title }` | Content block generation begins |
| `block-content` | `{ blockIndex, html }` | Partial or complete block HTML |
| `block-complete` | `{ blockIndex, blockId }` | Content block fully generated |
| `image-placeholder` | `{ blockIndex, imageId, alt }` | Placeholder inserted, image generating |
| `image-ready` | `{ blockIndex, imageId, url }` | Image URL available |
| `persist-start` | `{ target }` | Saving to storage begins |
| `persist-complete` | `{ url, target }` | Saved successfully |
| `generation-complete` | `{ success, totalDuration }` | Pipeline finished |
| `error` | `{ message, stage, recoverable }` | Error at any stage |

**Naming convention:** `{noun}-{verb}` for stage boundaries. Present tense for in-progress events, past participle for terminal events.

### Step 3: Client-Side EventSource

Use the EventSource API with typed handlers for each event.

```typescript
function connectSSE(url: string, handlers: EventHandlers): EventSource {
  const source = new EventSource(url);

  source.addEventListener('generation-start', (e: MessageEvent) => {
    handlers.onGenerationStart(JSON.parse(e.data));
  });

  source.addEventListener('block-content', (e: MessageEvent) => {
    handlers.onBlockContent(JSON.parse(e.data));
  });

  source.addEventListener('generation-complete', (e: MessageEvent) => {
    source.close(); // Always close on completion
    handlers.onComplete(JSON.parse(e.data));
  });

  source.addEventListener('error', (e: MessageEvent) => {
    if (e.data) handlers.onError(JSON.parse(e.data));
  });

  source.onerror = () => {
    if (source.readyState === EventSource.CLOSED) {
      handlers.onConnectionLost?.();
    }
  };

  return source;
}
```

**Important:** Always call `source.close()` on `generation-complete`. Otherwise the browser auto-reconnects, restarting the pipeline.

### Step 4: Skeleton Template System

Show placeholders immediately while waiting for streamed blocks.

```typescript
function renderSkeletons(totalBlocks: number): void {
  const container = document.getElementById('content');
  for (let i = 0; i < totalBlocks; i++) {
    const skeleton = document.createElement('div');
    skeleton.id = `block-${i}`;
    skeleton.className = 'skeleton-block';
    skeleton.innerHTML = `
      <div class="skeleton-title pulse"></div>
      <div class="skeleton-line pulse" style="width: 90%"></div>
      <div class="skeleton-line pulse" style="width: 75%"></div>
    `;
    container.appendChild(skeleton);
  }
}

function replaceSkeletonWithContent(blockIndex: number, html: string): void {
  const block = document.getElementById(`block-${blockIndex}`);
  if (block) {
    block.className = 'content-block fade-in';
    block.innerHTML = html;
  }
}
```

```css
.skeleton-block { padding: 1.5rem; margin-bottom: 1rem; border-radius: 8px; background: #f0f0f0; }
.skeleton-title { height: 24px; width: 40%; background: #e0e0e0; border-radius: 4px; margin-bottom: 12px; }
.skeleton-line { height: 14px; background: #e0e0e0; border-radius: 4px; margin-bottom: 8px; }
.pulse { animation: pulse 1.5s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.fade-in { animation: fadeIn 0.3s ease-in; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
```

### Step 5: State Management with GenerationState

Track progress with a state class using Map-based block tracking and sessionStorage persistence with 5-minute TTL.

```typescript
type Status = 'idle' | 'initializing' | 'generating' | 'complete' | 'error';

class GenerationState {
  status: Status = 'idle';
  sessionId: string | null = null;
  blocks: Map<number, BlockState> = new Map();
  private storageKey = 'sse-generation-state';
  private ttlMs = 5 * 60 * 1000;

  start(sessionId: string, totalBlocks: number): void {
    this.status = 'initializing';
    this.sessionId = sessionId;
    for (let i = 0; i < totalBlocks; i++) {
      this.blocks.set(i, { status: 'pending', content: null });
    }
    this.persist();
  }

  updateBlock(index: number, status: string, content?: string): void {
    this.blocks.set(index, { status, content: content ?? this.blocks.get(index)?.content ?? null });
    this.status = 'generating';
    this.persist();
  }

  persist(): void {
    sessionStorage.setItem(this.storageKey, JSON.stringify({
      status: this.status, sessionId: this.sessionId,
      blocks: Object.fromEntries(this.blocks), savedAt: Date.now(),
    }));
  }

  restore(): boolean {
    const raw = sessionStorage.getItem(this.storageKey);
    if (!raw) return false;
    const parsed = JSON.parse(raw);
    if (Date.now() - parsed.savedAt > this.ttlMs) {
      sessionStorage.removeItem(this.storageKey);
      return false;
    }
    Object.assign(this, { ...parsed, blocks: new Map(Object.entries(parsed.blocks)) });
    return true;
  }
}
```

### Step 6: Reconnection with Exponential Backoff

Attempt reconnection 3 times with exponential backoff, then fail with a user-visible error.

```typescript
function connectWithRetry(url: string, handlers: EventHandlers, maxAttempts = 3): void {
  let attempt = 0;

  function connect(): void {
    connectSSE(url, {
      ...handlers,
      onConnectionLost: () => {
        attempt++;
        if (attempt >= maxAttempts) {
          handlers.onError({ message: 'Connection lost after 3 attempts', recoverable: false });
          return;
        }
        const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
        setTimeout(connect, delay);
      },
    });
  }
  connect();
}
```

### Step 7: Page Visibility and Keep-Alive

**Page visibility:** Do NOT close EventSource when the tab is hidden. The browser queues incoming events and delivers them when the tab regains focus. Only reconnect if the connection was lost while hidden.

**Server-side keep-alive:** Send comments every 30s to prevent proxy timeouts (Cloudflare/nginx kill idle connections after 60-100s).

```typescript
function createKeepAlive(writer: WritableStreamDefaultWriter, encoder: TextEncoder) {
  const interval = setInterval(async () => {
    try { await writer.write(encoder.encode(': keep-alive\n\n')); }
    catch { clearInterval(interval); }
  }, 30_000);
  return () => clearInterval(interval);
}
```

### Step 8: CORS Configuration

SSE endpoints need CORS headers. Include `Last-Event-ID` in allowed headers for reconnection to work cross-origin.

```typescript
function corsHeaders(origin?: string): Record<string, string> {
  return {
    'Access-Control-Allow-Origin': origin || '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Cache-Control, Last-Event-ID',
    'Access-Control-Max-Age': '86400',
  };
}
```

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Events arrive all at once | nginx/Cloudflare buffering | Add `X-Accel-Buffering: no` header; ensure response is a ReadableStream |
| Client receives no events | CORS blocking | Add `Access-Control-Allow-Origin`; allow `Last-Event-ID` header |
| Connection drops after ~60s | Proxy idle timeout | Implement keep-alive comments every 30s |
| Handler not called | Wrong event name | `source.onmessage` only fires for unnamed events; use `addEventListener` for named events |
| Memory leak on long sessions | EventSource not closed | Always call `source.close()` on `generation-complete` and on unmount |
| Duplicate events on reconnect | Server resends from beginning | Use `id:` fields and deduplicate by block index on the client |
| `ERR_INCOMPLETE_CHUNKED_ENCODING` | Writer closed prematurely | Ensure `writer.close()` is in a `finally` block |

## Cross-References

- **multi-model-orchestrator** — SSE is the transport layer for multi-stage AI pipeline progress
- **cloudflare-fullstack** — SSE endpoints deploy as Cloudflare Workers routes
- **generative-page-pipeline** — Primary consumer; streams page blocks as they are generated
