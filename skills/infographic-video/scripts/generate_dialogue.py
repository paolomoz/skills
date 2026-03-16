#!/usr/bin/env python3
"""Generate dialogue audio for meeting recap video using ElevenLabs Text-to-Dialogue API.

Usage:
    python3 generate_dialogue.py <dialogue.json> <output-audio-dir> [--voices Alex=VOICE_ID,Jordan=VOICE_ID]

The dialogue.json file should have this structure:
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

Uses the Text-to-Dialogue API (POST /v1/text-to-dialogue) which produces a single
audio file per section with natural turn-taking and pacing between speakers.

Post-processing:
- Prepends 1.0s silence so audio doesn't start abruptly on slide transitions
- Speeds up audio by 20% (atempo=1.2) for faster-paced delivery
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# ── Defaults ──────────────────────────────────────────────────────────────────
DEFAULT_VOICES = {
    "Alex": "L0Dsvb3SLTyegXwtm47J",    # Archer — conversational, warm male guide
    "Jordan": "kdmDKE6EkgrWrrykO9Qt",   # Alexandra — realistic, chatty female reactor
}

DIALOGUE_URL = "https://api.elevenlabs.io/v1/text-to-dialogue"
MODEL_ID = "eleven_v3"

LEAD_IN_SILENCE = 1.0   # seconds of silence before dialogue starts
SPEED_FACTOR = 1.2       # 20% faster playback


# ── Audio Generation ──────────────────────────────────────────────────────────
def generate_dialogue_audio(
    dialogue: list, voices: dict, output_path: Path, api_key: str
) -> None:
    """Call ElevenLabs Text-to-Dialogue API for a section's dialogue.

    Sends all turns for a section in one request. The API returns a single
    audio file with natural pacing between speakers.

    Post-processing via ffmpeg:
    1. Prepend 1.0s silence (so dialogue doesn't start abruptly on crossfade)
    2. Speed up by 20% (atempo=1.2) for faster-paced delivery
    """
    inputs = []
    for turn in dialogue:
        speaker = turn["speaker"]
        text = re.sub(r"\[.*?\]\s*", "", turn["text"])
        voice_id = voices.get(speaker)
        if not voice_id:
            print(f"    WARNING: No voice for '{speaker}', skipping turn")
            continue
        inputs.append({
            "text": text,
            "voice_id": voice_id,
        })

    resp = requests.post(
        DIALOGUE_URL,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "inputs": inputs,
            "model_id": MODEL_ID,
        },
        timeout=120,
    )
    resp.raise_for_status()

    # Write raw API response to temp file
    raw_path = output_path.with_suffix(".raw.mp3")
    raw_path.write_bytes(resp.content)

    # Prepend silence + speed up via ffmpeg
    # IMPORTANT: -t must come BEFORE -i for lavfi sources to bound their duration
    subprocess.run(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-t", str(LEAD_IN_SILENCE), "-i", "anullsrc=r=44100:cl=stereo",
            "-i", str(raw_path),
            "-filter_complex",
            f"[0][1]concat=n=2:v=0:a=1[joined];[joined]atempo={SPEED_FACTOR}",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(output_path),
        ],
        check=True,
    )
    raw_path.unlink()
    print(f"    Generated: {output_path.name} ({output_path.stat().st_size / 1024:.1f} KB, +{LEAD_IN_SILENCE}s lead-in, {SPEED_FACTOR}x speed)")


def get_duration(audio_path: Path) -> float:
    """Get audio duration in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip()) if result.stdout.strip() else 0.0


def parse_voices(voices_str: str) -> dict:
    """Parse voice mapping from 'Name=ID,Name=ID' format."""
    voices = {}
    for pair in voices_str.split(","):
        name, voice_id = pair.strip().split("=")
        voices[name.strip()] = voice_id.strip()
    return voices


def main():
    parser = argparse.ArgumentParser(description="Generate dialogue audio from JSON")
    parser.add_argument("dialogue_json", type=Path, help="Path to dialogue.json")
    parser.add_argument("output_dir", type=Path, help="Output directory for audio files")
    parser.add_argument("--voices", type=str, help="Voice mapping: Name=ID,Name=ID")
    args = parser.parse_args()

    # Load .env from the dialogue file's parent directory
    load_dotenv(args.dialogue_json.parent / ".env")
    load_dotenv(Path.cwd() / ".env")

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not found in environment or .env")
        sys.exit(1)

    voices = parse_voices(args.voices) if args.voices else DEFAULT_VOICES

    # Load dialogue
    with open(args.dialogue_json) as f:
        data = json.load(f)
    sections = data["sections"]

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  ElevenLabs Text-to-Dialogue Generator")
    print("  Two-host conversation (Alex & Jordan)")
    print(f"  Lead-in silence: {LEAD_IN_SILENCE}s | Speed: {SPEED_FACTOR}x")
    print("=" * 60)

    total_duration = 0.0

    for section in sections:
        name = section["name"]
        dialogue = section["dialogue"]
        output_path = args.output_dir / f"{name}.mp3"

        print(f"\n  Section: {name}")
        print(f"  Turns: {len(dialogue)}")
        print(f"  {'─' * 40}")

        generate_dialogue_audio(dialogue, voices, output_path, api_key)

        duration = get_duration(output_path)
        total_duration += duration
        print(f"    Duration: {duration:.1f}s")

    print(f"\n{'=' * 60}")
    print(f"  All done! Total audio: {total_duration:.1f}s")
    print(f"  Files in: {args.output_dir}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
