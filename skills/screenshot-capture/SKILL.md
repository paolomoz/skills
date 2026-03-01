---
name: screenshot-capture
description: Capture full-page and viewport screenshots of websites using Playwright with overlay removal, cookie consent handling, and comparison modes. Use when "capturing screenshots", "website screenshots", "visual testing", or "page capture".
---

# Screenshot Capture

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| content | "capture screenshots", "website screenshots", "visual testing", "page capture" | Low | 5 projects |

Capture high-quality, full-page and viewport-sized screenshots of websites using Playwright and Chromium. The skill handles real-world complications that break naive screenshot approaches: cookie consent banners, age gates, sticky headers, modal overlays, and dynamic content that loads after initial paint. Outputs are clean PNGs suitable for audits, comparison reports, and stakeholder presentations.

## When to Use

- Capturing baseline screenshots of a website before a redesign or migration
- Taking before/after screenshots to validate visual changes
- Generating page screenshots for a content audit or brand consistency review
- Automating visual regression testing across multiple pages
- Capturing competitor site screenshots for design analysis
- Producing full-page captures for stakeholder review when they cannot access the live site

## Instructions

### Step 1: Set Up Playwright

Install Playwright with Chromium. This is the only browser engine needed for screenshot capture -- Chromium produces the most consistent rendering across platforms.

```bash
npm init -y
npm install playwright
npx playwright install chromium
```

If running in a CI environment or Docker container, install system dependencies:

```bash
npx playwright install-deps chromium
```

### Step 2: Configure the Capture

Define the viewport, timeouts, and output settings. These defaults produce consistent results across most websites.

```javascript
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const CONFIG = {
  viewport: { width: 1440, height: 900 },
  waitUntil: 'networkidle',      // Wait for network to be idle (no requests for 500ms)
  timeout: 30000,                 // 30 second timeout per page
  outputDir: 'screenshots',
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
};
```

**Viewport choice**: 1440x900 is the most common desktop resolution for stakeholder review. For mobile captures, use `{ width: 390, height: 844 }` (iPhone 14 equivalent). Always capture both if the site is responsive.

### Step 3: Define the Page List

Specify which pages to capture. Each entry has a human-readable name (used for the output filename) and a path relative to the base URL.

```javascript
const PAGES = [
  { name: 'home',          path: '/' },
  { name: 'about',         path: '/about' },
  { name: 'products',      path: '/products' },
  { name: 'product-detail', path: '/products/flagship-product' },
  { name: 'blog',          path: '/blog' },
  { name: 'contact',       path: '/contact' },
];
```

For dynamic page lists, generate from a sitemap or content index:

```javascript
async function loadPagesFromSitemap(sitemapUrl) {
  const response = await fetch(sitemapUrl);
  const xml = await response.text();
  const urls = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]);

  return urls.map(url => {
    const urlObj = new URL(url);
    const name = urlObj.pathname.replace(/\//g, '-').replace(/^-|-$/g, '') || 'home';
    return { name, path: urlObj.pathname };
  });
}
```

### Step 4: Implement Overlay Removal (nukeOverlays)

This is the most critical function. Real websites are cluttered with cookie consent banners, newsletter popups, age/profession gates, and sticky navigation that obscure the actual content. Remove them before capturing.

```javascript
async function nukeOverlays(page) {
  await page.evaluate(() => {
    // --- Phase 1: Click consent buttons ---
    const consentPatterns = [
      'Accept All', 'Accept Cookies', 'Accept all cookies',
      'I Accept', 'I Agree', 'Got It', 'OK', 'Allow All',
      'Alle akzeptieren', 'Tout accepter', 'Aceptar todo'
    ];

    const buttons = document.querySelectorAll('button, a[role="button"], [class*="consent"] a, [class*="cookie"] button');
    for (const btn of buttons) {
      const text = btn.textContent.trim();
      if (consentPatterns.some(pattern => text.toLowerCase().includes(pattern.toLowerCase()))) {
        btn.click();
        break;  // Only click the first match
      }
    }

    // --- Phase 2: Click age/profession gates ---
    const gatePatterns = [
      'I am a Healthcare Professional',
      'I am over 18', 'I am over 21',
      'Yes, I am of legal age',
      'Enter Site', 'Continue to site'
    ];

    for (const btn of document.querySelectorAll('button, a')) {
      const text = btn.textContent.trim();
      if (gatePatterns.some(p => text.toLowerCase().includes(p.toLowerCase()))) {
        btn.click();
        break;
      }
    }

    // --- Phase 3: Remove fixed/sticky overlays ---
    const allElements = document.querySelectorAll('*');
    for (const el of allElements) {
      const style = window.getComputedStyle(el);
      const position = style.position;
      const zIndex = parseInt(style.zIndex) || 0;

      // Remove position:fixed elements with high z-index (likely overlays)
      if ((position === 'fixed' || position === 'sticky') && zIndex > 999) {
        el.remove();
      }
    }

    // --- Phase 4: Target known overlay selectors ---
    const overlaySelectors = [
      '[class*="cookie"]', '[class*="consent"]', '[class*="gdpr"]',
      '[class*="overlay"]', '[class*="modal-backdrop"]',
      '[id*="cookie"]', '[id*="consent"]', '[id*="gdpr"]',
      '[class*="popup"]', '[class*="newsletter"]',
      '.onetrust-consent-sdk', '#CybotCookiebotDialog',
      '.cc-window', '.cookie-banner', '.privacy-banner'
    ];

    for (const selector of overlaySelectors) {
      for (const el of document.querySelectorAll(selector)) {
        el.remove();
      }
    }

    // --- Phase 5: Restore scrolling ---
    document.body.style.overflow = 'auto';
    document.body.style.position = 'static';
    document.documentElement.style.overflow = 'auto';
    document.documentElement.style.position = 'static';

    // Remove overflow:hidden from body (often set by modal scripts)
    document.body.classList.forEach(cls => {
      if (cls.includes('no-scroll') || cls.includes('modal-open') || cls.includes('overflow-hidden')) {
        document.body.classList.remove(cls);
      }
    });
  });

  // Wait for DOM to settle after removals
  await page.waitForTimeout(500);
}
```

**Ordering matters**: Click consent buttons first (Phase 1-2) because they often remove their own overlays when accepted. Only use the nuclear removal (Phase 3-4) for overlays that persist after clicking. If you remove elements before clicking, the consent state may not persist, causing the banner to reappear on the next navigation.

### Step 5: Implement the Capture Function

```javascript
async function captureScreenshots(baseUrl, pages, config = CONFIG) {
  // Ensure output directory exists
  fs.mkdirSync(config.outputDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: config.viewport,
    userAgent: config.userAgent,
    // Reduce motion to avoid capturing mid-animation
    reducedMotion: 'reduce'
  });

  const results = [];

  for (const pageConfig of pages) {
    const page = await context.newPage();
    const url = new URL(pageConfig.path, baseUrl).href;

    console.log(`Capturing: ${pageConfig.name} (${url})`);

    try {
      // Navigate and wait for content
      await page.goto(url, {
        waitUntil: config.waitUntil,
        timeout: config.timeout
      });

      // Remove overlays
      await nukeOverlays(page);

      // Wait for lazy-loaded images and dynamic content
      await autoScroll(page);
      await page.waitForTimeout(1000);  // Final settle time

      // Scroll back to top for viewport screenshot
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(300);

      // Capture full page
      const fullPath = path.join(config.outputDir, `${pageConfig.name}-full.png`);
      await page.screenshot({ path: fullPath, fullPage: true });

      // Capture viewport only
      const vpPath = path.join(config.outputDir, `${pageConfig.name}-viewport.png`);
      await page.screenshot({ path: vpPath, fullPage: false });

      results.push({
        name: pageConfig.name,
        url,
        fullPage: fullPath,
        viewport: vpPath,
        status: 'success'
      });

    } catch (error) {
      console.error(`Failed: ${pageConfig.name} - ${error.message}`);
      results.push({
        name: pageConfig.name,
        url,
        status: 'error',
        error: error.message
      });
    } finally {
      await page.close();
    }
  }

  await browser.close();
  return results;
}
```

### Step 6: Handle Lazy-Loaded Content

Many modern sites lazy-load images and content sections as the user scrolls. Scroll the full page before capturing to trigger all lazy loads.

```javascript
async function autoScroll(page) {
  await page.evaluate(async () => {
    const scrollHeight = document.body.scrollHeight;
    const viewportHeight = window.innerHeight;
    let currentPosition = 0;

    while (currentPosition < scrollHeight) {
      window.scrollTo(0, currentPosition);
      currentPosition += viewportHeight;
      // Small delay for lazy-loaded content to trigger and render
      await new Promise(resolve => setTimeout(resolve, 200));
    }

    // Scroll to absolute bottom to catch any final lazy loads
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(resolve => setTimeout(resolve, 500));
  });
}
```

### Step 7: Implement Comparison Mode

For before/after analysis, capture two sets of screenshots and generate a side-by-side comparison HTML file.

```javascript
async function generateComparison(beforeDir, afterDir, outputPath) {
  const beforeFiles = fs.readdirSync(beforeDir).filter(f => f.endsWith('-viewport.png'));

  let html = `<!DOCTYPE html>
<html><head><style>
  body { font-family: -apple-system, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
  .comparison { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 40px; }
  .comparison img { width: 100%; border: 1px solid #ddd; border-radius: 8px; }
  .label { text-align: center; font-weight: 600; padding: 8px; color: #333; }
  h2 { margin: 20px 0 10px; color: #131313; }
</style></head><body>
<h1>Visual Comparison Report</h1>`;

  for (const file of beforeFiles) {
    const name = file.replace('-viewport.png', '');
    const afterFile = path.join(afterDir, file);

    if (fs.existsSync(afterFile)) {
      html += `
<h2>${name}</h2>
<div class="comparison">
  <div>
    <div class="label">Before</div>
    <img src="${path.join(beforeDir, file)}" alt="Before: ${name}" />
  </div>
  <div>
    <div class="label">After</div>
    <img src="${afterFile}" alt="After: ${name}" />
  </div>
</div>`;
    }
  }

  html += '</body></html>';
  fs.writeFileSync(outputPath, html);
}
```

### Step 8: Run the Capture

Put it all together with a main entry point.

```javascript
async function main() {
  const baseUrl = process.env.BASE_URL || 'https://example.com';

  console.log(`Starting capture of ${baseUrl}`);
  console.log(`Output directory: ${CONFIG.outputDir}`);
  console.log(`Viewport: ${CONFIG.viewport.width}x${CONFIG.viewport.height}`);
  console.log(`Pages to capture: ${PAGES.length}`);
  console.log('---');

  const results = await captureScreenshots(baseUrl, PAGES);

  // Summary
  const successes = results.filter(r => r.status === 'success');
  const failures = results.filter(r => r.status === 'error');

  console.log('---');
  console.log(`Captured: ${successes.length}/${results.length} pages`);

  if (failures.length > 0) {
    console.log('Failed pages:');
    for (const f of failures) {
      console.log(`  - ${f.name}: ${f.error}`);
    }
  }

  // Write manifest
  fs.writeFileSync(
    path.join(CONFIG.outputDir, 'manifest.json'),
    JSON.stringify({ baseUrl, captured: new Date().toISOString(), results }, null, 2)
  );
}

main().catch(console.error);
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BASE_URL` | Yes | - | The target website URL (e.g., `https://example.com`) |

### Output Structure

```
screenshots/
  manifest.json          # Capture metadata and results
  home-full.png          # Full page screenshot
  home-viewport.png      # Viewport-only screenshot
  about-full.png
  about-viewport.png
  products-full.png
  products-viewport.png
  ...
```

The manifest.json contains:
```json
{
  "baseUrl": "https://example.com",
  "captured": "2025-12-01T15:30:00.000Z",
  "results": [
    {
      "name": "home",
      "url": "https://example.com/",
      "fullPage": "screenshots/home-full.png",
      "viewport": "screenshots/home-viewport.png",
      "status": "success"
    }
  ]
}
```

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Timeout on every page | `networkidle` waiting for persistent connections (analytics, WebSockets) | Switch to `domcontentloaded` and add an explicit `waitForTimeout(3000)` after navigation |
| Cookie banner still visible | Consent button text does not match any pattern in Phase 1 | Inspect the site manually, find the button text, and add it to `consentPatterns` |
| Page is blank or shows only header | SPA content loads after JavaScript execution | Add `await page.waitForSelector('main', { timeout: 10000 })` before capturing |
| Screenshots have grey placeholder images | Lazy-loaded images not triggered | Increase the delay in `autoScroll` from 200ms to 500ms per viewport scroll |
| Full-page screenshot is extremely tall | Infinite scroll or dynamically expanding content | Set a max scroll limit in `autoScroll` (e.g., `maxScrolls = 20`) |
| Comparison shows different crops | Viewport size changed between before/after runs | Always use the same `CONFIG.viewport` for both captures; store config in manifest |
| Overlay removal breaks page layout | Phase 3 (z-index nuclear option) removed navigation or headers | Increase the z-index threshold from 999 to 9999, or exclude elements matching `nav`, `header` selectors |
| Authentication required pages show login screen | Site requires authentication cookies | Use `context.addCookies()` to inject session cookies before navigation, or use `page.fill()` and `page.click()` to log in programmatically |

### Cross-References

- **site-auditor** — Uses screenshots as part of comprehensive site audit reports
- **design-system-extractor** — Analyzes screenshots to identify visual patterns and design tokens
- **block-detector** — Identifies content blocks from full-page screenshots for structural analysis
