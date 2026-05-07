---
name: ai-fluency-assessment
description: Assess your AI fluency using Anthropic's 4D framework (Dakan, Feller & Anthropic, 2025). Scans Claude Code sessions, Claude.ai exports, and git history, runs heuristic analysis on all messages, asks a self-assessment questionnaire, and generates a visual HTML report with scores and actionable feedback. Use when "assess fluency", "AI fluency", "fluency report", "fluency assessment", "4D framework", or "how AI fluent am I".
---

# AI Fluency Assessment

Assess a user's AI fluency based on Anthropic's 4D AI Fluency Framework (Dakan, Feller & Anthropic, 2025). The framework has 4 Competencies, 12 Sub-competencies, and 24 Behaviors (11 observable from conversation data, 13 self-assessed).

## Source Code

The assessment tool is open-source at https://github.com/paolomoz/ai-fluency. The skill expects it cloned to `~/.cache/ai-fluency` and all Python modules under `src/ai_fluency/`. Commands use `PYTHONPATH=~/.cache/ai-fluency/src python3 -m ai_fluency`.

## Instructions

### Step 0: Ensure the tool is installed

Before any other step, make sure the tool is available locally. Clone on first run; pull the latest on subsequent runs.

```bash
if [ ! -d ~/.cache/ai-fluency ]; then
  git clone https://github.com/paolomoz/ai-fluency.git ~/.cache/ai-fluency
else
  git -C ~/.cache/ai-fluency pull --ff-only
fi
```

### Step 1: Collect Evidence

Run the evidence collector. It scans three sources:

```bash
# Claude Code sessions (automatic — reads ~/.claude/projects/)
PYTHONPATH=~/.cache/ai-fluency/src python3 -m ai_fluency collect --max-sessions 2000

# With Claude.ai export (if user provides path)
PYTHONPATH=~/.cache/ai-fluency/src python3 -m ai_fluency collect --max-sessions 2000 --claude-export <PATH_TO_EXPORT>

# With git repos (scan parent directories for repos one level deep)
PYTHONPATH=~/.cache/ai-fluency/src python3 -m ai_fluency collect --max-sessions 2000 --scan-dirs ~/projects ~/work
```

**Important:** Use `--max-sessions 2000` (not 100) to capture all sessions. Many session files are subagent files with no user messages, so even with 2000 files the scan is fast.

Ask the user:
1. "Do you have a Claude.ai conversation export? If so, where is it?"
2. "Which directories contain your git repos? (e.g., ~/projects, ~/work)"

Evidence is saved to `.ai-fluency/evidence.json` in the current working directory.

### Step 2: Run Heuristic Analysis

Run the full-coverage heuristic analyzer on all collected messages. This checks every message against regex patterns for the 11 observable behaviors.

```bash
cd ~/.cache/ai-fluency
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

See [QUESTIONNAIRE.md](./QUESTIONNAIRE.md) for the full list of questions and how to save responses.

### Step 3b: Top Projects (Optional)

If the user wants to focus on their best/most representative projects, re-collect with `--top-projects`:

```bash
PYTHONPATH=~/.cache/ai-fluency/src python3 -m ai_fluency collect --max-sessions 2000 --top-projects 10
```

This keeps only the top 10 projects by message count. Run the heuristic analysis again after filtering. Consider showing both all-projects and top-projects views in the report for a fuller picture.

### Step 4: Score All 24 Behaviors

Read the evidence from `.ai-fluency/evidence.json` and heuristic results from `.ai-fluency/heuristic-analysis.json`. Score each behavior 1-5 using CEFR-aligned criteria. See [FRAMEWORK.md](./FRAMEWORK.md) for the full behavior map and scoring scale.

**For observable behaviors (1, 5, 7-15):** Base scores on conversation evidence and heuristic analysis. Assess *quality and range*, not just quantity — high frequency alone does NOT guarantee a high score.

**For unobservable behaviors (2-4, 6, 16-24):** Use the self-assessment rating as a starting point. Adjust based on any corroborating evidence visible in conversations.

### Step 5: Generate the Visual HTML Report

Generate a self-contained HTML report at `.ai-fluency/fluency-report.html`. See [DESIGN.md](./DESIGN.md) for the full design system (colors, typography) and detailed report structure.

### Step 6: Open the Report

```bash
open .ai-fluency/fluency-report.html
```

## Reference

- **[FRAMEWORK.md](./FRAMEWORK.md)** — Full 24-behavior map, competency groupings, and CEFR scoring criteria
- **[QUESTIONNAIRE.md](./QUESTIONNAIRE.md)** — 13 self-assessment questions and response saving
- **[DESIGN.md](./DESIGN.md)** — Report design system, layout structure, and heuristic bar formatting

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named ai_fluency` | Set `PYTHONPATH=~/.cache/ai-fluency/src` before the command (or re-run Step 0 to clone the repo) |
| 0 messages found | Check `~/.claude/projects/` exists with JSONL files |
| Questionnaire hangs | Ask in chat, save programmatically (see QUESTIONNAIRE.md) |
| Bars look like bad scores | Use relative scaling and absolute counts (see DESIGN.md) |
