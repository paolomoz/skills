---
name: infographic-video
description: Generates a short video recap from a meeting summary. Splits content into sections, creates infographics, generates two-host dialogue audio via ElevenLabs Text-to-Dialogue API, and assembles into MP4 with background music. Use when user asks to create a "meeting video", "video recap", "video summary", or "meeting recap video".
---

# Meeting Video Generator

Transforms a meeting summary (Markdown) into a short (~5 min) video with infographic visuals, two-host podcast-style dialogue audio, and background music.

## Pipeline

```
Meeting Summary (.md)
  → Section Splitting (6 sections)
  → Infographic Prompt Crafting (Sumi style+layout references → Claude)
  → Infographic Generation (Gemini 3 Pro Image Preview)
  → Dialogue Scripts (two-host, fast-paced podcast tone, with bridge lines)
  → Audio Generation (ElevenLabs Text-to-Dialogue API, 2 voices, 1.0s lead-in silence, 1.2x speed)
  → Video Assembly (moviepy + background music → MP4)
```

## Script Directory

**Agent Execution**:
1. `SKILL_DIR` = this SKILL.md file's directory
2. Scripts in `${SKILL_DIR}/scripts/`

## Usage

```
/infographic-video path/to/meeting-summary.md
/infographic-video path/to/summary.md --sections 6 --voices Alex=ID1,Jordan=ID2
/infographic-video path/to/summary.md --output video/output/
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--sections <n>` | Number of content sections | `6` |
| `--output <dir>` | Output directory for all artifacts | `meeting/` |
| `--voices <a,b>` | Voice mapping: `Name=ID,Name=ID` | Archer, Alexandra |
| `--host-names <a,b>` | Display names for the two hosts | `Alex, Jordan` |
| `--aspect` | Infographic aspect ratio | `landscape` (16:9) |
| `--lang` | Language for all text content | `en` |
| `--duration` | Target video duration in seconds | `300` (5 min) |

## Dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| `ffmpeg` | Audio probing, video encoding | `brew install ffmpeg` |
| `moviepy` | Video composition, crossfades, music mixing | `pip3 install moviepy` |
| `requests` | ElevenLabs API calls | `pip3 install requests` |
| `python-dotenv` | Load API keys from `.env` | `pip3 install python-dotenv` |
| `Pillow` | Title/outro card generation | `pip3 install Pillow` |
| `google-genai` | Gemini 3 Pro Image Preview for infographics | `pip3 install google-genai` |
| `anthropic` | Claude API for Sumi prompt crafting | `pip3 install anthropic` |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ELEVENLABS_API_KEY` | ElevenLabs API key (required for audio) |
| `GOOGLE_API_KEY` | Google AI API key (required for Gemini image generation) |
| `ANTHROPIC_API_KEY` | Anthropic API key (required for Sumi prompt crafting) |

## Default Voices

| Host | Voice | Voice ID | Character |
|------|-------|----------|-----------|
| Alex | Archer | `L0Dsvb3SLTyegXwtm47J` | Conversational, warm male guide |
| Jordan | Alexandra | `kdmDKE6EkgrWrrykO9Qt` | Realistic, chatty female reactor |

Fallback voices if defaults unavailable: Roger (`CwhRBWXzGAHq8TQ4Fs17`), Laura (`FGY2WhTYpPnrIDTdsKH5`).

Run `scripts/list_voices.py` to discover available ElevenLabs voices.

## Output Structure

```
{output-dir}/
├── sections/
│   ├── 01-{slug}/source.md               # Section content
│   ├── 02-{slug}/source.md
│   └── ...
├── infographic/
│   ├── 01-{slug}.png                     # Generated infographics
│   └── ...
├── audio/
│   ├── 01-{slug}.mp3                     # Generated dialogue audio
│   └── bgm.mp3                           # Background music (optional)
├── dialogue.json                          # Dialogue scripts (agent-generated)
├── video-config.json                      # Title/outro card config
└── output/
    └── meeting-recap-final.mp4           # Final video
```

## Workflow

### Step 1: Setup & Verify

1. Verify dependencies:
   ```bash
   ffmpeg -version
   python3 -c "import moviepy; import PIL; import requests; import dotenv"
   ```
2. Verify API keys in `.env`:
   ```bash
   grep ELEVENLABS_API_KEY .env
   grep GOOGLE_API_KEY .env
   grep ANTHROPIC_API_KEY .env
   ```
3. Create output directory structure

### Step 2: Analyze & Split Content

Read the source meeting summary and split into sections.

**Section Planning Guidelines:**
- Target 6 sections for a ~5 minute video
- Each section: ~130-160 words of dialogue → ~45-60s of audio
- Structure: opening context → core concepts → methodology → measurement → future → close
- Each section gets a `source.md` with extracted content from the summary

See `references/section-planning.md` for detailed guidelines.

### Step 3: Choose Layout × Style per Section

**Pick ONE style for all sections** for visual consistency. Vary **layouts only** across sections to match content type.

**Recommended layouts by content type:**

| Content Type | Layout |
|--------------|--------|
| Overview / Intro | `bento-grid` |
| Journey / Process | `winding-roadmap` |
| Core Concept / Mission | `hub-spoke` |
| Framework / Model | `linear-progression` |
| Metrics / KPIs | `dashboard` |
| Future / Technology | `circular-flow` |

**Good style choices** (pick one and use for all 6 sections): `bold-graphic`, `corporate-memphis`, `technical-schematic`, `storybook-watercolor`.

All infographics: **16:9 landscape** (1920×1080 or 2K equivalent).

### Step 4: Generate Infographics

For each section, generate an infographic using Sumi prompt crafting + Gemini 3 Pro:

```bash
python3 ${SKILL_DIR}/scripts/generate_image.py \
    {output}/sections/{NN}-{slug}/source.md \
    {output}/infographic/{NN}-{slug}.png \
    --layout {layout-id} --style {style-id}
```

The script:
1. Loads the Sumi style + layout reference markdown files (57 styles × 20 layouts available)
2. Sends them to Claude alongside the section content to craft a rich visual prompt
3. Passes the crafted prompt to Gemini 3 Pro Image Preview for generation
4. Saves the prompt to `{NN}-{slug}.prompt.md` for debugging

**Use the same `--style` for all sections** (vary `--layout` only).

Generate sequentially (one at a time) to ensure quality. Verify output exists and is 16:9 aspect ratio.

Sumi references are loaded from `/Users/paolo/playground/sumi/backend/sumi/references/data/` (override with `--sumi-dir`).

### Step 5: Write Dialogue Scripts

Write casual two-host dialogue for each section and save as `{output}/dialogue.json`:

```json
{
  "sections": [
    {
      "name": "01-intro",
      "dialogue": [
        {"speaker": "Alex", "text": "Opening line..."},
        {"speaker": "Jordan", "text": "Reaction..."},
        {"speaker": "Alex", "text": "Bridge to next section..."}
      ]
    }
  ]
}
```

**Dialogue Format:**
- Two hosts with contrasting roles:
  - **Host A** (Alex): Warm narrator/guide — explains, sets context, delivers key facts
  - **Host B** (Jordan): Energetic reactor/questioner — asks questions, reacts, highlights takeaways
- Fast-paced podcast-recap tone — punchy, high-density, no filler
- ~100-130 words per section targeting ~35-45s audio each (before 1.2x speed-up)
- Alternate turns between hosts (5-9 turns per section)
- Use natural emotional cues through word choice (not bracketed directives)
- **Bridge lines**: Every section except the last must end with a bridge line from Alex previewing the next topic

See `references/dialogue-format.md` for detailed guidelines, bridging examples, and voice configuration.

### Step 6: Generate Audio

Create `{output}/video-config.json` with title/outro card configuration:

```json
{
  "title": {
    "line1": "Meeting Title",
    "line2": "Meeting Recap",
    "line3": "Date"
  },
  "outro": {
    "quote": "A memorable closing quote from the meeting.",
    "attribution": "Speaker Name"
  }
}
```

Then run the dialogue generation script:

```bash
python3 ${SKILL_DIR}/scripts/generate_dialogue.py {output}/dialogue.json {output}/audio
```

**How it works:**
1. Reads dialogue from the JSON file
2. For each section, sends all dialogue turns to the ElevenLabs Text-to-Dialogue API in a single request
3. The API returns one audio file per section with natural turn-taking and pacing
4. Prepends 1.0s of silence via ffmpeg so dialogue doesn't start abruptly on crossfade transitions
5. Speeds up audio by 20% (atempo=1.2) for faster-paced delivery

**IMPORTANT ffmpeg note:** When generating silence with `-f lavfi`, the `-t` duration flag must come BEFORE `-i` to bound the source. Placing it after creates an unbounded silence source.

**Verification:**
- Each MP3 should be 30-50s duration (after 1.2x speed-up)
- Total audio should be under 6 minutes
- Both voices should be clearly distinguishable

### Step 7: Background Music (Optional)

Place a background music MP3 at `{output}/audio/bgm.mp3`. The assembler will automatically:
- Play music at full volume during the title card (3s)
- Reduce to 15% volume during dialogue sections
- Return to full volume during the outro card
- Fade out over the last 1.5s

If `bgm.mp3` is not present, the video assembles without background music.

**Recommended source:** Pixabay Music (free, no attribution required) — search for corporate/tech presentation background tracks, 1-2 minutes (will be looped automatically).

### Step 8: Assemble Video

Run the video assembly script:

```bash
python3 ${SKILL_DIR}/scripts/assemble_video.py {output}/video-config.json {output}/infographic {output}/audio {output}/output
```

**How it works:**
1. Reads card configuration from video-config.json
2. Generates title card PNG (red background) and outro card PNG (dark background) using Pillow
3. For each section: creates an ImageClip (infographic) with AudioFileClip (dialogue)
4. Concatenates all clips with 0.5s crossfade transitions
5. Layers background music (if bgm.mp3 exists) with volume envelope
6. Exports as MP4 (H.264 + AAC, 1920×1080, 24fps)

**Video structure:**
```
[Title Card 3s] → [Section 1] → [Section 2] → ... → [Section 6] → [Outro Card 3s]
         ↕ 0.5s crossfade between each clip ↕
     🎵 full vol        🎵 15% vol (under dialogue)       🎵 full → fade out
```

**Export settings:**

| Setting | Value |
|---------|-------|
| Resolution | 1920×1080 |
| FPS | 24 |
| Video codec | H.264 (libx264) |
| Audio codec | AAC |
| Video bitrate | 5000k |
| Audio bitrate | 192k |

### Step 9: Verify Output

1. Confirm file exists and size is reasonable (30-100 MB typical)
2. Check metadata:
   ```bash
   ffprobe -v quiet -show_entries format=duration \
     -show_entries stream=width,height,codec_name \
     -of json output/meeting-recap-final.mp4
   ```
3. Verify: 1920×1080, H.264+AAC, duration matches audio total + 6s for cards
4. Report final duration, file size, and output path

## Title & Outro Cards

**Title card** (3s):
- Adobe-red background (#EB1000 / RGB 235,16,0) — visible as Slack/Teams thumbnail
- Line 1: Meeting title (72pt bold white)
- Line 2: Subtitle (44pt light pink)
- Line 3: Date (36pt light pink)
- 0.5s fade in/out

**Outro card** (3s):
- Dark background (#12121C)
- Memorable closing quote from the meeting (48pt white)
- Attribution (36pt gray)
- 0.5s fade in/out

Cards are generated as PNGs via Pillow (no ImageMagick dependency).

## Error Handling

- Missing API key → error with setup instructions
- Text-to-Dialogue API failure → error with section name for debugging
- ffmpeg not found → install instructions
- moviepy import failure → install instructions
- Missing bgm.mp3 → skipped (music is optional), prints info message

## References

- `references/section-planning.md` — How to split content into sections
- `references/dialogue-format.md` — Dialogue writing guidelines, bridging, voice config, API details
