# Self-Assessment Questionnaire

13 questions for unobservable behaviors. Rate each 1-5 (1=Never, 5=Always).

Ask in conversation (don't run the interactive CLI — it doesn't work through Claude Code's Bash tool). Present one batch at a time to avoid overwhelming.

## Delegation

- **Q2**: Before using AI, how consistently do you analyze the nature of your work (e.g., is it time-consuming but simple, uncertain, requiring data, or requiring critical judgment)?
- **Q3**: How often do you evaluate whether a specific AI tool is the right fit for your task before starting?
- **Q4**: How actively do you compare and choose between different AI platforms (e.g., Claude vs ChatGPT vs Gemini) based on task requirements?
- **Q6**: How strategically do you divide work between yourself and AI, reserving critical judgment for yourself while leveraging AI for its strengths?

## Discernment

- **Q16**: How reliably do you catch when AI generates plausible-sounding but incorrect information (hallucinations)?
- **Q17**: How often do you evaluate whether the AI's communication style is actually effective for your needs and adjust accordingly?
- **Q18**: How alert are you to potential biases in AI outputs (e.g., cultural, gender, or perspective biases)?

## Diligence

- **Q19**: How carefully do you consider data privacy, security, and organizational policies before sharing information with AI systems?
- **Q20**: How aware are you of ethical implications throughout your AI interactions?
- **Q21**: How consistently do you disclose AI involvement in your work to stakeholders?
- **Q22**: How accurately do you represent the extent of AI's contribution when discussing your AI-assisted work?
- **Q23**: How thoroughly do you review and verify AI-assisted outputs before sharing or deploying?
- **Q24**: How fully do you accept personal accountability for the final quality of your AI-assisted work?

## Saving Responses

After collecting responses, save with:

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
