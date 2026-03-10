---
name: ai-fluency-assessment
description: Assess your AI fluency using Anthropic's 4D framework (Dakan, Feller & Anthropic, 2025). Scans Claude Code sessions, Claude.ai exports, and git history, runs heuristic analysis on all messages, asks a self-assessment questionnaire, and generates a visual HTML report with scores and actionable feedback. Use when "assess fluency", "AI fluency", "fluency report", "fluency assessment", "4D framework", or "how AI fluent am I".
---

# AI Fluency Assessment

Assess a user's AI fluency based on Anthropic's 4D AI Fluency Framework (Dakan, Feller & Anthropic, 2025). The framework has 4 Competencies, 12 Sub-competencies, and 24 Behaviors (11 observable from conversation data, 13 self-assessed).

## Source Code

The assessment tool lives at `/Users/paolo/playground/ai-fluency/`. All Python modules are under `src/ai_fluency/`. Run commands with `PYTHONPATH=/Users/paolo/playground/ai-fluency/src python3 -m ai_fluency`.

## Instructions

### Step 1: Collect Evidence

Run the evidence collector. It scans three sources:

```bash
# Claude Code sessions (automatic — reads ~/.claude/projects/)
PYTHONPATH=/Users/paolo/playground/ai-fluency/src python3 -m ai_fluency collect --max-sessions 2000

# With Claude.ai export (if user provides path)
PYTHONPATH=/Users/paolo/playground/ai-fluency/src python3 -m ai_fluency collect --max-sessions 2000 --claude-export <PATH_TO_EXPORT>

# With git repos (scan parent directories for repos one level deep)
PYTHONPATH=/Users/paolo/playground/ai-fluency/src python3 -m ai_fluency collect --max-sessions 2000 --scan-dirs ~/projects ~/work
```

**Important:** Use `--max-sessions 2000` (not 100) to capture all sessions. Many session files are subagent files with no user messages, so even with 2000 files the scan is fast.

Ask the user:
1. "Do you have a Claude.ai conversation export? If so, where is it?"
2. "Which directories contain your git repos? (e.g., ~/projects, ~/work)"

Evidence is saved to `.ai-fluency/evidence.json` in the current working directory.

### Step 2: Run Heuristic Analysis

Run the full-coverage heuristic analyzer on all collected messages. This checks every message against regex patterns for the 11 observable behaviors.

```bash
cd /Users/paolo/playground/ai-fluency
PYTHONPATH=src python3 -c "
from pathlib import Path
from ai_fluency.heuristics import analyze_all_messages, print_summary
import json

results = analyze_all_messages(Path('.ai-fluency/evidence.json'))
print_summary(results)

with open('.ai-fluency/heuristic-analysis.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
"
```

Record the heuristic results — they inform the observable behavior scores.

### Step 3: Self-Assessment Questionnaire

Ask the user the following 13 questions for the unobservable behaviors. Rate each 1-5 (1=Never, 5=Always).

Ask the questions in conversation (don't run the interactive CLI — it doesn't work through Claude Code's Bash tool). Present them one batch at a time to avoid overwhelming.

**Delegation:**
- Q2: Before using AI, how consistently do you analyze the nature of your work (e.g., is it time-consuming but simple, uncertain, requiring data, or requiring critical judgment)?
- Q3: How often do you evaluate whether a specific AI tool is the right fit for your task before starting?
- Q4: How actively do you compare and choose between different AI platforms (e.g., Claude vs ChatGPT vs Gemini) based on task requirements?
- Q6: How strategically do you divide work between yourself and AI, reserving critical judgment for yourself while leveraging AI for its strengths?

**Discernment:**
- Q16: How reliably do you catch when AI generates plausible-sounding but incorrect information (hallucinations)?
- Q17: How often do you evaluate whether the AI's communication style is actually effective for your needs and adjust accordingly?
- Q18: How alert are you to potential biases in AI outputs (e.g., cultural, gender, or perspective biases)?

**Diligence:**
- Q19: How carefully do you consider data privacy, security, and organizational policies before sharing information with AI systems?
- Q20: How aware are you of ethical implications throughout your AI interactions?
- Q21: How consistently do you disclose AI involvement in your work to stakeholders?
- Q22: How accurately do you represent the extent of AI's contribution when discussing your AI-assisted work?
- Q23: How thoroughly do you review and verify AI-assisted outputs before sharing or deploying?
- Q24: How fully do you accept personal accountability for the final quality of your AI-assisted work?

After collecting responses, save them:

```bash
cd /Users/paolo/playground/ai-fluency
PYTHONPATH=src python3 -c "
import json
from pathlib import Path
from ai_fluency.collectors.questionnaire import format_questionnaire_results

responses = {2: R2, 3: R3, 4: R4, 6: R6, 16: R16, 17: R17, 18: R18, 19: R19, 20: R20, 21: R21, 22: R22, 23: R23, 24: R24}

evidence_path = Path('.ai-fluency/evidence.json')
with open(evidence_path) as f:
    evidence = json.load(f)
evidence['questionnaire'] = format_questionnaire_results(responses)
with open(evidence_path, 'w') as f:
    json.dump(evidence, f, indent=2, default=str)
print('Questionnaire saved')
"
```

Replace R2, R3, etc. with the user's actual integer ratings.

### Step 3b: Top Projects (Optional)

If the user wants to focus on their best/most representative projects, re-collect with `--top-projects`:

```bash
PYTHONPATH=/Users/paolo/playground/ai-fluency/src python3 -m ai_fluency collect --max-sessions 2000 --top-projects 10
```

This keeps only the top 10 projects by message count. Run the heuristic analysis again after filtering. Consider showing both all-projects and top-projects views in the report for a fuller picture.

### Step 4: Score All 24 Behaviors

Read the evidence samples from `.ai-fluency/evidence.json` and the heuristic results from `.ai-fluency/heuristic-analysis.json`. Score each behavior 1-5:

**Scoring criteria (CEFR-aligned):**
- **0–0.9 — A1 Breakthrough**: No evidence of this behavior
- **1–1.9 — A2 Elementary**: Occasional or inconsistent evidence
- **2–2.9 — B1 Intermediate**: Regular evidence but room for improvement
- **3–3.89 — B2 Upper Intermediate**: Consistent evidence, some gaps
- **3.9–4.49 — C1 Advanced**: Consistent, effective demonstration
- **4.5–5.0 — C2 Mastery**: Sophisticated, nuanced mastery

Overall and competency scores use CEFR levels (e.g., "C1 — Advanced AI Fluency"). Per-behavior scores show the CEFR code instead of raw numbers: score 5 → C2, score 4 → C1, score 3 → B2, score 2 → A2, score 1 → A1.

**For observable behaviors (1, 5, 7-15):** Base scores primarily on conversation evidence and heuristic analysis. Consider:
- Heuristic match count (relative to other behaviors, NOT absolute percentage)
- Quality and sophistication of matching messages (read actual samples)
- Consistency across projects
- Range and variety within the behavior (e.g., B11: do they use multiple interaction modes, or just "don't stop"?)

**Important:** High heuristic frequency alone does NOT guarantee a high score. Assess *quality and range*, not just quantity. A user who says "just do it" 600 times scores lower on B11 than one who deliberately switches between execution, brainstorming, and challenge modes even if less frequently.

**For unobservable behaviors (2-4, 6, 16-24):** Use the self-assessment rating as a starting point. Adjust based on any corroborating evidence visible in conversations.

### Step 5: Generate the Visual HTML Report

Generate a self-contained HTML report at `.ai-fluency/fluency-report.html`. The report must include:

#### Design System
- Font: Inter (Google Fonts import) with system fallback
- Background: `#FAFAF9`, Surface: `#FFFFFF`, Border: `#E7E5E4`
- Competency colors:
  - Delegation: `#2563EB` (blue), light: `#EFF6FF`
  - Description: `#7C3AED` (purple), light: `#F5F3FF`
  - Discernment: `#0891B2` (cyan), light: `#ECFEFF`
  - Diligence: `#059669` (green), light: `#ECFDF5`
- Score colors: 1=`#EF4444`, 2=`#F97316`, 3=`#EAB308`, 4=`#22C55E`, 5=`#10B981`

#### Report Structure

1. **Header**: Title, date, overall score (large number with level label)

2. **Overall Score Card**: Large CEFR level (e.g., "B2") with "Upper Intermediate AI Fluency" label. Include numeric score and breakdown. Add a visual CEFR scale bar (A1→C2) with a "YOU" marker highlighting the current level.

3. **4 Competency Summary Cards**: Each shows competency name, numeric score, CEFR level (e.g., "B2 — Upper Intermediate"), color-coded progress bar. Score = average of sub-competency scores. Sub-competency score = average of behavior scores within it.

4. **Strengths & Growth Areas**: Side-by-side cards showing top 3 strengths (highest-scored behaviors) and top 3 growth areas (lowest-scored behaviors with specific recommendations).

5. **Full-Coverage Heatmap**: Horizontal bar chart ranking all 11 observable behaviors by heuristic count. Scale bars *relative to the highest behavior* (highest = 100% width), NOT as absolute percentages. Show absolute message counts. Color bars by competency color.

6. **Top Projects Breakdown**: Horizontal bar chart showing message volume per project (top 10), scaled relative to the busiest project. Alternate competency colors for visual variety.

7. **24 Behavior Cards**: One card per behavior, grouped by competency > sub-competency. Each card includes:
   - Behavior number, name, and Observable/Self-assessed badge
   - Score (1-5) with color-coded left border and dot indicators (filled/unfilled circles)
   - For observable behaviors: heuristic data bar showing "Detected in N messages" with bar width scaled relative to max behavior, plus "Strongest in" listing top projects without percentages
   - Evidence section: 3-4 bullet points citing specific examples from the data
   - Action section: 1-2 concrete, actionable recommendations

8. **Footer**: Framework attribution, generation date

#### Heuristic Bar Formatting (Critical)
- Label: "Detected in" (NOT "Detection rate")
- Value: "N messages" (NOT "N (X%)")
- Bar width: Scale relative to the max behavior count (e.g., if B7 has 736 matches, that's 100% width; B5 with 35 matches = 35/736 = 4.8% width)
- Projects: Label as "Strongest in" with just project names (NO percentages)
- This makes all bars look proportional and avoids small percentages looking like bad scores

### Step 6: Open the Report

```bash
open .ai-fluency/fluency-report.html
```

## Framework Reference

| # | Behavior | Competency | Observable |
|---|----------|-----------|-----------|
| 1 | Clarifies goal before asking for help | Delegation | Yes |
| 2 | Understands problem scope and nature | Delegation | No |
| 3 | Assesses AI fit | Delegation | No |
| 4 | Selects platform | Delegation | No |
| 5 | Consults AI on approach before execution | Delegation | Yes |
| 6 | Distributes work strategically | Delegation | No |
| 7 | Specifies format and structure needed | Description | Yes |
| 8 | Defines audience for the output | Description | Yes |
| 9 | Provides examples of what good looks like | Description | Yes |
| 10 | Iterates and refines | Description | Yes |
| 11 | Sets interaction mode | Description | Yes |
| 12 | Communicates tone and style preferences | Description | Yes |
| 13 | Checks facts and claims that matter | Discernment | Yes |
| 14 | Identifies when AI might be missing context | Discernment | Yes |
| 15 | Questions when AI reasoning doesn't hold up | Discernment | Yes |
| 16 | Detects hallucination | Discernment | No |
| 17 | Evaluates tone and communication fit | Discernment | No |
| 18 | Recognizes bias in AI outputs | Discernment | No |
| 19 | Chooses AI tools ethically | Diligence | No |
| 20 | Maintains ethical awareness during interaction | Diligence | No |
| 21 | Discloses AI involvement to stakeholders | Diligence | No |
| 22 | Represents AI contribution accurately | Diligence | No |
| 23 | Verifies and tests outputs before sharing | Diligence | No |
| 24 | Takes ongoing accountability | Diligence | No |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named ai_fluency` | Set `PYTHONPATH=/Users/paolo/playground/ai-fluency/src` before the command |
| 0 Claude Code messages found | Check that `~/.claude/projects/` exists and has JSONL session files |
| Questionnaire hangs | Don't run interactive mode through Bash; ask questions in chat and save programmatically |
| Heuristic bars look like bad scores | Use relative scaling (max behavior = 100% bar width) and show absolute counts, not percentages |
| Python 3.9 errors with `X \| None` | Use `Optional[X]` from typing instead |
