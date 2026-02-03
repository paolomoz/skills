#!/usr/bin/env python3
"""Assemble meeting recap video from infographics and audio.

Usage:
    python3 assemble_video.py <video-config.json> <infographic-dir> <audio-dir> <output-dir>

video-config.json structure:
{
    "title": {
        "line1": "Meeting Title",
        "line2": "Meeting Recap",
        "line3": "February 2, 2026"
    },
    "outro": {
        "quote": "A memorable closing quote.",
        "attribution": "Speaker Name"
    }
}

Infographic and audio files are matched by filename (e.g., 01-intro.png ↔ 01-intro.mp3).

Output: <output-dir>/meeting-recap-final.mp4 (H.264 + AAC, 1920x1080, 24fps)
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    vfx,
)

WIDTH, HEIGHT = 1920, 1080
FPS = 24
CROSSFADE = 0.5


# ── Card Generation (Pillow) ──────────────────────────────────────────────────

def _find_font(bold=False):
    """Find a usable system font on macOS."""
    candidates = (
        [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
        ]
        if bold
        else [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
        ]
    )
    for path in candidates:
        if Path(path).exists():
            return path
    return None


def _draw_centered_text(draw, text, y, font, fill, width):
    """Draw centered text at vertical position y."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)


def make_card_image(lines, output_path):
    """Generate a dark card with centered text lines.

    lines: list of (text, font_size, color, is_bold) tuples
    """
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(18, 18, 28))
    draw = ImageDraw.Draw(img)

    fonts = []
    heights = []
    for text, size, _color, bold in lines:
        font_path = _find_font(bold=bold)
        font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
        fonts.append(font)
        bbox = draw.textbbox((0, 0), text, font=font)
        heights.append(bbox[3] - bbox[1])

    line_spacing = 24
    total_h = sum(heights) + line_spacing * (len(lines) - 1)
    y = (HEIGHT - total_h) // 2

    for i, (text, _size, color, _bold) in enumerate(lines):
        _draw_centered_text(draw, text, y, fonts[i], color, WIDTH)
        y += heights[i] + line_spacing

    img.save(str(output_path))
    return output_path


def generate_title_card(config, output_dir):
    """Create title card PNG from config."""
    path = output_dir / "_title_card.png"
    title = config["title"]
    make_card_image(
        [
            (title["line1"], 72, (255, 255, 255), True),
            (title.get("line2", "Meeting Recap"), 44, (180, 180, 200), False),
            (title.get("line3", ""), 36, (140, 140, 160), False),
        ],
        path,
    )
    return path


def generate_outro_card(config, output_dir):
    """Create outro card PNG from config."""
    path = output_dir / "_outro_card.png"
    outro = config["outro"]
    quote = outro["quote"]
    attribution = outro.get("attribution", "")

    # Split long quotes across multiple lines (~45 chars each)
    words = quote.split()
    quote_lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 > 45:
            quote_lines.append(current_line)
            current_line = word
        else:
            current_line = f"{current_line} {word}".strip()
    if current_line:
        quote_lines.append(current_line)

    lines = []
    for i, ql in enumerate(quote_lines):
        prefix = '"' if i == 0 else ""
        suffix = '"' if i == len(quote_lines) - 1 else ""
        lines.append((f"{prefix}{ql}{suffix}", 48, (255, 255, 255), False))

    if attribution:
        lines.append(("", 20, (0, 0, 0), False))
        lines.append((f"— {attribution}", 36, (160, 160, 180), False))

    make_card_image(lines, path)
    return path


# ── Video Assembly ─────────────────────────────────────────────────────────────

def make_image_clip(image_path, duration):
    """Create an ImageClip from a PNG file with given duration."""
    clip = ImageClip(str(image_path)).with_duration(duration)
    w, h = clip.size
    if (w, h) != (WIDTH, HEIGHT):
        clip = clip.resized((WIDTH, HEIGHT))
    return clip


def make_section_clip(infographic_path, audio_path):
    """Create a section clip: infographic PNG + audio MP3."""
    audio = AudioFileClip(str(audio_path))
    clip = make_image_clip(infographic_path, audio.duration).with_audio(audio)
    return clip


def main():
    if len(sys.argv) < 5:
        print("Usage: assemble_video.py <video-config.json> <infographic-dir> <audio-dir> <output-dir>")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    infographic_dir = Path(sys.argv[2])
    audio_dir = Path(sys.argv[3])
    output_dir = Path(sys.argv[4])
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(config_path) as f:
        config = json.load(f)

    # Discover sections from audio files
    audio_files = sorted(audio_dir.glob("*.mp3"))
    audio_files = [f for f in audio_files if not f.name.startswith("_")]

    print("=" * 60)
    print("  Video Assembler — Meeting Recap")
    print("=" * 60)

    clips = []

    # Title card (3s) with fade in/out
    print("\n  Creating title card...")
    title_path = generate_title_card(config, output_dir)
    title_clip = make_image_clip(title_path, 3.0).with_effects(
        [vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)]
    )
    clips.append(title_clip)

    # Section clips
    for audio_path in audio_files:
        section_name = audio_path.stem
        infographic_path = infographic_dir / f"{section_name}.png"

        if not infographic_path.exists():
            print(f"  WARNING: Missing infographic {infographic_path}, skipping")
            continue

        print(f"  Adding section: {section_name}")
        clip = make_section_clip(infographic_path, audio_path)
        clips.append(clip)

    # Outro card (3s) with fade in/out
    print("  Creating outro card...")
    outro_path = generate_outro_card(config, output_dir)
    outro_clip = make_image_clip(outro_path, 3.0).with_effects(
        [vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)]
    )
    clips.append(outro_clip)

    if len(clips) < 3:
        print("\n  ERROR: Not enough clips to assemble video.")
        sys.exit(1)

    # Concatenate with crossfade transitions
    print(f"\n  Concatenating {len(clips)} clips with {CROSSFADE}s crossfade...")
    final = concatenate_videoclips(clips, padding=-CROSSFADE, method="compose")

    # Export
    output_path = output_dir / "meeting-recap-final.mp4"
    print(f"  Exporting to: {output_path}")
    final.write_videofile(
        str(output_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate="5000k",
        audio_bitrate="192k",
        logger="bar",
    )

    # Cleanup temp card images
    title_path.unlink(missing_ok=True)
    outro_path.unlink(missing_ok=True)

    print(f"\n{'=' * 60}")
    print(f"  Done! Video: {output_path}")
    print(f"  Duration: {final.duration:.1f}s")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
