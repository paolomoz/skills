# Block Development Patterns

## Block Lifecycle

1. Author creates a table in the CMS with the block name as the header
2. Backend converts the table to a `<div class="blockname">` with nested `<div>` rows/cells
3. `aem.js` detects the block, loads `blocks/blockname/blockname.js` and `.css`
4. Your `decorate()` function transforms the DOM
5. Block is marked `data-block-status="loaded"`

## DOM Structure Before Decoration

A block authored as a 2-row, 2-column table arrives as:

```html
<div class="my-block">
  <div>           <!-- row 1 -->
    <div>         <!-- cell 1 -->
      <picture>...</picture>
    </div>
    <div>         <!-- cell 2 -->
      <h2>Title</h2>
      <p>Description</p>
    </div>
  </div>
  <div>           <!-- row 2 -->
    <div>Cell 1 content</div>
    <div>Cell 2 content</div>
  </div>
</div>
```

Always inspect with `curl` or `console.log(block.innerHTML)` before coding.

## Common Decoration Patterns

### Iterate Rows

```javascript
export default function decorate(block) {
  [...block.children].forEach((row, index) => {
    const cells = [...row.children];
    // cells[0] = first column, cells[1] = second column, etc.
    row.classList.add('my-block-row');
    cells.forEach((cell, i) => cell.classList.add(`my-block-cell-${i}`));
  });
}
```

### Extract Configuration from First Row

```javascript
export default function decorate(block) {
  const rows = [...block.children];
  const configRow = rows.shift(); // Remove first row as config
  const config = {
    title: configRow.children[0]?.textContent.trim(),
    type: configRow.children[1]?.textContent.trim() || 'default',
  };

  // Process remaining rows as content
  rows.forEach((row) => {
    // ...
  });
}
```

### Rebuild DOM with Semantic Elements

```javascript
export default function decorate(block) {
  const items = [...block.children].map((row) => {
    const [imageCell, contentCell] = [...row.children];
    const picture = imageCell.querySelector('picture');
    const heading = contentCell.querySelector('h2, h3');
    const description = contentCell.querySelector('p');
    const link = contentCell.querySelector('a');

    const article = document.createElement('article');
    article.className = 'card';

    if (picture) {
      const figure = document.createElement('figure');
      figure.append(picture);
      article.append(figure);
    }

    const body = document.createElement('div');
    body.className = 'card-body';
    if (heading) body.append(heading);
    if (description) body.append(description);
    if (link) body.append(link);
    article.append(body);

    return article;
  });

  block.replaceChildren(...items);
}
```

### Accordion Pattern

```javascript
export default function decorate(block) {
  [...block.children].forEach((row) => {
    const label = row.children[0];
    const body = row.children[1];

    const details = document.createElement('details');
    const summary = document.createElement('summary');
    summary.append(...label.childNodes);
    details.append(summary, body);

    row.replaceWith(details);
  });

  // Open first item by default
  block.querySelector('details')?.setAttribute('open', '');
}
```

### Tabs Pattern

```javascript
export default function decorate(block) {
  const tabList = document.createElement('div');
  tabList.className = 'tab-list';
  tabList.setAttribute('role', 'tablist');

  const panels = [];

  [...block.children].forEach((row, index) => {
    const [labelCell, contentCell] = [...row.children];

    // Create tab button
    const tab = document.createElement('button');
    tab.className = 'tab';
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-selected', index === 0 ? 'true' : 'false');
    tab.textContent = labelCell.textContent.trim();
    tab.id = `tab-${index}`;
    tab.setAttribute('aria-controls', `panel-${index}`);
    tabList.append(tab);

    // Create panel
    const panel = document.createElement('div');
    panel.className = 'tab-panel';
    panel.setAttribute('role', 'tabpanel');
    panel.id = `panel-${index}`;
    panel.setAttribute('aria-labelledby', `tab-${index}`);
    panel.hidden = index !== 0;
    panel.append(...contentCell.childNodes);
    panels.push(panel);

    row.remove();
  });

  block.prepend(tabList);
  panels.forEach((panel) => block.append(panel));

  // Tab switching
  tabList.addEventListener('click', (e) => {
    const clickedTab = e.target.closest('.tab');
    if (!clickedTab) return;

    tabList.querySelectorAll('.tab').forEach((t) => t.setAttribute('aria-selected', 'false'));
    clickedTab.setAttribute('aria-selected', 'true');

    block.querySelectorAll('.tab-panel').forEach((p) => { p.hidden = true; });
    const panelId = clickedTab.getAttribute('aria-controls');
    block.querySelector(`#${panelId}`).hidden = false;
  });
}
```

### Carousel Pattern

```javascript
export default function decorate(block) {
  const slides = [...block.children];
  const track = document.createElement('div');
  track.className = 'carousel-track';

  slides.forEach((slide, i) => {
    slide.className = 'carousel-slide';
    slide.setAttribute('aria-hidden', i !== 0);
    track.append(slide);
  });

  block.replaceChildren(track);

  // Navigation
  const nav = document.createElement('div');
  nav.className = 'carousel-nav';
  nav.innerHTML = `
    <button class="carousel-prev" aria-label="Previous slide">&#8249;</button>
    <button class="carousel-next" aria-label="Next slide">&#8250;</button>
  `;
  block.append(nav);

  let current = 0;
  const total = slides.length;

  function goTo(index) {
    current = ((index % total) + total) % total;
    track.style.transform = `translateX(-${current * 100}%)`;
    slides.forEach((s, i) => s.setAttribute('aria-hidden', i !== current));
  }

  nav.querySelector('.carousel-prev').addEventListener('click', () => goTo(current - 1));
  nav.querySelector('.carousel-next').addEventListener('click', () => goTo(current + 1));
}
```

## Loading Dependencies

### Import from scripts.js utilities

```javascript
import { createOptimizedPicture } from '../../scripts/aem.js';
import { loadFragment } from '../fragment/fragment.js';
```

### Lazy-load heavy modules

```javascript
export default async function decorate(block) {
  // Only import when this block is actually used
  const { Chart } = await import('./chart-library.js');
  // ...
}
```

## Helper Functions from aem.js

These are available to import from `scripts/aem.js`:

- `createOptimizedPicture(src, alt, eager, breakpoints)` — Generates responsive `<picture>` with WebP/fallback
- `loadCSS(href)` — Dynamically load a CSS file
- `loadScript(src, attrs)` — Dynamically load a JS file
- `getMetadata(name)` — Read `<meta>` tag value by name
- `toClassName(name)` — Convert string to CSS class name format
- `buildBlock(blockName, content)` — Programmatically create a block element
- `loadBlock(block)` — Trigger block loading (decoration)
- `decorateBlock(block)` — Add block classes and attributes
- `decorateIcons(element)` — Convert `:icon-name:` references to inline SVGs
- `decorateSections(main)` — Process sections from raw HTML
- `decorateBlocks(main)` — Discover and prepare all blocks
- `loadSection(section)` — Load and decorate a single section
- `loadSections(main)` — Load all sections

## Block Variants

Authors add variants by putting them in parentheses: `Hero (dark, wide)` → `.hero.dark.wide`

Handle variants in CSS when possible (no JS needed):

```css
main .hero.dark { background: var(--dark-color); color: white; }
main .hero.wide { max-width: none; }
main .hero.centered { text-align: center; }
```

Only use JS for variants that require structural DOM changes.

## Fragments

Fragments are reusable content pieces loaded into any page:

```javascript
// In scripts.js buildAutoBlocks, or in a block
import { loadFragment } from '../fragment/fragment.js';

const fragment = await loadFragment('/fragments/my-fragment');
if (fragment) {
  const section = fragment.querySelector('.section');
  block.append(section);
}
```

Header and footer are typically loaded as fragments during the lazy phase.

## Tips

- **Always use `curl` first** to inspect what the backend sends before writing decoration code
- **Handle missing content** — authors may leave cells empty, your code shouldn't break
- **Keep blocks self-contained** — each block should work independently
- **Prefer CSS over JS** — if something can be done with CSS alone, do it that way
- **Test responsive** — blocks must work at 375px, 768px, and 1200px+
- **No external dependencies** — vanilla JavaScript only, no npm packages in blocks
