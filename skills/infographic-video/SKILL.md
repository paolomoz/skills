---
name: infographic-video
description: Generates a short video recap from a meeting summary. Splits content into sections, creates infographics, generates two-host dialogue audio via ElevenLabs, and assembles into MP4. Use when user asks to create a "meeting video", "video recap", "video summary", or "meeting recap video".
---

# Meeting Video Generator

Transforms a meeting summary (Markdown) into a short (~5 min) video with infographic visuals and two-host podcast-style dialogue audio.

## Pipeline

```
Meeting Summary (.md)
  → Section Splitting (6 sections)
  → Infographic Generation (1 per section, any image gen tool)
  → Dialogue Scripts (two-host, casual podcast tone)
  → Audio Generation (ElevenLabs TTS, 2 voices)
  → Video Assembly (moviepy + ffmpeg → MP4)
```

## Script Directory

**Agent Execution**:
1. `SKILL_DIR` = this SKILL.md file's directory
2. Scripts in `${SKILL_DIR}/scripts/`

## Usage

```
/infographic-video path/to/meeting-summary.md
/infographic-video path/to/summary.md --sections 6 --voices roger,laura
/infographic-video path/to/summary.md --output video/output/
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--sections <n>` | Number of content sections | `6` |
| `--output <dir>` | Output directory for all artifacts | `meeting/` |
| `--voices <a,b>` | ElevenLabs voice IDs (host-a,host-b) | Roger, Laura |
| `--host-names <a,b>` | Display names for the two hosts | `Alex, Jordan` |
| `--aspect` | Infographic aspect ratio | `landscape` (16:9) |
| `--lang` | Language for all text content | `en` |
| `--duration` | Target video duration in seconds | `300` (5 min) |

## Dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| `ffmpeg` | Audio concat, video encoding | `brew install ffmpeg` |
| `moviepy` | Video composition, crossfades | `pip3 install moviepy` |
| `requests` | ElevenLabs API calls | `pip3 install requests` |
| `python-dotenv` | Load API keys from `.env` | `pip3 install python-dotenv` |
| `Pillow` | Title/outro card generation | `pip3 install Pillow` |

Infographic images can be generated with any image generation tool available to the agent.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ELEVENLABS_API_KEY` | ElevenLabs API key (required for audio) |

## Default Voices

| Host | Voice | Voice ID | Character |
|------|-------|----------|-----------|
| Alex | Roger | `CwhRBWXzGAHq8TQ4Fs17` | Warm male, laid-back narrator/guide |
| Jordan | Laura | `FGY2WhTYpPnrIDTdsKH5` | Energetic female, reactor/questioner |

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
│   └── ...
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

Select a layout×style combination for each section's infographic. Vary styles across sections for visual interest.

**Recommended pairings by content type:**

| Content Type | Layout | Style |
|--------------|--------|-------|
| Overview / Intro | `bento-grid` | `corporate-memphis` |
| Journey / Process | `winding-roadmap` | `storybook-watercolor` |
| Core Concept / Mission | `hub-spoke` | `bold-graphic` |
| Framework / Model | `linear-progression` | `technical-schematic` |
| Metrics / KPIs | `dashboard` | `corporate-memphis` |
| Future / Technology | `circular-flow` | `cyberpunk-neon` |

All infographics: **16:9 landscape** (1920×1080 or 2K equivalent).

### Step 4: Generate Infographics

For each section, generate an infographic image:

1. Write a detailed prompt describing the layout, style, and content
2. Generate the image using whatever image generation tool is available
3. Save to `{output}/infographic/{NN}-{slug}.png`
4. Verify output exists and is 16:9 aspect ratio

Generate sequentially (one at a time) to ensure quality.

### Step 5: Write Dialogue Scripts

Write casual two-host dialogue for each section and save as `{output}/dialogue.json`:

```json
{
  "sections": [
    {
      "name": "01-intro",
      "dialogue": [
        {"speaker": "Alex", "text": "Opening line..."},
        {"speaker": "Jordan", "text": "Reaction..."}
      ]
    }
  ]
}
```

**Dialogue Format:**
- Two hosts with contrasting roles:
  - **Host A** (Alex): Warm narrator/guide — explains, sets context, delivers key facts
  - **Host B** (Jordan): Energetic reactor/questioner — asks questions, reacts, highlights takeaways
- Casual podcast-recap tone, conversational and accessible
- ~130-160 words per section targeting ~50s audio each
- Alternate turns between hosts (5-9 turns per section)
- Use natural emotional cues through word choice (not bracketed directives)

See `references/dialogue-format.md` for detailed guidelines and examples.

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
2. For each dialogue turn, calls ElevenLabs TTS
3. Concatenates turns with 350ms silence gaps using ffmpeg
4. Outputs one MP3 per section to the audio directory

**Verification:**
- Each MP3 should be 40-65s duration
- Total audio should be under 6 minutes
- Both voices should be clearly distinguishable

### Step 7: Assemble Video

Run the video assembly script:

```bash
python3 ${SKILL_DIR}/scripts/assemble_video.py {output}/video-config.json {output}/infographic {output}/audio {output}/output
```

**How it works:**
1. Reads card configuration from video-config.json
2. Generates title and outro card PNGs using Pillow
3. For each section: creates an ImageClip (infographic) with AudioFileClip (dialogue)
4. Concatenates all clips with 0.5s crossfade transitions
5. Exports as MP4 (H.264 + AAC, 1920×1080, 24fps)

**Video structure:**
```
[Title Card 3s] → [Section 1] → [Section 2] → ... → [Section 6] → [Outro Card 3s]
         ↕ 0.5s crossfade between each clip ↕
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

### Step 8: Verify Output

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
- Dark background (#12121C)
- Line 1: Meeting title (72pt bold white)
- Line 2: "Meeting Recap" (44pt light gray)
- Line 3: Date (36pt gray)
- 0.5s fade in/out

**Outro card** (3s):
- Dark background (#12121C)
- Memorable closing quote from the meeting (48pt white)
- Attribution (36pt gray)
- 0.5s fade in/out

Cards are generated as PNGs via Pillow (no ImageMagick dependency).

## Error Handling

- Missing API key → error with setup instructions
- TTS failure → error with specific turn info for debugging
- ffmpeg not found → install instructions
- moviepy import failure → install instructions

## References

- `references/section-planning.md` — How to split content into sections
- `references/dialogue-format.md` — Dialogue writing guidelines and examples
