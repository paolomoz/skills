# Testing & Performance

## Linting

### Configuration

EDS projects come pre-configured with:
- **ESLint** — Airbnb style rules for JavaScript
- **Stylelint** — Standard rules for CSS

### Running Lints

```bash
npm run lint          # Run both ESLint and Stylelint
npm run lint:fix      # Auto-fix what can be fixed
npm run lint:js       # JavaScript only
npm run lint:css      # CSS only
```

### Common ESLint Issues

| Issue | Fix |
|-------|-----|
| Missing `.js` extension in import | Always include: `import { fn } from './file.js'` |
| `no-param-reassign` | Use `element.className = 'x'` instead of reassigning function params |
| `prefer-destructuring` | `const [first] = array` instead of `const first = array[0]` |
| `no-restricted-syntax` | Avoid `for...in`, use `Object.keys()` or `Object.entries()` |

### Common Stylelint Issues

| Issue | Fix |
|-------|-----|
| `selector-class-pattern` | Use lowercase-kebab-case for class names |
| `no-descending-specificity` | Reorder selectors so higher specificity comes later |
| `declaration-block-no-duplicate-properties` | Remove duplicate CSS properties |

## Performance Best Practices

### The Golden Rule: Keep It 100

Target a **100 score** on Google PageSpeed Insights for both mobile and desktop.

Test URL: `https://developers.google.com/speed/pagespeed/insights/?url=YOUR_URL`

### Critical Path (Eager Phase)

Only load what's needed for the Largest Contentful Paint:

**DO:**
- Keep `styles.css` under 20KB (compressed)
- Load only the first section eagerly
- Use system fonts or font-display: swap
- Inline critical above-fold styles

**DON'T:**
- Import external CSS frameworks
- Load all blocks upfront
- Use web fonts without fallbacks
- Add analytics/tracking in eager phase

### Image Optimization

**Author-uploaded images** (via CMS):
- Automatically optimized by aem.live CDN
- Served as WebP with proper srcset
- No action needed

**Git-committed images** (icons, logos, etc.):
- Optimize before committing: `npx svgo icons/*.svg`
- Use WebP format for raster images
- Keep file sizes under 100KB where possible
- Compress PNGs: `pngquant --quality=65-80 image.png`

### Lazy Loading

```css
/* Below-fold images are automatically lazy-loaded */
/* For eager loading (above-fold hero): */
main .hero img {
  loading: eager;
}
```

### JavaScript Performance

- **No dependencies** — vanilla JS only, no npm packages in production code
- **Automatic code splitting** — each block loads independently
- **Async decoration** — blocks can use `async/await` for lazy imports
- **Minimal DOM manipulation** — batch DOM changes, avoid layout thrashing

```javascript
// Good: batch DOM operations
const fragment = document.createDocumentFragment();
items.forEach((item) => fragment.append(createItem(item)));
block.append(fragment);

// Bad: DOM mutation in a loop
items.forEach((item) => block.append(createItem(item)));
```

### CSS Performance

- Use CSS custom properties (computed once, reused everywhere)
- Prefer `transform` and `opacity` for animations (GPU-accelerated)
- Avoid expensive selectors (`*`, `:nth-child(odd)` in large lists)
- Use `will-change` sparingly and only when animating

### Font Loading Strategy

Fonts are loaded conditionally in `scripts.js`:

```javascript
// Only load fonts on desktop or when already cached
if (window.innerWidth >= 900 || sessionStorage.getItem('fonts-loaded')) {
  loadFonts();
}
```

This prevents font-loading from blocking LCP on mobile devices.

## Responsive Testing

### Breakpoints

| Breakpoint | Target | Media Query |
|-----------|--------|-------------|
| Default | Mobile (375px) | Base styles |
| 600px | Tablet | `@media (width >= 600px)` |
| 900px | Desktop | `@media (width >= 900px)` |
| 1200px | Wide desktop | `@media (width >= 1200px)` |

### Testing Widths

Test at these specific widths:
- **375px** — iPhone SE / small mobile
- **428px** — iPhone Pro Max
- **768px** — iPad portrait
- **1024px** — iPad landscape
- **1280px** — Standard desktop
- **1440px** — Wide desktop

### Browser Testing

```bash
# Use Playwright for automated screenshots
npx playwright install chromium
```

```javascript
// Quick screenshot script
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  for (const width of [375, 768, 1280]) {
    await page.setViewportSize({ width, height: 800 });
    await page.goto('http://localhost:3000/');
    await page.screenshot({ path: `screenshot-${width}.png`, fullPage: true });
  }

  await browser.close();
})();
```

## Accessibility Testing

### Checklist

- [ ] Proper heading hierarchy (H1 → H2 → H3, no skipping)
- [ ] Alt text on all images (empty `alt=""` for decorative images)
- [ ] ARIA labels on interactive elements (buttons, toggles, nav)
- [ ] Keyboard navigation works (Tab, Enter, Escape, Arrow keys)
- [ ] Focus indicators visible on all interactive elements
- [ ] Color contrast ratio >= 4.5:1 (text) / 3:1 (large text)
- [ ] No information conveyed by color alone
- [ ] Form inputs have associated labels
- [ ] Skip navigation link present
- [ ] Language attribute set on `<html>`

### Automated Testing

```bash
# Run Lighthouse accessibility audit
npx lighthouse http://localhost:3000/ --only-categories=accessibility --output=html --output-path=./a11y-report.html
```

### ARIA Patterns for Common Blocks

**Accordion:**
```html
<details>
  <summary>Question</summary>
  <div>Answer</div>
</details>
```

**Tabs:**
```html
<div role="tablist">
  <button role="tab" aria-selected="true" aria-controls="panel-1">Tab 1</button>
</div>
<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">Content</div>
```

**Carousel:**
```html
<div role="region" aria-label="Image carousel" aria-roledescription="carousel">
  <div aria-live="polite">
    <div role="group" aria-roledescription="slide" aria-label="Slide 1 of 5">
      <!-- Slide content -->
    </div>
  </div>
  <button aria-label="Previous slide">‹</button>
  <button aria-label="Next slide">›</button>
</div>
```

## Content Validation

### Inspect Page Output

```bash
# Full decorated HTML
curl http://localhost:3000/page

# Raw markdown
curl http://localhost:3000/page.md

# Plain HTML (before decoration)
curl http://localhost:3000/page.plain.html
```

### Verify Block Loading

Open browser dev tools and check:
1. **Network tab** — Blocks should load only when they appear on the page
2. **Console** — No JavaScript errors
3. **Elements panel** — Block has `data-block-status="loaded"`
4. **Performance tab** — LCP element is in the first section

## Pre-Deployment Checklist

Before opening a PR:

- [ ] `npm run lint` passes with no errors
- [ ] All blocks render correctly in dev server
- [ ] Responsive design tested at 375px, 768px, 1280px
- [ ] No console errors or warnings
- [ ] Images are optimized (git-committed ones)
- [ ] Accessibility basics verified
- [ ] PageSpeed Insights score is 100 (test against feature preview URL)
- [ ] PR includes preview URL: `https://{branch}--{repo}--{owner}.aem.page/{path}`

## Debugging Tips

- **Block not rendering?** Check `data-block-status` attribute — `loading` means JS is running, `error` means it failed
- **Styles not applying?** Verify selectors are scoped to the block class
- **Content missing?** Use `curl` to check if the backend is delivering expected HTML
- **Fonts not loading?** Check `sessionStorage` for `fonts-loaded` key, and viewport width
- **Performance regression?** Compare `styles.css` size, check for new synchronous loads in eager phase
