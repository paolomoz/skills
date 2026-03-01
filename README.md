# Claude Code Skills

Personal collection of **26 reusable Claude Code skills** extracted from 12 production projects. Each skill encapsulates a proven pattern — from AI pipeline orchestration to brand extraction to accessibility auditing — as instructional prompts that Claude Code can follow.

## Skills Catalog

| # | Skill | Category | Description |
|---|-------|----------|-------------|
| 1 | [railway-deploy](skills/railway-deploy/SKILL.md) | deploy | Deploy monorepos to Railway with Dockerfiles, config-as-code, and GraphQL API |
| 2 | [infographic-video](skills/infographic-video/SKILL.md) | content | Transform meeting summaries into ~5 min videos with infographics and dialogue |
| 3 | [infographics-generate-style](skills/infographics-generate-style/SKILL.md) | content | Generate infographic style definitions from reference material |
| 4 | [highlight-reel](skills/highlight-reel/SKILL.md) | content | Create 60-90s polished highlight reels from screen recordings using Remotion |
| 5 | [screenshot-capture](skills/screenshot-capture/SKILL.md) | content | Capture full-page and viewport screenshots with overlay removal |
| 6 | [sse-streaming](skills/sse-streaming/SKILL.md) | patterns | SSE streaming from Cloudflare Workers with reconnection and state persistence |
| 7 | [multi-model-orchestrator](skills/multi-model-orchestrator/SKILL.md) | patterns | Multi-stage AI pipelines with role-based model routing |
| 8 | [cloudflare-fullstack](skills/cloudflare-fullstack/SKILL.md) | patterns | Full-stack apps on Cloudflare Workers with KV, D1, R2, Vectorize |
| 9 | [session-context](skills/session-context/SKILL.md) | patterns | Multi-turn session tracking with sessionStorage and KV caching |
| 10 | [incremental-processor](skills/incremental-processor/SKILL.md) | patterns | Hash-based change detection for resumable batch processing |
| 11 | [multi-provider-fallback](skills/multi-provider-fallback/SKILL.md) | patterns | AI provider abstraction with automatic fallback and result synthesis |
| 12 | [brand-extractor](skills/brand-extractor/SKILL.md) | brand-design | Extract brand profiles from URLs or descriptions using multi-tier AI analysis |
| 13 | [brand-css-generator](skills/brand-css-generator/SKILL.md) | brand-design | Generate CSS custom property overrides from brand profiles |
| 14 | [figma-token-sync](skills/figma-token-sync/SKILL.md) | brand-design | Bidirectional sync between CSS custom properties and Figma variables |
| 15 | [design-system-extractor](skills/design-system-extractor/SKILL.md) | brand-design | Extract design tokens from live websites using Puppeteer |
| 16 | [generative-page-pipeline](skills/generative-page-pipeline/SKILL.md) | page-generation | Multi-stage AI pipeline: query → intent → blocks → images → published page |
| 17 | [conversational-page-builder](skills/conversational-page-builder/SKILL.md) | page-generation | Interactive AI agent loop for iterative page creation with Claude tool calling |
| 18 | [ai-image-generator](skills/ai-image-generator/SKILL.md) | page-generation | Multi-provider image generation with fallbacks, caching, and R2 storage |
| 19 | [da-content-pipeline](skills/da-content-pipeline/SKILL.md) | page-generation | Convert HTML to DA format and upload to AEM Edge Delivery Services |
| 20 | [site-auditor](skills/site-auditor/SKILL.md) | audit | Cross-reference query indexes, sitemaps, and navigation for content gaps |
| 21 | [pagespeed-audit](skills/pagespeed-audit/SKILL.md) | audit | Collect and analyze Core Web Vitals and PageSpeed scores |
| 22 | [accessibility-auditor](skills/accessibility-auditor/SKILL.md) | audit | WCAG 2.1 AA compliance and content safety auditing |
| 23 | [block-detector](skills/block-detector/SKILL.md) | audit | Detect and catalog content blocks on web pages using Puppeteer |
| 24 | [content-graph](skills/content-graph/SKILL.md) | data-intelligence | Build semantic content graphs for navigation and recommendations |
| 25 | [data-intelligence-pipeline](skills/data-intelligence-pipeline/SKILL.md) | data-intelligence | End-to-end pipeline: fetch → analyze → synthesize → dashboard |
| 26 | [report-hub-generator](skills/report-hub-generator/SKILL.md) | data-intelligence | Generate single-page HTML report hubs with interactive navigation |

## Categories

### deploy — Deployment & Infrastructure
Skills for deploying applications to cloud platforms.

- **railway-deploy** — Railway monorepo deployment with Dockerfiles and config-as-code

### content — Content Generation & Media
Skills for generating videos, images, and visual content.

- **infographic-video** — Meeting summary → infographic video pipeline (ElevenLabs + Gemini)
- **infographics-generate-style** — Style definition generator for infographic production
- **highlight-reel** — Screen recording → polished demo video (Remotion)
- **screenshot-capture** — Automated website screenshots with overlay removal (Playwright)

### patterns — Cross-Cutting Infrastructure
Foundational patterns used across multiple domain skills. These are the building blocks.

- **sse-streaming** — Server-Sent Events with ReadableStream, EventSource, reconnection
- **multi-model-orchestrator** — Route tasks to optimal models by role (classify → reason → generate)
- **cloudflare-fullstack** — Workers + KV + D1 + R2 + Vectorize + AI bindings
- **session-context** — Session tracking across multi-turn interactions
- **incremental-processor** — Process large datasets incrementally with hash-based change detection
- **multi-provider-fallback** — Provider abstraction with automatic fallback chains

```
┌─────────────────────────────────────────────────────────┐
│                    patterns (foundation)                  │
│  sse-streaming ─── multi-model-orchestrator              │
│       │                    │                             │
│  cloudflare-fullstack  session-context                   │
│       │                    │                             │
│  incremental-processor  multi-provider-fallback          │
└───────────┬────────────────┬────────────────┬────────────┘
            │                │                │
   ┌────────▼──┐    ┌───────▼───┐    ┌───────▼───┐
   │ page-gen  │    │   audit   │    │   data    │
   │ pipeline  │    │  tools    │    │  intel    │
   └───────────┘    └───────────┘    └───────────┘
```

### brand-design — Brand & Design Systems
Extract, generate, and sync brand identity assets and design tokens.

- **brand-extractor** — Multi-tier brand profile extraction (web search → AI knowledge → fallback)
- **brand-css-generator** — CSS custom properties from brand profiles with WCAG AA enforcement
- **figma-token-sync** — Push/pull/diff CSS tokens ↔ Figma variables
- **design-system-extractor** — Puppeteer-based computed style extraction from live sites

```
brand-extractor ──→ brand-css-generator ──→ figma-token-sync
                          ↑                        ↑
              design-system-extractor ──────────────┘
```

### page-generation — AI Page Creation
End-to-end pipelines for generating web pages with AI.

- **generative-page-pipeline** — Query → intent → blocks → images → published page
- **conversational-page-builder** — Multi-turn chat agent for iterative page editing
- **ai-image-generator** — Multi-provider image generation (fal.ai, Imagen, Gemini)
- **da-content-pipeline** — HTML → DA format conversion and AEM upload

```
generative-page-pipeline ──→ da-content-pipeline
         │                           ↑
         ├── ai-image-generator      │
         │                           │
conversational-page-builder ─────────┘
```

### audit — Website Analysis
Audit websites for content quality, performance, accessibility, and structure.

- **site-auditor** — Cross-reference indexes, sitemaps, and navigation for 11 gap categories
- **pagespeed-audit** — Core Web Vitals collection and analysis
- **accessibility-auditor** — WCAG 2.1 AA compliance with content safety testing
- **block-detector** — Content block detection with CSS selector generation

### data-intelligence — Data Pipelines & Reports
Transform raw data into structured intelligence and visual reports.

- **content-graph** — Semantic content graphs for topic mapping and recommendations
- **data-intelligence-pipeline** — Slack/document → AI extraction → synthesis → dashboard
- **report-hub-generator** — Single-page HTML report hubs with interactive components

```
data-intelligence-pipeline
         │
         ├── content-graph
         │
         └── report-hub-generator
```

## Quick Start

### Using a skill

Skills are installed as a Claude Code plugin. Once installed, Claude Code matches user requests to skills via trigger keywords in the skill description.

```bash
# Install the plugin (from this repo root)
claude plugin install .

# Then just ask Claude Code naturally:
# "Set up SSE streaming for my Cloudflare Worker"
# "Extract the brand identity from https://example.com"
# "Audit this website for accessibility issues"
# "Generate a report hub from these analysis results"
```

### Skill structure

Each skill lives in its own directory under `skills/`:

```
skills/
└── skill-name/
    ├── SKILL.md              # Instructions (required)
    ├── references/            # Supporting docs (optional)
    │   └── schema.md
    └── scripts/               # Executable scripts (optional)
        └── run.py
```

### Adding a new skill

1. Create a directory under `skills/` with a descriptive kebab-case name
2. Add a `SKILL.md` with YAML front matter (`name`, `description` with trigger keywords) and instructions
3. Register it in `.claude-plugin/marketplace.json` under the appropriate plugin category
4. Optionally add `references/` for supporting documentation and `scripts/` for executable tools

See `skills/_template/SKILL.md` for the minimal template.

## Contributing

This is a personal skills collection, but the patterns are designed to be generally applicable. Each skill documents:

- **When to Use** — Scenarios that trigger the skill
- **Step-by-step Instructions** — What Claude Code should do
- **Code Snippets** — Production-tested patterns from real projects
- **Troubleshooting** — Common issues with causes and fixes
- **Cross-References** — Related skills for composition
