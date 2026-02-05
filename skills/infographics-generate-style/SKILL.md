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

## Pre-Flight Gate

Before investing time in style generation, answer these 3 questions. If any answer is "no", stop and tell the user why.

1. **Is this a visual style, not a rendering medium?** Mediums (chalkboard, claymation, craft-handmade) describe *how* something is rendered but lack a distinctive visual vocabulary — they produce generic images "rendered as chalk." A style has specific colors, motifs, compositional rules, and recognizable visual DNA.

2. **Can this style produce recognizably different images across 3+ layout types?** Test mentally: would a bento-grid, a linear-progression, and a tree-branching layout each look distinct and good in this style? Styles that only work for one layout type (e.g., subway-map) are too narrow for the library.

3. **Does this overlap with an existing library style?** If yes, proceed only if you can write at least 5 specific Anti-Patterns differentiating the new style from the existing one. If you can't articulate the difference, the style is redundant.

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

**Reference images — use selectively**: When the user provides images as style references, save 2-4 of the strongest/most representative ones in a `references/` subdirectory next to the style file. These can be passed as `--ref` images during generation.

**However, reference images can add noise for illustration styles.** Photos from Unsplash are photographs, not illustrations — they guide palette and motifs but push the generator toward over-decoration and photorealism. Only use reference images when:
- The user provides actual artwork/illustrations in the target style
- The style is photographic or realistic in nature
- The style is from a cultural tradition where specific visual details matter and the text description alone is insufficient

For most illustration styles (comics, graphic design, ink-based, geometric), a well-written style definition with strong Anti-Patterns produces better results than adding photographic references.

### URLs / websites
Fetch the page and analyze visual design. Extract same properties as images.

### Verbal descriptions
Work with the user to pin down concrete visual properties. Ask clarifying questions about colors, typography feel, layout preferences, and reference examples.

---

## Step 2: Understand the Target Format by Reading Existing Styles

**Before writing anything, read 2-3 existing style files** from `backend/sumi/references/data/styles/` to calibrate on the actual format, tone, and detail level used in practice. Pick styles that are adjacent to the one you're creating — they'll also serve as Anti-Pattern targets in Step 3.

This step is critical. Writing from an abstract template alone produces inconsistent structure, mismatched section formatting, and weaker Anti-Patterns. Reading real files ensures your output matches the established library standard.

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

### CRITICAL: Write for the image generation model, not a design textbook

The style definition is a **prompt** that guides an AI image generator. Every description must be vivid, concrete, and visually evocative — as if you're painting a picture with words. The generation model responds to sensory language, not abstract theory.

**DO — use concrete, evocative descriptions:**
- "Large bold circles with luminous colored halos radiating outward — pink glow around black, blue aura around yellow"
- "Sweeping thin black lines shooting diagonally across the entire composition"
- "Warm cream parchment-toned background with subtle tonal variation — never sterile white"
- "Faces built from overlapping bold geometric shapes — eyes as concentric colored rings, noses as sharp triangles"

**DON'T — use abstract design theory:**
- ~~"Pure geometric primitives as foundational shapes"~~ (too abstract, produces flat clip-art)
- ~~"Asymmetric but rigorously balanced compositions"~~ (design principle, not a visual instruction)
- ~~"Primary colors assigned to shapes per Kandinsky's theory"~~ (academic reference, not actionable)
- ~~"Modular, repeatable units assembled into larger structures"~~ (systems thinking, not visual)

The difference is stark: theory-oriented descriptions produce sterile, diagrammatic output. Prompt-oriented descriptions produce expressive, artistic output. Always ask: "Can the model see what I'm describing?" If the answer requires understanding design history, rewrite it.

```markdown
# {style-id}

{1-2 sentence description capturing the essence and visual identity of the style. Make it vivid — describe what you SEE, not what design movement it belongs to.}

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

## Anti-Patterns

{THE MOST IMPORTANT SECTION. This is what prevents the generation model from producing generic output. Write at least 8 anti-patterns for styles with close siblings in the library, at least 5 for unique styles. Be aggressive, specific, and repetitive.}

- **NOT {adjacent-style-id}** — {explain the specific visual difference, e.g., "NOT bauhaus — Bauhaus uses primary colors in geometric grids; this style uses earth tones in organic flowing forms"}
- **NOT {another-adjacent-style-id}** — {explain difference}
- **NOT {most likely wrong interpretation}** — {what it looks like when the model gets it wrong}
- **NOT {sterile/corporate version}** — {describe the generic fallback to avoid}
- {Quantitative threshold}: "{maximum N shapes per figure}", "{at least N% negative space}", "{no more than N colors per composition}"
- {Repeat the single most important constraint with emphasis}: "Flat fills only. NO gradients. ZERO shading. Flat. Flat. Flat."
- {End with a grounding sentence}: "This must look like [specific real-world artifact from a specific year/place], not [generic fallback]"

## Reference Images

{If reference images were provided, list them here with brief descriptions of what each contributes to the style definition. These are passed as --ref during generation.}

- `references/{filename}` — {what this image demonstrates about the style}

## Best For

{Comma-separated list of ideal use cases — this is used by the recommendation engine to match styles to content}
```

### Non-negotiable sections

**Every style — regardless of complexity — MUST include:**
- **Color Palette** with hex codes and Palette Combinations table
- **Variants** table (at least 3 variants)
- **Visual Elements** (at least 10 bullets)
- **Anti-Patterns** (at least 5, ideally 8+)
- **Best For**

Never skip Anti-Patterns for "simple" styles. Styles that seem self-explanatory (like "pixel art" or "chalkboard") actually need strong Anti-Patterns most, because the model's default interpretation of these terms is often too generic to produce distinctive infographics.

**Optional sections** (include for rich/artistic styles, skip for straightforward ones):
- Compositional Patterns table
- Visual Metaphor Mappings table

### Writing effective Anti-Patterns (most impactful section)

Anti-Patterns have more impact on output quality than any other section. A style with weak Visual Elements but strong Anti-Patterns produces better images than the reverse. Follow these rules:

**1. Name adjacent styles by their library ID:**
- Good: "**NOT bauhaus** — Bauhaus uses primary colors in strict geometric grids with functional clarity. This style uses earth tones in organic curves."
- Bad: "NOT geometric" (too vague — half the library is geometric)

**2. Include quantitative thresholds:**
- "Maximum 6 shapes per figure — if you can count more than 10, it is TOO detailed"
- "At least 30% of the canvas must be open background color"
- "No more than 4 colors per composition excluding black and white"

**3. Repeat the #1 constraint with aggressive emphasis:**
- "Flat fills only. NO gradients. ZERO shading anywhere. Not even subtle gradients. Flat. Flat. Flat."
- The generation model responds to repetition — saying it once is not enough for the most critical constraint.

**4. Name the most likely failure mode specifically:**
- "The most common mistake is adding decorative scattered elements to fill empty space. DO NOT fill empty space. The empty space IS the design."

**5. End with a grounding sentence:**
- "This must look like a 1984 Keith Haring Pop Shop poster, not a generic flat illustration with thick outlines."
- Anchoring to a specific real-world artifact gives the model a concrete target.

**Example — Charley Harper anti-patterns (strong):**
```
- **NOT atomic-age/mid-century generic** — While Harper IS mid-century, his style is specifically
  about EXTREME geometric reduction of NATURE subjects. Not starbursts, not boomerangs, not Googie.
- **NOT corporate Memphis** — Memphis uses pastel humanoid figures with noodle arms. Harper uses
  bold-colored geometric animals. The reduction is toward geometry, not toward soft blobby shapes.
- **NOT clip art** — Clip art has too many curves and details. Harper animals are geometrically
  pure — a bird body is a literal triangle, not a rounded cartoon blob.
- Maximum 8 geometric shapes per animal. If you can count more than 10, reduce further.
- This must look like a mid-century wildlife serigraph print where a cardinal is literally a red
  triangle with eyes, not a generic flat illustration of a bird.
```

### Writing effective Visual Elements

Each bullet in Visual Elements should pass the **"can you see it?"** test. Compare:
- Bad: "Dynamic diagonal compositions" → vague, the model doesn't know what to draw
- Good: "Sweeping thin black lines shooting diagonally across the entire canvas, creating tension between curved arcs and sharp angles" → the model can render this

Specific patterns that produce strong results:
- Describe **color interactions**: "pink glow radiating around black circles", not "accent colors"
- Describe **surface quality**: "warm cream parchment background with subtle tonal variation", not "off-white background"
- Describe **how figures are built**: "faces constructed from overlapping triangles and circles — eyes as concentric colored rings", not "geometric figure constructions"
- Describe **what NOT to render**: "never sterile white", "not clip-art", "not a flat corporate diagram"

---

## Step 4: Validate

After writing the file:

1. **Check the loader** — confirm `_kebab_to_title()` produces the correct display name. If not, add to `_NAME_OVERRIDES` in `backend/sumi/references/loader.py`.
2. **Review the H1** — must match the filename stem exactly (e.g., `# adobe-slide` in `adobe-slide.md`).
3. **Review section headings** — must use `## Color Palette`, `## Best For` exactly (the loader regex depends on these).
4. **Read back the file** to verify formatting.

## Step 5: Test Generation

Generate a test infographic using the new style definition to catch issues that only surface at generation time.

1. **Generate a test infographic** using simple content (e.g., "5 steps to make coffee" or "3 types of renewable energy") — something with enough structure to exercise the style across headings, labels, and illustrations.
2. **If the user provided reference artwork**, include it as `--ref` images. Do NOT use generic stock photos as references — they push illustration styles toward photorealism.
3. **Diagnose common failure modes:**
   - **Too flat/sterile**: The Visual Elements section uses abstract theory instead of vivid descriptions. Rewrite with concrete, sensory language.
   - **Too generic / looks like another style**: The Anti-Patterns section is too weak. Add more entries that name specific adjacent styles and include quantitative thresholds.
   - **Wrong color mood**: The Color Palette describes colors by name only. Add emotional/sensory qualities ("warm cream parchment", "dense velvety black", "luminous colored halos").
   - **Lifeless figures**: People/characters described generically. Add specific construction details ("eyes as concentric colored rings, nose as sharp triangle, hair as sweeping arcs").
   - **Over-decorated / too busy**: Too many Visual Elements describing motifs. Reduce to fewer elements and add Anti-Patterns like "NO scattered decorative elements", "NO filling empty space".
4. **Iterate** — update the style definition based on test results and regenerate until the output is distinctive and recognizable.

---

## Existing Styles (for reference and differentiation)

There are currently 42 styles in the library. **Read 2-3 of the most adjacent ones** before writing a new style — they are your primary Anti-Pattern targets.

aged-academia, airline-travel-poster, art-nouveau, art-nouveau-mucha, atomic-age, axonometric, bauhaus, bold-graphic, charley-harper, constructivism, de-stijl, dia-de-muertos, fantasy-map, futurism, golden-age-comics, googie, ikea-manual, isometric-technical, isotype, jack-kirby, kandinsky, keith-haring, knolling, ligne-claire, matsumoto, memphis, moebius, origami, osamu-tezuka, patent-drawing, pop-art-lichtenstein, renaissance-diagram, richard-scarry, saul-bass, shan-shui, storybook-watercolor, studio-ghibli, sumi-e, superflat, synthwave, tibetan-thangka, ukiyo-e

If the new style overlaps significantly with an existing one, you must either:
1. Write at least 5 specific Anti-Patterns differentiating the two, or
2. Tell the user the style is redundant and suggest the existing alternative.
