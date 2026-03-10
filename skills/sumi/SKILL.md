---
name: sumi
description: Generate artistic infographics from any topic. Runs the Sumi pipeline (analyze → structure → craft prompt → generate image) locally. Use when "generate infographic", "create infographic", "sumi", "make an infographic about", or "visualize topic".
---

# Sumi — Artistic Infographic Generator

Generate a beautiful infographic from a text topic using the Sumi pipeline: analyze content → structure → craft image prompt → generate image via Gemini.

## Usage

The user provides:
- **topic** (required): The subject or pasted text to turn into an infographic
- **style** (optional): A style ID like `ukiyo-e`, `bauhaus`, `sumi-e`, etc.
- **layout** (optional): A layout ID like `bento-grid`, `hub-spoke`, `iceberg`, etc.
- **mode** (optional): `detailed` (Claude) or `fast` (Cerebras). Default: `detailed`
- **aspect_ratio** (optional): e.g. `16:9`, `9:16`, `1:1`. Default: `16:9`

If style or layout are not specified, recommend 3 combinations using the recommender and let the user pick.

## Instructions

### Step 0: Environment Setup

The Sumi backend lives at `/Users/paolo/playground/sumi/backend`. It needs a Python venv with dependencies installed. The `.env` file at `/Users/paolo/playground/sumi/.env` has the API keys.

Run all Python commands from `/Users/paolo/playground/sumi/backend` using the venv:

```bash
cd /Users/paolo/playground/sumi/backend && source .venv/bin/activate && python -c "..."
```

### Step 1: If style/layout not specified, recommend combinations

Run the recommender to suggest 3 layout×style pairings. Show the user the recommendations with rationales and ask them to pick one (or specify their own).

```bash
cd /Users/paolo/playground/sumi/backend && source .venv/bin/activate && python -c "
import asyncio
from sumi.engine.content_analyzer import analyze_content
from sumi.engine.combination_recommender import recommend_combinations

async def main():
    analysis = await analyze_content('''TOPIC_HERE''', mode='detailed')
    recs = await recommend_combinations('''TOPIC_HERE''', analysis)
    for r in recs:
        print(f\"{r['approach']}: {r['layout_name']} × {r['style_name']}\")
        print(f\"  Layout: {r['layout_id']}, Style: {r['style_id']}\")
        print(f\"  {r['rationale']}\")
        print()

asyncio.run(main())
"
```

Present the 3 options clearly and ask the user to pick. If they say "1", "2", or "3", or name a style/layout, use that.

### Step 2: Run the full pipeline

Once style and layout are confirmed, run the complete pipeline. This executes:
1. **Pre-synthesis** — condenses long input (>10K chars) into a brief
2. **Analysis** — analyzes the topic for infographic creation
3. **Structuring** — transforms analysis into designer-ready content
4. **Prompt crafting** — generates a rich visual prompt using layout + style references
5. **Image generation** — calls Gemini to generate the infographic

```bash
cd /Users/paolo/playground/sumi/backend && source .venv/bin/activate && python -c "
import asyncio, time, os
from pathlib import Path
from sumi.engine.content_synthesizer import synthesize_if_needed
from sumi.engine.content_analyzer import analyze_content
from sumi.engine.content_structurer import generate_structured_content
from sumi.engine.prompt_crafter import craft_prompt
from sumi.engine.image_generator import generate_image

TOPIC = '''TOPIC_HERE'''
STYLE = 'STYLE_ID_HERE'
LAYOUT = 'LAYOUT_ID_HERE'
MODE = 'MODE_HERE'  # 'detailed' or 'fast'
ASPECT_RATIO = 'ASPECT_RATIO_HERE'

async def main():
    t_start = time.monotonic()

    print('Synthesizing...', flush=True)
    topic = await synthesize_if_needed(TOPIC, mode=MODE)

    print('Analyzing...', flush=True)
    analysis = await analyze_content(topic, mode=MODE)

    print('Structuring...', flush=True)
    structured = await generate_structured_content(topic, analysis, mode=MODE)

    print('Crafting prompt...', flush=True)
    analysis_md = analysis.get('analysis_markdown', '')
    prompt = await craft_prompt(
        layout_id=LAYOUT,
        style_id=STYLE,
        structured_content=structured,
        topic=topic,
        analysis=analysis_md,
        aspect_ratio=ASPECT_RATIO,
        mode=MODE,
    )

    # Save prompt for reference
    out_dir = Path('output/skill')
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'prompt.md').write_text(prompt)

    print('Generating image...', flush=True)
    image_path = await generate_image(
        prompt=prompt,
        output_path=str(out_dir / 'infographic.png'),
        aspect_ratio=ASPECT_RATIO,
    )

    elapsed = time.monotonic() - t_start
    print(f'Done in {elapsed:.1f}s')
    print(f'Image saved: {os.path.abspath(image_path)}')

asyncio.run(main())
"
```

### Step 3: Show result

After the image is generated:
1. Tell the user the file path
2. Use `open <path>` on macOS to open the image
3. Mention the prompt was saved to `output/skill/prompt.md` in case they want to iterate

### Available Styles

acid-glow, aged-academia, airline-travel-poster, art-nouveau, art-nouveau-mucha, atomic-age, axonometric, bauhaus, bold-graphic, botanical-illustration, chalkboard, charley-harper, claymation, constructivism, corporate-memphis, craft-handmade, cubism, daniel-clowes, de-stijl, dia-de-muertos, dr-seuss, fantasy-map, futurism, golden-age-comics, googie, ikea-manual, isometric-technical, isotype, jack-kirby, kandinsky, kawaii, keith-haring, knolling, ligne-claire, matsumoto, memphis, moebius, origami, osamu-tezuka, patent-drawing, paul-rand, pixel-art, pop-art-lichtenstein, renaissance-diagram, richard-scarry, rinpa, saul-bass, shan-shui, storybook-watercolor, studio-ghibli, subway-map, sumi-e, superflat, synthwave, technical-schematic, tibetan-thangka, treasure-map, ukiyo-e

### Available Layouts

bento-grid, binary-comparison, bridge, circular-flow, comic-strip, comparison-matrix, dashboard, funnel, hierarchical-layers, hub-spoke, iceberg, isometric-map, jigsaw, linear-progression, periodic-table, story-mountain, structural-breakdown, tree-branching, venn-diagram, winding-roadmap
