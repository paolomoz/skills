# AI Image Generation

Generate high-quality site images using AI instead of stock photography. This guide covers three providers — choose based on budget, quality needs, and existing credentials.

## Provider Comparison

| Feature | Gemini 3 Pro | FLUX 2 Pro | Firefly |
|---------|-------------|------------|---------|
| Provider | Google | Black Forest Labs | Adobe |
| Best for | General site imagery, fast iteration | Highest visual quality, photorealism | Brand-safe, Adobe ecosystem integration |
| Output format | Base64 JPEG inline | Signed URL (10 min expiry) | Pre-signed S3 URL |
| Aspect control | Via prompt text | `width` + `height` params | `size` param with presets |
| Auth | API key header | API key header | OAuth client credentials |
| Rate limits | ~15 RPM | 24 concurrent tasks | Varies by plan |
| Cost | Pay-per-use (Gemini pricing) | Pay-per-image ($0.05-0.06) | Credits-based |
| Env var | `GOOGLE_API_KEY` | `BFL_API_KEY` | `FIREFLY_CLIENT_ID` + `FIREFLY_CLIENT_SECRET` |

## Workflow

1. **Define image inventory** — List all images needed (hero, card, column) with descriptions and aspect ratios
2. **Write style prefix** — A consistent prompt prefix that ensures brand cohesion across all images
3. **Generate images** — Run the generation script for your chosen provider (saves to `images/`)
4. **Deploy to public CDN** — Upload images to Cloudflare Pages (or similar) to get public URLs
5. **Update HTML references** — Replace placeholder URLs with public CDN URLs in draft HTML
6. **Upload to DA** — DA automatically ingests images from the public URLs

## Style Prefix

Every prompt should start with a consistent style description to ensure visual cohesion:

```
Professional pharmaceutical photography, clean modern aesthetic, soft lighting,
muted teal and warm amber tones, high-end medical/scientific visual.
No text, no logos, no watermarks.
```

Adapt the style prefix to your brand. Reference your brand voice document for imagery tier guidance.

## Image Categories

| Category | Typical Aspect | Use |
|----------|---------------|-----|
| Hero | 16:9 (1600×600) | Full-width banner at top of page |
| Card | 4:3 (750×560) | Cards block thumbnails |
| Column | 4:3 (800×600) | Columns block illustrations |

---

## Option 1: Gemini 3 Pro (Google)

### Setup

Add to `.env`:
```env
GOOGLE_API_KEY=your_api_key_here
```

Get a key at https://aistudio.google.com/apikey

### API Call

```bash
MODEL="gemini-3-pro-image-preview"
API_URL="https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent"

curl -s -X POST "$API_URL" \
  -H "x-goog-api-key: $GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "YOUR PROMPT HERE"}]}],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"]
    }
  }'
```

### Response Handling

The response contains base64-encoded image data inline:

```json
{
  "candidates": [{
    "content": {
      "parts": [
        {
          "inlineData": {
            "mimeType": "image/jpeg",
            "data": "BASE64_ENCODED_IMAGE_DATA..."
          }
        }
      ]
    }
  }]
}
```

Extract and save with Python:

```python
import json, base64, sys
data = json.load(sys.stdin)
for part in data['candidates'][0]['content']['parts']:
    if 'inlineData' in part:
        img = base64.b64decode(part['inlineData']['data'])
        with open('output.jpeg', 'wb') as f:
            f.write(img)
        break
```

### Aspect Ratio

Gemini doesn't have explicit width/height parameters for image generation. Control aspect ratio through the prompt text:
- Add "Aspect ratio 16:9." for wide/cinematic shots
- Add "Aspect ratio 4:3." for standard images
- Add "Aspect ratio 1:1." for square images

### Rate Limiting

Add 2-second delays between requests to avoid hitting rate limits:

```bash
sleep 2
```

### Script Template

```bash
#!/bin/bash
set -euo pipefail

GOOGLE_API_KEY=$(grep "GOOGLE_API_KEY" .env | sed 's/GOOGLE_API_KEY=//' | tr -d '"')
MODEL="gemini-3-pro-image-preview"
API_URL="https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent"
IMAGES_DIR="./images"
mkdir -p "$IMAGES_DIR"

STYLE="Your style prefix here. No text, no logos, no watermarks."

generate_image() {
  local filename="$1" prompt="$2"
  local output_path="$IMAGES_DIR/$filename"

  [ -f "$output_path" ] && echo "SKIP: $filename" && return 0
  echo "Generating: $filename ..."

  local response
  response=$(curl -s -X POST "$API_URL" \
    -H "x-goog-api-key: $GOOGLE_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"contents\": [{\"parts\": [{\"text\": \"$prompt\"}]}],
      \"generationConfig\": {\"responseModalities\": [\"TEXT\", \"IMAGE\"]}
    }")

  echo "$response" | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
if 'error' in data:
    print('ERROR: ' + data['error'].get('message', 'unknown'))
    sys.exit(1)
for part in data['candidates'][0]['content']['parts']:
    if 'inlineData' in part:
        img = base64.b64decode(part['inlineData']['data'])
        with open('$output_path', 'wb') as f:
            f.write(img)
        print(f'OK: {len(img)} bytes')
        break
else:
    print('ERROR: no image in response')
"
  sleep 2
}

# Generate images
generate_image "hero-example.jpeg" "$STYLE Wide cinematic shot of ... Aspect ratio 16:9."
generate_image "card-example.jpeg" "$STYLE Close-up of ... Aspect ratio 4:3."
```

---

## Option 2: FLUX 2 Pro (Black Forest Labs)

### Setup

Add to `.env`:
```env
BFL_API_KEY=your_api_key_here
```

Get a key at https://api.bfl.ml/

### API Call

FLUX uses an async pattern — submit a job, then poll for the result:

```bash
# Step 1: Submit generation request
RESPONSE=$(curl -s -X POST "https://api.bfl.ai/v1/flux-2-pro" \
  -H "x-key: $BFL_API_KEY" \
  -H "Content-Type: application/json" \
  -H "accept: application/json" \
  -d '{
    "prompt": "YOUR PROMPT HERE",
    "width": 1440,
    "height": 810
  }')

POLLING_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['polling_url'])")

# Step 2: Poll until ready
while true; do
  RESULT=$(curl -s -X GET "$POLLING_URL" \
    -H "x-key: $BFL_API_KEY" \
    -H "accept: application/json")
  STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  if [ "$STATUS" = "Ready" ]; then
    IMAGE_URL=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['sample'])")
    curl -s -o output.jpeg "$IMAGE_URL"
    break
  elif [ "$STATUS" = "Error" ] || [ "$STATUS" = "Failed" ]; then
    echo "Generation failed"
    break
  fi
  sleep 2
done
```

### Aspect Ratio

FLUX uses explicit `width` and `height` parameters:

| Aspect | Width | Height |
|--------|-------|--------|
| 16:9 | 1440 | 810 |
| 4:3 | 1024 | 768 |
| 1:1 | 1024 | 1024 |

### Key Details

- Signed image URLs expire after **10 minutes** — download immediately
- Max **24 concurrent tasks** (HTTP 429 if exceeded)
- Regional endpoints: `api.bfl.ai`, `api.eu.bfl.ai`, `api.us.bfl.ai`

### Script Template

```bash
#!/bin/bash
set -euo pipefail

BFL_API_KEY=$(grep "BFL_API_KEY" .env | sed 's/BFL_API_KEY=//' | tr -d '"')
IMAGES_DIR="./images"
mkdir -p "$IMAGES_DIR"

STYLE="Your style prefix here. No text, no logos, no watermarks."

generate_image() {
  local filename="$1" prompt="$2" width="${3:-1024}" height="${4:-768}"
  local output_path="$IMAGES_DIR/$filename"

  [ -f "$output_path" ] && echo "SKIP: $filename" && return 0
  echo "Generating: $filename ..."

  local response polling_url
  response=$(curl -s -X POST "https://api.bfl.ai/v1/flux-2-pro" \
    -H "x-key: $BFL_API_KEY" \
    -H "Content-Type: application/json" \
    -H "accept: application/json" \
    -d "{\"prompt\": \"$prompt\", \"width\": $width, \"height\": $height}")

  polling_url=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['polling_url'])")

  while true; do
    local result status
    result=$(curl -s -X GET "$polling_url" -H "x-key: $BFL_API_KEY" -H "accept: application/json")
    status=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
    if [ "$status" = "Ready" ]; then
      local image_url
      image_url=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['sample'])")
      curl -s -o "$output_path" "$image_url"
      echo "OK: $filename ($(wc -c < "$output_path") bytes)"
      return 0
    elif [ "$status" = "Error" ] || [ "$status" = "Failed" ]; then
      echo "FAIL: $filename"
      return 1
    fi
    sleep 2
  done
}

# Generate images — FLUX uses explicit dimensions
generate_image "hero-example.jpeg" "$STYLE Wide cinematic shot of ..." 1440 810
generate_image "card-example.jpeg" "$STYLE Close-up of ..." 1024 768
```

---

## Option 3: Adobe Firefly

### Setup

Add to `.env`:
```env
FIREFLY_CLIENT_ID=your_client_id
FIREFLY_CLIENT_SECRET=your_client_secret
```

Get credentials at https://developer.adobe.com/firefly-services/docs/guides/get-started/

### Authentication

Firefly uses OAuth client credentials — exchange for an access token first:

```bash
ACCESS_TOKEN=$(curl -s -X POST "https://ims-na1.adobelogin.com/ims/token/v3" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=$FIREFLY_CLIENT_ID&client_secret=$FIREFLY_CLIENT_SECRET&scope=openid,AdobeID,firefly_api,ff_apis" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### API Call

```bash
curl -s -X POST "https://firefly-api.adobe.io/v3/images/generate" \
  -H "X-Api-Key: $FIREFLY_CLIENT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "YOUR PROMPT HERE",
    "n": 1,
    "size": {"width": 2048, "height": 1152}
  }'
```

### Response Handling

Firefly returns pre-signed S3 URLs for downloading:

```json
{
  "size": {"width": 2048, "height": 1152},
  "outputs": [{
    "seed": 123456,
    "image": {
      "url": "https://pre-signed-s3-url..."
    }
  }]
}
```

Download with:
```bash
IMAGE_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['outputs'][0]['image']['url'])")
curl -s -o output.jpeg "$IMAGE_URL"
```

### Size Presets

| Aspect | Width | Height |
|--------|-------|--------|
| 16:9 | 2048 | 1152 |
| 4:3 | 1408 | 1024 |
| 1:1 | 1024 | 1024 |

### Script Template

```bash
#!/bin/bash
set -euo pipefail

FIREFLY_CLIENT_ID=$(grep "FIREFLY_CLIENT_ID" .env | sed 's/FIREFLY_CLIENT_ID=//' | tr -d '"')
FIREFLY_CLIENT_SECRET=$(grep "FIREFLY_CLIENT_SECRET" .env | sed 's/FIREFLY_CLIENT_SECRET=//' | tr -d '"')
IMAGES_DIR="./images"
mkdir -p "$IMAGES_DIR"

# Get access token
ACCESS_TOKEN=$(curl -s -X POST "https://ims-na1.adobelogin.com/ims/token/v3" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=$FIREFLY_CLIENT_ID&client_secret=$FIREFLY_CLIENT_SECRET&scope=openid,AdobeID,firefly_api,ff_apis" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

STYLE="Your style prefix here. No text, no logos, no watermarks."

generate_image() {
  local filename="$1" prompt="$2" width="${3:-1408}" height="${4:-1024}"
  local output_path="$IMAGES_DIR/$filename"

  [ -f "$output_path" ] && echo "SKIP: $filename" && return 0
  echo "Generating: $filename ..."

  local response image_url
  response=$(curl -s -X POST "https://firefly-api.adobe.io/v3/images/generate" \
    -H "X-Api-Key: $FIREFLY_CLIENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$prompt\", \"n\": 1, \"size\": {\"width\": $width, \"height\": $height}}")

  image_url=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['outputs'][0]['image']['url'])")
  curl -s -o "$output_path" "$image_url"
  echo "OK: $filename ($(wc -c < "$output_path") bytes)"
}

# Generate images
generate_image "hero-example.jpeg" "$STYLE Wide cinematic shot of ..." 2048 1152
generate_image "card-example.jpeg" "$STYLE Close-up of ..." 1408 1024
```

---

## After Generation

### 1. Deploy Images to a Public CDN

DA ingests images from public URLs. Deploy generated images to Cloudflare Pages:

```bash
# One-time: create Pages project
npx wrangler pages project create my-site-images --production-branch main

# Deploy all images
npx wrangler pages deploy ./images --project-name my-site-images
# → https://my-site-images.pages.dev/hero-example.jpeg
```

Verify accessibility:
```bash
curl -s -o /dev/null -w "%{http_code}" "https://my-site-images.pages.dev/hero-example.jpeg"
# → 200
```

### 2. Update HTML References

Replace placeholder URLs with public Cloudflare URLs in draft HTML:

```bash
# Replace all at once
CDN_URL="https://my-site-images.pages.dev"
find drafts -name '*.plain.html' -exec sed -i '' "s|/images/|${CDN_URL}/|g" {} \;
```

Or use a per-file sed script for specific URL-to-URL replacements:
```bash
sed -i '' \
  -e 's|https://images.unsplash.com/photo-OLD_URL|https://my-site-images.pages.dev/hero-example.jpeg|g' \
  "$DRAFTS_DIR/page.plain.html"
```

### 3. Verify No Placeholders Remain

```bash
grep -rn "unsplash.com\|placehold.co" drafts/ --include="*.html" || echo "All clean"
```

### 4. Upload to DA

Upload the updated drafts — DA will automatically ingest the images from the public URLs:

```bash
./tools/upload-to-da.sh    # Upload all drafts
./tools/preview-all.sh     # Refresh CDN preview
```

After preview, images are served by the AEM media CDN (optimized and cached by aem.live).

## Prompt Writing Tips

1. **Be specific about composition** — "close-up", "wide cinematic shot", "macro photograph"
2. **Specify lighting** — "soft natural light", "blue ambient lighting", "warm studio light"
3. **Include mood** — "conveying trust and safety", "sense of scientific discovery"
4. **Mention what to exclude** — "No text, no logos, no watermarks" in every prompt
5. **State aspect ratio** — Especially for Gemini which uses prompt-based aspect control
6. **Use domain vocabulary** — "pharmaceutical", "clinical", "molecular" for medical sites
7. **Reference photography style** — "editorial photography", "product photography", "lifestyle"
