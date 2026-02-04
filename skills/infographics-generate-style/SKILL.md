---
name: infographics-generate-style
description: Generates a new infographic style definition from reference material (images, PPTX files, URLs, or verbal descriptions). Analyzes the source, extracts design DNA, and writes a style markdown file. Use when user asks to "create a style", "new infographic style", "generate style", "add a style from", or "extract style from".
---

# Infographic Style Generator

Analyzes source material — PPTX files, images, URLs, or verbal descriptions — and produces a structured style definition that the LLM-based infographic generation pipeline can use.

## Usage

```
/infographics-generate-style path/to/reference.pptx
/infographics-generate-style path/to/screenshot.png
/infographics-generate-style https://example.com/design-page
/infographics-generate-style "dark tech aesthetic with neon accents"
```

## Source: $ARGUMENTS

---

## Step 1: Analyze the Source Material

Adapt your analysis approach to the source type:

### PPTX files
PPTX files are ZIP archives containing XML. Unzip to a temp directory and extract:
- **Theme colors** from `ppt/theme/*.xml` — look for `<a:clrScheme>` with dk1, lt1, dk2, lt2, accent1–6
- **Fonts** from `<a:majorFont>` and `<a:minorFont>` in theme XML
- **Slide dimensions** from `ppt/presentation.xml` — `<p:sldSz>` (EMUs ÷ 914400 = inches)
- **Backgrounds** from `ppt/slideMasters/*.xml` and actual slides — solid fills, gradients, image treatments
- **Text styling** from slide XML — font sizes (hundredths of a point), weights, spacing, alignment
- **Layout patterns** from `ppt/slideLayouts/*.xml` — names and structure of content arrangements
- **Recurring elements** from `ppt/slides/slide*.xml` — panels, dividers, image treatments, repeated shapes

### Images / screenshots
Read the image files directly (Claude is multimodal). Identify:
- Dominant and accent colors (estimate hex values)
- Typography characteristics (serif/sans-serif, weight, size hierarchy)
- Layout grid and compositional structure
- Recurring visual motifs and textures
- Background treatments
- Illustration style (flat, 3D, hand-drawn, photographic, etc.)

### URLs / websites
Fetch the page and analyze visual design. Extract same properties as images.

### Verbal descriptions
Work with the user to pin down concrete visual properties. Ask clarifying questions about colors, typography feel, layout preferences, and reference examples.

---

## Step 2: Understand the Target Format

Style definitions live at: `backend/sumi/references/data/styles/{style-id}.md`

The filename becomes the style ID (kebab-case). The loader at `backend/sumi/references/loader.py` parses them automatically.

### Parsed fields
The `StyleRef` dataclass extracts:
- **`id`**: From filename stem (e.g., `adobe-slide` from `adobe-slide.md`)
- **`name`**: From H1 heading, converted via `_kebab_to_title()` or `_NAME_OVERRIDES` dict
- **`best_for`**: Text content of the `## Best For` section
- **`color_palette_desc`**: Text content of the `## Color Palette` section
- **`content`**: Full markdown (passed to the LLM during generation)

### Name handling
The loader converts kebab-case IDs to title case automatically (`cyberpunk-neon` → `Cyberpunk Neon`). If the style name needs special casing (e.g., acronyms, proper nouns, non-standard capitalization), add an entry to `_NAME_OVERRIDES` in `backend/sumi/references/loader.py`:

```python
_NAME_OVERRIDES: dict[str, str] = {
    "ukiyo-e": "Ukiyo-e",
    "art-nouveau": "Art Nouveau",
    # add new override here if needed
}
```

---

## Step 3: Write the Style Definition

Use this template. All sections are important — the full markdown is passed to the LLM during infographic generation.

```markdown
# {style-id}

{1-2 sentence description capturing the essence and visual identity of the style.}

## Color Palette

- Primary: {2-4 dominant colors with hex codes}
- Background: {Background colors/treatments with hex codes}
- Accents: {3-6 accent colors with hex codes}
- Text: {Text color rules — what color on what background}

### Palette Combinations

| Combination | Colors |
|-------------|--------|
| {Name} | {Color A + Color B + Color C + ...} |
{3-4 combinations covering different moods/contexts}

## Variants

| Variant | Focus | Visual Emphasis |
|---------|-------|-----------------|
| **{Name}** | {Use case} | {Key visual characteristics} |
{2-4 variants offering meaningful visual diversity within the style}

## Visual Elements

- {10-15 bullet points defining the visual vocabulary}
- {What shapes, textures, treatments ARE used}
- {What is explicitly NOT used — helps the LLM avoid wrong choices}
- {Specific rendering rules: stroke weights, corner radii, fills, effects}

## Compositional Patterns

| Content Structure | Composition | Reference |
|-------------------|-------------|-----------|
| Hierarchy/levels | {How this style represents hierarchy} | {Visual reference} |
| Flow/process | {How this style represents sequences} | {Visual reference} |
| Comparison | {How this style represents side-by-side analysis} | {Visual reference} |
| Categories | {How this style groups related items} | {Visual reference} |
{Map 6-10 common content structures to style-specific compositions}

## Visual Metaphor Mappings

| Abstract Concept | {Style Name} Metaphor |
|------------------|----------------------|
| Data/information | {How this style visualizes data} |
| Processes | {How this style represents steps/flows} |
| Connections | {How this style shows relationships} |
| Growth | {How this style represents increase/progress} |
| Time | {How this style represents temporal progression} |
| Hierarchy | {How this style shows importance/ranking} |
{Map 10-15 abstract concepts to concrete visual representations}

## Typography

- {Font style: serif, sans-serif, hand-drawn, monospace, etc.}
- {Weight hierarchy: what weight for headings, body, captions}
- {Size hierarchy: relative or absolute size relationships}
- {Special treatments: letter-spacing, line-height, effects}
- {Alignment rules}
- {What to avoid}

## Best For

{Comma-separated list of ideal use cases — this is used by the recommendation engine to match styles to content}
```

### Calibrating detail level

- **Simple styles** (like `bold-graphic`, `corporate-memphis`): Skip Compositional Patterns and Visual Metaphor Mappings. Keep Visual Elements to 6-8 items. These are styles where the visual identity is immediately obvious and the LLM needs less guidance.
- **Mid-complexity styles** (like `technical-schematic`): Include Variants and detailed Visual Elements. Add Compositional Patterns if the style has specific ways of handling different content types.
- **Rich styles** (like `art-nouveau`, `ukiyo-e`): Include all sections. These styles have deep visual vocabularies that benefit from explicit mapping.

The right level depends on how much ambiguity the LLM would face. A style like "pixel art" is self-explanatory; a style like "ukiyo-e" needs compositional guidance to avoid generic results.

---

## Step 4: Validate

After writing the file:

1. **Check the loader** — confirm `_kebab_to_title()` produces the correct display name. If not, add to `_NAME_OVERRIDES` in `backend/sumi/references/loader.py`.
2. **Review the H1** — must match the filename stem exactly (e.g., `# adobe-slide` in `adobe-slide.md`).
3. **Review section headings** — must use `## Color Palette`, `## Best For` exactly (the loader regex depends on these).
4. **Read back the file** to verify formatting.

---

## Existing Styles (for reference and differentiation)

There are currently 20 styles in the system. Make sure the new style is **distinct** from all of these:

aged-academia, adobe-slide, art-nouveau, bold-graphic, chalkboard, claymation, corporate-memphis, craft-handmade (default), cyberpunk-neon, ikea-manual, kawaii, knolling, lego-brick, origami, pixel-art, storybook-watercolor, subway-map, technical-schematic, ui-wireframe, ukiyo-e

If the new style overlaps significantly with an existing one, call it out to the user and suggest differentiation strategies.
