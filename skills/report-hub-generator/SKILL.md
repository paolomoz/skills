---
name: report-hub-generator
description: Generate single-page HTML report hubs that aggregate multiple analysis reports with interactive navigation, view toggles, and consistent theming. Use when building "report dashboards", "analysis hubs", "HTML reports", or "data visualization pages".
---

# Report Hub Generator

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| data-intelligence | "report dashboard", "analysis hub", "HTML report", "data visualization page" | Medium | 6 projects |

Generate self-contained, single-page HTML report hubs that aggregate multiple analysis reports into an interactive dashboard with sidebar navigation, view toggles (grid/list/detail), search and filtering, and a consistent design system. All CSS and JavaScript are embedded inline with zero external dependencies, making reports portable and hostable anywhere.

## When to Use

- Aggregating multiple analysis outputs (content audit, performance, SEO, image quality) into one navigable hub
- Building a dashboard for stakeholders who need interactive exploration without developer tools
- Creating a portable HTML report that can be shared via email, hosted on a static server, or opened locally
- Presenting data with charts, tables, status indicators, and expandable detail sections
- Delivering an analysis where the output format is "a single HTML file they can open in a browser"

## Instructions

### Step 1: Establish the Design System

Every report hub starts from the same CSS custom properties. This ensures visual consistency across all reports and makes theming trivial.

```css
:root {
  /* Primary */
  --blue: #3B63FB;
  --blue-light: #EBF0FF;
  --blue-dark: #2A4AD4;

  /* Backgrounds */
  --bg: #F8F8F8;
  --bg-white: #FFFFFF;

  /* Foreground */
  --fg: #292929;
  --fg-heading: #131313;
  --fg-muted: #717171;

  /* Semantic status */
  --red: #D7373F;
  --red-light: #FDF0F0;
  --amber: #CB6F10;
  --amber-light: #FFF5EB;
  --green: #12805C;
  --green-light: #EDFAF5;
  --purple: #7A6AFD;
  --purple-light: #F0EEFF;

  /* Typography */
  --font: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'Source Code Pro', 'SF Mono', Consolas, monospace;
  --fs-sm: 0.8125rem;
  --fs-base: 0.9375rem;
  --fs-lg: 1.125rem;
  --fs-xl: 1.5rem;
  --fs-2xl: 2rem;
  --lh: 1.6;

  /* Spacing & shape */
  --radius: 8px;
  --radius-sm: 4px;
  --radius-lg: 12px;
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-hover: 0 4px 16px rgba(0, 0, 0, 0.12);
  --transition: 200ms ease;
}
```

**Semantic status color usage** (never deviate from these mappings):
- **Red** (`--red`): Errors, critical issues, failing scores, blockers. Use `--red-light` as background.
- **Amber** (`--amber`): Warnings, needs attention, moderate issues. Use `--amber-light` as background.
- **Green** (`--green`): Success, passing scores, healthy metrics. Use `--green-light` as background.
- **Purple** (`--purple`): Informational, neutral highlights, metadata. Use `--purple-light` as background.

Never use red for informational content or green for warnings. Status colors carry semantic meaning that users learn to trust across reports.

### Step 2: Build the Page Layout

The report hub uses a fixed sidebar + scrollable content area layout that works from 1024px to ultrawide screens.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Report Title}</title>
  <style>
    /* Design system variables (from Step 1) */
    /* Reset */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font);
      font-size: var(--fs-base);
      line-height: var(--lh);
      color: var(--fg);
      background: var(--bg);
      display: flex;
      height: 100vh;
      overflow: hidden;
    }

    /* Sidebar */
    .sidebar {
      width: 260px;
      background: var(--bg-white);
      border-right: 1px solid #E5E5E5;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      overflow-y: auto;
    }
    .sidebar-header {
      padding: 24px 20px 16px;
      border-bottom: 1px solid #E5E5E5;
    }
    .sidebar-header h1 {
      font-size: var(--fs-lg);
      color: var(--fg-heading);
      font-weight: 700;
    }
    .sidebar-nav {
      padding: 12px 0;
      flex: 1;
    }
    .nav-item {
      display: flex;
      align-items: center;
      padding: 10px 20px;
      cursor: pointer;
      color: var(--fg);
      text-decoration: none;
      transition: background var(--transition);
      font-size: var(--fs-sm);
    }
    .nav-item:hover { background: var(--bg); }
    .nav-item.active {
      background: var(--blue-light);
      color: var(--blue);
      font-weight: 600;
    }

    /* Content area */
    .content {
      flex: 1;
      overflow-y: auto;
      padding: 32px 40px;
    }
  </style>
</head>
<body>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h1>{Report Title}</h1>
      <p style="color: var(--fg-muted); font-size: var(--fs-sm);">Generated {date}</p>
    </div>
    <nav class="sidebar-nav" id="nav">
      <!-- Navigation items injected here -->
    </nav>
  </aside>
  <main class="content" id="content">
    <!-- Report sections injected here -->
  </main>
</body>
</html>
```

### Step 3: Configure the Report Manifest

Define which reports are available and how they appear in navigation. Store this as a `manifest.json` or embed it directly in the HTML as a JavaScript object.

```javascript
const MANIFEST = {
  title: "Site Analysis Report Hub",
  generated: "2025-12-01T15:30:00Z",
  reports: [
    {
      id: "content-gaps",
      label: "Content Gap Analysis",
      icon: "gap",
      description: "Pages missing from expected content matrix",
      status: "complete",     // complete | partial | error
      itemCount: 47,
      severity: "amber"       // Drives the status indicator color
    },
    {
      id: "performance",
      label: "RUM Performance",
      icon: "speed",
      description: "Real User Monitoring metrics across all pages",
      status: "complete",
      itemCount: 1243,
      severity: "green"
    },
    {
      id: "image-quality",
      label: "Image Quality Audit",
      icon: "image",
      description: "Oversized, unoptimized, and missing images",
      status: "complete",
      itemCount: 89,
      severity: "red"
    },
    {
      id: "brand-consistency",
      label: "Brand Consistency",
      icon: "brand",
      description: "Color, typography, and voice adherence scores",
      status: "complete",
      itemCount: 156,
      severity: "green"
    }
  ]
};
```

### Step 4: Implement View Toggles

Provide three view modes for content sections: Grid (cards), List (compact rows), and Detail (expanded single-item view).

```javascript
function renderViewToggles(containerId) {
  return `
    <div class="view-toggles" data-container="${containerId}">
      <button class="toggle active" data-view="grid" title="Grid view">
        <svg width="16" height="16" viewBox="0 0 16 16">
          <rect x="1" y="1" width="6" height="6" rx="1" fill="currentColor"/>
          <rect x="9" y="1" width="6" height="6" rx="1" fill="currentColor"/>
          <rect x="1" y="9" width="6" height="6" rx="1" fill="currentColor"/>
          <rect x="9" y="9" width="6" height="6" rx="1" fill="currentColor"/>
        </svg>
      </button>
      <button class="toggle" data-view="list" title="List view">
        <svg width="16" height="16" viewBox="0 0 16 16">
          <rect x="1" y="2" width="14" height="3" rx="1" fill="currentColor"/>
          <rect x="1" y="7" width="14" height="3" rx="1" fill="currentColor"/>
          <rect x="1" y="12" width="14" height="3" rx="1" fill="currentColor"/>
        </svg>
      </button>
      <button class="toggle" data-view="detail" title="Detail view">
        <svg width="16" height="16" viewBox="0 0 16 16">
          <rect x="1" y="1" width="14" height="14" rx="1" fill="currentColor"/>
        </svg>
      </button>
    </div>
  `;
}

// View toggle CSS
const viewToggleCSS = `
  .view-toggles { display: flex; gap: 4px; }
  .toggle {
    padding: 6px 8px; border: 1px solid #E5E5E5; background: var(--bg-white);
    border-radius: var(--radius-sm); cursor: pointer; color: var(--fg-muted);
    transition: all var(--transition);
  }
  .toggle:hover { border-color: var(--blue); color: var(--blue); }
  .toggle.active { background: var(--blue-light); border-color: var(--blue); color: var(--blue); }

  .report-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
  .report-list { display: flex; flex-direction: column; gap: 8px; }
  .report-detail { max-width: 800px; }
`;
```

### Step 5: Build Report Type Templates

Each report type has a specific rendering template. Here are the most common patterns from real projects.

#### KPI Cards

```html
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-value" style="color: var(--blue);">1,243</div>
    <div class="kpi-label">Pages Analyzed</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: var(--green);">94.2%</div>
    <div class="kpi-label">Pass Rate</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: var(--red);">47</div>
    <div class="kpi-label">Critical Issues</div>
  </div>
</div>
```

```css
.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 32px; }
.kpi-card {
  background: var(--bg-white); border-radius: var(--radius); padding: 24px;
  box-shadow: var(--shadow-card); text-align: center;
}
.kpi-value { font-size: var(--fs-2xl); font-weight: 700; }
.kpi-label { font-size: var(--fs-sm); color: var(--fg-muted); margin-top: 4px; }
```

#### Status Badge

```html
<span class="badge badge-red">Critical</span>
<span class="badge badge-amber">Warning</span>
<span class="badge badge-green">Passing</span>
<span class="badge badge-purple">Info</span>
```

```css
.badge {
  display: inline-block; padding: 2px 10px; border-radius: 100px;
  font-size: var(--fs-sm); font-weight: 600;
}
.badge-red { background: var(--red-light); color: var(--red); }
.badge-amber { background: var(--amber-light); color: var(--amber); }
.badge-green { background: var(--green-light); color: var(--green); }
.badge-purple { background: var(--purple-light); color: var(--purple); }
```

#### Data Table

```css
.data-table { width: 100%; border-collapse: collapse; font-size: var(--fs-sm); }
.data-table th {
  text-align: left; padding: 10px 16px; border-bottom: 2px solid #E5E5E5;
  color: var(--fg-muted); font-weight: 600; cursor: pointer; user-select: none;
}
.data-table th:hover { color: var(--fg-heading); }
.data-table td { padding: 10px 16px; border-bottom: 1px solid #F0F0F0; }
.data-table tr:hover { background: var(--bg); }
```

Make tables sortable by adding click handlers to `<th>` elements that sort the underlying data array and re-render the `<tbody>`.

#### Funnel Chart (Pure CSS)

```html
<div class="funnel">
  <div class="funnel-stage" style="--width: 100%; --color: var(--blue);">
    <span class="funnel-label">Awareness</span>
    <span class="funnel-count">1,243</span>
  </div>
  <div class="funnel-stage" style="--width: 72%; --color: var(--purple);">
    <span class="funnel-label">Consideration</span>
    <span class="funnel-count">895</span>
  </div>
  <div class="funnel-stage" style="--width: 38%; --color: var(--amber);">
    <span class="funnel-label">Evaluation</span>
    <span class="funnel-count">472</span>
  </div>
  <div class="funnel-stage" style="--width: 15%; --color: var(--green);">
    <span class="funnel-label">Conversion</span>
    <span class="funnel-count">186</span>
  </div>
</div>
```

```css
.funnel { display: flex; flex-direction: column; gap: 8px; max-width: 600px; }
.funnel-stage {
  width: var(--width); background: var(--color); color: white;
  padding: 12px 20px; border-radius: var(--radius-sm);
  display: flex; justify-content: space-between; align-items: center;
  font-weight: 600; font-size: var(--fs-sm); min-width: 200px;
  transition: width 600ms ease;
}
```

#### Bar Chart (Pure CSS)

```css
.bar-chart { display: flex; flex-direction: column; gap: 12px; }
.bar-row { display: flex; align-items: center; gap: 12px; }
.bar-label { width: 120px; font-size: var(--fs-sm); color: var(--fg-muted); text-align: right; flex-shrink: 0; }
.bar-track { flex: 1; height: 28px; background: var(--bg); border-radius: var(--radius-sm); overflow: hidden; }
.bar-fill {
  height: 100%; background: var(--blue); border-radius: var(--radius-sm);
  display: flex; align-items: center; padding-left: 10px;
  color: white; font-size: var(--fs-sm); font-weight: 600;
  transition: width 600ms ease;
}
```

#### Donut Chart (SVG)

```javascript
function renderDonut(data, size = 160) {
  const total = data.reduce((s, d) => s + d.value, 0);
  const radius = size / 2 - 10;
  const innerRadius = radius * 0.6;
  let cumulative = 0;

  const paths = data.map(d => {
    const startAngle = (cumulative / total) * 2 * Math.PI - Math.PI / 2;
    cumulative += d.value;
    const endAngle = (cumulative / total) * 2 * Math.PI - Math.PI / 2;
    const largeArc = endAngle - startAngle > Math.PI ? 1 : 0;
    const x1 = size/2 + radius * Math.cos(startAngle);
    const y1 = size/2 + radius * Math.sin(startAngle);
    const x2 = size/2 + radius * Math.cos(endAngle);
    const y2 = size/2 + radius * Math.sin(endAngle);
    const ix1 = size/2 + innerRadius * Math.cos(endAngle);
    const iy1 = size/2 + innerRadius * Math.sin(endAngle);
    const ix2 = size/2 + innerRadius * Math.cos(startAngle);
    const iy2 = size/2 + innerRadius * Math.sin(startAngle);
    return `<path d="M${x1},${y1} A${radius},${radius} 0 ${largeArc} 1 ${x2},${y2}
      L${ix1},${iy1} A${innerRadius},${innerRadius} 0 ${largeArc} 0 ${ix2},${iy2} Z"
      fill="${d.color}" />`;
  });

  return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">${paths.join('')}
    <text x="${size/2}" y="${size/2}" text-anchor="middle" dominant-baseline="middle"
      font-size="20" font-weight="700" fill="var(--fg-heading)">${total}</text></svg>`;
}
```

### Step 6: Add Search and Filtering

```javascript
function initSearch(inputId, containerSelector, itemSelector) {
  const input = document.getElementById(inputId);
  input.addEventListener('input', () => {
    const query = input.value.toLowerCase();
    const items = document.querySelectorAll(`${containerSelector} ${itemSelector}`);
    items.forEach(item => {
      const text = item.textContent.toLowerCase();
      item.style.display = text.includes(query) ? '' : 'none';
    });
  });
}
```

Place the search input in the section header, above the view toggles. For large datasets (100+ items), debounce the input handler by 150ms to avoid janky re-renders.

### Step 7: Wire Navigation

```javascript
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const sections = document.querySelectorAll('.report-section');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetId = item.dataset.target;
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');
      sections.forEach(s => s.style.display = s.id === targetId ? 'block' : 'none');
      document.getElementById('content').scrollTop = 0;
    });
  });

  // Activate first item
  if (navItems.length) navItems[0].click();
}
```

### Step 8: Final Assembly Checklist

Before delivering the HTML file, verify:

1. All CSS is inlined in a single `<style>` block (no external stylesheets)
2. All JavaScript is inlined in a single `<script>` block at the end of `<body>` (no external scripts)
3. No external font requests (use system font stack as fallback; only reference Google Fonts if explicitly approved)
4. File size is under 2MB (compress data arrays; remove raw data not needed for display)
5. Navigation works with all sections accessible
6. View toggles switch between grid, list, and detail views
7. Search filters items in real-time
8. Tables are sortable by clicking column headers
9. Status colors are semantically correct (red=bad, amber=warning, green=good, purple=info)
10. The file opens correctly in Chrome, Firefox, and Safari

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Report sections overlap or stack incorrectly | Missing `display: none` on inactive sections | Initialize with all sections hidden, then show first via `navItems[0].click()` |
| Charts render incorrectly at small widths | Fixed pixel widths on chart containers | Use `max-width` with percentage-based widths; add `min-width` on funnel stages |
| File too large to email (>10MB) | Raw data arrays embedded in HTML | Aggregate data server-side; only embed display-ready summaries |
| Font rendering inconsistent | Missing system font fallbacks | Always include the full fallback chain in `--font` |
| Status colors feel arbitrary | Using red/amber/green without consistent meaning | Follow the semantic mapping strictly: red=error, amber=warning, green=success |
| Sidebar nav doesn't scroll | Missing `overflow-y: auto` on sidebar | Add `overflow-y: auto` to `.sidebar` and `height: 100vh` to the parent flex container |

### Cross-References

- **site-auditor** — Primary producer of report data consumed by the hub generator
- **data-intelligence-pipeline** — Generates dashboard output using this design system
- **pagespeed-audit** — Produces performance metrics visualized as report sections
- **content-graph** — Provides graph visualization data rendered within report hubs
