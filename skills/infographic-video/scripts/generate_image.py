#!/usr/bin/env python3
"""Generate infographic images using Sumi prompt crafting + Gemini 3 Pro Image.

Usage:
    python3 generate_image.py <source.md> <output.png> \
        --layout hub-spoke --style bold-graphic \
        --sumi-dir /path/to/sumi/backend/sumi/references/data

Pipeline:
    1. Load Sumi style + layout references
    2. Craft a rich visual prompt (LLM-assisted via Claude)
    3. Generate image via Gemini 3 Pro Image Preview

Environment:
    GOOGLE_API_KEY:    Google AI API key (required)
    ANTHROPIC_API_KEY: Anthropic API key (required for prompt crafting)
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "google-genai"])
    from google import genai
    from google.genai import types

try:
    import anthropic
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "anthropic"])
    import anthropic

from dotenv import load_dotenv


# ── Sumi Reference Loading ───────────────────────────────────────────────────

DEFAULT_SUMI_DATA_DIR = Path("/Users/paolo/playground/sumi/backend/sumi/references/data")


def load_reference(data_dir: Path, kind: str, ref_id: str) -> str:
    """Load a style or layout markdown file from the Sumi references."""
    path = data_dir / f"{kind}s" / f"{ref_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Sumi {kind} '{ref_id}' not found at {path}")
    return path.read_text(encoding="utf-8")


# ── Prompt Crafting (Claude) ─────────────────────────────────────────────────

CRAFT_SYSTEM = """\
You are an expert visual designer crafting prompts for an AI image generator (Gemini 3 Pro). \
You will be given a layout reference, style reference, and section content. \
Your job is to produce a single, rich image generation prompt that describes:

1. **Layout Guidelines** — Adapt the generic layout structure to this specific content.
2. **Style Guidelines** — Include full color palette, visual elements, compositional patterns, \
visual metaphor mappings, and typography instructions from the style reference.
3. **Content as Visual Scenes** — Describe each content area as a concrete visual scene \
with exact text labels to render.

## CRITICAL RULES
- Describe VISUAL SCENES, not abstract concepts. Tell the generator what to DRAW.
- Keep all source quotes and data VERBATIM.
- Output raw markdown with NO code fences, NO preamble, NO commentary.
- Start directly with the prompt content.
- The output will be sent directly to an image generation model."""


def craft_prompt(
    section_content: str,
    layout_content: str,
    style_content: str,
    layout_name: str,
    style_name: str,
    aspect_ratio: str = "16:9",
) -> str:
    """Use Claude to craft a rich visual prompt from Sumi references + section content."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=api_key)

    user_message = f"""Create an image generation prompt for a single {aspect_ratio} infographic.

## Parameters
- **Layout**: {layout_name}
- **Style**: {style_name}
- **Aspect Ratio**: {aspect_ratio}

## Layout Reference

{layout_content}

## Style Reference

{style_content}

## Section Content (transform into visual scenes)

{section_content}

---

Generate a complete image generation prompt that combines layout structure, style aesthetics, \
and content into vivid visual scene descriptions with exact text labels. \
The prompt should be directly usable by an image generation model."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        temperature=0.7,
        system=CRAFT_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
    )

    prompt = response.content[0].text

    # Prepend fixed header
    header = f"Create a single {aspect_ratio} infographic in {style_name} style using a {layout_name} layout. Use rich visual scenes with clear hierarchy and ample whitespace.\n\n"
    return header + prompt


# ── Image Generation (Gemini 3 Pro) ─────────────────────────────────────────

def generate_image(prompt: str, output_path: str, aspect_ratio: str = "16:9") -> str:
    """Generate an infographic image using Gemini 3 Pro Image Preview."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio.replace(":", ":"),
            ),
        ),
    )

    for part in response.parts:
        if part.inline_data is not None:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            image = part.as_image()
            image.save(str(output_file))
            print(f"  Saved: {output_file}")
            return str(output_file)

    raise RuntimeError("Gemini returned no image in response")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate infographic via Sumi prompt crafting + Gemini 3 Pro"
    )
    parser.add_argument("source", type=Path, help="Section source.md file")
    parser.add_argument("output", type=str, help="Output image path (e.g., infographic/01-intro.png)")
    parser.add_argument("--layout", required=True, help="Sumi layout ID (e.g., hub-spoke)")
    parser.add_argument("--style", required=True, help="Sumi style ID (e.g., bold-graphic)")
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument(
        "--sumi-dir", type=Path, default=DEFAULT_SUMI_DATA_DIR,
        help="Path to Sumi references/data directory"
    )
    args = parser.parse_args()

    load_dotenv(Path.cwd() / ".env")

    # 1. Load inputs
    section_content = args.source.read_text(encoding="utf-8")
    layout_content = load_reference(args.sumi_dir, "layout", args.layout)
    style_content = load_reference(args.sumi_dir, "style", args.style)

    # Derive names from IDs
    layout_name = " ".join(w.capitalize() for w in args.layout.split("-"))
    style_name = " ".join(w.capitalize() for w in args.style.split("-"))

    print(f"  Crafting prompt: {args.layout} × {args.style}")

    # 2. Craft prompt via Claude
    prompt = craft_prompt(
        section_content, layout_content, style_content,
        layout_name, style_name, args.aspect_ratio
    )

    # Save prompt for debugging
    prompt_path = Path(args.output).with_suffix(".prompt.md")
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")
    print(f"  Prompt saved: {prompt_path}")

    # 3. Generate image via Gemini
    print(f"  Generating image via Gemini 3 Pro...")
    generate_image(prompt, args.output, args.aspect_ratio)
    print(f"  Done: {args.output}")


if __name__ == "__main__":
    main()
