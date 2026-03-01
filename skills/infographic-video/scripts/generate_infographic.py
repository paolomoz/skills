#!/usr/bin/env python3
"""
Generate infographic images using Gemini 3 Pro Image (Nano Banana Pro).

Usage:
    python3 generate_infographic.py "your prompt here" --output output.png

Environment:
    GOOGLE_API_KEY: Your Google AI API key
"""

import argparse
import os
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


def generate_infographic(prompt: str, output_path: str, aspect_ratio: str = "16:9") -> str:
    """
    Generate an infographic image using Gemini 3 Pro Image (Nano Banana Pro).

    Args:
        prompt: The image generation prompt
        output_path: Path to save the generated image
        aspect_ratio: Aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4, etc.)

    Returns:
        Path to the saved image
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
            ),
        ),
    )

    # Extract image from response
    for part in response.parts:
        if part.inline_data is not None:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            image = part.as_image()
            image.save(str(output_file))
            print(f"Image saved to: {output_file}")
            return str(output_file)

    raise RuntimeError("No image was generated")


def main():
    parser = argparse.ArgumentParser(description="Generate infographics with Nano Banana Pro")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument(
        "--output", "-o",
        default="generated_infographic.png",
        help="Output file path (default: generated_infographic.png)",
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        default="16:9",
        choices=["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"],
        help="Aspect ratio (default: 16:9)",
    )

    args = parser.parse_args()

    try:
        output = generate_infographic(args.prompt, args.output, args.aspect_ratio)
        print(f"Generated: {output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
