---
name: extension-e2e-test
description: Run automated E2E tests against a Chrome extension using Puppeteer. Use when "test extension", "e2e extension", "verify extension works", "extension testing", or "test in Chrome extension mode".
---

# Chrome Extension E2E Testing with Puppeteer

Automate end-to-end testing of Chrome extensions by loading them in a real Chrome instance via Puppeteer. This skill covers the full lifecycle: launching Chrome with the extension, getting the extension ID, navigating extension pages (side panel, popup, options), interacting with sandbox iframes, and verifying cross-context messaging (content script ↔ service worker ↔ offscreen document ↔ side panel).

## When to Use

- Verifying a Chrome extension feature works after code changes
- Testing message routing between extension contexts (side panel, offscreen, service worker)
- Interacting with CSP-exempt sandbox iframes inside an extension
- Debugging extension-specific issues that can't be reproduced in CLI/standalone mode
- Running automated regression tests before shipping an extension update

## Prerequisites

The project must have `puppeteer` installed:

```bash
npm install --save-dev puppeteer
# or: npm install puppeteer (if already a dependency)
```

The extension must be built before testing (e.g., `npm run build:extension` → `dist/extension/`).

## Instructions

### Step 1: Build the Extension

Always build fresh before testing:

```bash
npm run build:extension
```

Identify the extension output directory (typically `dist/extension/`). This is the path you pass to Chrome's `--load-extension` flag.

### Step 2: Launch Chrome with the Extension

Key flags:
- `--disable-extensions-except=<path>` — Only load your extension (no others)
- `--load-extension=<path>` — Load unpacked extension from this directory
- `--no-first-run` — Skip Chrome's first-run UI
- `--user-data-dir=/tmp/...` — Isolated profile so tests don't interfere with your real browser

```typescript
import puppeteer from 'puppeteer';
import path from 'node:path';

const EXTENSION_PATH = path.resolve(__dirname, 'dist/extension');

const browser = await puppeteer.launch({
  headless: false,  // Extensions require headed mode
  protocolTimeout: 60000,
  args: [
    `--disable-extensions-except=${EXTENSION_PATH}`,
    `--load-extension=${EXTENSION_PATH}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-default-apps',
    '--disable-popup-blocking',
    `--user-data-dir=/tmp/ext-e2e-${Date.now()}`,
  ],
});
```

**Critical**: Extensions do NOT work in headless mode. You must use `headless: false`.

### Step 3: Get the Extension ID

The extension ID is assigned dynamically when loading unpacked. Get it from the service worker target URL:

```typescript
const swTarget = await browser.waitForTarget(
  t => t.type() === 'service_worker' && t.url().includes('service-worker'),
  { timeout: 30000 },
);
const extensionId = swTarget.url().match(/chrome-extension:\/\/([^/]+)/)![1];
```

If your extension doesn't have a service worker (Manifest V2 with background page), use:

```typescript
const bgTarget = await browser.waitForTarget(
  t => t.type() === 'background_page',
  { timeout: 30000 },
);
```

### Step 4: Open Extension Pages

Extension pages (side panel, popup, options) can be opened by navigating directly to their `chrome-extension://` URL:

```typescript
const page = await browser.newPage();
await page.goto(`chrome-extension://${extensionId}/index.html`, {
  waitUntil: 'domcontentloaded',
  timeout: 30000,
});
```

Common extension page paths:
- Side panel: `index.html` or `sidepanel.html`
- Popup: `popup.html`
- Options: `options.html`
- Offscreen: `offscreen.html` (usually created programmatically, not navigated to)

### Step 5: Wait for Extension Initialization

Extensions often need time to initialize (offscreen document creation, IndexedDB population, service worker startup). Poll for readiness:

```typescript
// Wait for a global flag set by your extension code
await page.waitForFunction(
  () => !!(window as any).__myExtensionReady,
  { timeout: 30000 }
);

// Or poll for specific state
for (let i = 0; i < 20; i++) {
  await new Promise(r => setTimeout(r, 1000));
  const ready = await page.evaluate(() => {
    // Check whatever indicates your extension is initialized
    return document.querySelector('.main-content') !== null;
  });
  if (ready) break;
  if (i === 19) throw new Error('Extension did not initialize within 20s');
}
```

### Step 6: Interact with Sandbox Iframes

Extension sandbox iframes (CSP-exempt pages listed in `manifest.json` `sandbox.pages`) are cross-origin — `iframe.contentDocument` returns `null`. Use Puppeteer's **frame API** instead:

```typescript
// Find the sandbox iframe's frame by URL pattern
const sandboxFrame = page.frames().find(
  f => f.url().includes('sandbox.html')
);

if (sandboxFrame) {
  // Evaluate inside the sandbox iframe
  const heading = await sandboxFrame.evaluate(() =>
    document.querySelector('h1')?.textContent?.trim() || '(none)'
  );

  // Check for bridge objects injected via postMessage
  const hasBridge = await sandboxFrame.evaluate(() =>
    typeof (window as any).myBridge !== 'undefined'
  );

  // Click buttons inside the sandbox
  await sandboxFrame.evaluate(() => {
    (document.querySelector('#my-button') as HTMLButtonElement)?.click();
  });
}
```

**Why not contentDocument?** Sandbox iframes run on a unique `null` origin, making them cross-origin even within the same extension. Puppeteer's frame API uses CDP to access them directly.

### Step 7: Test Cross-Context Messaging

To verify messages flow between contexts (e.g., side panel → service worker → offscreen):

```typescript
// Set up a listener in the page to catch messages
await page.evaluate(() => {
  (window as any).__capturedMessages = [];
  window.addEventListener('message', (e) => {
    (window as any).__capturedMessages.push(e.data);
  });
});

// Trigger an action that sends a message (e.g., from a sandbox iframe)
if (sandboxFrame) {
  await sandboxFrame.evaluate(() => {
    (window as any).myBridge.sendEvent({ action: 'test', data: { n: 1 } });
  });
}

// Wait and check
await new Promise(r => setTimeout(r, 1000));
const messages = await page.evaluate(() => (window as any).__capturedMessages);
console.assert(messages.length > 0, 'No messages received');
```

For chrome.runtime message verification (panel → offscreen), you typically can't directly observe the offscreen document from puppeteer. Instead, verify the **effect** — e.g., check that the UI updated, a DOM element changed, or state was persisted.

### Step 8: Test Data Push (Parent → Iframe)

To verify data flowing from the parent page into a sandbox iframe:

```typescript
// Register a handler inside the iframe
await sandboxFrame.evaluate(() => {
  (window as any).__receivedData = null;
  (window as any).myBridge.on('update', (data: any) => {
    (window as any).__receivedData = data;
  });
});

// Send data from the parent page
await page.evaluate(() => {
  (window as any).myManager.sendData('target-name', { msg: 'hello', n: 42 });
});

await new Promise(r => setTimeout(r, 1000));

const received = await sandboxFrame.evaluate(() => (window as any).__receivedData);
console.assert(received?.n === 42, 'Data not received in iframe');
```

### Step 9: Take Screenshots for Debugging

Capture screenshots at key points for visual verification and debugging failures:

```typescript
await page.screenshot({ path: '/tmp/ext-test-step1.png', fullPage: true });
```

### Step 10: Clean Up

Always close the browser, even on failure:

```typescript
try {
  await runTests();
} catch (err) {
  console.error('FATAL:', err);
  process.exit(1);
} finally {
  await browser.close().catch(() => {});
}
```

### Complete Test Script Template

```typescript
import puppeteer, { type Browser } from 'puppeteer';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const EXTENSION_PATH = path.resolve(__dirname, 'dist/extension');
const TIMEOUT = 60000;

let browser: Browser;

function log(step: string, msg: string, data?: unknown) {
  const ts = new Date().toISOString().slice(11, 23);
  const d = data !== undefined ? ' ' + JSON.stringify(data) : '';
  console.log(`[${ts}] ${step}: ${msg}${d}`);
}

async function sleep(ms: number) {
  return new Promise(r => setTimeout(r, ms));
}

async function run() {
  // 1. Launch
  browser = await puppeteer.launch({
    headless: false,
    protocolTimeout: TIMEOUT,
    args: [
      `--disable-extensions-except=${EXTENSION_PATH}`,
      `--load-extension=${EXTENSION_PATH}`,
      '--no-first-run', '--no-default-browser-check',
      '--disable-default-apps', '--disable-popup-blocking',
      `--user-data-dir=/tmp/ext-e2e-${Date.now()}`,
    ],
  });

  // 2. Get extension ID
  const swTarget = await browser.waitForTarget(
    t => t.type() === 'service_worker' && t.url().includes('service-worker'),
    { timeout: TIMEOUT },
  );
  const extensionId = swTarget.url().match(/chrome-extension:\/\/([^/]+)/)![1];
  log('SETUP', 'Extension ID: ' + extensionId);

  // 3. Open extension page
  const page = await browser.newPage();
  await page.goto(`chrome-extension://${extensionId}/index.html`, {
    waitUntil: 'domcontentloaded', timeout: TIMEOUT,
  });

  // 4. Wait for initialization
  // ... (poll for your extension's ready state)

  // 5. Run tests
  // ... (use page.evaluate, frame API, screenshots)

  log('DONE', 'All tests complete');
}

run()
  .catch(err => { console.error('FATAL:', err); process.exit(1); })
  .finally(async () => { if (browser) await browser.close().catch(() => {}); });
```

Run with: `npx tsx test-extension.ts`

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Extension not loading | Wrong path or missing manifest.json | Verify `dist/extension/manifest.json` exists; rebuild with `npm run build:extension` |
| `headless: true` fails | Extensions require headed Chrome | Always use `headless: false` |
| `waitForTarget` times out | Service worker not starting | Check for errors in `chrome://extensions`; ensure manifest has `service_worker` field |
| `iframe.contentDocument` is null | Sandbox iframes are cross-origin | Use `page.frames().find(f => f.url().includes('...'))` instead |
| `page.evaluate` can't access extension APIs | `chrome.*` APIs only work in extension contexts | The puppeteer page navigated to `chrome-extension://` URL does have access; verify URL is correct |
| Flaky initialization | Race between service worker, offscreen doc, and side panel | Add polling loops with generous timeouts (up to 20s); don't rely on fixed `sleep()` |
| Multiple sandbox iframes | Can't distinguish which frame is which | Filter by URL or by excluding `mainFrame()` and previously found frames |
| Extension ID changes between runs | Unpacked extensions get dynamic IDs | Always extract ID from service worker URL at runtime; never hardcode |
