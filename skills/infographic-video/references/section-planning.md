# Section Planning Guide

How to split a meeting summary into sections for video generation.

## Target Structure

For a ~5 minute video, split into **6 sections** of roughly equal spoken length (~50s each).

## Section Arc

Follow a narrative arc that mirrors how meetings naturally flow:

| # | Role | Example |
|---|------|---------|
| 1 | **Opening / Context** | Why this meeting matters, who's involved, what's at stake |
| 2 | **Strategic Framework** | The big picture — journey, lifecycle, landscape |
| 3 | **Core Concept** | Mission statement, central thesis, key message |
| 4 | **Methodology / Model** | How it works in practice — framework, process, operating model |
| 5 | **Measurement** | How success is measured — KPIs, metrics, value framework |
| 6 | **Future / Call to Action** | What's next, technology shifts, team invitation |

## How to Extract Sections

1. Read the full meeting summary
2. Identify the major topic shifts (usually 4-8 in a 1-hour meeting)
3. Group related topics into 6 balanced sections
4. For each section, extract:
   - Key facts and data points (verbatim)
   - Notable quotes with attribution
   - Concrete examples or proof points
   - The "so what" — why this matters
5. Write a `source.md` per section with the extracted content

## Word Count Targets

| Duration Target | Words per Section |
|-----------------|-------------------|
| ~40s | ~120 words |
| ~50s | ~145 words |
| ~60s | ~170 words |

TTS speech rate is approximately 2.8-3.0 words per second.

## Section source.md Format

```markdown
# [Section Title]

## [Subsection 1]
- Bullet point with key fact
- Another fact
- Concrete example if available

## [Subsection 2]
- More content
- Data points verbatim

## Key Quote
> "Exact quote from the meeting" — Speaker Name
```

## Layout × Style Selection

Vary the visual style across sections to maintain viewer interest. Avoid using the same layout or style for adjacent sections.

**Proven combinations:**

| Content Type | Layout | Style |
|--------------|--------|-------|
| Multi-topic overview | `bento-grid` | `corporate-memphis` |
| Journey / lifecycle | `winding-roadmap` | `storybook-watercolor` |
| Central concept | `hub-spoke` | `bold-graphic` |
| Sequential process | `linear-progression` | `technical-schematic` |
| Metrics / dashboard | `dashboard` | `corporate-memphis` |
| Technology / future | `circular-flow` | `cyberpunk-neon` |
| Comparison | `binary-comparison` | `corporate-memphis` |
| Hierarchy | `hierarchical-layers` | `craft-handmade` |
| Categories | `periodic-table` | `bold-graphic` |
| Narrative | `comic-strip` | `storybook-watercolor` |
