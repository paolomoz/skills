#!/usr/bin/env python3
"""Generate dialogue audio for meeting recap video using ElevenLabs TTS.

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
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

# ── Defaults ──────────────────────────────────────────────────────────────────
DEFAULT_VOICES = {
    "Alex": "CwhRBWXzGAHq8TQ4Fs17",    # Roger — male, laid-back, resonant
    "Jordan": "FGY2WhTYpPnrIDTdsKH5",   # Laura — female, energetic, quirky
}

MODEL_ID = "eleven_multilingual_v2"
TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
SILENCE_MS = 350


# ── TTS Generation ─────────────────────────────────────────────────────────────
def generate_speech(text: str, voice_id: str, output_path: Path, api_key: str) -> None:
    """Call ElevenLabs TTS and save audio to output_path."""
    clean_text = re.sub(r"\[.*?\]\s*", "", text)

    resp = requests.post(
        TTS_URL.format(voice_id=voice_id),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": clean_text,
            "model_id": MODEL_ID,
            "voice_settings": {
                "stability": 0.50,
                "similarity_boost": 0.75,
                "style": 0.30,
            },
        },
        timeout=60,
    )
    resp.raise_for_status()
    output_path.write_bytes(resp.content)
    print(f"    Generated: {output_path.name} ({len(resp.content) / 1024:.1f} KB)")


def generate_silence(path: Path, duration_ms: int) -> None:
    """Generate a silent MP3 of given duration."""
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(duration_ms / 1000),
            "-c:a", "libmp3lame", "-q:a", "2",
            str(path),
        ],
        capture_output=True,
        check=True,
    )


def concatenate_audio(parts: list, silence_path: Path, output: Path) -> None:
    """Concatenate audio files with silence gaps using ffmpeg concat demuxer."""
    list_path = output.parent / f"_concat_{output.stem}.txt"
    with open(list_path, "w") as f:
        for i, part in enumerate(parts):
            f.write(f"file '{part}'\n")
            if i < len(parts) - 1:
                f.write(f"file '{silence_path}'\n")

    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_path),
            "-ar", "44100", "-ac", "2",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(output),
        ],
        capture_output=True,
        check=True,
    )
    list_path.unlink(missing_ok=True)


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
    print("  ElevenLabs Dialogue Generator")
    print("=" * 60)

    # Pre-generate a silence clip for reuse
    silence_path = args.output_dir / "_silence.mp3"
    generate_silence(silence_path, SILENCE_MS)

    total_duration = 0.0

    for section in sections:
        name = section["name"]
        dialogue = section["dialogue"]
        output_path = args.output_dir / f"{name}.mp3"

        print(f"\n  Section: {name}")
        print(f"  {'─' * 40}")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            parts = []

            for i, turn in enumerate(dialogue):
                speaker = turn["speaker"]
                text = turn["text"]
                voice_id = voices.get(speaker)
                if not voice_id:
                    print(f"    WARNING: No voice ID for speaker '{speaker}', skipping")
                    continue
                part_path = tmp / f"{i:02d}-{speaker.lower()}.mp3"
                generate_speech(text, voice_id, part_path, api_key)
                parts.append(part_path)

            concatenate_audio(parts, silence_path, output_path)

        duration = get_duration(output_path)
        total_duration += duration
        print(f"    Output: {output_path.name} ({duration:.1f}s)")

    # Cleanup
    silence_path.unlink(missing_ok=True)

    print(f"\n{'=' * 60}")
    print(f"  All done! Total audio duration: {total_duration:.1f}s")
    print(f"  Files in: {args.output_dir}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
