---
name: sumi
description: Generate artistic infographics from any topic. Runs the Sumi pipeline (analyze → structure → craft prompt → generate image) entirely within Claude Code. Use when "generate infographic", "create infographic", "sumi", "make an infographic about", or "visualize topic".
---

# Sumi — Artistic Infographic Generator

Generate a beautiful infographic from a text topic. Claude does all the thinking (analysis, structuring, prompt crafting) using curated reference files. Only the final image generation calls an external API (Gemini).

## Usage

The user provides:
- **topic** (required): The subject or pasted text to turn into an infographic
- **style** (optional): A style ID like `ukiyo-e`, `bauhaus`, `sumi-e`, etc.
- **layout** (optional): A layout ID like `bento-grid`, `hub-spoke`, `iceberg`, etc.
- **aspect_ratio** (optional): e.g. `16:9`, `9:16`, `1:1`. Default: `16:9`

If style or layout are not specified, recommend 3 combinations and let the user pick.

## Reference Files

All reference files live in this skill's `references/` directory:

- `references/analysis-framework.md` — Framework for analyzing content
- `references/structured-content-template.md` — Template for structuring content
- `references/base-prompt.md` — Base prompt template for image generation
- `references/styles/{style-id}.md` — Style definitions (60+ styles)
- `references/layouts/{layout-id}.md` — Layout definitions (20 layouts)

**IMPORTANT**: Read the relevant reference files before each step. These contain the secret sauce — detailed visual instructions, color palettes, compositional patterns, and visual metaphor mappings that make the infographics excellent.

## Instructions

### Step 1: If style/layout not specified, recommend combinations

1. Read `references/analysis-framework.md`
2. Analyze the user's topic using the framework (just do the analysis yourself — you ARE Claude)
3. Based on the content type, complexity, and audience, recommend 3 layout×style combinations:
   - **best_match** — most appropriate for the content
   - **creative** — unexpected, visually striking pairing
   - **accessible** — broadest appeal, balances clarity and aesthetics
4. For each recommendation, give a 1-2 sentence rationale
5. Ask the user to pick (1/2/3 or name their own)

To make good recommendations, consult the analysis framework's Content Type Classification table which maps content types to layouts and styles.

### Step 2: Analyze content

Read `references/analysis-framework.md` and apply it to the topic. Produce a thorough analysis covering:

- Content type classification (timeline, process, comparison, hierarchy, etc.)
- Learning objectives (what the viewer will understand)
- Audience analysis
- Complexity assessment
- Visual opportunity mapping
- Data verbatim extraction (preserve all statistics, quotes, dates EXACTLY)

This analysis is internal working material — don't dump it on the user. Just mention you're analyzing.

### Step 3: Structure content

Read `references/structured-content-template.md` and transform the analysis into designer-ready structured content:

- Title and overview
- Sections with key concepts, content points, visual elements, and text labels
- All data points preserved verbatim
- Clear visual element descriptions per section

### Step 4: Craft the image generation prompt

This is where it all comes together. Read:
- `references/layouts/{selected-layout-id}.md` — the full layout definition
- `references/styles/{selected-style-id}.md` — the full style definition
- `references/base-prompt.md` — the base prompt template

Then craft a rich, detailed image generation prompt with these sections:

**Fixed header** (one line):
```
Create a single {aspect_ratio} infographic in {Style Name} style using a {Layout Name} layout. All text in English. Use rich visual scenes with clear hierarchy and ample whitespace.
```

**Layout Guidelines**: Adapt the generic layout structure to this specific content. Replace placeholders with content-specific descriptions.

**Style Guidelines**: Include the FULL style description plus:
- Color Palette with specific usage instructions
- Visual Elements list
- A Compositional Patterns table mapping content structures to style-specific compositions
- Visual Metaphor Mappings that translate EACH content section into a concrete, style-specific visual scene
- Typography instructions

**Content**: Describe each content section as a VISUAL SCENE. Each section must have:
- A descriptive title (e.g., "CENTER HUB: The Castle")
- A vivid description of what to DRAW — objects, characters, spatial layout, colors, mood
- The exact text to render

**Text Labels**: Organize ALL text that should appear in the infographic, grouped by area: Title, Hub/Center, Section Labels, Section Content, Key Phrases, Attribution.

### CRITICAL PROMPT CRAFTING RULES

- Describe VISUAL SCENES, not abstract concepts. Tell the image generator what to DRAW.
- Visual metaphor mappings must be SPECIFIC to the content AND style (e.g., for ukiyo-e: "Trust Signals → guardian komainu statues or a samurai standing watch")
- Keep all source quotes and data VERBATIM — never summarize or rephrase
- The prompt should be 1500-3000 words — rich enough for Gemini to produce a detailed infographic

Save the crafted prompt to a file for reference.

### Step 5: Generate the image

The ONLY step that needs an external API call. Use the Sumi backend's image generator:

```bash
cd /Users/paolo/playground/sumi/backend && source .venv/bin/activate && python -c "
import asyncio
from sumi.engine.image_generator import generate_image

PROMPT = open('/tmp/sumi-prompt.md').read()
ASPECT_RATIO = 'ASPECT_RATIO_HERE'
OUTPUT_PATH = '/tmp/sumi-infographic.png'

async def main():
    path = await generate_image(prompt=PROMPT, output_path=OUTPUT_PATH, aspect_ratio=ASPECT_RATIO)
    print(f'Image saved: {path}')

asyncio.run(main())
"
```

Before running this:
1. Write the crafted prompt to `/tmp/sumi-prompt.md`
2. After generation, open the image with `open <path>` on macOS
3. Tell the user the file path

### Step 6: Iterate (if requested)

If the user wants to tweak:
- **Different style/layout**: Re-do steps 4-5 with new references (skip analysis/structuring)
- **Prompt adjustments**: Edit the saved prompt and re-run step 5
- **Content changes**: Re-do from step 2

## Available Styles

aged-academia, airline-travel-poster, art-nouveau, art-nouveau-mucha, atomic-age, axonometric, bauhaus, bold-graphic, botanical-illustration, chalkboard, charley-harper, claymation, constructivism, corporate-memphis, craft-handmade, cubism, daniel-clowes, de-stijl, dia-de-muertos, dr-seuss, fantasy-map, futurism, golden-age-comics, googie, ikea-manual, isometric-technical, isotype, jack-kirby, kandinsky, kawaii, keith-haring, knolling, ligne-claire, matsumoto, memphis, moebius, origami, osamu-tezuka, patent-drawing, paul-rand, pixel-art, pop-art-lichtenstein, renaissance-diagram, richard-scarry, rinpa, saul-bass, shan-shui, storybook-watercolor, studio-ghibli, subway-map, sumi-e, superflat, synthwave, technical-schematic, tibetan-thangka, treasure-map, ukiyo-e

## Available Layouts

bento-grid, binary-comparison, bridge, circular-flow, comic-strip, comparison-matrix, dashboard, funnel, hierarchical-layers, hub-spoke, iceberg, isometric-map, jigsaw, linear-progression, periodic-table, story-mountain, structural-breakdown, tree-branching, venn-diagram, winding-roadmap
