#!/usr/bin/env python3
"""List available ElevenLabs voices to help select dialogue speakers."""

import os, requests, sys
from pathlib import Path

# Load API key from .env
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

api_key = os.environ.get("ELEVENLABS_API_KEY")
if not api_key:
    print("ERROR: ELEVENLABS_API_KEY not found in .env")
    sys.exit(1)

resp = requests.get(
    "https://api.elevenlabs.io/v1/voices",
    headers={"xi-api-key": api_key}
)
resp.raise_for_status()

voices = resp.json()["voices"]
print(f"Found {len(voices)} voices:\n")
print(f"{'VOICE_ID':<28} {'NAME':<22} {'GENDER':<8} {'ACCENT':<14} {'AGE':<10} {'DESCRIPTION'}")
print("-" * 120)

for v in sorted(voices, key=lambda x: x.get("name", "")):
    labels = v.get("labels", {})
    print(
        f"{v['voice_id']:<28} "
        f"{v.get('name','?'):<22} "
        f"{labels.get('gender','?'):<8} "
        f"{labels.get('accent','?'):<14} "
        f"{labels.get('age','?'):<10} "
        f"{labels.get('description','?')}"
    )
