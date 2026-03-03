---
name: briefing-critique
description: Compare generated draft pages against the source briefing to catch copy errors, missing content, wrong block types, and structural mismatches. Use when "critique drafts", "check briefing compliance", "verify content fidelity", "QA against briefing", or "validate draft pages".
---

# Briefing Critique

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| audit | "critique drafts", "check briefing compliance", "verify content fidelity", "QA against briefing" | High | az-sitebuilder |

Systematically compare generated draft `.plain.html` pages against a source briefing document to detect copy errors, missing content, wrong block types, image mismatches, and structural problems. Produces a severity-rated findings report with fix suggestions. Auto-detects fidelity level from the briefing's own instructions to avoid false positives.

## When to Use
- After generating site pages from a briefing and before uploading to DA
- User wants to verify all briefing content made it into the drafts accurately
- User asks to "QA", "check", "review", or "validate" drafts against a briefing
- Before running `upload-to-da.sh` as a final quality gate
- After making bulk edits to drafts and needing to re-verify compliance
- User suspects copy or image drift between briefing and generated pages

## Instructions

### Step 1: Identify Sources and Determine Fidelity Level

Locate the briefing and draft files for the target site:

- **Briefing**: `sites/{sitename}/briefing.md` or `sites/{sitename}/briefing.docx`
  - For `.docx` files, extract text content (use a tool or read what's available)
  - For `.md` files, read directly
- **Drafts**: All `drafts/{sitename}/*.plain.html` files

Read the briefing thoroughly and detect three independent fidelity dimensions by examining the briefing's own instructions and structure:

| Dimension | Strict | Flexible |
|-----------|--------|----------|
| **Copy** | Briefing says "must be used exactly as written", "verbatim", "MLR-approved", or provides precise copy per section | No such instruction; briefing provides descriptions, outlines, or topic summaries |
| **Block types** | Briefing specifies block types explicitly (e.g., `**Block:** hero-teaser`) per section | Briefing describes content intent ("three cards", "image left text right") without naming blocks |
| **Image mapping** | Briefing specifies exact image filenames per section (e.g., `Image: hero-home.jpeg`) | Briefing gives general image descriptions without specific filenames |

The detected fidelity level determines what subsequent steps check and how strictly they check it:

- **Strict copy**: Paragraph-by-paragraph verbatim comparison after normalization
- **Flexible copy**: Check intent coverage — are all key topics, messages, and data points present?
- **Strict blocks**: Exact block type match per section
- **Flexible blocks**: Verify the chosen block is reasonable for the content intent
- **Strict images**: Verify the correct image filename appears in the draft for each section
- **Flexible images**: Verify an appropriate image exists in each section that expects one

State the detected fidelity level at the top of the report with evidence (quote the briefing text that determined each dimension).

---

### Step 2: Page Inventory

Compare the set of expected pages (from the briefing's page/sitemap list) against the actual files found in `drafts/{sitename}/`.

| Check | Severity |
|-------|----------|
| Page listed in briefing but no corresponding `.plain.html` file | CRITICAL |
| `.plain.html` file exists with no corresponding briefing entry | LOW |
| `nav.plain.html` missing | CRITICAL |
| `footer.plain.html` missing | CRITICAL |

List all expected pages and their found/missing status. Include `nav.plain.html` and `footer.plain.html` in the inventory.

---

### Step 3: Nav and Footer Verification

#### Nav checks:
- Nav links match the briefing's page list (correct pages, correct order)
- All links use `/{sitename}/` prefix
- Logo `<img src>` uses CDN URL (`https://{sitename}-images.pages.dev/`)
- Search icon uses CDN URL
- Top bar links present (Contact Us, AZ Employee Login)

#### Footer checks:
- Footer page links match the briefing's page list
- Approval code matches briefing (if specified)
- Brand trademark text present with correct drug/brand name
- AstraZeneca logo uses CDN URL
- Regulatory links present (Report Adverse Event, Medical Information, Privacy, Terms, Accessibility)
- Date of preparation present

Flag any mismatch with severity HIGH.

---

### Step 4: Structural Comparison

For each page, compare the structural layout between briefing and draft:

1. **Section count**: Does the number of content sections match?
2. **Block types per section**:
   - Strict mode: Does each section use the exact block type specified in the briefing?
   - Flexible mode: Is the chosen block type reasonable for the described content?
3. **Section-metadata styles**: Do `highlight`, `light`, or other style variants match what the briefing specifies?
4. **Section ordering**: Are sections in the same order as the briefing?
5. **Metadata block**: Does the page have a metadata block with Title and Description?

| Finding | Severity |
|---------|----------|
| Missing content section | HIGH |
| Wrong block type (strict mode) | MEDIUM |
| Block type could be better (flexible mode) | LOW |
| Wrong section-metadata style | MEDIUM |
| Sections in wrong order | MEDIUM |
| Missing metadata block | MEDIUM |

---

### Step 5: Copy Fidelity

This is the critical step. The approach depends on the detected fidelity level.

#### Strict Mode (verbatim copy specified)

Normalize both the briefing text and draft text before comparing:

1. Strip all HTML tags
2. Decode HTML entities (`&amp;` → `&`, `&lt;` → `<`, `&ge;` → `≥`, `&ndash;` → `–`, etc.)
3. Strip superscript reference markers (`<sup>1</sup>`, `<sup>†</sup>`)
4. Collapse whitespace (multiple spaces/newlines → single space)
5. Trim leading/trailing whitespace

Then compare paragraph-by-paragraph within each section. For table data, compare cell-by-cell.

**Important exclusions** — do NOT flag these as copy differences:
- `<strong>` wrapping on CTAs (this is structural markup per block conventions)
- `<em>` wrapping for emphasis in block markup
- Link `<a href>` wrapping around text
- `<br>` tags within paragraphs
- Bullet list formatting differences (`<ul><li>` vs paragraph text)

| Finding | Severity |
|---------|----------|
| Clinical data differs (numbers, percentages, p-values) | CRITICAL |
| Drug name or dosing information differs | CRITICAL |
| Body copy text differs from briefing | CRITICAL |
| Heading text differs from briefing | HIGH |
| CTA text differs from briefing | HIGH |
| Table cell content differs | CRITICAL |

#### Flexible Mode (intent-based copy)

Check that all key messages, topics, and data points from the briefing appear somewhere in the draft:

1. Extract the key topics and messages from the briefing for each page
2. For each topic, verify it appears in the corresponding draft page
3. Verify all clinical data points (numbers, percentages) are present and accurate

| Finding | Severity |
|---------|----------|
| Clinical data missing or differs | CRITICAL |
| Key topic completely absent from draft | HIGH |
| Data point present but rephrased — acceptable | Not flagged |

---

### Step 6: Image Verification

Compare images by **filename** (the last path segment of the URL), NOT by full URL. DA reprocesses images and assigns new URLs on the published site, so full URL comparison produces false positives.

For each section where the briefing specifies an image:

1. Extract the expected image filename from the briefing (e.g., `hero-home.jpeg`)
2. Find `<img src>` and `<source srcset>` attributes in the corresponding draft section
3. Check that the expected filename appears in the draft's image URL path

Additional image checks across all pages:

| Check | Severity |
|-------|----------|
| Briefing image filename not found in draft section | HIGH |
| No image in a section that expects one | HIGH |
| Local image path (`src="/..."` not using CDN) | CRITICAL |
| `about:error` in any image src | CRITICAL |
| Alt text significantly differs from briefing | LOW |
| Image present but for wrong section | HIGH |

---

### Step 7: Metadata Comparison

Check each page's metadata block (the last section containing Title and Description):

- **Strict mode**: Title and Description must match the briefing exactly (after normalization)
- **Flexible mode**: Title and Description must contain the key terms from the briefing

| Finding | Severity |
|---------|----------|
| Missing metadata block | MEDIUM |
| Title doesn't match briefing | LOW |
| Description doesn't match briefing | LOW |

---

### Step 8: Cross-Page Checks

These checks span all pages in the site:

1. **Accordion consistency**: The prescribing information / important safety information accordion should be identical (or near-identical) across all pages that include it. Diff the accordion content between pages and flag differences.

2. **Nav completeness**: Every page listed in the briefing should appear as a link in `nav.plain.html`.

3. **No local image paths**: Run `grep -rn 'src="/' drafts/{sitename}/ --include='*.html'` — should return nothing. Any matches are CRITICAL.

4. **No about:error**: Run `grep -rn 'about:error' drafts/{sitename}/ --include='*.html'` — should return nothing. Any matches are CRITICAL.

5. **Consistent CDN base URL**: All image URLs should use `https://{sitename}-images.pages.dev/` as the base. Flag any image using a different CDN or domain.

6. **Internal link validity**: All `<a href="/{sitename}/...">` links should point to pages that exist in the drafts folder.

---

### Step 9: Install Critique Overlay (one-time setup)

The interactive report requires a small overlay script in the project's `scripts/delayed.js`. Check if it already exists — if not, append the contents of `references/critique-overlay.js` to `scripts/delayed.js`.

The overlay activates **only** when `?critique-section` or `?critique-target` query params are present in the URL. It has zero impact on production pages.

It supports three targeting modes:
- `?critique-section=N` — highlights the Nth `<main> .section` (1-indexed)
- `?critique-target=header` — highlights the `<header>` element
- `?critique-target=footer` — highlights the `<footer>` element
- `?critique-label=TEXT` — optional label shown as a tag on the highlighted element

---

### Step 10: Generate Interactive HTML Report

Write the report to `sites/{sitename}/critique.html`. Read the template from `references/report-template.html` and populate all `{{PLACEHOLDER}}` values with the actual findings data.

#### Template placeholders

| Placeholder | Value |
|-------------|-------|
| `{{SITENAME}}` | Site folder name (e.g., `zenturis`) |
| `{{DRUG_BRAND}}` | Brand name from briefing (e.g., `Zenturis`) |
| `{{DRUG_GENERIC}}` | Generic name from briefing (e.g., `zenturigliptin`) |
| `{{BRIEFING_PATH}}` | Relative path to briefing (e.g., `sites/zenturis/briefing.docx`) |
| `{{DATE}}` | Current date |
| `{{COPY_FIDELITY}}`, `{{BLOCKS_FIDELITY}}`, `{{IMAGES_FIDELITY}}` | `Strict` or `Flexible` |
| `{{COPY_EVIDENCE}}`, `{{BLOCKS_EVIDENCE}}`, `{{IMAGES_EVIDENCE}}` | Quote from briefing that determined the fidelity level |
| `{{CRITICAL_COUNT}}`, `{{HIGH_COUNT}}`, `{{MEDIUM_COUNT}}`, `{{LOW_COUNT}}` | Integer counts |
| `{{VERDICT_CLASS}}` | `pass`, `needs-fixes`, or `blocked` |
| `{{VERDICT_TEXT}}` | Verdict text with summary |

#### Fidelity badge classes

Set the `.value` div class based on the detected fidelity level:
- `badge-strict` (red) for strict dimensions
- `badge-flexible` (green) for flexible dimensions

#### Findings markup

Each finding is a clickable `<div class="finding">` with data attributes for preview targeting:

```html
<div class="finding" data-page="PAGE" data-section="N" data-label="SHORT LABEL">
  <div class="location">PAGE &rarr; Section N (BLOCK)</div>
  <div class="description">DESCRIPTION</div>
  <div class="diff">
    <div>
      <div class="diff-label">Expected</div>
      <div class="diff-expected">BRIEFING TEXT</div>
    </div>
    <div>
      <div class="diff-label">Actual</div>
      <div class="diff-actual">DRAFT TEXT</div>
    </div>
  </div>
  <div class="fix">FIX SUGGESTION</div>
  <div class="view-hint">Click to view in preview &rarr;</div>
</div>
```

**Preview targeting rules:**
- For content section findings: `data-page="pageslug"` + `data-section="N"` (1-indexed)
- For nav findings: `data-page="index"` + `data-target="header"` (shows nav in context of home page)
- For footer findings: `data-page="index"` + `data-target="footer"` (shows footer in context of home page)
- The diff block is optional — include it when there's a concrete expected vs actual comparison

#### Page status table

Each `<tr>` has `data-page="pageslug"` to make the row clickable. Use these classes:
- `class="match"` (green) for passing counts
- `class="mismatch"` (orange) for failing counts
- Status cell: `class="status-pass"` / `class="status-warn"` / `class="status-fail"`

#### Cross-page checklist

Each `<li>` uses one of: `class="check-pass"`, `class="check-warn"`, `class="check-fail"`

#### Report layout behaviour

The report starts **full-width** (centered, comfortable reading). When the user clicks any finding card or page table row, the report panel animates to 440px on the left and the preview iframe slides in from the right, loading the relevant page from `http://localhost:3000` with the critique overlay highlighting the affected section. A close button collapses the preview back to full-width.

#### Verdict criteria

| Verdict | Class | Condition |
|---------|-------|-----------|
| PASS | `pass` | Zero CRITICAL and zero HIGH |
| NEEDS FIXES | `needs-fixes` | Zero CRITICAL, but HIGH or MEDIUM exist |
| BLOCKED | `blocked` | One or more CRITICAL |

#### Severity criteria summary

| Severity | Criteria |
|----------|----------|
| CRITICAL | Copy text differs from briefing (strict mode); clinical data wrong; missing page; local image path; `about:error` |
| HIGH | Missing image; wrong image filename; missing content section; wrong link target; key topic missing (flexible mode) |
| MEDIUM | Wrong block type (strict mode); wrong section-metadata style; wrong link text; missing metadata |
| LOW | Extra file not in briefing; metadata mismatch; alt text differs; block type could be better (flexible mode) |

After writing the file, open it in the browser and tell the user the path. Remind them the preview iframe requires the dev server running at `localhost:3000`.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Too many CRITICAL copy findings | Briefing has HTML entities, drafts have decoded characters | Ensure normalization in Step 5 decodes all HTML entities before comparison |
| False positives on `<strong>` text | CTA text wrapped in `<strong>` per block conventions | Step 5 explicitly excludes structural markup wrapping from copy diffs |
| Image comparison flags every image | Comparing full URLs instead of filenames | Step 6 specifies filename-only comparison (last path segment) |
| Briefing is `.docx` and unreadable | Binary Word document | Extract text using available tools, or ask user to provide a text/markdown version |
| Accordion diffs across pages | Pages were generated independently | Flag in Step 8 cross-page checks; provide the specific diff |
| Entity encoding differences (`&ge;` vs `≥`) | Briefing uses HTML entities, draft uses Unicode | Normalization handles this — decode entities in both sources before comparing |
| Table cell ordering differs | Table rows or columns reordered in draft | Compare cell content regardless of position within the same table; flag if data is missing entirely |

## Cross-References

- **eds-website-builder**: The skill that generates the drafts this skill audits
- **generative-page-pipeline**: Alternative page generation pipeline whose output can also be critiqued
- **site-auditor**: Broader site-level audit (content gaps, metadata) — complementary to briefing-level fidelity checking
- **accessibility-auditor**: Can be run after briefing critique to verify generated pages meet WCAG standards
