---
name: pagespeed-audit
description: Collect and analyze Core Web Vitals and PageSpeed scores across multiple URLs using the PageSpeed Insights API and RUM data aggregation. Use when "running PageSpeed tests", "Core Web Vitals audit", "performance benchmarking", or "CWV analysis".
---

# PageSpeed Audit

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| audit | "running PageSpeed tests", "Core Web Vitals audit", "performance benchmarking", "CWV analysis" | Medium | 5 projects |

Aggregate and analyze Core Web Vitals from Real User Monitoring (RUM) bundles and the PageSpeed Insights API. Produces per-URL performance profiles with device segmentation, traffic analysis, and cross-referenced quality issues. The output feeds directly into report-hub-generator for stakeholder reporting and into site-auditor for traffic-weighted content prioritization.

## When to Use
- User wants to audit Core Web Vitals across a set of pages or an entire domain
- User has RUM bundle data and needs it aggregated into actionable metrics
- User wants to identify the worst-performing pages by LCP, CLS, INP, or TTFB
- User needs device-segmented performance data (mobile vs. desktop)
- User wants to cross-reference performance data with content quality from site-auditor
- A downstream skill (report-hub-generator) needs structured performance data as input

## Instructions

### Step 1: Determine the Data Source

The skill supports two data sources. Use whichever is available; if both are available, prefer RUM data (it represents real user experience) and supplement with PSI API data for lab metrics.

| Source | What It Provides | When to Use |
|--------|-----------------|-------------|
| RUM Bundles | Real user CWV, traffic data, referrers, device types | When the user has access to RUM collection (e.g., Adobe RUM, custom RUM) |
| PageSpeed Insights API | Lab CWV, Lighthouse scores, optimization suggestions | When no RUM data is available, or for supplementary lab benchmarks |

---

### Step 2: Process RUM Bundle Data

RUM data arrives as an array of bundles, each representing a single page view with weighted sampling.

#### Bundle Structure

```javascript
// Each bundle represents one or more page views (weight-based sampling)
{
  "id": "abc123",
  "url": "https://example.com/blog/performance-tips",
  "weight": 100,        // This bundle represents ~100 actual page views
  "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)...",
  "events": [
    { "checkpoint": "cwv-lcp", "value": 2340, "source": "img.hero-image" },
    { "checkpoint": "cwv-cls", "value": 0.042 },
    { "checkpoint": "cwv-inp", "value": 156, "source": "button.add-to-cart" },
    { "checkpoint": "cwv-ttfb", "value": 380 },
    { "checkpoint": "click", "source": "a.cta-primary", "target": "/pricing" },
    { "checkpoint": "enter", "source": "https://google.com/search?q=..." },
    { "checkpoint": "404" },
    { "checkpoint": "missingresource", "source": "/scripts/legacy-widget.js" }
  ]
}
```

Key checkpoint types:
- `cwv-lcp`: Largest Contentful Paint in milliseconds
- `cwv-cls`: Cumulative Layout Shift (unitless score)
- `cwv-inp`: Interaction to Next Paint in milliseconds
- `cwv-ttfb`: Time to First Byte in milliseconds
- `click`: User click event with source selector and target URL
- `enter`: Page entry with referrer source
- `404`: Page returned a 404 status
- `missingresource`: A subresource (JS, CSS, image) failed to load

#### Aggregation Per URL

For each unique URL, aggregate CWV metrics using the weight field:

```javascript
function aggregateMetrics(bundles) {
  const urlMap = new Map()

  for (const bundle of bundles) {
    const path = new URL(bundle.url).pathname
    if (!urlMap.has(path)) {
      urlMap.set(path, { views: 0, lcp: [], cls: [], inp: [], ttfb: [] })
    }
    const entry = urlMap.get(path)
    entry.views += bundle.weight

    for (const event of bundle.events) {
      if (event.checkpoint === 'cwv-lcp') entry.lcp.push({ value: event.value, weight: bundle.weight })
      if (event.checkpoint === 'cwv-cls') entry.cls.push({ value: event.value, weight: bundle.weight })
      if (event.checkpoint === 'cwv-inp') entry.inp.push({ value: event.value, weight: bundle.weight })
      if (event.checkpoint === 'cwv-ttfb') entry.ttfb.push({ value: event.value, weight: bundle.weight })
    }
  }

  return urlMap
}
```

For each metric array, compute:
- **Weighted average**: `sum(value * weight) / sum(weight)`
- **p75 (75th percentile)**: Sort by value, find the value at the 75th weighted percentile. This is the metric Google uses for CWV assessment.
- **Sample count**: Number of bundles contributing to this metric (not the weighted total)

---

### Step 3: Apply CWV Thresholds

Classify each metric using Google's official thresholds:

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | <= 2500ms | 2500-4000ms | > 4000ms |
| CLS | <= 0.1 | 0.1-0.25 | > 0.25 |
| INP | <= 200ms | 200-500ms | > 500ms |
| TTFB | <= 800ms | 800-1800ms | > 1800ms |

A page **passes** Core Web Vitals if LCP, CLS, and INP are all in the "Good" range at the p75. TTFB is an auxiliary metric -- it is not part of the official CWV assessment but is a strong diagnostic signal.

```javascript
function assessCWV(metrics) {
  return {
    lcp: { value: metrics.lcp.p75, rating: metrics.lcp.p75 <= 2500 ? 'good' : metrics.lcp.p75 <= 4000 ? 'needs-improvement' : 'poor' },
    cls: { value: metrics.cls.p75, rating: metrics.cls.p75 <= 0.1 ? 'good' : metrics.cls.p75 <= 0.25 ? 'needs-improvement' : 'poor' },
    inp: { value: metrics.inp.p75, rating: metrics.inp.p75 <= 200 ? 'good' : metrics.inp.p75 <= 500 ? 'needs-improvement' : 'poor' },
    ttfb: { value: metrics.ttfb.p75, rating: metrics.ttfb.p75 <= 800 ? 'good' : metrics.ttfb.p75 <= 1800 ? 'needs-improvement' : 'poor' },
    passing: metrics.lcp.p75 <= 2500 && metrics.cls.p75 <= 0.1 && metrics.inp.p75 <= 200
  }
}
```

---

### Step 4: Segment by Device Type

Classify each bundle's userAgent into one of four device categories:

| Category | Detection Pattern |
|----------|-----------------|
| mobile | Contains `Mobile`, `iPhone`, `Android` (but not `Tablet`) |
| tablet | Contains `iPad`, `Tablet`, `Android` with large viewport hints |
| desktop | Does not match mobile or tablet patterns, not a bot |
| bot | Contains `bot`, `crawler`, `spider`, `Googlebot`, `Bingbot`, `lighthouse` |

Exclude bot traffic from CWV calculations entirely -- bot performance data is not representative of user experience. Track bot traffic separately for crawl budget analysis.

Produce separate CWV assessments for mobile and desktop. Mobile metrics are typically worse and are the primary signal Google uses for ranking.

---

### Step 5: Analyze Traffic Patterns

Extract non-CWV insights from the RUM bundles:

#### Top Referrers
Aggregate `enter` checkpoint sources by domain. Group into categories: organic search (google, bing, duckduckgo), social (twitter, facebook, linkedin), direct (no referrer), and other.

#### Top Click Targets
Aggregate `click` checkpoints by target URL. This reveals the most-used navigation paths and CTAs.

#### Error Signals
- **404 pages**: Bundles with a `404` checkpoint. Cross-reference with site-auditor to identify broken links that are actively generating user errors.
- **Missing resources**: Bundles with `missingresource` checkpoints. Aggregate by resource URL to find globally missing assets.

---

### Step 6: Cross-Reference with Site Auditor Data (Optional)

If site-auditor has been run and `data/audit/analysis.json` exists, enrich the performance data:

- **Stale pages with traffic**: Pages flagged as stale in the audit that still receive significant traffic (views > median). These are high-priority refreshes.
- **Missing OG images with social traffic**: Pages missing OG images that receive referral traffic from social media platforms. These are losing click-through rate on every share.
- **Poor CWV on high-traffic pages**: Pages in the top 20% by traffic volume that fail CWV assessment. These have the highest user impact.

---

### Step 7: Generate the Output

Write the structured output to `data/audit/performance.json`:

```json
{
  "meta": {
    "domain": "example.com",
    "period": { "start": "2024-12-01", "end": "2024-12-15" },
    "generatedAt": "2024-12-15T10:30:00Z",
    "source": "rum",
    "bundleCount": 14523
  },
  "summary": {
    "totalViews": 1452300,
    "uniqueUrls": 847,
    "cwvPassRate": 0.72,
    "totalClicks": 328400,
    "devices": {
      "mobile": { "views": 870000, "cwvPassRate": 0.65 },
      "desktop": { "views": 540000, "cwvPassRate": 0.82 },
      "tablet": { "views": 42300, "cwvPassRate": 0.71 }
    }
  },
  "pages": [
    {
      "path": "/blog/performance-tips",
      "views": 12400,
      "cwv": {
        "lcp": { "avg": 2100, "p75": 2680, "samples": 124, "rating": "needs-improvement" },
        "cls": { "avg": 0.04, "p75": 0.08, "samples": 124, "rating": "good" },
        "inp": { "avg": 120, "p75": 180, "samples": 98, "rating": "good" },
        "ttfb": { "avg": 340, "p75": 520, "samples": 124, "rating": "good" }
      },
      "passing": false,
      "lcpElement": "img.hero-image",
      "topReferrers": ["google.com", "twitter.com"],
      "topClicks": ["/pricing", "/docs/getting-started"]
    }
  ],
  "issues": {
    "fourOhFourPages": [
      { "path": "/old-page", "views": 340, "topReferrers": ["google.com"] }
    ],
    "poorCwv": [
      { "path": "/products/gallery", "metric": "lcp", "p75": 5200, "views": 8900 }
    ],
    "globalMissingResources": [
      { "resource": "/scripts/legacy-widget.js", "affectedPages": 124, "affectedViews": 45000 }
    ]
  }
}
```

---

### Step 8: Present Results to the User

Summarize the performance audit with these sections:

1. **Overall CWV pass rate**: What percentage of pages pass Core Web Vitals? How does mobile compare to desktop?
2. **Worst offenders**: Top 5 pages by traffic volume that fail CWV, with the specific failing metric and its value
3. **Quick wins**: Pages where a single metric is barely failing (e.g., LCP at 2600ms -- likely fixable with image optimization)
4. **Global issues**: Missing resources or errors that affect many pages simultaneously
5. **Traffic insights**: Top referrers, most-clicked CTAs, and any 404 pages receiving traffic

Always frame performance numbers in user impact terms: "12,400 users per month experience an LCP of 2.7 seconds on this page" rather than just reporting the raw number.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| CWV metrics are all null | Bundles contain no `cwv-*` checkpoints | RUM library may not be collecting CWV. Check that the CWV collection script is installed. |
| Mobile pass rate is much lower than desktop | Normal -- mobile networks are slower | Focus optimization on mobile. Consider separate mobile/desktop analysis. |
| p75 is much higher than average | Long-tail distribution with outliers | This is expected. p75 is the correct metric; average understates user pain. |
| Bot traffic is inflating view counts | Bots not filtered | Apply device segmentation (Step 4) and exclude bot category from all metrics. |
| Missing resource affects 0 pages | Resource URL does not match any page | The resource may be loaded dynamically; check if it is a third-party script. |
| PSI API returns rate limit errors | Too many requests in a short period | Batch requests with 1-second delays between calls. PSI API allows 25,000 queries/day with an API key. |

## Cross-References

- **site-auditor**: Provides content quality data for cross-referencing with performance metrics (stale pages with traffic, broken links with clicks)
- **accessibility-auditor**: Performance and accessibility often share root causes (e.g., large unoptimized images affect both LCP and screen reader experience)
- **report-hub-generator**: Consumes performance.json to produce formatted performance reports for stakeholders
