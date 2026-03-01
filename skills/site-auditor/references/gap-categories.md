# Site Auditor Gap Categories Reference

This document defines all 11 gap categories used by the site-auditor skill. Each category includes its detection logic, severity level, and concrete examples.

---

## Category 1: In Index but Not Sitemap

**Detection**: Path exists in `query-index.json` data but has no matching `<loc>` in `sitemap.xml`.

**Severity**: High

**What it means**: The page exists in the content management system and is served to users, but search engines cannot discover it through the sitemap. This may be intentional (draft content, internal pages) or accidental (sitemap generation pipeline excludes certain paths).

**Examples**:
- `/blog/draft-performance-guide` -- draft content that was published but the sitemap was not regenerated
- `/internal/style-guide` -- internal page intentionally excluded, but should be verified
- `/products/new-feature-preview` -- new page added after last sitemap rebuild

**Action**: For each path, determine if the exclusion is intentional. If not, trigger a sitemap rebuild or add the path to the sitemap template.

---

## Category 2: In Sitemap but Not Index

**Detection**: URL appears in `sitemap.xml` but has no matching entry in `query-index.json` data.

**Severity**: Medium

**What it means**: The sitemap tells search engines this page exists, but the content index has no record of it. The page may have been deleted, redirected, or excluded from the CMS export.

**Examples**:
- `/event/2022-annual-conference` -- event page that was removed from the CMS but the sitemap was not updated
- `/blog/retracted-post` -- post that was unpublished but the sitemap still references it
- `/products/discontinued-widget` -- product removed from catalog but lingering in the sitemap

**Action**: Verify whether the URL returns a 200, 301, or 404. Remove 404s from the sitemap. For 301s, update the sitemap to point to the redirect target.

---

## Category 3: Stale Content

**Detection**: `lastModified` timestamp in the query index is older than 12 months from the audit date.

**Severity**: Low to Medium (context-dependent)

**What it means**: The content has not been updated in over a year. For blog posts and news articles, this is expected. For product pages, documentation, and landing pages, staleness signals neglect and may present outdated information to users.

**Examples**:
- `/docs/api-v2-reference` (last modified: 2022-06-15) -- API documentation for a version that may have changed
- `/blog/2021/industry-predictions` (last modified: 2021-01-03) -- naturally aging blog content, low concern
- `/pricing` (last modified: 2023-01-10) -- pricing page that may show outdated rates

**Action**: Review stale pages by category. Product/pricing/docs pages should be refreshed. Blog posts can be left as-is unless they contain outdated factual claims. Consider adding "last reviewed" dates to evergreen content.

---

## Category 4: Missing Descriptions

**Detection**: The `description` field in the query index entry is empty, null, undefined, or shorter than 20 characters.

**Severity**: Medium

**What it means**: The page lacks a meaningful meta description. Search engines will auto-generate a snippet from page content, which is often suboptimal. Social sharing cards will also lack descriptive text.

**Examples**:
- `/about` with description: `""` -- completely empty
- `/products/analytics` with description: `"Analytics"` -- too short to be useful (10 characters)
- `/blog/2024/launch` with description: `null` -- field not populated by CMS

**Action**: Write unique, compelling descriptions of 120-160 characters for each page. Prioritize high-traffic pages and pages with social sharing potential.

---

## Category 5: Missing OG Images

**Detection**: The `image` field in the query index entry is empty, null, or matches known placeholder patterns (`placeholder`, `default`, `no-image`, generic stock photo paths).

**Severity**: Medium

**What it means**: When the page is shared on social media (Twitter/X, LinkedIn, Facebook, Slack), the link preview will either show no image or a generic placeholder. This significantly reduces click-through rates on social shares.

**Examples**:
- `/blog/2024/performance-guide` with image: `""` -- no image at all
- `/products/enterprise` with image: `/media/placeholder.png` -- placeholder detected
- `/about/team` with image: `/default-og.jpg` -- default fallback image, not page-specific

**Action**: Create unique OG images for high-value pages. At minimum, generate branded OG images using the page title and brand colors. Use a tool like the generative-page-pipeline to automate OG image creation.

---

## Category 6: Duplicate Titles

**Detection**: Two or more entries in the query index share the exact same `title` value after trimming leading and trailing whitespace.

**Severity**: Medium

**What it means**: Duplicate titles confuse search engine ranking signals and make it difficult for users to distinguish between pages in search results or browser tabs.

**Examples**:
- Three pages all titled `"Home"`: `/`, `/home`, `/index`
- Two pages titled `"Getting Started"`: `/docs/getting-started`, `/developer/getting-started`
- Five pages titled `"Blog"`: `/blog`, `/blog/page/2`, `/blog/page/3`, `/blog/page/4`, `/blog/page/5` (pagination pages inheriting the parent title)

**Action**: Ensure every page has a unique, descriptive title. For pagination, append page numbers: "Blog - Page 2". For similar content in different sections, add section context: "Getting Started - Developer Docs" vs. "Getting Started - User Guide".

---

## Category 7: Broken Navigation Links

**Detection**: A path found in the site navigation (parsed from `<a href>` in nav/header/footer elements) does not appear in either the query index or the sitemap.

**Severity**: High

**What it means**: Users clicking this navigation link may encounter a 404 error. The link is visible and prominent (it is in the main navigation), making this a high-impact user experience issue.

**Examples**:
- `/products/retired-saas-tool` -- product was discontinued but the nav was not updated
- `/careers` -- careers page moved to an external ATS platform but internal link remains
- `/blog/featured` -- featured blog landing page that was removed during a redesign

**Action**: Either restore the target page, update the navigation link to point to the correct URL, or remove the link from navigation entirely. Verify with an HTTP request to confirm the 404 before taking action.

---

## Category 8: Old Branding References

**Detection**: The `title` or `description` field contains strings that match a configurable list of outdated brand terms.

**Severity**: Medium

**What it means**: The page still references a previous company name, retired product name, old tagline, or deprecated terminology. This creates brand inconsistency and may confuse users or partners.

**Examples**:
- `/about` with description containing "Formerly known as OldCo" -- rebrand reference that should have been removed
- `/products/widget-pro` with title "WidgetPro by LegacyBrand" -- old parent brand name
- `/docs/setup` with description mentioning "CloudSync" -- product renamed to "DataBridge" six months ago

**Action**: Update all references to use current brand terminology. Maintain a brand term mapping (old term -> new term) in the brand-extractor skill's output for automated detection.

---

## Category 9: Pages in Navigation but Not Index

**Detection**: A path from the navigation exists in the sitemap but does NOT exist in the query index.

**Severity**: Medium

**What it means**: The page is linked in the navigation and indexed by search engines via the sitemap, but the content management system does not have an entry for it. This suggests a content pipeline gap -- the page was created outside the normal CMS workflow.

**Examples**:
- `/partners` -- a static HTML page created by the marketing team outside the CMS
- `/events/2024-summit` -- an event page managed by a separate system
- `/legal/privacy` -- a legal page maintained by the legal team in a different tool

**Action**: Either add the page to the CMS/content index, or document it as an intentional exception. If the page is managed externally, consider adding a manual entry to the query index for completeness.

---

## Category 10: Deprecated Pages

**Detection**: The path or title contains deprecation signals:
- Path segments: `/deprecated/`, `/archive/`, `/legacy/`, `/old/`, `/v1/` (when higher versions exist), `/retired/`
- Title keywords: "deprecated", "archived", "legacy", "end of life", "sunset", "retired"

**Severity**: Low

**What it means**: The page is explicitly marked as deprecated or archived through its URL structure or title. It may still receive traffic from bookmarks, external links, or search results.

**Examples**:
- `/legacy/v1-api-reference` -- old API docs that should redirect to the current version
- `/archive/2020-annual-report` -- archived content, intentionally preserved
- `/docs/deprecated-feature-x` -- documentation for a removed feature

**Action**: For each deprecated page, decide one of three outcomes: (1) redirect to the current equivalent, (2) add a prominent deprecation banner with a link to the replacement, or (3) leave as-is if the content is still valid for historical reference. Remove deprecated pages from active navigation.

---

## Category 11: Lab/Experimental Pages

**Detection**: The path contains experimental signals: `/lab/`, `/labs/`, `/experimental/`, `/beta/`, `/preview/`, `/sandbox/`, `/canary/`, `/prototype/`.

**Severity**: Low to Medium

**What it means**: These pages may be internal experiments, beta features, or sandbox environments that were accidentally (or intentionally) exposed in the public index or sitemap. If intentional, they should be clearly labeled. If accidental, they represent a potential information leak.

**Examples**:
- `/labs/ai-chat-prototype` -- internal prototype accidentally indexed
- `/beta/new-dashboard` -- beta feature preview, intentionally public but should have a beta banner
- `/sandbox/test-checkout` -- test environment page that should never be public

**Action**: Verify whether each lab/experimental page should be publicly accessible. For intentional beta pages, ensure they have appropriate "beta" or "experimental" labeling. For accidental exposures, remove from the index and sitemap, and add a `robots.txt` disallow rule or `noindex` meta tag.

---

## Severity Summary

| Severity | Categories | Action Timeline |
|----------|-----------|----------------|
| **High** | 1 (Index not Sitemap), 7 (Broken Nav Links) | Fix within 24-48 hours |
| **Medium** | 2 (Sitemap not Index), 4 (Missing Descriptions), 5 (Missing OG Images), 6 (Duplicate Titles), 8 (Old Branding), 9 (Nav not Index) | Fix within current sprint |
| **Low** | 3 (Stale Content), 10 (Deprecated Pages), 11 (Lab Pages) | Review during content audit cycles |

## Cross-Reference with RUM Data

When Real User Monitoring data is available, severity should be adjusted based on actual traffic:

- A **Low** severity stale page with 10,000+ monthly views becomes **High** severity
- A **High** severity broken nav link with zero clicks in 90 days becomes **Medium** severity
- A **Medium** severity missing OG image on a page with high social referral traffic becomes **High** severity

Always prioritize fixes by combining the category severity with traffic impact.
