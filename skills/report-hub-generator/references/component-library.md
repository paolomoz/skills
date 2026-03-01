# Report Hub Component Library

Reusable HTML/CSS components for building report hubs. Each component is self-contained and uses the design system CSS variables defined in the main SKILL.md. Copy and adapt these patterns directly into your generated HTML reports.

---

## KPI Card Row

A horizontal row of metric cards. Use at the top of a report section to summarize key numbers.

```html
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-value" style="color: var(--blue);">1,243</div>
    <div class="kpi-label">Pages Analyzed</div>
    <div class="kpi-delta positive">+12% vs last run</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: var(--green);">94.2%</div>
    <div class="kpi-label">Pass Rate</div>
    <div class="kpi-delta positive">+3.1% vs last run</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: var(--red);">47</div>
    <div class="kpi-label">Critical Issues</div>
    <div class="kpi-delta negative">+8 vs last run</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: var(--amber);">2.3s</div>
    <div class="kpi-label">Avg Load Time</div>
    <div class="kpi-delta neutral">No change</div>
  </div>
</div>
```

```css
.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}
.kpi-card {
  background: var(--bg-white);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow-card);
  text-align: center;
  transition: box-shadow var(--transition);
}
.kpi-card:hover {
  box-shadow: var(--shadow-hover);
}
.kpi-value {
  font-size: var(--fs-2xl);
  font-weight: 700;
  line-height: 1.2;
}
.kpi-label {
  font-size: var(--fs-sm);
  color: var(--fg-muted);
  margin-top: 4px;
}
.kpi-delta {
  font-size: var(--fs-sm);
  margin-top: 8px;
  font-weight: 600;
}
.kpi-delta.positive { color: var(--green); }
.kpi-delta.negative { color: var(--red); }
.kpi-delta.neutral { color: var(--fg-muted); }
```

**Usage notes**: Aim for 3-5 KPI cards per row. On narrow screens, the grid auto-wraps. Use semantic colors for the value: blue for neutral counts, green for positive rates, red for negative counts, amber for metrics that need context.

---

## Status Badge

Inline badge for tagging items with a status level.

```html
<span class="badge badge-red">Critical</span>
<span class="badge badge-amber">Warning</span>
<span class="badge badge-green">Passing</span>
<span class="badge badge-purple">Info</span>
```

```css
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 100px;
  font-size: var(--fs-sm);
  font-weight: 600;
  white-space: nowrap;
}
.badge-red { background: var(--red-light); color: var(--red); }
.badge-amber { background: var(--amber-light); color: var(--amber); }
.badge-green { background: var(--green-light); color: var(--green); }
.badge-purple { background: var(--purple-light); color: var(--purple); }
```

**Usage notes**: One badge per item. Never stack multiple badges. If an item has multiple statuses, show only the most severe one.

---

## Sortable Data Table

Full-width table with sortable columns and hover highlighting.

```html
<div class="table-container">
  <table class="data-table" id="pages-table">
    <thead>
      <tr>
        <th data-sort="path">Page Path <span class="sort-icon"></span></th>
        <th data-sort="score" data-type="number">Score <span class="sort-icon"></span></th>
        <th data-sort="status">Status <span class="sort-icon"></span></th>
        <th data-sort="issues" data-type="number">Issues <span class="sort-icon"></span></th>
      </tr>
    </thead>
    <tbody>
      <!-- Rows populated dynamically -->
    </tbody>
  </table>
</div>
```

```css
.table-container {
  background: var(--bg-white);
  border-radius: var(--radius);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--fs-sm);
}
.data-table th {
  text-align: left;
  padding: 12px 16px;
  border-bottom: 2px solid #E5E5E5;
  color: var(--fg-muted);
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
.data-table th:hover {
  color: var(--fg-heading);
}
.data-table th .sort-icon::after {
  content: ' \2195';  /* up-down arrow */
  opacity: 0.3;
}
.data-table th.sort-asc .sort-icon::after {
  content: ' \2191';  /* up arrow */
  opacity: 1;
}
.data-table th.sort-desc .sort-icon::after {
  content: ' \2193';  /* down arrow */
  opacity: 1;
}
.data-table td {
  padding: 10px 16px;
  border-bottom: 1px solid #F0F0F0;
  vertical-align: middle;
}
.data-table tr:hover {
  background: var(--bg);
}
.data-table tr:last-child td {
  border-bottom: none;
}
```

```javascript
function initSortableTable(tableId) {
  const table = document.getElementById(tableId);
  const headers = table.querySelectorAll('th[data-sort]');
  let currentSort = { key: null, direction: 'asc' };

  headers.forEach(th => {
    th.addEventListener('click', () => {
      const key = th.dataset.sort;
      const type = th.dataset.type || 'string';

      // Toggle direction
      if (currentSort.key === key) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
      } else {
        currentSort = { key, direction: 'asc' };
      }

      // Update visual indicators
      headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
      th.classList.add(`sort-${currentSort.direction}`);

      // Sort rows
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const colIndex = Array.from(th.parentNode.children).indexOf(th);

      rows.sort((a, b) => {
        let va = a.children[colIndex].textContent.trim();
        let vb = b.children[colIndex].textContent.trim();

        if (type === 'number') {
          va = parseFloat(va.replace(/[^0-9.\-]/g, '')) || 0;
          vb = parseFloat(vb.replace(/[^0-9.\-]/g, '')) || 0;
        }

        const cmp = va < vb ? -1 : va > vb ? 1 : 0;
        return currentSort.direction === 'asc' ? cmp : -cmp;
      });

      rows.forEach(row => tbody.appendChild(row));
    });
  });
}
```

**Usage notes**: Add `data-type="number"` to numeric columns for correct sorting. The sort indicator arrows use Unicode characters to avoid icon dependencies.

---

## Expandable Section

A collapsible content section with animated open/close.

```html
<div class="expandable">
  <button class="expandable-header" onclick="toggleExpand(this)">
    <span class="expandable-title">Section Title</span>
    <span class="expandable-meta">47 items</span>
    <span class="expandable-arrow">&#9660;</span>
  </button>
  <div class="expandable-body">
    <!-- Section content here -->
  </div>
</div>
```

```css
.expandable {
  background: var(--bg-white);
  border-radius: var(--radius);
  box-shadow: var(--shadow-card);
  margin-bottom: 12px;
  overflow: hidden;
}
.expandable-header {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 16px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-family: var(--font);
  font-size: var(--fs-base);
  text-align: left;
  gap: 12px;
}
.expandable-header:hover {
  background: var(--bg);
}
.expandable-title {
  font-weight: 600;
  color: var(--fg-heading);
  flex: 1;
}
.expandable-meta {
  font-size: var(--fs-sm);
  color: var(--fg-muted);
}
.expandable-arrow {
  font-size: 12px;
  color: var(--fg-muted);
  transition: transform var(--transition);
}
.expandable.open .expandable-arrow {
  transform: rotate(180deg);
}
.expandable-body {
  max-height: 0;
  overflow: hidden;
  transition: max-height 300ms ease;
  padding: 0 20px;
}
.expandable.open .expandable-body {
  max-height: 2000px;  /* Large enough to accommodate content */
  padding: 0 20px 20px;
}
```

```javascript
function toggleExpand(header) {
  const section = header.parentElement;
  section.classList.toggle('open');
}
```

**Usage notes**: Use for detail sections that should be hidden by default. Pre-open the first expandable in a group by adding the `open` class. The `max-height` transition is a CSS-only animation trick that avoids JavaScript height calculations.

---

## Progress Bar

Horizontal progress indicator with label and percentage.

```html
<div class="progress-group">
  <div class="progress-row">
    <span class="progress-label">Mobile Performance</span>
    <div class="progress-track">
      <div class="progress-fill" style="width: 73%; background: var(--amber);"></div>
    </div>
    <span class="progress-value">73%</span>
  </div>
  <div class="progress-row">
    <span class="progress-label">Desktop Performance</span>
    <div class="progress-track">
      <div class="progress-fill" style="width: 92%; background: var(--green);"></div>
    </div>
    <span class="progress-value">92%</span>
  </div>
</div>
```

```css
.progress-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.progress-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.progress-label {
  width: 160px;
  font-size: var(--fs-sm);
  color: var(--fg);
  flex-shrink: 0;
}
.progress-track {
  flex: 1;
  height: 8px;
  background: var(--bg);
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 600ms ease;
}
.progress-value {
  width: 48px;
  font-size: var(--fs-sm);
  font-weight: 600;
  color: var(--fg-heading);
  text-align: right;
  flex-shrink: 0;
}
```

**Usage notes**: Color the fill bar based on the value: green for 80%+, amber for 50-79%, red for below 50%. These thresholds match Lighthouse scoring conventions that stakeholders already understand.

---

## Filter Bar

Horizontal filter controls for narrowing down displayed items.

```html
<div class="filter-bar">
  <div class="search-box">
    <input type="text" id="search-input" placeholder="Search pages..." class="search-input" />
  </div>
  <div class="filter-group">
    <button class="filter-btn active" data-filter="all">All (247)</button>
    <button class="filter-btn" data-filter="critical">Critical (12)</button>
    <button class="filter-btn" data-filter="warning">Warning (45)</button>
    <button class="filter-btn" data-filter="passing">Passing (190)</button>
  </div>
</div>
```

```css
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.search-box {
  flex: 1;
  min-width: 200px;
}
.search-input {
  width: 100%;
  padding: 8px 14px;
  border: 1px solid #E5E5E5;
  border-radius: var(--radius-sm);
  font-family: var(--font);
  font-size: var(--fs-sm);
  outline: none;
  transition: border-color var(--transition);
}
.search-input:focus {
  border-color: var(--blue);
}
.filter-group {
  display: flex;
  gap: 4px;
}
.filter-btn {
  padding: 6px 14px;
  border: 1px solid #E5E5E5;
  background: var(--bg-white);
  border-radius: 100px;
  font-family: var(--font);
  font-size: var(--fs-sm);
  cursor: pointer;
  color: var(--fg-muted);
  transition: all var(--transition);
  white-space: nowrap;
}
.filter-btn:hover {
  border-color: var(--blue);
  color: var(--blue);
}
.filter-btn.active {
  background: var(--blue-light);
  border-color: var(--blue);
  color: var(--blue);
  font-weight: 600;
}
```

```javascript
function initFilters(filterBarSelector, itemSelector) {
  const buttons = document.querySelectorAll(`${filterBarSelector} .filter-btn`);

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      const items = document.querySelectorAll(itemSelector);

      items.forEach(item => {
        if (filter === 'all') {
          item.style.display = '';
        } else {
          item.style.display = item.dataset.status === filter ? '' : 'none';
        }
      });
    });
  });
}
```

**Usage notes**: Always include an "All" filter button with the total count. Update counts in button labels dynamically if items can be added or removed. Combine with search for large datasets.

---

## Empty State

Placeholder shown when a section has no data.

```html
<div class="empty-state">
  <div class="empty-icon">
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
      <circle cx="24" cy="24" r="20" stroke="var(--fg-muted)" stroke-width="2" stroke-dasharray="4 4"/>
      <path d="M18 24h12M24 18v12" stroke="var(--fg-muted)" stroke-width="2" stroke-linecap="round"/>
    </svg>
  </div>
  <div class="empty-title">No results found</div>
  <div class="empty-description">Try adjusting your search or filter criteria.</div>
</div>
```

```css
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--fg-muted);
}
.empty-icon {
  margin-bottom: 16px;
}
.empty-title {
  font-size: var(--fs-lg);
  font-weight: 600;
  color: var(--fg);
  margin-bottom: 4px;
}
.empty-description {
  font-size: var(--fs-sm);
}
```

**Usage notes**: Always show an empty state rather than a blank area. This confirms to the user that the section loaded correctly but has no matching data. Customize the message based on context ("No critical issues found" is better than "No results").

---

## Tooltip

Lightweight tooltip for adding context to values or labels.

```html
<span class="has-tooltip">
  LCP
  <span class="tooltip">Largest Contentful Paint: measures loading performance. Target: under 2.5 seconds.</span>
</span>
```

```css
.has-tooltip {
  position: relative;
  cursor: help;
  border-bottom: 1px dotted var(--fg-muted);
}
.tooltip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--fg-heading);
  color: white;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-sm);
  line-height: 1.4;
  width: max-content;
  max-width: 280px;
  z-index: 100;
  pointer-events: none;
  transition: opacity var(--transition), visibility var(--transition);
}
.tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: var(--fg-heading);
}
.has-tooltip:hover .tooltip {
  visibility: visible;
  opacity: 1;
}
```

**Usage notes**: Use tooltips sparingly for technical terms, metric abbreviations, and threshold explanations. Do not put critical information only in tooltips -- the information should be accessible without hovering for accessibility reasons.
