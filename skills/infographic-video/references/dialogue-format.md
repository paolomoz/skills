# Dialogue Format Guide

Guidelines for writing two-host podcast-style dialogue from meeting content.

## Host Roles

| Host | Role | Character | Voice Quality |
|------|------|-----------|---------------|
| **Host A** (Alex) | Narrator / Guide | Warm, knowledgeable, sets context, delivers facts | Male, laid-back, resonant |
| **Host B** (Jordan) | Reactor / Questioner | Energetic, curious, highlights takeaways, asks follow-ups | Female, enthusiastic, quirky |

## Dialogue Structure per Section

Each section should have **5-9 turns** alternating between hosts:

```
Host A: [Sets context, introduces the topic]
Host B: [Reacts, asks a question, or highlights significance]
Host A: [Explains the key concept with specifics]
Host B: [Connects it to something relatable or asks follow-up]
Host A: [Delivers the main insight or data point]
Host B: [Wraps up with a takeaway or bridges to next section]
```

## Writing Guidelines

### Tone
- Casual podcast-recap — like two colleagues discussing over coffee
- Accessible to listeners who weren't at the meeting
- Enthusiastic but not forced — genuinely interested in the content

### Content Rules
- Preserve key facts, quotes, and data points verbatim from the source
- Spell out abbreviations on first use
- Write numbers as words for TTS clarity ("two hundred" not "200")
- Use "G-A" for "GA" (General Availability) to help TTS pronunciation
- Spell out dates naturally ("February second, twenty twenty-six")

### Emotional Cues
Express emotion through word choice and sentence structure, NOT bracketed directives:

| Instead of | Write |
|------------|-------|
| `[excited]` | "This is where it gets really interesting..." |
| `[laughs]` | "Ha, he literally said..." |
| `[thoughtfully]` | "What really stood out to me..." |
| `[impressed]` | "And here's the powerful part..." |

Bracketed directives are stripped before TTS — use natural language instead.

### Pacing
- Short sentences for emphasis and energy
- Longer sentences for explanation and context
- Mix question-and-answer patterns to maintain engagement
- End sections with a forward-looking or summarizing statement

## Word Count Targets

| Target Duration | Words | Turns |
|-----------------|-------|-------|
| ~40s | ~120 | 5-6 |
| ~50s | ~145 | 6-8 |
| ~60s | ~170 | 7-9 |

## Example Dialogue

```json
[
    {"speaker": "Alex", "text": "So let's talk about the customer journey. Think of the lifecycle as a continuous loop, not a funnel."},
    {"speaker": "Jordan", "text": "Right, pre-sales in blue, post-sales in green, and it just keeps cycling through renewal, upsell, and expansion."},
    {"speaker": "Alex", "text": "And here's the key insight — there are two lines on the chart. The orange line is the status quo, and the blue line is the engineered path."},
    {"speaker": "Jordan", "text": "The gap between them is the opportunity! That's where the team comes in."}
]
```

## Data Format for Scripts

Dialogue is stored as a JSON file (`dialogue.json`) with this structure:

```json
{
    "sections": [
        {
            "name": "01-intro",
            "dialogue": [
                {"speaker": "Alex", "text": "Opening line introducing the topic..."},
                {"speaker": "Jordan", "text": "Reaction or question..."},
                {"speaker": "Alex", "text": "Key explanation..."}
            ]
        }
    ]
}
```

## TTS Configuration

| Setting | Value |
|---------|-------|
| Model | `eleven_multilingual_v2` |
| Stability | `0.50` |
| Similarity boost | `0.75` |
| Style | `0.30` |
| Silence between turns | `350ms` |

Higher stability = more consistent voice. Lower style = less dramatic variation.
Adjust style upward (0.4-0.6) for more expressive delivery.
