---
name: da-content-pipeline
description: Convert generated HTML to Document Authoring (DA) format and upload with authentication, batch processing, and preview triggering for AEM Edge Delivery Services. Use when "uploading to DA", "DA content pipeline", "AEM content authoring", or "plain HTML to DA conversion".
---

# DA Content Pipeline

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| page-generation | "uploading to DA", "DA content pipeline", "AEM content authoring", "plain HTML to DA conversion" | High | 4 projects |

Convert generated or authored HTML content from `.plain.html` block format to Document Authoring (DA) table-based format, upload it to DA with IMS authentication, and trigger AEM Edge Delivery Services preview. This skill covers the complete pipeline from raw EDS block HTML through DA format conversion, authenticated upload, batch processing, and preview/publish triggering.

## When to Use

- Converting EDS `.plain.html` block-structured HTML to DA's table-based format for editing
- Uploading generated page content to DA (admin.da.live) programmatically
- Building an automated pipeline that generates content and persists it to AEM Edge Delivery Services
- Batch-uploading multiple pages with rate limiting and error recovery
- Triggering preview and publish after content upload
- Integrating DA uploads into a Cloudflare Worker or serverless function

## Instructions

### .plain.html to DA Format Conversion

DA uses a specific table-based HTML format for content authoring. The source format (`.plain.html`) uses `<div>` elements with class names for block types, separated by `<hr/>` tags. The DA format converts each block into a `<table>` with a `<thead>` containing the block name and a `<tbody>` containing the block's rows and cells.

**Source format (.plain.html):**

```html
<div class="hero">
  <div>
    <div>
      <h1>Welcome to Our Site</h1>
      <p>Building the future of web experiences.</p>
      <p><a href="/get-started">Get Started</a></p>
    </div>
    <div>
      <picture><img src="/media/hero.webp" alt="Hero image" /></picture>
    </div>
  </div>
</div>
<hr/>
<div class="cards">
  <div>
    <div><picture><img src="/media/card1.webp" alt="Feature 1" /></picture></div>
    <div>
      <h3>Feature One</h3>
      <p>Description of feature one.</p>
    </div>
  </div>
  <div>
    <div><picture><img src="/media/card2.webp" alt="Feature 2" /></picture></div>
    <div>
      <h3>Feature Two</h3>
      <p>Description of feature two.</p>
    </div>
  </div>
</div>
```

**DA format output:**

```html
<body>
  <header></header>
  <main>
    <div>
      <h1>Welcome to Our Site</h1>
      <p>Building the future of web experiences.</p>
      <p><a href="/get-started">Get Started</a></p>
      <picture><img src="/media/hero.webp" alt="Hero image" /></picture>
    </div>
    <table>
      <thead>
        <tr><th colspan="2">hero</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <h1>Welcome to Our Site</h1>
            <p>Building the future of web experiences.</p>
            <p><a href="/get-started">Get Started</a></p>
          </td>
          <td>
            <picture><img src="/media/hero.webp" alt="Hero image" /></picture>
          </td>
        </tr>
      </tbody>
    </table>
    <hr/>
    <table>
      <thead>
        <tr><th colspan="2">cards</th></tr>
      </thead>
      <tbody>
        <tr>
          <td><picture><img src="/media/card1.webp" alt="Feature 1" /></picture></td>
          <td>
            <h3>Feature One</h3>
            <p>Description of feature one.</p>
          </td>
        </tr>
        <tr>
          <td><picture><img src="/media/card2.webp" alt="Feature 2" /></picture></td>
          <td>
            <h3>Feature Two</h3>
            <p>Description of feature two.</p>
          </td>
        </tr>
      </tbody>
    </table>
  </main>
  <footer></footer>
</body>
```

See `references/da-format-spec.md` for the complete DA HTML format specification.

---

### Conversion Algorithm

The conversion follows a deterministic algorithm that parses `.plain.html` blocks and converts each to a DA table:

```python
import re
from html.parser import HTMLParser

def convert_plain_to_da(html_content, title=""):
    """Convert .plain.html block format to DA table format."""

    # Split content into sections by <hr/> separators
    sections = re.split(r'<hr\s*/?>', html_content)

    da_sections = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract block name from outer div class
        block_match = re.match(
            r'<div\s+class="([^"]+)"[^>]*>(.*)</div>\s*$',
            section,
            re.DOTALL
        )

        if block_match:
            block_name = block_match.group(1)
            block_content = block_match.group(2)
            da_sections.append(convert_block_to_table(block_name, block_content))
        else:
            # Default content (no block wrapper) -- pass through as-is
            da_sections.append(f'<div>{section}</div>')

    # Assemble the DA document
    sections_html = '\n<hr/>\n'.join(da_sections)

    return f"""<body>
  <header></header>
  <main>
    {sections_html}
  </main>
  <footer></footer>
</body>"""


def convert_block_to_table(block_name, block_content):
    """Convert a single block's content to a DA table."""

    # Extract rows (direct child divs of the block)
    rows = re.findall(
        r'<div>(.*?)</div>',
        block_content,
        re.DOTALL
    )

    if not rows:
        # Single-row block
        return f"""<table>
  <thead>
    <tr><th>{block_name}</th></tr>
  </thead>
  <tbody>
    <tr><td>{block_content.strip()}</td></tr>
  </tbody>
</table>"""

    # Multi-row block
    tbody_rows = []
    max_cols = 1

    for row in rows:
        # Extract cells (nested divs within each row)
        cells = re.findall(r'<div>(.*?)</div>', row, re.DOTALL)

        if cells:
            max_cols = max(max_cols, len(cells))
            tds = ''.join(f'<td>{cell.strip()}</td>' for cell in cells)
        else:
            tds = f'<td>{row.strip()}</td>'

        tbody_rows.append(f'    <tr>{tds}</tr>')

    colspan = f' colspan="{max_cols}"' if max_cols > 1 else ''

    return f"""<table>
  <thead>
    <tr><th{colspan}>{block_name}</th></tr>
  </thead>
  <tbody>
{chr(10).join(tbody_rows)}
  </tbody>
</table>"""
```

Key rules:
- The `<thead>` always contains a single row with the block name as the header text.
- Set `colspan` on the `<th>` to match the maximum number of cells in any row of the block.
- Content that is not wrapped in a `<div class="blockname">` is treated as default content and passed through as-is in a `<div>`.
- Always wrap the output in `<body><header/><main>...</main><footer/></body>`. DA expects this exact structure.
- Preserve all HTML within cells (links, images, formatted text). Do not strip or sanitize inner HTML.

---

### Authentication Flow

DA uses Adobe IMS (Identity Management System) for authentication. Obtain an access token using service account credentials:

```typescript
interface IMSTokenResponse {
  access_token: string
  token_type: 'bearer'
  expires_in: number   // seconds
}

async function getIMSAccessToken(env: Env): Promise<string> {
  // Check KV cache first
  const cached = await env.KV.get('da_ims_token')
  if (cached) return cached

  const response = await fetch('https://ims-na1.adobelogin.com/ims/token/v3', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: env.DA_CLIENT_ID,
      client_secret: env.DA_CLIENT_SECRET,
      scope: 'AdobeID,openid,aem.authoring'
    })
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`IMS token exchange failed: ${response.status} ${error}`)
  }

  const data: IMSTokenResponse = await response.json()

  // Cache with buffer (expire 5 minutes early)
  await env.KV.put('da_ims_token', data.access_token, {
    expirationTtl: data.expires_in - 300
  })

  return data.access_token
}
```

Key rules:
- Always cache the IMS token in KV. Token exchange adds 200-500ms latency and has rate limits.
- Expire the cached token 5 minutes before the actual expiration to avoid race conditions.
- The scope `aem.authoring` is required for DA write operations. Without it, uploads will return 403.
- If the token exchange fails with a 401, the client credentials may have expired. Check the Adobe Developer Console for the integration's status.

---

### Upload to DA

Upload converted HTML to DA using a FormData PUT request:

```typescript
async function uploadToDA(
  html: string,
  path: string,
  env: Env
): Promise<{ success: boolean; path: string; status: number }> {
  const token = await getIMSAccessToken(env)

  // Ensure path ends with .html
  const fullPath = path.endsWith('.html') ? path : `${path}.html`

  const formData = new FormData()
  formData.append(
    'data',
    new Blob([html], { type: 'text/html' }),
    fullPath.split('/').pop()  // filename only
  )

  const url = `https://admin.da.live/source/${env.DA_ORG}/${env.DA_REPO}/${fullPath}`

  const response = await fetch(url, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: formData
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`DA upload failed: ${response.status} ${error} for ${fullPath}`)
  }

  return {
    success: true,
    path: fullPath,
    status: response.status
  }
}
```

Key rules:
- Use `PUT`, not `POST`. DA uses PUT for creating and updating content.
- The `Content-Type` header must NOT be set manually -- `FormData` sets it automatically with the correct boundary.
- The filename in the `formData.append` call must match the last segment of the path (e.g., `index.html` for path `/index.html`).
- Maximum upload size is 10MB. If the HTML exceeds this (unlikely for text content, possible with inline images), strip inline base64 images and upload them separately.

---

### Upload Script Features

For batch operations, use a script that handles conversion, upload, rate limiting, and error recovery:

```python
#!/usr/bin/env python3
"""Batch upload .plain.html files to DA with automatic conversion."""

import os
import sys
import time
import glob
import argparse
import requests

def batch_upload(source_dir, org, repo, token, dry_run=False, rate_limit=0.5):
    """Upload all .plain.html files from source_dir to DA."""

    files = glob.glob(os.path.join(source_dir, '**/*.plain.html'), recursive=True)
    print(f"Found {len(files)} files to upload")

    results = {'success': 0, 'failed': 0, 'skipped': 0}

    for filepath in sorted(files):
        # Derive DA path from file path
        rel_path = os.path.relpath(filepath, source_dir)
        da_path = rel_path.replace('.plain.html', '.html')

        # Read and convert
        with open(filepath, 'r') as f:
            plain_html = f.read()

        title = os.path.splitext(os.path.basename(filepath))[0]
        da_html = convert_plain_to_da(plain_html, title=title)

        if dry_run:
            print(f"[DRY RUN] Would upload: {da_path} ({len(da_html)} bytes)")
            results['skipped'] += 1
            continue

        # Upload with retry
        success = upload_with_retry(da_html, da_path, org, repo, token)

        if success:
            results['success'] += 1
            print(f"[OK] {da_path}")
        else:
            results['failed'] += 1
            print(f"[FAIL] {da_path}")

        # Rate limiting
        time.sleep(rate_limit)

    print(f"\nResults: {results['success']} uploaded, "
          f"{results['failed']} failed, {results['skipped']} skipped")
    return results


def upload_with_retry(html, path, org, repo, token, max_retries=3):
    """Upload a single file with exponential backoff retry."""

    for attempt in range(max_retries):
        try:
            url = f"https://admin.da.live/source/{org}/{repo}/{path}"

            files = {
                'data': (os.path.basename(path), html.encode('utf-8'), 'text/html')
            }
            headers = {'Authorization': f'Bearer {token}'}

            response = requests.put(url, files=files, headers=headers)

            if response.status_code in (200, 201, 204):
                return True

            if response.status_code == 429:
                # Rate limited -- wait and retry
                wait = (2 ** attempt) * 2
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue

            if response.status_code == 401:
                print(f"  Authentication failed -- token may be expired")
                return False

            print(f"  Upload failed: {response.status_code} {response.text[:200]}")

        except requests.exceptions.RequestException as e:
            print(f"  Request error: {e}")

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)

    return False
```

**Script options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--source` | Directory containing `.plain.html` files | Required |
| `--org` | DA organization name | `$DA_ORG` env var |
| `--repo` | DA repository name | `$DA_REPO` env var |
| `--dry-run` | Show what would be uploaded without uploading | `false` |
| `--rate-limit` | Seconds between uploads | `0.5` |
| `--retry` | Max retries per file | `3` |

---

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DA_CLIENT_ID` | Adobe IMS client ID from Developer Console | Yes |
| `DA_CLIENT_SECRET` | Adobe IMS client secret | Yes |
| `DA_ORG` | DA organization slug (e.g., `mycompany`) | Yes |
| `DA_REPO` | DA repository name (e.g., `mysite`) | Yes |
| `DA_SERVICE_TOKEN` | Pre-generated long-lived service token (alternative to client credentials) | No |

When `DA_SERVICE_TOKEN` is set, skip the IMS token exchange and use it directly as the Bearer token. This is useful for local development and CI/CD pipelines where you do not want to manage client credentials.

---

### Preview Triggering

After uploading content to DA, trigger a preview to make the content visible on the AEM Edge Delivery Services preview environment:

```typescript
async function triggerPreview(
  owner: string,
  repo: string,
  branch: string,
  path: string
): Promise<{ success: boolean; previewUrl: string }> {
  // Remove .html extension for the preview path
  const previewPath = path.replace(/\.html$/, '')

  const response = await fetch(
    `https://admin.hlx.page/preview/${owner}/${repo}/${branch}/${previewPath}`,
    { method: 'POST' }
  )

  if (!response.ok) {
    throw new Error(`Preview trigger failed: ${response.status}`)
  }

  return {
    success: true,
    previewUrl: `https://${branch}--${repo}--${owner}.aem.page/${previewPath}`
  }
}
```

For publishing (making content live):

```typescript
async function triggerPublish(
  owner: string,
  repo: string,
  branch: string,
  path: string
): Promise<{ success: boolean; liveUrl: string }> {
  const publishPath = path.replace(/\.html$/, '')

  const response = await fetch(
    `https://admin.hlx.page/live/${owner}/${repo}/${branch}/${publishPath}`,
    { method: 'POST' }
  )

  return {
    success: true,
    liveUrl: `https://${branch}--${repo}--${owner}.aem.live/${publishPath}`
  }
}
```

Key rules:
- Preview and publish are separate operations. Preview makes content visible on `.aem.page`; publish makes it visible on `.aem.live`.
- The path in the preview/publish URL should NOT include the `.html` extension.
- The branch is typically `main` but can be any branch for feature branch previews.
- Preview triggering is idempotent -- calling it multiple times is safe.
- After batch uploads, trigger preview for each page. Add a 1-second delay between preview triggers to avoid rate limiting.

---

### Worker Integration (TypeScript)

For Cloudflare Workers integration, use the `@nova/da-client` package (or build a minimal client):

```typescript
import { DAAdminClient } from '@nova/da-client'

interface DAWorkerEnv {
  DA_CLIENT_ID: string
  DA_CLIENT_SECRET: string
  DA_ORG: string
  DA_REPO: string
  DA_TOKEN_CACHE: KVNamespace  // KV for token caching
}

class DAContentPipeline {
  private client: DAAdminClient
  private env: DAWorkerEnv

  constructor(env: DAWorkerEnv) {
    this.env = env
    this.client = new DAAdminClient({
      org: env.DA_ORG,
      repo: env.DA_REPO,
      clientId: env.DA_CLIENT_ID,
      clientSecret: env.DA_CLIENT_SECRET,
      tokenCache: env.DA_TOKEN_CACHE
    })
  }

  async uploadPage(path: string, plainHtml: string): Promise<void> {
    // Convert .plain.html to DA format
    const daHtml = this.convertToDA(plainHtml)

    // Upload to DA
    await this.client.putSource(path, daHtml)

    // Trigger preview
    await this.client.preview(path)
  }

  async uploadBatch(
    pages: Array<{ path: string; html: string }>,
    onProgress?: (completed: number, total: number) => void
  ): Promise<{ success: string[]; failed: string[] }> {
    const success: string[] = []
    const failed: string[] = []

    for (let i = 0; i < pages.length; i++) {
      try {
        await this.uploadPage(pages[i].path, pages[i].html)
        success.push(pages[i].path)
      } catch (error) {
        console.error(`Upload failed for ${pages[i].path}:`, error)
        failed.push(pages[i].path)
      }

      onProgress?.(i + 1, pages.length)

      // Rate limiting
      if (i < pages.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500))
      }
    }

    return { success, failed }
  }

  private convertToDA(plainHtml: string): string {
    // Implementation follows the conversion algorithm above
    // Adapted for TypeScript/browser environment
    // ...
  }
}
```

**KV Token Caching:**

The Worker integration caches IMS tokens in KV to avoid token exchange on every request:

```typescript
async function getCachedToken(kv: KVNamespace, clientId: string, clientSecret: string): Promise<string> {
  const cacheKey = 'da_ims_token'
  const cached = await kv.get(cacheKey)
  if (cached) return cached

  const token = await exchangeIMSToken(clientId, clientSecret)

  // Cache for 23 hours (tokens are valid for 24 hours)
  await kv.put(cacheKey, token, { expirationTtl: 82800 })

  return token
}
```

---

### Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| IMS 401 | Invalid or expired credentials | Verify client ID/secret in Adobe Developer Console |
| IMS 400 | Missing or wrong scope | Ensure scope includes `aem.authoring` |
| DA 401 | Expired access token | Clear KV cache, re-exchange token |
| DA 403 | Insufficient permissions | Check org/repo access for the service account |
| DA 413 | Payload too large | Split content or remove inline images |
| DA 429 | Rate limited | Increase `rate_limit` delay, implement exponential backoff |
| Preview 404 | Page not yet indexed | Wait 5-10 seconds after upload, then retry preview |
| Conversion fails | Malformed input HTML | Validate HTML structure before conversion; ensure blocks have class names |

---

### Cross-References

- **generative-page-pipeline** -- Stage 5 uses this skill to persist generated pages to DA
- **conversational-page-builder** -- Page management tools invoke DA upload for content persistence
