---
name: demo-video
description: Build a narrated demo video from a screen recording, a talk track script with act timelines, branded intro/outro slides, background music, and AI-generated voiceover via ElevenLabs. Use when user asks to create a "demo video", "product demo", "narrated screencast", "talk track video", or "voiceover video".
---

# Demo Video Builder

Assembles a polished narrated demo video from a screen recording, a scripted talk track with per-act timelines, branded intro/outro slides, background music, and AI voiceover. Output is a single MP4 ready for sharing.

## When to Use

- User has a screen recording of a product demo
- They want a scripted voiceover narration on top
- The video needs branded intro/outro slides
- Background music on intro/outro (never overlapping with voice)

## Pipeline

```
Screen recording + script + music + brand assets
  -> Slide generation (PIL)
  -> TTS voiceover per act (ElevenLabs)
  -> Segment assembly per act (ffmpeg)
  -> Final concatenation with re-encode (ffmpeg)
  -> Output MP4
```

## Usage

```
/demo-video path/to/recording.mov
/demo-video path/to/recording.mov --music path/to/music.mp3 --voice Eric
```

## Required Input

Gather from user before building:

### 1. Screen Recording
- File path to the demo video
- Run `ffprobe` to get resolution, duration, FPS

### 2. Talk Track Script with Timelines
Each act needs:
- **Act name/number** and description
- **Start-end timestamps** in the source video (or "slide" for intro/outro)
- **Narration text**

Example:
```
Act 1 (intro, slide): With AEM, teams can build a complete site in minutes.
Act 2 (0:00-0:15): Here we're building the Tavex site from a detailed briefing.
Act 3 (0:16-0:45): The agent reads the briefing and gets to work...
```

### 3. Intro Slide Content
- Title text
- Subtitle text
- Background color (default: Adobe red `#EB1000`)

### 4. Outro Slide Content
- Logo image URL or path
- Background color (default: same as intro)

### 5. Music
- Path to background music file (MP3)
- Music plays ONLY on intro and outro slides, never during narrated acts

### 6. Voice
- ElevenLabs voice name/ID (ask user to pick from samples if unsure)
- Generate 2-3 samples of act 1 script for comparison before committing

## Script Writing Methodology

The build pipeline assumes a finished script. Writing that script well is a separate discipline — generic scripts feel dubbed, synced scripts feel alive. Run this process before the build.

### 1. Extract frames at high frequency
Use `ffmpeg -vf "fps=1/2,scale=800:-1"` — every 2s for transition-heavy videos, every 5s for simple ones. Read every frame visually to build a precise timeline.

### 2. Build a frame-analysis table
Map timestamps → screen content → production notes. Save as `frame-analysis.md` alongside the script. This is the source of truth for act boundaries.

### 3. Read the brand's voice guidelines before writing
Extract: banned words, preferred vocabulary, sentence rhythm, anti-traits. Don't invent a tone — match it. A "cheeky" first draft often has to be completely rewritten once the brand's actual voice is in view.

### 4. Identify structural transitions
Mark exact timestamps where the UI changes (panels appearing/disappearing, page changes, loading states). These become act boundaries with deliberate pauses and narration bridges.

### 5. Reference specific on-screen elements, not generic descriptions
Mention the exact product name, the exact UI element ("See the interest bars?"), the exact text on screen ("Five forty-five a.m."). This is what makes narration feel synced rather than dubbed.

### 6. Handle visual transitions explicitly in the talk track
When a new UI element appears, the narration should prime the viewer ("let me show you what I see") → 0.5s pause → element appears. When it disappears, the last line should land on it → 0.5s pause → resume.

### 7. Word-count budget: ~2.5 words/second
Count words per act, compare against act duration. Over-length acts need trimming or freeze-frame extension.

### 8. Save the script as `script.md`
Include: metadata (source video, duration, character, tone), brand voice rules, and each act with timestamps + on-screen description + narration + production notes.

## Architecture

### Build Directory Structure

```
build-demo/
  frames/            # Extracted frames for analysis (step 1)
  frame-analysis.md  # Timeline mapping timestamps to screen content (step 2)
  script.md          # Talk track script (step 8)
  audio/             # TTS voiceover MP3 per act
  images/            # Generated slide PNGs
  segments/          # Assembled MP4 per act
  concat.txt         # ffmpeg concat manifest
  build.py           # Build script
  aem-demo.mp4       # Final output
```

### Incremental Builds

The build script skips existing artifacts. To rebuild a specific act:
1. Delete its audio file (`audio/actN.mp3`)
2. Delete its segment file (`segments/NN-actN.mp4`)
3. Delete the final video (`aem-demo.mp4`)
4. Re-run `build.py`

## Reference

Detailed technical reference is split into supplementary files — consult as needed during the build:

- **[FFMPEG_REFERENCE.md](./FFMPEG_REFERENCE.md)** — Audio filter chains, video scaling, encoding settings, concatenation rules, and slide generation tips
- **[ELEVENLABS.md](./ELEVENLABS.md)** — TTS API usage, voice selection workflow, speed tuning, pacing guidelines, and recommended voices

## Workflow

### Step 1: Gather Input
1. Get screen recording path, run `ffprobe` for specs
2. Get talk track script with act timelines — if the script doesn't exist yet, run the [Script Writing Methodology](#script-writing-methodology) first
3. Get intro/outro slide content
4. Get music file path
5. Get voice preference (or generate samples)

### Step 2: Setup Build Directory
```bash
mkdir -p build-demo/{audio,images,segments}
```

### Step 3: Generate Slides (PIL)
- Intro: solid color background + centered title + subtitle
- Outro: solid color background + centered white logo
- Font: Helvetica from `/System/Library/Fonts/Helvetica.ttc`

### Step 4: Generate TTS
- One MP3 per act via ElevenLabs `/v1/text-to-speech/{voice_id}`
- Model: `eleven_multilingual_v2`
- Voice settings: `stability=0.6, similarity_boost=0.8, style=0.15`

### Step 5: Build Segments

**Intro segment:**
1. Loop intro slide image as video
2. Music: trim to N seconds, fade in first half, fade out second half
3. VO: delay by N seconds (after music ends)
4. Mix with `amix:normalize=0` (no overlap, just sequential)

**Video segments (per act):**
1. Cut source video at start/end timestamps
2. Scale/pad to 1920x1080
3. If VO longer than video: tpad freeze-frame
4. VO: adelay 300ms + aresample + apad + pan stereo
5. Encode with consistent settings

**Outro segment:**
1. Loop outro slide image
2. Music: fade in, hold, fade out
3. No voice

### Step 6: Concatenate
1. Write `concat.txt` with all segment paths in order
2. Re-encode both streams (never `-c copy`)

### Step 7: Open and Verify
```bash
open output.mp4
```

Check: audio plays on both channels, no sync drift at act transitions, music doesn't overlap voice.

### Step 8: Iterate
Common adjustments (delete affected files and re-run):
- **Script too short/long for segment?** Adjust script length (~2.5 words/sec), delete `audio/actN.mp3` + `segments/NN-actN.mp4`
- **Wrong voice?** Delete all `audio/act*.mp3` + all `segments/*.mp4`
- **Slide text change?** Delete `images/*.png` + `segments/00-intro.mp4` or `segments/99-outro.mp4`
- **Music timing?** Delete affected segment + final video

## Dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| `ffmpeg` | Video/audio assembly, concat | `brew install ffmpeg` |
| `ffprobe` | Source video analysis | Included with ffmpeg |
| `Pillow` | Slide image generation | `pip install Pillow` |
| `requests` | ElevenLabs API calls | `pip install requests` |
| `python-dotenv` | Load API keys from `.env` | `pip install python-dotenv` |

## Environment

Requires `ELEVENLABS_API_KEY` in `.env` file.

See [ELEVENLABS.md](./ELEVENLABS.md) for API reference and voice recommendations.
