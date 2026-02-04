# Dialogue Format Guide

Guidelines for writing two-host podcast-style dialogue from meeting content.

## Host Roles

| Host | Role | Character | Voice Quality |
|------|------|-----------|---------------|
| **Host A** (Alex) | Narrator / Guide | Warm, knowledgeable, sets context, delivers facts | Male, conversational, warm |
| **Host B** (Jordan) | Reactor / Questioner | Energetic, curious, highlights takeaways, asks follow-ups | Female, realistic, chatty |

## Dialogue Structure per Section

Each section should have **5-9 turns** alternating between hosts:

```
Host A: [Sets context, introduces the topic]
Host B: [Reacts, asks a question, or highlights significance]
Host A: [Explains the key concept with specifics]
Host B: [Connects it to something relatable or asks follow-up]
Host A: [Delivers the main insight or data point]
Host B: [Wraps up with a takeaway]
Host A: [Bridge line previewing next section's topic]
```

## Bridging Between Sections

Every section except the last should end with a **bridge line** — 1-2 sentences spoken by Alex that preview the next section's topic. This creates smooth transitions between sections.

**Rules:**
- Bridge is always the final turn of the section
- Always spoken by Alex (the guide)
- Should feel like a natural segue, not a forced transition
- Keep it short — one sentence is ideal

**Examples:**
| Transition | Bridge Line |
|-----------|-------------|
| Intro → Breakthroughs | "So how did we get here? Three breakthroughs made this possible." |
| Breakthroughs → Value | "With the tech in place, let's see what this actually means for visitors." |
| Value → Pipeline | "Behind all of that is a three-stage AI pipeline. Let's break it down." |
| Pipeline → Interaction | "The system supports two ways visitors interact — explicit and implicit." |
| Interaction → Conclusion | "Both paths lead to the same fundamental shift in how websites work." |

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
- End sections with a forward-looking bridge (except the final section)

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
    {"speaker": "Jordan", "text": "The gap between them is the opportunity! That's where the team comes in."},
    {"speaker": "Alex", "text": "Now let's look at how the team actually measures that gap."}
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
                {"speaker": "Alex", "text": "Key explanation..."},
                {"speaker": "Alex", "text": "Bridge to next section..."}
            ]
        }
    ]
}
```

## API & Voice Configuration

### Text-to-Dialogue API

| Setting | Value |
|---------|-------|
| Endpoint | `POST https://api.elevenlabs.io/v1/text-to-dialogue` |
| Model | `eleven_v3` |
| Response | `audio/mpeg` (single file with all speakers, natural pacing) |

The API handles turn-taking, pacing, and natural conversation flow internally.
No per-voice `voice_settings` needed — v3 handles this natively.

**Request body:**
```json
{
    "inputs": [
        {"text": "First speaker line", "voice_id": "voice1_id"},
        {"text": "Second speaker line", "voice_id": "voice2_id"}
    ],
    "model_id": "eleven_v3"
}
```

### Default Voices

| Host | Voice Name | Voice ID | Character |
|------|-----------|----------|-----------|
| Alex | Archer | `L0Dsvb3SLTyegXwtm47J` | Conversational, warm male guide |
| Jordan | Alexandra | `kdmDKE6EkgrWrrykO9Qt` | Realistic, chatty female reactor |

**Fallback voices** (if defaults unavailable):

| Host | Voice Name | Voice ID |
|------|-----------|----------|
| Alex | Roger | `CwhRBWXzGAHq8TQ4Fs17` |
| Jordan | Laura | `FGY2WhTYpPnrIDTdsKH5` |

Run `scripts/list_voices.py` to discover available ElevenLabs voices.
