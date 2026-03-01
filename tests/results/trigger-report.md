# Skill Trigger Test Report
Generated: 2026-03-01T08:41:38.693Z
Model: global.anthropic.claude-opus-4-6-v1

## Summary
- Total: 82 | Pass: 60 | Fallback: 17 | Fail: 1
- Negative (no trigger): 4/4

## Results

| # | Skill | Prompt | Expected | Detected | Method | Status |
|---|-------|--------|----------|----------|--------|--------|
| 1 | sse-streaming | "Set up SSE streaming in my Cloudflare Worker" | sse-streaming | sse-streaming | tool_use | PASS |
| 2 | sse-streaming | "I need real-time server push events to the browser" | sse-streaming | sse-streaming | tool_use | PASS |
| 3 | sse-streaming | "Add event streaming with reconnection to my API" | sse-streaming | sse-streaming | tool_use | PASS |
| 4 | multi-model-orchestrator | "Build a multi-stage AI pipeline that classifies..." | multi-model-orchestrator | multi-model-orchestrator | tool_use | PASS |
| 5 | multi-model-orchestrator | "I need to route prompts to different LLM models..." | multi-model-orchestrator | multi-model-orchestrator | tool_use | PASS |
| 6 | multi-model-orchestrator | "Create an orchestrator that chains Claude and G..." | multi-model-orchestrator | multi-model-orchestrator | tool_use | PASS |
| 7 | cloudflare-fullstack | "Build a full-stack app on Cloudflare Workers wi..." | cloudflare-fullstack | cloudflare-fullstack | tool_use | PASS |
| 8 | cloudflare-fullstack | "Create a serverless app with KV storage and R2 ..." | cloudflare-fullstack | cloudflare-fullstack | tool_use | PASS |
| 9 | cloudflare-fullstack | "Set up a Cloudflare Workers project with wrangl..." | cloudflare-fullstack | cloudflare-fullstack | tool_use | PASS |
| 10 | session-context | "Add multi-turn session tracking with KV storage" | session-context | session-context | tool_use | PASS |
| 11 | session-context | "Implement conversation context that persists ac..." | session-context | session-context | tool_use | PASS |
| 12 | session-context | "Track user journey stages with sessionStorage a..." | session-context | session-context | tool_use | PASS |
| 13 | incremental-processor | "Build a hash-based change detection system for ..." | incremental-processor | incremental-processor | tool_use | PASS |
| 14 | incremental-processor | "I need resumable batch processing that skips un..." | incremental-processor | incremental-processor | tool_use | PASS |
| 15 | incremental-processor | "Create an incremental pipeline that detects fil..." | incremental-processor | incremental-processor | tool_use | PASS |
| 16 | multi-provider-fallback | "Create an AI client that falls back between pro..." | multi-provider-fallback | multi-provider-fallback | tool_use | PASS |
| 17 | multi-provider-fallback | "Build a multi-provider abstraction for Claude, ..." | multi-provider-fallback | multi-provider-fallback | tool_use | PASS |
| 18 | multi-provider-fallback | "I need automatic provider switching when one AI..." | multi-provider-fallback | multi-provider-fallback | tool_use | PASS |
| 19 | railway-deploy | "Deploy my monorepo to Railway with Dockerfiles" | railway-deploy | railway-deploy | tool_use | PASS |
| 20 | railway-deploy | "Set up Railway deployment with config-as-code f..." | railway-deploy | railway-deploy | tool_use | PASS |
| 21 | railway-deploy | "I need to deploy multiple services to Railway f..." | railway-deploy | railway-deploy | tool_use | PASS |
| 22 | infographic-video | "Create a video recap from this meeting summary" | infographic-video | infographic-video | tool_use | PASS |
| 23 | infographic-video | "Generate a meeting recap video with two-host di..." | infographic-video | infographic-video | tool_use | PASS |
| 24 | infographic-video | "Turn these meeting notes into a 5-minute video ..." | infographic-video | none | text_match | FALLBACK |
| 25 | infographics-generate-style | "Create a new infographic style from this refere..." | infographics-generate-style | none | text_match | FALLBACK |
| 26 | infographics-generate-style | "Generate a style definition for my infographics..." | infographics-generate-style | none | text_match | FALLBACK |
| 27 | infographics-generate-style | "Extract an infographic style from this PowerPoi..." | infographics-generate-style | infographics-generate-style | tool_use | PASS |
| 28 | highlight-reel | "Create a highlight reel from these screen recor..." | highlight-reel | highlight-reel | tool_use | PASS |
| 29 | highlight-reel | "Make a 60-second sizzle reel from my demo videos" | highlight-reel | highlight-reel | tool_use | PASS |
| 30 | highlight-reel | "Build a product demo video with title cards and..." | highlight-reel | highlight-reel | tool_use | PASS |
| 31 | screenshot-capture | "Capture full-page screenshots of these URLs wit..." | screenshot-capture | none | text_match | FALLBACK |
| 32 | screenshot-capture | "Take viewport screenshots of my website for vis..." | screenshot-capture | none | text_match | FALLBACK |
| 33 | screenshot-capture | "Screenshot these pages and handle cookie consen..." | screenshot-capture | none | text_match | FALLBACK |
| 34 | brand-extractor | "Extract the brand identity from https://example..." | brand-extractor | brand-extractor | tool_use | PASS |
| 35 | brand-extractor | "Analyze the brand profile including tone and po..." | brand-extractor | none | text_match | FALLBACK |
| 36 | brand-extractor | "Build a comprehensive brand profile from this w..." | brand-extractor | none | text_match | FALLBACK |
| 37 | brand-css-generator | "Generate CSS custom properties from this brand ..." | brand-css-generator | brand-css-generator | tool_use | PASS |
| 38 | brand-css-generator | "Create design tokens and a CSS theme from our b..." | brand-css-generator | none | text_match | FALLBACK |
| 39 | brand-css-generator | "Build WCAG AA compliant CSS variables from our ..." | brand-css-generator | none | text_match | FALLBACK |
| 40 | figma-token-sync | "Sync our CSS custom properties to Figma variables" | figma-token-sync | figma-token-sync | tool_use | PASS |
| 41 | figma-token-sync | "Pull variables from Figma and sync them to CSS ..." | figma-token-sync | figma-token-sync | tool_use | PASS |
| 42 | figma-token-sync | "Run a diff to detect drift between our CSS toke..." | figma-token-sync | figma-token-sync | tool_use | PASS |
| 43 | design-system-extractor | "Extract the design system from this live websit..." | design-system-extractor | none | text_match | FALLBACK |
| 44 | design-system-extractor | "Reverse-engineer the CSS tokens from https://ex..." | design-system-extractor | design-system-extractor | tool_use | PASS |
| 45 | design-system-extractor | "Extract the design system tokens from https://e..." | design-system-extractor | design-system-extractor | tool_use | PASS |
| 46 | generative-page-pipeline | "Build a generative page pipeline that creates H..." | generative-page-pipeline | generative-page-pipeline | tool_use | PASS |
| 47 | generative-page-pipeline | "Create a page generation system with intent cla..." | generative-page-pipeline | generative-page-pipeline | tool_use | PASS |
| 48 | generative-page-pipeline | "Implement a generative page pipeline with RAG i..." | generative-page-pipeline | generative-page-pipeline | tool_use | PASS |
| 49 | conversational-page-builder | "Build a chat-based website builder with multi-t..." | conversational-page-builder | conversational-page-builder | tool_use | PASS |
| 50 | conversational-page-builder | "Create an interactive AI agent that builds page..." | conversational-page-builder | conversational-page-builder | tool_use | PASS |
| 51 | conversational-page-builder | "Implement a conversational page editor with rea..." | conversational-page-builder | conversational-page-builder | tool_use | PASS |
| 52 | ai-image-generator | "Set up multi-provider AI image generation with ..." | ai-image-generator | ai-image-generator | tool_use | PASS |
| 53 | ai-image-generator | "Build an image generation service with caching ..." | ai-image-generator | ai-image-generator | tool_use | PASS |
| 54 | ai-image-generator | "Create a hero image generator with FLUX and Ima..." | ai-image-generator | ai-image-generator | tool_use | PASS |
| 55 | da-content-pipeline | "Convert this HTML page to DA format and upload ..." | da-content-pipeline | da-content-pipeline | tool_use | PASS |
| 56 | da-content-pipeline | "Build a pipeline to convert plain HTML to Docum..." | da-content-pipeline | da-content-pipeline | tool_use | PASS |
| 57 | da-content-pipeline | "Upload content to DA with IMS authentication an..." | da-content-pipeline | da-content-pipeline | tool_use | PASS |
| 58 | site-auditor | "Audit this website for content gaps by cross-re..." | site-auditor | none | text_match | FALLBACK |
| 59 | site-auditor | "Run a site quality audit comparing query index,..." | site-auditor | site-auditor | tool_use | PASS |
| 60 | site-auditor | "Find orphan pages and content gaps across my we..." | site-auditor | content-graph | tool_use | **FAIL** |
| 61 | pagespeed-audit | "Run a Core Web Vitals audit across these URLs" | pagespeed-audit | none | text_match | FALLBACK |
| 62 | pagespeed-audit | "Collect PageSpeed scores and CWV data for my site" | pagespeed-audit | none | text_match | FALLBACK |
| 63 | pagespeed-audit | "Benchmark performance with RUM data and PSI API..." | pagespeed-audit | none | text_match | FALLBACK |
| 64 | accessibility-auditor | "Run a WCAG 2.1 AA compliance audit on these pages" | accessibility-auditor | none | text_match | FALLBACK |
| 65 | accessibility-auditor | "Test accessibility with standard, adversarial, ..." | accessibility-auditor | accessibility-auditor | tool_use | PASS |
| 66 | accessibility-auditor | "Audit this site for a11y issues including banne..." | accessibility-auditor | none | text_match | FALLBACK |
| 67 | block-detector | "Detect and catalog all content blocks on https:..." | block-detector | block-detector | tool_use | PASS |
| 68 | block-detector | "Extract page blocks with bounding boxes and CSS..." | block-detector | block-detector | tool_use | PASS |
| 69 | block-detector | "Analyze the block structure of https://example...." | block-detector | block-detector | tool_use | PASS |
| 70 | content-graph | "Build a semantic content graph from my site's p..." | content-graph | content-graph | tool_use | PASS |
| 71 | content-graph | "Map content relationships and find orphan pages..." | content-graph | content-graph | tool_use | PASS |
| 72 | content-graph | "Create a topic network with hub analysis from m..." | content-graph | content-graph | tool_use | PASS |
| 73 | data-intelligence-pipeline | "Build an end-to-end data pipeline from Slack ch..." | data-intelligence-pipeline | data-intelligence-pipeline | tool_use | PASS |
| 74 | data-intelligence-pipeline | "Create an intelligence gathering pipeline that ..." | data-intelligence-pipeline | data-intelligence-pipeline | tool_use | PASS |
| 75 | data-intelligence-pipeline | "Build a Slack data pipeline that extracts messa..." | data-intelligence-pipeline | data-intelligence-pipeline | tool_use | PASS |
| 76 | report-hub-generator | "Generate a single-page HTML report hub with int..." | report-hub-generator | report-hub-generator | tool_use | PASS |
| 77 | report-hub-generator | "Create an analysis dashboard with grid/list/det..." | report-hub-generator | report-hub-generator | tool_use | PASS |
| 78 | report-hub-generator | "Build a report hub page with sidebar nav and co..." | report-hub-generator | report-hub-generator | tool_use | PASS |
| 79 | __negative__ | "What is the weather today?" | __none__ | none | none | PASS |
| 80 | __negative__ | "Help me write a Python fibonacci function" | __none__ | none | none | PASS |
| 81 | __negative__ | "Explain how TCP/IP works" | __none__ | none | none | PASS |
| 82 | __negative__ | "What is the capital of France?" | __none__ | none | none | PASS |

## Failed Tests

### site-auditor
- **Prompt**: "Find orphan pages and content gaps across my website"
- **Expected**: site-auditor
- **Detected**: content-graph
- **Snippet**: I'll help you build a content relationship graph to identify orphan pages, content gaps, and topic clusters across you

