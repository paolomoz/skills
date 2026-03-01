# ThreadExtraction Schema Reference

This document defines the full ThreadExtraction type used by the data-intelligence-pipeline Analyze stage. Every extraction produced by Claude conforms to this schema.

## ThreadExtraction Type Definition

```typescript
interface ThreadExtraction {
  // Envelope metadata (added by the pipeline, not by Claude)
  extraction_id: string;        // Format: "ext-{channel_id}-{thread_ts}"
  extracted_at: string;         // ISO 8601 timestamp of extraction

  // Source information (added by the pipeline)
  source: {
    channel_id: string;         // Slack channel ID (e.g., "C04N8BXHZ")
    channel_name: string;       // Human-readable channel name
    thread_ts: string;          // Slack thread timestamp (parent message)
    permalink?: string;         // Direct link to the thread in Slack
    date: string;               // Date of the parent message (YYYY-MM-DD)
    participants: string[];     // Display names of all thread participants
    message_count: number;      // Total messages in thread (parent + replies)
  };

  // Extracted fields (produced by Claude)
  customers: CustomerMention[];
  stakeholders: StakeholderMention[];
  experiments: Experiment[];
  accelerators: Accelerator[];
  micro_learnings: MicroLearning[];
  gaps: Gap[];
  thread_summary: string;       // 2-3 sentence summary of the thread
}
```

## Field Definitions

### CustomerMention

A reference to an external customer or partner organization discussed in the thread.

```typescript
interface CustomerMention {
  name: string;         // Company or organization name as mentioned
  context: string;      // 1-2 sentences describing what was discussed about them
}
```

**Extraction guidance**: Look for company names that appear as external parties being discussed. Do not include internal team names or product names. Include the specific context of why they were mentioned (e.g., "evaluating our product", "reported a bug", "co-developing a feature").

### StakeholderMention

An internal or external person with a notable role or stance in the discussion.

```typescript
interface StakeholderMention {
  name: string;         // Person's display name
  role: string;         // Their role or title if mentioned
  stance: string;       // Their position or opinion on the topic discussed
}
```

**Extraction guidance**: Focus on people who expressed a strong opinion, made a decision, or blocked/unblocked progress. Do not list every participant as a stakeholder — only those whose stance materially affected the discussion outcome.

### Experiment

A product experiment, proof-of-concept, pilot, or test discussed in the thread.

```typescript
interface Experiment {
  title: string;        // Descriptive name for the experiment
  status: 'planned' | 'active' | 'completed' | 'dropped' | 'production';
  outcome: string;      // What happened or is expected to happen
}
```

**Status definitions**:
- `planned`: Discussed but not yet started
- `active`: Currently in progress
- `completed`: Finished with results available
- `dropped`: Abandoned or deprioritized
- `production`: Shipped to production and in active use

### Accelerator

A tool, technique, framework, or approach that sped up work or enabled something new.

```typescript
interface Accelerator {
  title: string;        // Name of the accelerator
  description: string;  // What it does and how it helped
  impact: 'high' | 'medium' | 'low';
}
```

**Extraction guidance**: Look for moments where someone shares a tool that saved time, a technique that solved a hard problem, or a reusable pattern. Rate impact as `high` if it affected multiple people or projects, `medium` if it helped one project significantly, `low` if it was a minor convenience.

### MicroLearning

A small but valuable insight, tip, or piece of knowledge shared in the thread.

```typescript
interface MicroLearning {
  insight: string;      // The learning itself, written as a standalone statement
  source: string;       // Who shared it or what context it came from
}
```

**Extraction guidance**: These are the "I didn't know that" moments. Write each insight as a standalone sentence that would be valuable even without the thread context. Attribute it to the person who shared it.

### Gap

A problem, blocker, missing capability, or unmet need identified in the thread.

```typescript
interface Gap {
  description: string;  // What is missing or broken
  severity: 'high' | 'medium' | 'low';
}
```

**Severity definitions**:
- `high`: Blocks multiple customers or a critical workflow
- `medium`: Significant pain point but workarounds exist
- `low`: Nice-to-have improvement

---

## Claude Extraction Prompt Template

Below is the full prompt template used in the Analyze stage. The placeholders `{channel_name}`, `{date}`, and `{thread_text}` are filled by the pipeline before sending to Claude.

```
Analyze this Slack thread and extract structured intelligence.

Thread from #{channel_name} on {date}:
---
{thread_text}
---

Extract the following as JSON. Be specific and quote the thread where possible.
Every field must be present even if the array is empty.

{
  "customers": [
    {"name": "Company name as mentioned", "context": "1-2 sentences on what was discussed about them"}
  ],
  "stakeholders": [
    {"name": "Person name", "role": "Their role if mentioned", "stance": "Their position on the topic"}
  ],
  "experiments": [
    {"title": "Experiment name", "status": "planned|active|completed|dropped|production", "outcome": "Result or expected result"}
  ],
  "accelerators": [
    {"title": "Tool or technique name", "description": "What it does and how it helped", "impact": "high|medium|low"}
  ],
  "micro_learnings": [
    {"insight": "The learning as a standalone statement", "source": "Who shared it"}
  ],
  "gaps": [
    {"description": "What is missing or broken", "severity": "high|medium|low"}
  ],
  "thread_summary": "2-3 sentence summary of the thread's key discussion and any decisions made"
}

Rules:
1. Only include items explicitly discussed in the thread. Do not infer or speculate.
2. For customers, use the exact company name as written in the thread.
3. For experiments, always assign a status based on the thread evidence.
4. For gaps, only include problems that were identified as actual blockers or needs, not hypothetical risks.
5. If a field has no relevant items, return an empty array [].
6. The thread_summary must capture the main topic, any decisions made, and any action items.
7. Return ONLY valid JSON with no additional text or markdown formatting.
```

## Validation Rules

After receiving Claude's response, validate the extraction before saving:

1. Parse as JSON — retry with a corrective prompt if parsing fails
2. Verify all seven top-level keys are present
3. Verify each array element conforms to its interface (required fields present)
4. Verify `status` values are from the allowed enum
5. Verify `impact` and `severity` values are from their allowed enums
6. Strip any markdown formatting Claude may have wrapped around the JSON (e.g., ```json blocks)
7. Reject extractions where `thread_summary` is empty or fewer than 10 words

## Example Extraction

```json
{
  "extraction_id": "ext-C04N8BXHZ-1701234567.890123",
  "extracted_at": "2025-12-01T15:30:00.000Z",
  "source": {
    "channel_id": "C04N8BXHZ",
    "channel_name": "customer-success",
    "thread_ts": "1701234567.890123",
    "permalink": "https://team.slack.com/archives/C04N8BXHZ/p1701234567890123",
    "date": "2025-11-29",
    "participants": ["Alice Chen", "Bob Martinez", "Carol Wu"],
    "message_count": 8
  },
  "customers": [
    {"name": "Meridian Health", "context": "Evaluating our analytics module for their patient portal. Need HIPAA compliance docs before proceeding."}
  ],
  "stakeholders": [
    {"name": "Alice Chen", "role": "Account Manager", "stance": "Pushing for expedited compliance review to keep deal on track"},
    {"name": "Bob Martinez", "role": "Security Lead", "stance": "Wants full audit before sharing any compliance documentation"}
  ],
  "experiments": [
    {"title": "Meridian Health analytics pilot", "status": "planned", "outcome": "Blocked on compliance documentation; target start Q1 2026"}
  ],
  "accelerators": [
    {"title": "Compliance doc template", "description": "Carol shared a pre-filled HIPAA compliance template that reduces prep time from 2 weeks to 3 days", "impact": "high"}
  ],
  "micro_learnings": [
    {"insight": "Healthcare prospects always ask for HIPAA docs before technical evaluation. Preparing them proactively saves 2-3 weeks per deal.", "source": "Alice Chen"}
  ],
  "gaps": [
    {"description": "No self-service compliance documentation portal. Every request requires manual security team involvement.", "severity": "medium"}
  ],
  "thread_summary": "Discussion about Meridian Health's interest in the analytics module. Deal is blocked on HIPAA compliance documentation. Carol shared a template that could accelerate the process. Team agreed to create a self-service compliance portal as a longer-term fix."
}
```
