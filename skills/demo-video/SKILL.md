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

## Architecture

### Build Directory Structure

```
build-demo/
  audio/          # TTS voiceover MP3 per act
  images/         # Generated slide PNGs
  segments/       # Assembled MP4 per act
  concat.txt      # ffmpeg concat manifest
  build.py        # Build script
  aem-demo.mp4    # Final output
```

### Incremental Builds

The build script skips existing artifacts. To rebuild a specific act:
1. Delete its audio file (`audio/actN.mp3`)
2. Delete its segment file (`segments/NN-actN.mp4`)
3. Delete the final video (`aem-demo.mp4`)
4. Re-run `build.py`

## Critical Rules (Lessons Learned)

### Audio

1. **NEVER overlap music and voice.** Music plays only during intro/outro slides. Voice-only during video acts. No background music under narration.

2. **Intro music structure:** Music fades in and fades out within its duration (e.g., 5s), THEN voice starts. Use `atrim` to cut music to exact duration, `afade` for fade in/out, then `amix` with the delayed VO. Since music ends before VO starts, there is no overlap.
   ```
   [music]atrim=0:5,afade=t=in:st=0:d=2.5,afade=t=out:st=2.5:d=2.5,volume=0.35[music];
   [vo]adelay=5000|5000[vo];
   [music][vo]amix=inputs=2:duration=longest:normalize=0[aout]
   ```

3. **All segments MUST output stereo audio (2 channels).** ElevenLabs outputs mono MP3. If some segments are mono and others stereo, concatenation produces audio glitches (voice from one side, artifacts on the other). Fix with `pan=stereo|c0=c0|c1=c0` in the filter chain and `-ac 2` in output flags.

4. **Add 300ms voice delay in video segments.** Without a delay, the voice starts slightly before the visual transition at act boundaries. Use `adelay=300|300` at the start of the VO filter chain.

5. **Full audio filter chain for video segments:**
   ```
   [1:a]adelay=300|300,aresample=async=1,apad=pad_dur={duration},pan=stereo|c0=c0|c1=c0[aout]
   ```

### Video

6. **Freeze-frame extension.** When VO is longer than the video segment, pad with last frame using `tpad=stop_mode=clone:stop_duration={pad_time}`.

7. **Scale and pad to target resolution.** Source video may not be 1920x1080:
   ```
   scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2
   ```

8. **Consistent encoding across all segments.** Every segment must use:
   ```
   -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -r 25
   -c:a aac -ac 2 -b:a 192k
   ```

### Concatenation

9. **Always re-encode on concat.** Using `-c copy` with concat causes audio/video sync drift at segment boundaries. Always re-encode:
   ```
   ffmpeg -y -f concat -safe 0 -i concat.txt \
     -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -r 25 \
     -c:a aac -ac 2 -b:a 192k output.mp4
   ```

### Slides

10. **Use PIL (Pillow) for slide generation, not ffmpeg drawtext.** macOS ffmpeg often lacks the freetype/drawtext filter. PIL with system fonts (`/System/Library/Fonts/Helvetica.ttc`) works reliably.

11. **Logo color inversion for outro.** If the source logo is colored on transparent, iterate pixels and set all non-transparent pixels to white (or desired color) while preserving alpha.

### TTS / Voice

12. **Voice selection workflow.** Generate 2-3 voice samples of act 1 script before committing to a voice. Let user compare.

13. **ElevenLabs speed parameter.** Range 0.7-1.2, default 1.0. If user wants faster/slower delivery, adjust via the `speed` field in the API request JSON (not voice_settings).

14. **Voice consistency.** Store the chosen voice ID in the build script. When changing voice, delete ALL `audio/act*.mp3` files and ALL `segments/*.mp4` files to force full regeneration. Cached audio from a previous voice will silently persist otherwise.

15. **Script length vs. segment duration.** Target ~2.5 words/second for natural narration pace. For a 15s video segment, aim for ~37 words. Generate TTS and check actual duration — ElevenLabs varies by voice and content.

## Workflow

### Step 1: Gather Input
1. Get screen recording path, run `ffprobe` for specs
2. Get talk track script with act timelines
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

## ElevenLabs API Reference

### List voices
```bash
curl -H "xi-api-key: $KEY" https://api.elevenlabs.io/v1/voices
```

### Generate speech
```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}" \
  -H "xi-api-key: $KEY" -H "Content-Type: application/json" \
  -d '{"text": "...", "model_id": "eleven_multilingual_v2",
       "voice_settings": {"stability": 0.6, "similarity_boost": 0.8, "style": 0.15}}'
```

### Recommended voices for product demos
| Voice | ID | Style |
|-------|----|-------|
| Eric | `cjVigY5qzO86Huf0OWal` | Smooth, trustworthy |
| Daniel | `onwK4e9ZLuTAKqWW03F9` | Steady broadcaster |
| Brian | `nPczCjzI2devNBz1zQrb` | Deep, resonant |
| George | `JBFqnCBsd6RMkjVDRZzb` | Warm storyteller |
