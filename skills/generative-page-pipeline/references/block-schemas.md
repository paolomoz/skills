# Block Content Schemas

Complete content schema definitions for every block type supported by the generative page pipeline. Each schema defines the JSON structure that content generation models must produce.

---

## Hero Block

The hero block is the opening section of the page. It contains a headline, subheadline, call-to-action, and an optional background or side image.

```typescript
interface HeroContent {
  type: 'hero'
  headline: string           // 5-12 words, primary value proposition
  subheadline: string        // 15-30 words, supporting detail
  cta: {
    text: string             // 2-5 words, action-oriented ("Get Started", "Learn More")
    href: string             // Relative path or absolute URL
  }
  image?: {
    alt: string              // Descriptive alt text, 8-15 words
    prompt: string           // Image generation prompt if AI-generated
  }
  layout: 'centered' | 'split'  // centered = text over image, split = text left, image right
}
```

**Guardrails:**
- Headline must not exceed 80 characters
- Subheadline must not exceed 200 characters
- CTA text must be action-oriented (start with a verb)
- Always provide alt text for images, never use empty alt on hero images

**EDS HTML output:**
```html
<div class="hero">
  <div>
    <div>
      <h1>Headline</h1>
      <p>Subheadline text goes here.</p>
      <p><strong><a href="/path">CTA Text</a></strong></p>
    </div>
    <div>
      <picture><img src="/media/hero.webp" alt="Descriptive alt text" /></picture>
    </div>
  </div>
</div>
```

---

## Cards Block

A grid of 3-6 cards, each with an optional image, title, and description. Used for features, services, products, or team members.

```typescript
interface CardsContent {
  type: 'cards'
  items: CardItem[]           // 3-6 items
}

interface CardItem {
  title: string               // 3-8 words
  description: string         // 20-50 words
  image?: {
    alt: string
    prompt: string
  }
  link?: {
    text: string
    href: string
  }
}
```

**Guardrails:**
- Minimum 3 cards, maximum 6 cards
- All cards in a set should have consistent structure (all with images, or all without)
- Card titles should be parallel in grammatical structure
- Descriptions should be roughly equal length across cards (within 20% word count)

**EDS HTML output:**
```html
<div class="cards">
  <div>
    <div><picture><img src="/media/card1.webp" alt="Alt text" /></picture></div>
    <div>
      <h3>Card Title</h3>
      <p>Card description text goes here with supporting details.</p>
      <p><a href="/path">Link Text</a></p>
    </div>
  </div>
  <!-- Repeat for each card -->
</div>
```

---

## Columns Block

Side-by-side content in 2-4 columns. Each column can contain a mix of text, images, and links.

```typescript
interface ColumnsContent {
  type: 'columns'
  variant?: 'default' | 'highlight'  // highlight adds background color to first column
  items: ColumnItem[]                 // 2-4 columns
}

interface ColumnItem {
  heading?: string            // Optional column heading
  content: string             // Markdown-formatted text content (paragraphs, lists)
  image?: {
    alt: string
    prompt: string
  }
  cta?: {
    text: string
    href: string
  }
}
```

**Guardrails:**
- Minimum 2 columns, maximum 4 columns
- Content length should be balanced across columns (no single column 3x longer than others)
- If one column has an image, all columns should have images (or none should)
- Use the `highlight` variant only when the first column contains a key differentiator

**EDS HTML output:**
```html
<div class="columns">
  <div>
    <div>
      <picture><img src="/media/col1.webp" alt="Alt text" /></picture>
      <h3>Column Heading</h3>
      <p>Column content here.</p>
    </div>
    <div>
      <h3>Column Heading</h3>
      <p>Column content here.</p>
    </div>
  </div>
</div>
```

---

## Accordion Block

Collapsible sections for FAQ content or progressive disclosure. Each item has a question/title and an expandable answer/body.

```typescript
interface AccordionContent {
  type: 'accordion'
  items: AccordionItem[]      // 4-10 items
}

interface AccordionItem {
  question: string            // The visible header/question
  answer: string              // Markdown-formatted answer (can include paragraphs, lists, links)
}
```

**Guardrails:**
- Minimum 4 items, maximum 10 items
- Questions should be phrased as actual questions (start with who, what, when, where, why, how, can, does, is, etc.)
- Answers should be 30-150 words each
- First item should address the most common/important question
- Do not nest accordions inside accordions

**EDS HTML output:**
```html
<div class="accordion">
  <div>
    <div>
      <p><strong>What is the return policy?</strong></p>
    </div>
    <div>
      <p>Our return policy allows returns within 30 days of purchase. Items must be in original condition.</p>
    </div>
  </div>
  <!-- Repeat for each item -->
</div>
```

---

## Tabs Block

Tabbed content panels for organizing related content into switchable views. Common for pricing tiers, product categories, or feature comparisons.

```typescript
interface TabsContent {
  type: 'tabs'
  items: TabItem[]            // 2-5 tabs
}

interface TabItem {
  label: string               // Tab label, 1-3 words
  content: string             // Markdown-formatted content for this tab panel
  image?: {
    alt: string
    prompt: string
  }
}
```

**Guardrails:**
- Minimum 2 tabs, maximum 5 tabs
- Tab labels must be short (1-3 words) and fit on a single line
- Tab labels should be parallel in structure (all nouns, all verbs, etc.)
- Content length can vary between tabs but each should have at least 50 words
- First tab should contain the most commonly viewed content (it is the default open tab)

**EDS HTML output:**
```html
<div class="tabs">
  <div>
    <div>
      <p><strong>Tab Label</strong></p>
    </div>
    <div>
      <p>Tab content goes here with full formatting support.</p>
    </div>
  </div>
  <!-- Repeat for each tab -->
</div>
```

---

## Table Block

Structured data in rows and columns. Used for comparison tables, specification lists, pricing matrices, and feature checklists.

```typescript
interface TableContent {
  type: 'table'
  caption?: string            // Optional table caption
  headers: string[]           // Column headers
  rows: string[][]            // Row data, each row is an array of cell values
  highlightColumn?: number    // Optional: index of column to visually highlight (0-based)
}
```

**Guardrails:**
- Minimum 2 columns, maximum 6 columns
- Minimum 2 rows, maximum 20 rows
- Header text should be short (1-4 words per header)
- Cell content should be concise (1-20 words per cell)
- Use checkmarks or dashes for boolean comparisons, not "Yes"/"No"
- If highlighting a column (e.g., "recommended" pricing tier), set `highlightColumn`

**EDS HTML output:**
```html
<div class="table">
  <div>
    <div>
      <table>
        <thead>
          <tr>
            <th>Feature</th>
            <th>Basic</th>
            <th>Pro</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Storage</td>
            <td>10 GB</td>
            <td>100 GB</td>
          </tr>
          <!-- More rows -->
        </tbody>
      </table>
    </div>
  </div>
</div>
```

---

## Testimonials Block

Customer quotes, reviews, or case study excerpts. Each testimonial includes a quote, attribution, and optional company/role.

```typescript
interface TestimonialsContent {
  type: 'testimonials'
  items: TestimonialItem[]    // 2-4 testimonials
}

interface TestimonialItem {
  quote: string               // 20-60 words, the actual customer quote
  name: string                // Person's name
  role?: string               // Job title or role
  company?: string            // Company name
  image?: {
    alt: string
    prompt: string            // For generating a headshot placeholder
  }
}
```

**Guardrails:**
- Minimum 2 testimonials, maximum 4 testimonials
- Quotes must sound authentic -- avoid superlatives like "best ever" or "absolutely perfect"
- Include specific details in quotes (metrics, outcomes, timeframes) for credibility
- Always include at minimum the person's name
- Quote length should be balanced across all testimonials (within 30% word count)

**EDS HTML output:**
```html
<div class="testimonials">
  <div>
    <div>
      <p>"This platform reduced our deployment time from 4 hours to 15 minutes."</p>
      <p><strong>Jane Smith</strong></p>
      <p>VP of Engineering, Acme Corp</p>
    </div>
  </div>
  <!-- Repeat for each testimonial -->
</div>
```

---

## CTA Block

Call-to-action section designed to drive conversion. Contains a headline, supporting text, and one or two action buttons.

```typescript
interface CTAContent {
  type: 'cta'
  headline: string            // 4-10 words, compelling action-oriented headline
  description: string         // 15-40 words, supporting context
  primaryAction: {
    text: string              // 2-5 words, verb-first ("Start Free Trial")
    href: string
  }
  secondaryAction?: {
    text: string              // 2-5 words, lower commitment ("Watch Demo")
    href: string
  }
  variant: 'default' | 'dark' | 'accent'  // Visual treatment
}
```

**Guardrails:**
- Headline must be action-oriented or benefit-oriented
- Primary CTA text must start with a verb
- Secondary CTA (if present) should be a lower-commitment action than primary
- Never use "Click Here" or "Submit" as CTA text
- Do not use more than 2 CTAs per block -- decision paralysis reduces conversion
- Place CTA blocks at natural decision points (after social proof, after feature explanation)

**EDS HTML output:**
```html
<div class="cta">
  <div>
    <div>
      <h2>Ready to Get Started?</h2>
      <p>Join thousands of teams shipping faster with our platform.</p>
      <p>
        <strong><a href="/signup">Start Free Trial</a></strong>
        <a href="/demo">Watch Demo</a>
      </p>
    </div>
  </div>
</div>
```

---

## Validation Utility

Use this function to validate generated content against the schema before assembly:

```typescript
function validateBlockContent(content: any, blockType: string): ValidationResult {
  const schema = BLOCK_CONTENT_SCHEMAS[blockType]
  if (!schema) return { valid: false, errors: [`Unknown block type: ${blockType}`] }

  const errors: string[] = []

  // Check required fields
  for (const field of schema.required) {
    if (!(field in content)) {
      errors.push(`Missing required field: ${field}`)
    }
  }

  // Check array length constraints
  if (content.items && schema.minItems && content.items.length < schema.minItems) {
    errors.push(`${blockType} requires at least ${schema.minItems} items, got ${content.items.length}`)
  }
  if (content.items && schema.maxItems && content.items.length > schema.maxItems) {
    errors.push(`${blockType} allows at most ${schema.maxItems} items, got ${content.items.length}`)
  }

  return { valid: errors.length === 0, errors }
}
```

When validation fails, log the errors and either retry content generation with the errors appended to the prompt, or emit a warning event and proceed with the content as-is if the errors are non-critical (e.g., slightly exceeding word count limits).
