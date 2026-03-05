---
name: az-briefing-builder
description: Transform incomplete or immature product input into a comprehensive AstraZeneca HCP website briefing for AEM Edge Delivery Services. Use when "build briefing", "create briefing", "write briefing", "briefing from scratch", "new site briefing", "turn this into a briefing", or "expand this into a full briefing". The output briefing is designed to be consumed directly by the eds-site-builder skill to generate the website.
---

# AZ Briefing Builder

Transform a simple, incomplete product description into a comprehensive, brand-compliant website briefing that the `eds-site-builder` skill can consume to generate a complete AEM Edge Delivery Services HCP website.

## When to Use

- User provides basic drug/product info and wants a full website briefing
- User has a partial brief (just drug profile, or just clinical data) that needs expanding
- User wants to create a new site and doesn't have a completed briefing yet
- User says "build me a site for [drug]" — generate the briefing first, then hand off to site generation

## What This Skill Does NOT Do

- Does not generate HTML pages or draft files — that's `eds-site-builder`
- Does not modify MLR-approved copy — if input is marked as approved, it's preserved verbatim
- Does not invent clinical data — uses only what's provided or marks sections as `[PLACEHOLDER — requires medical input]`

---

## Instructions

### Step 0: Read Project Context

Before starting, read these files to understand the block library, brand voice, and briefing conventions:

1. `CLAUDE.md` — project architecture, block list, design context, multi-site nav templates
2. `blocks/BLOCK-REFERENCE.md` — HTML markup for every available block
3. `brand/az-brand-voice.md` — AZ UK brand voice rules and copy patterns

These inform every decision in the briefing: which blocks to use, how to write copy, and what structure to follow.

### Step 1: Assess the Input

Read whatever the user provides. It could be anything from a single paragraph to a detailed clinical dossier. Classify each aspect:

| Aspect | Has it? | Quality |
|--------|---------|---------|
| Drug name (brand + generic) | Yes/No | Complete / Partial |
| Drug class / MoA | Yes/No | Detailed / Summary / Missing |
| Indication | Yes/No | Precise / Vague |
| Formulation & dosing | Yes/No | Complete / Partial / Missing |
| Clinical trial data | Yes/No | Full results / Headlines only / Missing |
| Safety profile | Yes/No | Detailed AE table / Summary / Missing |
| Prescribing information | Yes/No | Full PI text / Abbreviated / Missing |
| AE reporting text | Yes/No | Present / Missing |
| References | Yes/No | Complete / Partial / Missing |
| Brand colours | Yes/No | Specified / Missing |
| Approval code & DOP | Yes/No | Specified / Missing |
| Desired pages / navigation | Yes/No | Explicit / Implied / Missing |
| Tagline | Yes/No | Specified / Missing |
| Image assets / CDN | Yes/No | URLs provided / Descriptions only / Missing |

Report this assessment to the user. For missing critical items, explain what's needed and whether you can generate reasonable defaults or must leave placeholders.

### Step 2: Determine Fidelity Level

Ask the user one question:

> **Is any of this copy MLR-approved and must be used verbatim, or should I write/expand the copy freely?**

This determines the fidelity instruction at the top of the briefing:
- **Strict**: Copy is MLR-approved → briefing will say "must be used exactly as written"
- **Flexible**: Copy is draft/indicative → briefing will say "copy is indicative and may be adapted for web presentation"

If the user doesn't answer or says "just make it work", default to **flexible**.

### Step 3: Build the Drug Profile (Section 1)

Generate the drug profile table. Use the input verbatim where provided; fill gaps with reasonable defaults or placeholders:

```markdown
## 1. Drug Profile

| Field | Detail |
|-------|--------|
| Brand name | {BRAND} |
| Generic name | {generic} |
| Drug class | {class} |
| Indication | {indication} |
| Formulation | {formulation} |
| Dosing | {dosing} |
| Approval | MHRA — {date} |
| Brand colour | {hex} |
| Accent colour | {hex} |
| Approval code | {code} |
```

**Brand colour selection** — if not specified, choose a colour that:
- Is distinct from AZ Magenta (#830051) and AZ Gold (#EFAB00)
- Reflects the therapy area (e.g., teal/green for respiratory, warm tones for cardiology, deep blue for oncology)
- Meets WCAG AA contrast on white background
- Pair with a complementary accent colour

**Approval code** — if not provided, use `[GB-XXXXX — assign before MLR submission]`

Add a brand rule paragraph:

```markdown
{BRAND} brand rule: {BRAND} always appears in capitals, with ® on first mention per page. Generic name ({generic}) appears in lowercase parentheses on first mention. {If tagline provided: The approved tagline "{tagline}" may only be used verbatim — no variations permitted.}
```

### Step 4: Build Mechanism of Action (Section 2)

Write or expand the MoA section. Follow the AZ brand voice:
- Open with what the drug IS (class, target)
- Explain the disease biology that the drug addresses
- List the pharmacological effects as bullet points
- Close with selectivity/safety differentiation if relevant

If the user provided detailed MoA text, use it. If only a summary, expand it using the drug class and indication as context. If missing, write `[PLACEHOLDER — requires medical/scientific input]`.

Always include superscript reference numbers (¹ ² ³) pointing to the references section.

### Step 5: Build Clinical Programme (Section 3)

For each clinical trial provided:

```markdown
### {TRIAL-NAME} (Phase {X}, {descriptor})

- Design: {design}
- Population: {population}
- Duration: {duration}
- Primary endpoint: {endpoint}
- Key secondary endpoints: {endpoints}
- Publication: {authors} {journal} {year}; {volume}: {pages}

Key results:

| Endpoint | {BRAND} (n=X) | Placebo/Comparator (n=X) | Treatment effect |
|----------|--------------|--------------------------|------------------|
| {primary} | X% | Y% | Δ Z%; P<0.001 |
```

**Rules:**
- Use the trial programme name consistently (e.g., CLARITY, TRAJECTORY)
- Include ALL endpoints the user provided — do not summarise away data points
- Format treatment effects consistently: absolute difference (Δ), hazard ratio (HR), or relative reduction as appropriate
- If only headline results are given, structure them into the table format but flag: `[Note: full results table requires medical review]`
- If no trial data provided, write placeholder: `[PLACEHOLDER — clinical programme data required]`

### Step 6: Build Safety Profile (Section 4)

Structure safety data into these subsections:
1. Most common adverse events table (≥5% incidence)
2. System-specific safety sections (cardiac, hepatic, GI, etc. — as relevant to the drug class)
3. Key safety findings summary (SAEs, discontinuation, mortality, MACE if relevant)
4. Special populations (T2D, elderly, renal, hepatic, pregnancy)

If the user provided raw AE data, format it. If only a summary, expand it into the structure. If missing, placeholder the entire section.

### Step 7: Build Prescribing Information (Section 5)

Generate an abbreviated PI from the drug profile and safety data. This appears as an accordion on every page. Structure:

```markdown
## 5. Prescribing Information (abbreviated — for every page footer)

{BRAND} ({generic}) {formulations}. Please refer to the Summary of Product Characteristics (SmPC) before prescribing. Indication: {indication}. Dosage and administration: {dosing}. Contraindications: {contraindications}. Warnings and precautions: {warnings}. Interactions: {interactions}. Side effects: Very common (≥1/10): {AEs}. Common (≥1/100 to <1/10): {AEs}. Legal category: POM. Pack and price: {if available, else [to be confirmed]}. Marketing authorisation holder: AstraZeneca UK Ltd. MA number: {if available, else [PLGB XXXXX/XXXX]}. Full prescribing information available from: AstraZeneca UK Ltd, 2 Pancras Square, London N1C 4AG. {approval code} | DOP: {date}.
```

If insufficient data to write a complete PI, flag it: `[PLACEHOLDER — full PI text requires regulatory/medical input]`

### Step 8: Build AE Reporting & References (Sections 6-7)

**AE Reporting** — standard text unless the user specifies different:

```markdown
## 6. Adverse Event Reporting (for every page footer)

Adverse events should be reported. Reporting forms and information can be found at www.mhra.gov.uk/yellowcard or search for MHRA Yellow Card in the Google Play or Apple App Store. Adverse events should also be reported to AstraZeneca by visiting contactazmedical.astrazeneca.com or by calling 0800 783 0033.
```

**References** — compile from all superscript references used in the briefing:

```markdown
## 7. References (for every page footer)

1. {First author} et al. {Journal} {Year}; {Volume}: {Pages}.
2. ...
```

### Step 9: Define Site Navigation (Section 8)

Based on the available content, define the site pages. Use this decision framework:

| Content available | Recommended pages |
|-------------------|-------------------|
| Drug profile + MoA + trials + safety + dosing | Home, Disease Context, Clinical Data, How {Drug} Works, Safety/Dosing/Monitoring, HCP Resources |
| Drug profile + trials + safety (no detailed MoA) | Home, Clinical Data, Safety & Dosing, HCP Resources |
| Drug profile only (minimal data) | Home, About {Drug}, HCP Resources |
| Combination therapy with complex data | Home, Disease Context, Monotherapy Data, Combination Data, Safety/Dosing, Resources |

**Navigation rules:**
- Maximum 6 top-level pages (plus Home)
- Single-product sites: flat nav, no dropdowns
- Page names should be clinical and specific, not generic ("CLARITY Data" not "Clinical Evidence")
- URL slugs: lowercase, hyphenated, no abbreviations

```markdown
## 8. Site Navigation

- Top bar links: Contact Us (https://www.astrazeneca.co.uk/contact-us.html) | AZ Employee Login (https://login.astrazeneca.com)
- Main navigation pages: {Page 1} | {Page 2} | {Page 3} | ...
- Utility: Search | Login
```

### Step 10: Write Page Content (Section 9)

This is the largest section. For each page, write the full content specification.

**Start with the fidelity instruction:**

```markdown
## 9. Page Content

{If strict: IMPORTANT: All copy below is final and MLR-approved. It must be used exactly as written — do not modify, rephrase, or abbreviate any text.}
{If flexible: Copy below is indicative and may be adapted for web presentation while preserving all clinical claims and data points verbatim.}

Each page must end with expandable sections for Prescribing Information, Adverse Event Reporting, and References (see sections 5, 6, and 7 above).

{BRAND} brand rule: {brand rule from Step 3}
```

**For each page, follow this template:**

```markdown
### PAGE {N}: {Page Name}
URL path: /{sitename}/{slug}

#### Section {N} — {Description} ({visual hint})
Block: {block-name}
{Section metadata: Style: highlight/light — if applicable}

{If image needed: Image: {CDN URL or description for image generation}}

- Heading: {heading text}
- Body text: {body text with superscript references}
- Call to action: {CTA text} → /{sitename}/{target-slug}

#### Page metadata
- Title: {SEO title | Drug Name | AstraZeneca UK}
- Description: {Meta description, 150-160 chars}
```

**Block selection rules** — choose blocks based on content intent:

| Content pattern | Block | When to use |
|----------------|-------|-------------|
| Full-width image with text overlay | `hero-teaser` | Page hero, first section of key pages |
| Page header, text only | `title` | Data pages, resource pages that don't need a hero |
| Centred lead-in text | `introduction` | Section openers, key stat callouts |
| Image + text side-by-side | `columns-teaser` | MoA explanations, dosing details, 2-column content |
| 3 equal cards with images | `cards-teaser` | Benefit cards, resource cards, feature highlights |
| Tabbed content panels | `tabs-large` | Multiple trials, treatment arms, before/after comparisons |
| Data table | `table-data` | Monitoring schedules, AE tables, trial results |
| Sliding content panels | `carousel-teaser` | Headline statistics, key data points (4+ items) |
| Expandable FAQ/details | `accordion` | PI footer, disease pathways, detailed clinical content |

**Section background alternation** — use `section-metadata Style` to create visual rhythm:
- Default (white) → `light` (#f8f8f8) → default → `highlight` (#f4eef2 with magenta border)
- Never use two consecutive sections with the same background style
- Hero sections are always default (no section-metadata)
- The PI accordion at the bottom is always default

**Copy writing rules** (for flexible mode — when generating copy):
- Follow AZ brand voice: clinically authoritative, supportively warm, evidence-led
- Lead with the patient benefit, not the drug name
- Every clinical claim needs a superscript reference number
- Use UK English spelling (e.g., "favourably", "recognised", "programme")
- No contractions in clinical copy
- Statistics: always include the comparator, confidence interval or p-value
- CTA text: action verbs ("Explore", "View", "Learn about") + specific target ("the CLARITY data", "dosing information")
- Headings: bold, specific, data-forward where possible ("37% achieved fibrosis improvement" not "Clinical results")

**Home page structure** (standard pattern):
1. Hero with product headline + key benefit statement + CTA to data page
2. Three benefit cards (cards-teaser) — headline stats linking to relevant pages
3. MoA or differentiator teaser (columns-teaser, highlight background)
4. PI accordion

**Clinical data page structure:**
1. Title or hero
2. Headline statistics carousel (carousel-teaser, light background)
3. Detailed trial data in tabs (tabs-large) — one tab per trial
4. PI accordion

**Safety/dosing page structure:**
1. Title
2. Dosing regimen (columns-teaser, highlight background)
3. Key safety topic cards (cards-teaser)
4. Monitoring schedule table (table-data, light background)
5. Drug interactions (columns-teaser)
6. PI accordion

**Disease context page structure:**
1. Hero with disease headline
2. Disease burden cards (cards-teaser)
3. Disease pathway accordion (accordion, light background)
4. Patient identification section (introduction, highlight background)
5. PI accordion

**Resources page structure:**
1. Title
2. Resource cards (cards-teaser) — downloadable guides, tools, summaries
3. Contact information (introduction, light background)
4. PI accordion

### Step 11: Define Footer Content (Section 10)

```markdown
## 10. Footer Content

The footer must appear on every page and contain the following elements:

- Logo: AstraZeneca logo (linked to /{sitename}/)
- Approval code: {code} | DOP: {date}
- Copyright: © {year} AstraZeneca. All rights reserved. {BRAND} is a registered trademark of the AstraZeneca group of companies.
- Page links: {list of nav pages}
- Regulatory links: Report Adverse Event (https://yellowcard.mhra.gov.uk/) | Medical Information (https://contactazmedical.astrazeneca.com/) | Privacy Policy (https://www.astrazeneca.co.uk/our-company/privacy-notice.html) | Terms of Use (https://www.astrazeneca.co.uk/our-company/terms-of-use.html) | Accessibility (https://www.astrazeneca.co.uk/accessibility.html)
- Date of preparation: Date of Preparation: {month year}
```

### Step 12: Define Image Assets (Section 11)

**IMPORTANT: Reuse existing images first.** The project has a library of AI-generated images already deployed to CDN across multiple sites. These are high-quality, brand-aligned images that can be reused across sites. **Always check the catalogue below before generating new images.**

Do NOT reuse images from the `velox` site — those are reserved for a specific product.

#### Existing Image Catalogue (deployed to CDN)

Scan the `images/` directory for all available sites and their images:

```bash
for site in images/*/; do
  sitename=$(basename "$site")
  [ "$sitename" = "velox" ] && continue
  [ "$sitename" = "demo" ] && continue
  echo "=== $sitename ==="
  ls "$site"*.jpeg 2>/dev/null | sed "s|images/$sitename/|https://${sitename}-images.pages.dev/|"
  echo ""
done
```

#### Image categories available for reuse

**Heroes** (landscape, tier 1/2 style — suitable for any therapy area):
- `hero-home.jpeg` — available from: eluvion, lumivex, novapril, revantha, treluxia, vitessa, zenturis
- `hero-efficacy.jpeg` — available from: eluvion, lumivex, novapril, revantha, treluxia, vitessa, zenturis
- `hero-moa.jpeg` — available from: eluvion, lumivex, novapril, revantha, vitessa
- `hero-dosing.jpeg` — available from: eluvion, novapril, revantha, treluxia, vitessa
- `hero-safety.jpeg` — available from: novapril, revantha
- `hero-resources.jpeg` — available from: novapril, revantha

**Cards** (square/4:3, tier 2 style):
- `card-efficacy.jpeg` — eluvion, lumivex, novapril, revantha, vitessa, zenturis
- `card-safety.jpeg` — eluvion, lumivex, novapril, revantha, vitessa, zenturis
- `card-dosing.jpeg` — eluvion, lumivex, novapril, revantha, vitessa, zenturis
- `card-clinical-data.jpeg` — lumivex, treluxia, zenturis
- `card-prescribing.jpeg` — lumivex, zenturis
- `card-patient-guide.jpeg` — lumivex, zenturis
- Safety-specific: `card-hepatic.jpeg` (zenturis), `card-gi.jpeg` (zenturis), `card-infections.jpeg` (lumivex, treluxia), `card-anaphylaxis.jpeg` (treluxia), `card-isr.jpeg` (treluxia)

**Columns** (4:3, tier 2/3 style — image+text layouts):
- `columns-moa.jpeg` — lumivex, zenturis
- `columns-admin.jpeg` — lumivex, treluxia, zenturis
- `columns-dosing.jpeg` — treluxia
- `columns-monitoring.jpeg` — lumivex
- `columns-special-pops.jpeg` — lumivex, treluxia, zenturis
- `moa-preview.jpeg` — eluvion, novapril, revantha, vitessa

**Tabs** (trial results imagery):
- `tab-zenith1.jpeg`, `tab-zenith2.jpeg` — zenturis
- `tab-luminance1.jpeg`, `tab-luminance2.jpeg` — lumivex
- `tab-luminos1.jpeg`, `tab-luminos-ocs.jpeg` — treluxia

**Resources & contact**:
- `contact-support.jpeg` — lumivex, novapril, revantha, vitessa
- `contact-medical.jpeg` — eluvion
- `resource-prescribing.jpeg` — eluvion, novapril, vitessa
- `resource-clinical.jpeg` — eluvion, vitessa
- `resource-patient.jpeg` — eluvion, novapril, revantha
- `resource-education.jpeg` — novapril, revantha
- `resource-training.jpeg` — vitessa

**MoA / pathway diagrams**:
- `pathway-cascade.jpeg`, `pathway-disease.jpeg` — eluvion
- `dual-inhibition.jpeg`, `baff-pathway.jpeg`, `april-pathway.jpeg` — novapril
- `bispecific-advantage.jpeg`, `pdl1-pathway.jpeg`, `tigit-pathway.jpeg` — revantha
- `tyk2-il23-cascade.jpeg`, `lumivex-blockade.jpeg` — lumivex
- `vitessa-blockade.jpeg`, `cascade-amplification.jpeg`, `epithelial-damage.jpeg` — vitessa
- `columns-tslp-pathway.jpeg`, `columns-mechanism.jpeg` — treluxia

**Safety-specific**:
- `safety-hepatic.jpeg`, `safety-hypertension.jpeg`, `safety-proteinuria.jpeg` — eluvion
- `safety-helminth.jpeg`, `safety-injection.jpeg`, `safety-zoster.jpeg` — vitessa
- `immune-monitoring.jpeg` — revantha

#### Image selection strategy

1. **First**: Check if an existing image matches the content intent by name and category
2. **Match by role**: A `hero-home.jpeg` from any site works as a homepage hero for a new site — the imagery is abstract/lifestyle, not product-specific
3. **Match by context**: `card-efficacy.jpeg` images show warm lifestyle/scientific imagery suitable for any efficacy card
4. **Tab images**: Trial result tab images are generic enough to reuse across products
5. **Only generate new images** when no existing image fits the content intent, or when the therapy area requires a distinctly different visual (e.g., oncology tier 4 imagery)
6. **Reference the source CDN directly**: Use `https://{source-sitename}-images.pages.dev/{filename}` — no need to copy or redeploy

#### Image asset table format

For each image referenced in the page content, create an entry:

```markdown
## 11. Image Assets

Images reused from existing site CDNs. New images to be generated are marked with [GENERATE].

| Filename | Usage | Source |
|----------|-------|--------|
| hero-home.jpeg | Home — hero | https://eluvion-images.pages.dev/hero-home.jpeg |
| card-efficacy.jpeg | Home — efficacy card | https://novapril-images.pages.dev/card-efficacy.jpeg |
| new-image.jpeg | Home — unique section | [GENERATE] Tier 2: description for AI generation |
```

**Image description rules** (for images marked [GENERATE]):
- Be specific about the scene, not abstract ("woman walking through a sunlit park" not "healthy lifestyle")
- Include the image tier recommendation from the AZ image style system:
  - `tier1` (double-exposure artistic) for homepage heroes, therapy area cards
  - `tier2` (warm lifestyle) for product heroes, patient benefit sections
  - `tier3` (product/device photography) for dosing pages
  - `tier4` (dramatic/abstract) for oncology, severe disease
- Avoid medical imagery that could trigger content safety filters
- Specify orientation needs (landscape for heroes, square for cards)

### Step 13: Write Output & Validate

Write the completed briefing to `sites/{sitename}/briefing.md`.

Before finishing, run these validation checks:

1. **Reference integrity**: Every superscript number (¹ ² ³) in the body text has a corresponding entry in Section 7
2. **Internal link consistency**: Every CTA target (`→ /{sitename}/{slug}`) points to a page defined in Section 9
3. **Nav completeness**: Every page in Section 8 nav has content in Section 9
4. **Image completeness**: Every image referenced in Section 9 has an entry in Section 11
5. **Block validity**: Every `Block:` value matches a block in the AZ block library: `accordion`, `action-bar`, `cards-teaser`, `carousel-teaser`, `columns-teaser`, `embed`, `footer`, `fragment`, `header`, `hero-teaser`, `image`, `introduction`, `table-data`, `tabs-large`, `title`
6. **Placeholder count**: Report how many `[PLACEHOLDER]` markers remain

Report the validation results and any remaining gaps to the user.

### Step 14: Suggest Next Steps

Tell the user:

```
Briefing written to sites/{sitename}/briefing.md

To generate the website from this briefing, run:
/eds-site-builder

Remaining gaps that need input before MLR submission:
- {list any [PLACEHOLDER] sections}
- {list any missing data}
```

---

## Examples

### Minimal input → full briefing

**User provides:**
> "Velustra is a new SGLT2 inhibitor for heart failure. Approved January 2026. 20mg once daily. Main trial showed 24% reduction in CV death or HF hospitalisation."

**Skill generates:** A complete 11-section briefing with:
- Drug profile (SGLT2i, oral 20mg, HF indication)
- MoA section (SGLT2 mechanism in heart failure context)
- Clinical data section with the headline result structured into a table, plus `[PLACEHOLDER]` for secondary endpoints
- Safety section with class-effect SGLT2i safety topics as framework, plus `[PLACEHOLDER]` for trial-specific AE data
- Abbreviated PI (partial, with placeholders)
- Standard AE reporting text
- References (placeholder for publication details)
- 5-page nav: Home, Understanding Heart Failure, Clinical Data, Safety & Dosing, HCP Resources
- Full page content for all 5 pages with appropriate blocks
- Image descriptions for each section (with tier recommendations)
- Footer with approval code placeholder

### Rich input → polished briefing

**User provides:** A detailed clinical dossier with full trial results, complete AE tables, SmPC-level safety data, and a brand colour palette.

**Skill generates:** A complete briefing with all data structured, copy written in AZ brand voice, appropriate blocks selected, and zero placeholders. Ready for MLR review and site generation.

---

## Cross-References

- **eds-site-builder**: Consumes this skill's output to generate the website
- **briefing-critique**: Validates generated pages against this skill's output
- **brand-extractor**: Can provide brand colours and visual identity if not specified
- **ai-image-generator**: Generates images from the descriptions in Section 11
