# Document Authoring (DA) Integration

## Overview

Document Authoring (DA) is Adobe's browser-based CMS for Edge Delivery Services, accessible at `da.live`. Content authored in DA is served via the aem.live CDN to your EDS site.

For automated workflows (CI/CD, bulk content upload, AI-driven content creation), DA supports programmatic access via service tokens authenticated through Adobe IMS (Identity Management System).

## Architecture

```
Local drafts (.plain.html)
  → plain-to-da.py (convert to DA table format)
  → upload-to-da.sh (authenticate + POST to DA API)
  → preview-all.sh (trigger CDN preview refresh)
  → Content available at https://main--{repo}--{org}.aem.page/
```

## Prerequisites

### 1. DA Service Credentials

You need an Adobe IMS service account with DA access. The credentials consist of:

| Variable | Description |
|----------|-------------|
| `DA_CLIENT_ID` | IMS client/application ID (e.g., `my-project-da-prod`) |
| `DA_CLIENT_SECRET` | IMS client secret |
| `DA_SERVICE_TOKEN` | Long-lived authorization code (JWT) for service-to-service auth |
| `DA_ORG` | Your GitHub org/user that owns the DA content |
| `DA_REPO` | Your GitHub repo name |

### 2. .env File

Store credentials in `.env` at the project root (add to `.gitignore`):

```env
DA_ORG=my-org
DA_REPO=my-site
DA_CLIENT_ID=my-project-da-prod
DA_CLIENT_SECRET="your-client-secret"
DA_SERVICE_TOKEN="eyJhbGciOiJSUzI1NiIs..."
```

The service token is a JWT issued by Adobe IMS. It's exchanged for a short-lived access token at runtime.

### 3. .gitignore and .hlxignore

Ensure credentials and tools are not exposed:

```gitignore
# .gitignore
.env
tools/
```

```
# .hlxignore (prevents serving on aem.live)
.env
tools/
drafts/
```

## Authentication Flow

DA uses a two-step OAuth flow with service credentials:

### Step 1: Exchange Service Token for Access Token

```bash
ACCESS_TOKEN=$(curl -s -X POST "https://ims-na1.adobelogin.com/ims/token/v3" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&client_id=$DA_CLIENT_ID&client_secret=$DA_CLIENT_SECRET&code=$DA_SERVICE_TOKEN" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

The IMS endpoint returns a JSON response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86399
}
```

### Step 2: Use Access Token for DA API Calls

```bash
curl -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "data=@file.html;type=text/html" \
  "https://admin.da.live/source/$DA_ORG/$DA_REPO/path/to/page.html"
```

## DA API Endpoints

### Upload/Update Content

```
POST https://admin.da.live/source/{org}/{repo}/{path}.html
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

Form field: data=@file.html;type=text/html
```

Returns: `200` (updated), `201` (created), or `204` (no content change)

### Preview Content (Trigger CDN Refresh)

After uploading to DA, trigger a preview to make content available on `.aem.page`:

```
POST https://admin.hlx.page/preview/{org}/{repo}/main/{path}
Authorization: Bearer {access_token}
```

This tells the Edge Delivery CDN to fetch fresh content from DA.

### Publish Content (Go Live)

To publish content to `.aem.live` (production):

```
POST https://admin.hlx.page/live/{org}/{repo}/main/{path}
Authorization: Bearer {access_token}
```

## Content Format Conversion

### The Problem

EDS `.plain.html` files use `<div>` structures for blocks:
```html
<div class="hero">
  <div>
    <div><picture>...</picture></div>
    <div><h2>Title</h2></div>
  </div>
</div>
```

DA expects `<table>` structures:
```html
<table>
  <tr><th colspan="2">Hero</th></tr>
  <tr>
    <td><picture>...</picture></td>
    <td><h2>Title</h2></td>
  </tr>
</table>
```

### Conversion Script: `plain-to-da.py`

This Python script handles the conversion:

```python
#!/usr/bin/env python3
"""Convert .plain.html (EDS format) to DA authoring format (table-based HTML)."""

import sys
import re


def convert_plain_to_da(html_content, title=""):
    """Convert .plain.html content to DA document format."""
    sections = re.split(r'<hr\s*/?>', html_content)
    da_sections = []

    for section in sections:
        section = section.strip()
        if not section:
            continue
        converted = convert_section(section)
        if converted.strip():
            da_sections.append(f"<div>\n{converted}\n</div>")

    main_content = "\n".join(da_sections)

    return f"""<html>
<head><title>{title}</title></head>
<body>
<header></header>
<main>
{main_content}
</main>
<footer></footer>
</body>
</html>"""


def convert_section(section_html):
    """Convert a single section from plain to DA format."""
    section_html = section_html.strip()
    # Remove outer <div> wrapper if present
    if section_html.startswith('<div>') and section_html.endswith('</div>'):
        inner = remove_outer_div(section_html)
        if inner is not None:
            section_html = inner
    return convert_blocks_to_tables(section_html)


def remove_outer_div(html):
    """Remove the outermost <div>...</div> wrapper, respecting nesting."""
    html = html.strip()
    if not html.startswith('<div>'):
        return None
    depth = 0
    i = 0
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i = html.index('>', i) + 1
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                if i + 6 >= len(html) or html[i+6:].strip() == '':
                    return html[html.index('>', 0) + 1:i].strip()
                else:
                    return None
            i += 6
        else:
            i += 1
    return None


def convert_blocks_to_tables(html):
    """Convert <div class="blockname"> structures to <table> structures."""
    result = []
    pos = 0
    while pos < len(html):
        match = re.search(r'<div\s+class="([^"]+)">', html[pos:])
        if not match:
            result.append(html[pos:])
            break
        result.append(html[pos:pos + match.start()])
        block_name = match.group(1)
        block_start = pos + match.start()
        block_inner_start = block_start + len(match.group(0))
        block_end = find_closing_div(html, block_start)
        if block_end is None:
            result.append(html[pos + match.start():])
            break
        block_inner = html[block_inner_start:block_end]
        table = convert_block_to_table(block_name, block_inner)
        result.append(table)
        pos = block_end + 6
    return ''.join(result)


def find_closing_div(html, start):
    """Find the position of the closing </div> for the div starting at start."""
    depth = 0
    i = start
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i = html.index('>', i) + 1
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return i
            i += 6
        else:
            i += 1
    return None


def convert_block_to_table(block_name, inner_html):
    """Convert a block's inner HTML from div rows/cells to table rows/cells."""
    parts = block_name.split()
    base_name = parts[0]
    variants = parts[1:] if len(parts) > 1 else []
    display_name = base_name.replace('-', ' ').title()
    if variants:
        variant_str = ', '.join(v.replace('-', ' ') for v in variants)
        display_name = f'{display_name} ({variant_str})'
    rows = extract_direct_child_divs(inner_html)
    table_rows = []
    for row_html in rows:
        cells = extract_direct_child_divs(row_html)
        if cells:
            tds = ''.join(f'<td>{cell.strip()}</td>' for cell in cells)
        else:
            tds = f'<td>{row_html.strip()}</td>'
        table_rows.append(f'<tr>{tds}</tr>')
    first_row_cells = extract_direct_child_divs(rows[0]) if rows else []
    colspan = max(len(first_row_cells), 1)
    header = f'<tr><th colspan="{colspan}">{display_name}</th></tr>'
    return f'<table>\n{header}\n{"".join(table_rows)}\n</table>'


def extract_direct_child_divs(html):
    """Extract content of direct child <div> elements."""
    html = html.strip()
    children = []
    pos = 0
    while pos < len(html):
        match = re.search(r'<div[^>]*>', html[pos:])
        if not match:
            break
        div_start = pos + match.start()
        div_inner_start = div_start + len(match.group(0))
        div_end = find_closing_div(html, div_start)
        if div_end is None:
            break
        children.append(html[div_inner_start:div_end])
        pos = div_end + 6
    return children


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 plain-to-da.py input.plain.html [title]", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        content = f.read()
    title = sys.argv[2] if len(sys.argv) > 2 else ""
    print(convert_plain_to_da(content, title))
```

Save this as `tools/plain-to-da.py` in your project.

## Upload Script: `upload-to-da.sh`

This shell script authenticates and uploads all draft content to DA:

```bash
#!/bin/bash
# Upload draft HTML files to DA (Document Authoring)
# Usage: ./tools/upload-to-da.sh [specific-file]
# If no file specified, uploads all .plain.html files in drafts/

set -euo pipefail

DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true; shift ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DRAFTS_DIR="$PROJECT_DIR/drafts"

# Read env vars from .env file
DA_CLIENT_ID=$(grep "DA_CLIENT_ID" "$PROJECT_DIR/.env" | sed 's/DA_CLIENT_ID=//' | tr -d '"')
DA_CLIENT_SECRET=$(grep "DA_CLIENT_SECRET" "$PROJECT_DIR/.env" | sed 's/DA_CLIENT_SECRET=//' | tr -d '"')
DA_SERVICE_TOKEN=$(grep "DA_SERVICE_TOKEN" "$PROJECT_DIR/.env" | sed 's/DA_SERVICE_TOKEN=//' | tr -d '"')
DA_ORG=$(grep "DA_ORG" "$PROJECT_DIR/.env" | sed 's/DA_ORG=//' | tr -d '"')
DA_REPO=$(grep "DA_REPO" "$PROJECT_DIR/.env" | sed 's/DA_REPO=//' | tr -d '"')

DA_API="https://admin.da.live/source/$DA_ORG/$DA_REPO"

ACCESS_TOKEN=""
if [ "$DRY_RUN" = false ]; then
  echo "Authenticating with Adobe IMS..."
  ACCESS_TOKEN=$(curl -s -X POST "https://ims-na1.adobelogin.com/ims/token/v3" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=authorization_code&client_id=$DA_CLIENT_ID&client_secret=$DA_CLIENT_SECRET&code=$DA_SERVICE_TOKEN" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

  if [ -z "$ACCESS_TOKEN" ]; then
    echo "ERROR: Failed to obtain IMS access token"
    exit 1
  fi
  echo "Authenticated."
  echo ""
fi

upload_file() {
  local plain_file="$1"
  local progress="${2:-}"
  local rel_path="${plain_file#$DRAFTS_DIR/}"
  local da_path="${rel_path%.plain.html}.html"
  local prefix=""
  [ -n "$progress" ] && prefix="[$progress] "

  # Convert plain HTML to DA format
  local tmp_file
  tmp_file=$(mktemp /tmp/da-upload-XXXXXX.html)
  python3 "$SCRIPT_DIR/plain-to-da.py" "$plain_file" > "$tmp_file" 2>/dev/null

  if [ ! -s "$tmp_file" ]; then
    echo "${prefix}SKIP: $rel_path (empty conversion)"
    rm -f "$tmp_file"
    return 1
  fi

  if [ "$DRY_RUN" = true ]; then
    echo "${prefix} DRY: $da_path ($(wc -c < "$tmp_file" | tr -d ' ') bytes)"
    rm -f "$tmp_file"
    return 0
  fi

  local url="$DA_API/$da_path"
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -F "data=@$tmp_file;type=text/html" \
    "$url")

  rm -f "$tmp_file"

  if [ "$status" = "200" ] || [ "$status" = "201" ] || [ "$status" = "204" ]; then
    echo "${prefix}  OK: $da_path ($status)"
    return 0
  else
    echo "${prefix}FAIL: $da_path (HTTP $status)"
    return 1
  fi
}

if [ "$DRY_RUN" = true ]; then
  echo "DRY RUN — no uploads will be made"
fi
echo "Uploading to DA: $DA_API"
echo "---"

SUCCESS=0
FAIL=0

if [ -n "${1:-}" ] && [ "$1" != "--dry-run" ]; then
  upload_file "$1" && SUCCESS=$((SUCCESS+1)) || FAIL=$((FAIL+1))
else
  TOTAL=$(find "$DRAFTS_DIR" -name "*.plain.html" | wc -l | tr -d ' ')
  COUNT=0
  while IFS= read -r file; do
    COUNT=$((COUNT+1))
    upload_file "$file" "$COUNT/$TOTAL" && SUCCESS=$((SUCCESS+1)) || FAIL=$((FAIL+1))
    if [ "$DRY_RUN" = false ]; then
      sleep 0.5
    fi
  done < <(find "$DRAFTS_DIR" -name "*.plain.html" | sort)
fi

echo "---"
echo "Done: $SUCCESS uploaded, $FAIL failed out of ${TOTAL:-1}"
```

Save as `tools/upload-to-da.sh` and make executable: `chmod +x tools/upload-to-da.sh`

## Preview Script: `preview-all.sh`

After uploading content, trigger the CDN to refresh:

```bash
#!/bin/bash
# Preview all uploaded pages on AEM Edge Delivery
# Triggers the preview CDN to pick up content from DA

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DRAFTS_DIR="$PROJECT_DIR/drafts"
DA_ORG=$(grep "^DA_ORG" "$PROJECT_DIR/.env" | sed 's/DA_ORG=//' | tr -d '"')
DA_REPO=$(grep "^DA_REPO" "$PROJECT_DIR/.env" | sed 's/DA_REPO=//' | tr -d '"')
ADMIN_API="https://admin.hlx.page/preview/$DA_ORG/$DA_REPO/main"

# Authenticate
DA_CLIENT_ID=$(grep "DA_CLIENT_ID" "$PROJECT_DIR/.env" | sed 's/DA_CLIENT_ID=//' | tr -d '"')
DA_CLIENT_SECRET=$(grep "DA_CLIENT_SECRET" "$PROJECT_DIR/.env" | sed 's/DA_CLIENT_SECRET=//' | tr -d '"')
DA_SERVICE_TOKEN=$(grep "DA_SERVICE_TOKEN" "$PROJECT_DIR/.env" | sed 's/DA_SERVICE_TOKEN=//' | tr -d '"')

echo "Authenticating with Adobe IMS..."
ACCESS_TOKEN=$(curl -s -X POST "https://ims-na1.adobelogin.com/ims/token/v3" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&client_id=$DA_CLIENT_ID&client_secret=$DA_CLIENT_SECRET&code=$DA_SERVICE_TOKEN" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$ACCESS_TOKEN" ]; then
  echo "ERROR: Failed to obtain IMS access token"
  exit 1
fi
echo "Authenticated."
echo ""

TOTAL=$(find "$DRAFTS_DIR" -name "*.plain.html" | wc -l | tr -d ' ')
COUNT=0
SUCCESS=0
FAIL=0

echo "Previewing $TOTAL pages..."
echo "---"

while IFS= read -r file; do
  COUNT=$((COUNT+1))
  rel_path="${file#$DRAFTS_DIR/}"
  page_path="${rel_path%.plain.html}"

  status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    "$ADMIN_API/$page_path")

  if [ "$status" = "200" ] || [ "$status" = "201" ] || [ "$status" = "204" ]; then
    echo "[$COUNT/$TOTAL]   OK: /$page_path ($status)"
    SUCCESS=$((SUCCESS+1))
  else
    echo "[$COUNT/$TOTAL] FAIL: /$page_path (HTTP $status)"
    FAIL=$((FAIL+1))
  fi

  sleep 0.5
done < <(find "$DRAFTS_DIR" -name "*.plain.html" | sort)

echo "---"
echo "Done: $SUCCESS previewed, $FAIL failed out of $TOTAL"
```

Save as `tools/preview-all.sh` and make executable: `chmod +x tools/preview-all.sh`

## Complete Workflow

### Initial Setup

```bash
# 1. Create tools directory
mkdir -p tools

# 2. Create .env with your DA credentials
cat > .env << 'EOF'
DA_ORG=my-org
DA_REPO=my-site
DA_CLIENT_ID=my-project-da-prod
DA_CLIENT_SECRET="your-secret-here"
DA_SERVICE_TOKEN="your-jwt-token-here"
EOF

# 3. Add to .gitignore
echo ".env" >> .gitignore

# 4. Copy the scripts (plain-to-da.py, upload-to-da.sh, preview-all.sh)
# 5. Make shell scripts executable
chmod +x tools/upload-to-da.sh tools/preview-all.sh
```

### Content Workflow

```bash
# 1. Create/edit draft content locally
#    (files in drafts/*.plain.html)

# 2. Test locally with dev server
aem up --no-open --html-folder drafts

# 3. Upload all drafts to DA
./tools/upload-to-da.sh

# 4. Trigger CDN preview refresh
./tools/preview-all.sh

# 5. Verify on preview URL
open "https://main--my-site--my-org.aem.page/"
```

### Upload a Single File

```bash
./tools/upload-to-da.sh drafts/products/aspirin.plain.html
```

### Dry Run (No Uploads)

```bash
./tools/upload-to-da.sh --dry-run
```

## Troubleshooting

### Authentication Fails

```
ERROR: Failed to obtain IMS access token
```

- **Expired service token**: Service tokens have a limited lifetime. Request a new one from your Adobe admin.
- **Wrong client ID/secret**: Verify credentials in `.env` match the IMS service account.
- **Network issues**: Ensure `ims-na1.adobelogin.com` is reachable.

Debug the IMS response:
```bash
curl -v -X POST "https://ims-na1.adobelogin.com/ims/token/v3" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&client_id=$DA_CLIENT_ID&client_secret=$DA_CLIENT_SECRET&code=$DA_SERVICE_TOKEN"
```

### Upload Returns 403

- The service account may not have write access to the DA org/repo.
- Verify `DA_ORG` and `DA_REPO` match the DA content path.

### Preview Returns 404

- Content may not have been uploaded yet (upload before preview).
- The page path may not match — DA paths don't include `.plain.html`.

### Content Not Appearing on aem.page

After uploading + previewing, allow 30-60 seconds for CDN propagation. If still not visible:

```bash
# Force a cache bust
curl -X POST "https://admin.hlx.page/preview/$DA_ORG/$DA_REPO/main/path/to/page" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Security Notes

- **Never commit `.env`** — it contains secrets that grant write access to your content
- **Service tokens are powerful** — they bypass interactive authentication, treat them like passwords
- **Rotate tokens periodically** — especially if team members change
- **Scope permissions minimally** — request only `system,aem.frontend.all` scope
- **Use `.hlxignore`** to prevent tools directory from being served on aem.live
