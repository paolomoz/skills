---
name: highlight-reel
description: Creates a compact highlight reel video from multiple demo/screen recording videos using Remotion. Composites clips with section title cards, typewriter prompt captions, insight labels, transitions, music, and a branded poster frame. Use when user asks to create a "highlight reel", "demo video", "sizzle reel", "recap video", or "product video" from screen recordings.
---

# Highlight Reel Video Generator

Creates a polished, compact highlight reel from multiple screen recording videos using Remotion (React-based video framework). The output is a branded MP4 with section titles, typewriter prompt captions, insight labels, smooth transitions, background music, and an embedded thumbnail for Slack/social sharing.

## When to Use

- User has 2-6 screen recordings of product demos or use cases
- They want a compact 60-90 second highlight video
- The video should look polished with captions, transitions, and music

## Pipeline

```
Source videos + timestamps + prompts
  → Remotion project setup (if needed)
  → Composition config (clips, speeds, labels, prompts)
  → Component scaffold (poster, titles, captions, transitions)
  → Preview in Remotion Studio
  → Render to MP4 with embedded thumbnail
```

## Usage

```
/highlight-reel
/highlight-reel path/to/video1.mov path/to/video2.mov
```

## Required Input

Gather the following from the user before building:

### 1. Source Videos
- File paths to 2-6 screen recording videos
- Run `ffprobe` on each to get resolution, duration, and FPS

### 2. Use Case Descriptions
For each video, ask the user for:
- **Short title** (e.g., "Prompt to Website")
- **Subtitle** (e.g., "Full AEM EDS site from a single prompt")

### 3. Highlight Moments (Timestamps)
For each video, the user provides **2-6 key moments**:
- **Start/end timestamps** in the source video (e.g., `0:00-0:17`)
- **What's happening** — becomes the on-screen caption

### 4. Prompt Text
For clips where the user types a prompt/command, ask for the **exact prompt text**. This will be displayed as a typewriter caption overlay. If possible, ask the user for screenshots of the prompts.

### 5. Music
- Check if an existing `music.mp3` is available in `video/public/`
- Otherwise, ask the user to provide one or suggest royalty-free sources (Uppbeat, Artlist, Pixabay Music)

## Clip Configuration

Each clip needs:

| Field | Type | Description |
|-------|------|-------------|
| `startSec` | number | Start time in source video (seconds) |
| `endSec` | number | End time in source video (seconds) |
| `speed` | number | Playback rate (1.0 = normal, 2.0 = 2x fast) |
| `label` | string? | Insight text for result clips (white text, pill badge) |
| `prompt` | string? | User prompt text for typewriter caption (replaces label) |

**Speed guidelines:**
- Prompt clips (user typing): `1.0-1.5x` — slower so viewers can read
- Action clips (AI generating): `2.0-2.5x` — fast to show speed
- Result clips (finished output): `1.5-2.0x` — moderate pace

**Prompt text guidelines:**
- For long prompts (>150 chars), truncate to the key part
- Keep the most descriptive/impressive phrases
- End with a period

## Architecture

### Remotion Project Structure

```
video/
├── public/
│   ├── uc1.mov, uc2.mov, ...    # Source videos
│   └── music.mp3                 # Background music
├── src/
│   ├── Root.tsx                   # Registers all compositions
│   ├── HighlightReel.tsx          # Main composition (config-driven)
│   ├── components/
│   │   ├── Poster.tsx             # Static frame 0 (thumbnail/social)
│   │   ├── SectionTitle.tsx       # Animated section title card
│   │   ├── SectionBadge.tsx       # Persistent top-left section indicator
│   │   ├── InsightLabel.tsx       # Result caption (bold white pill)
│   │   ├── PromptCaption.tsx      # Typewriter prompt overlay
│   │   ├── VideoFrame.tsx         # Rounded corners + glow (no browser chrome)
│   │   ├── ClipCrossfade.tsx      # Dark dip between non-contiguous clips
│   │   └── SceneTransition.tsx    # Gradient wipe between sections
│   └── scenes/
│       ├── LogoReveal.tsx         # Animated intro
│       └── CTAFinale.tsx          # Closing CTA
├── package.json
└── tsconfig.json
```

### Key Design Decisions (Lessons Learned)

1. **No BrowserFrame wrapper** — Screen recordings already contain browser chrome. Wrapping in a fake browser creates a distracting browser-inside-browser effect. Use `VideoFrame` (rounded corners + gradient glow) instead.

2. **Poster component at frame 0** — The first frame MUST be visually rich (logo, title, particles). Frame 0 is used as the thumbnail by Slack, QuickTime, and social platforms. A black/empty first frame looks terrible when shared.

3. **Typewriter prompt captions** — When the user types a prompt in the recording, overlay a `PromptCaption` component that types out the text in sync. This ensures readability even at sped-up playback. Include a "PROMPT" label with sparkle icon and blinking cursor.

4. **Prompt hold time** — After a prompt finishes typing, hold the video for ~1.3 seconds (40 frames at 30fps) so viewers can read the full text. The video freezes on the last frame during this hold.

5. **Bold insight labels** — Use white text (not gradient) on a high-contrast dark backdrop with glow. Font size 28px, weight 700. Gradient text looks subtle at video scale and is hard to read.

6. **Persistent section badge** — A small badge in the top-left (e.g., "01 Prompt to Website") stays visible across all clips in a section, providing context when jumping between non-contiguous clips.

7. **Crossfade between clips** — When jumping between non-contiguous timestamps within the same video, add a brief (0.4s) dark dip crossfade. This signals a time skip without being jarring.

8. **Section title cards** — Show for ~1.9 seconds (56 frames). Shorter is too fast to read; longer wastes time in a compact reel.

9. **Source video FPS matters** — Screen recordings are often 60fps. The `startFrom` prop on `<OffthreadVideo>` uses the source video's frame rate, so convert seconds to frames using `SOURCE_FPS`, not the composition's FPS.

10. **Embedded thumbnail** — After rendering, use ffmpeg to embed the first frame as an MP4 thumbnail for maximum compatibility:
    ```bash
    ffmpeg -y -i output.mp4 -vframes 1 -q:v 2 /tmp/thumb.jpg
    ffmpeg -y -i output.mp4 -i /tmp/thumb.jpg -map 0 -map 1 -c copy -c:v:1 mjpeg -disposition:v:1 attached_pic output-final.mp4
    ```

## Timeline Structure

```
[Poster+LogoReveal 2.8s]
  → [Section 1 Title 1.9s] → [Clips...] → [Transition 0.8s]
  → [Section 2 Title 1.9s] → [Clips...] → [Transition 0.8s]
  → ...
  → [Section N Title 1.9s] → [Clips...]
  → [Transition 0.8s] → [CTA Finale 5s]
```

**Timing budget for 60-70s target:**
- Intro: ~3s
- Per section: title (2s) + clips (8-15s) = 10-17s
- Transitions: ~1s each
- CTA: ~5s
- With 4 sections: ~55-75s

If total exceeds target, increase playback speeds on non-prompt clips.

## Brand Tokens

```
COLORS = {
  dark: "#0A0A12",
  darkBlue: "#0D0F2B",
  cyan: "#8AD5FF",
  indigo: "#7A6AFD",
  fuchsia: "#EC69FF",
  white: "#FFFFFF",
}

GRADIENT = "linear-gradient(135deg, #8AD5FF 0%, #7A6AFD 50%, #EC69FF 100%)"
FONT = "SF Pro Display, -apple-system, sans-serif"
```

Adjust brand tokens to match the product being demoed.

## Composition Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `FPS` | 30 | Composition frame rate |
| `SOURCE_FPS` | 60 | Source video frame rate (check with ffprobe) |
| `TITLE_DURATION` | 56 frames | Section title card duration (~1.9s) |
| `TRANSITION_DURATION` | 24 frames | Wipe transition duration (~0.8s) |
| `TRANSITION_OVERLAP` | 20 frames | Overlap for seamless transitions |
| `CROSSFADE_DURATION` | 12 frames | Dark dip between clips (~0.4s) |
| `PROMPT_HOLD_FRAMES` | 40 frames | Extra hold after prompt typing (~1.3s) |

## Workflow

### Step 1: Gather Input

1. Ask user for source video paths
2. Run `ffprobe` on each to get dimensions, duration, FPS
3. Ask for use case titles, timestamps, prompts, and insight labels
4. Confirm music source

### Step 2: Setup Remotion Project

If no existing Remotion project:

```bash
mkdir -p video/public video/src/components video/src/scenes video/out
cd video && npm init -y
npm install remotion @remotion/cli @remotion/player react react-dom
npm install -D @types/react typescript
```

If existing project, reuse it.

### Step 3: Copy Source Videos

```bash
cp /path/to/video1.mov video/public/uc1.mov
cp /path/to/video2.mov video/public/uc2.mov
# etc.
```

### Step 4: Create Components

Create all components from `references/components.md` template, adapting brand tokens as needed:
- `Poster.tsx` — static poster for frame 0
- `SectionTitle.tsx` — animated section title card
- `SectionBadge.tsx` — persistent section indicator
- `InsightLabel.tsx` — bold result caption
- `PromptCaption.tsx` — typewriter prompt overlay
- `VideoFrame.tsx` — rounded video frame with glow
- `ClipCrossfade.tsx` — dark dip transition
- `SceneTransition.tsx` — gradient wipe
- `LogoReveal.tsx` — animated intro
- `CTAFinale.tsx` — closing screen

### Step 5: Build Composition

Create the main composition file with:
1. `SECTIONS` config array with all clips, prompts, labels, speeds
2. Timeline builder that computes frame positions automatically
3. Audio with fade in/out
4. Poster overlay at frame 0
5. Sequences for all sections, clips, badges, transitions

Register in `Root.tsx` and add render script to `package.json`.

### Step 6: Preview in Remotion Studio

```bash
cd video && npx remotion studio
```

- Open http://localhost:3001
- Select the composition
- Play through to verify:
  - Prompt captions are readable and timed correctly
  - Insight labels are visible
  - Transitions are smooth
  - Section badges show correct context
  - Music volume is balanced
  - Total duration is within target

### Step 7: Iterate

Common adjustments:
- **Too long?** Increase playback speeds on non-prompt clips, reduce `PROMPT_HOLD_FRAMES`
- **Prompts hard to read?** Decrease speed on prompt clips, increase hold time
- **Captions not visible?** Increase font size, strengthen backdrop
- **Jarring cuts?** Add or lengthen crossfades

### Step 8: Render Final MP4

```bash
cd video && npx remotion render CompositionId out/highlight-reel.mp4 --codec h264
```

### Step 9: Embed Thumbnail

Extract frame 0 and embed as MP4 thumbnail for Slack/social:

```bash
ffmpeg -y -i out/highlight-reel.mp4 -vframes 1 -q:v 2 /tmp/thumb.jpg
ffmpeg -y -i out/highlight-reel.mp4 -i /tmp/thumb.jpg \
  -map 0 -map 1 -c copy -c:v:1 mjpeg \
  -disposition:v:1 attached_pic out/highlight-reel-final.mp4
mv out/highlight-reel-final.mp4 out/highlight-reel.mp4
```

### Step 10: Open and Verify

```bash
open -a "QuickTime Player" out/highlight-reel.mp4
```

Verify: thumbnail shows in QuickTime/Finder, video plays smoothly, captions are readable.

## Dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| `remotion` | React-based video framework | `npm install remotion @remotion/cli` |
| `ffmpeg` | Thumbnail embedding, video probing | `brew install ffmpeg` |
| `ffprobe` | Source video analysis | Included with ffmpeg |

## References

- `references/components.md` — Full source code for all Remotion components
