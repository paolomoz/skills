# Report Design System

## Typography & Colors

- Font: Inter (Google Fonts import) with system fallback
- Background: `#FAFAF9`, Surface: `#FFFFFF`, Border: `#E7E5E4`
- Competency colors:
  - Delegation: `#2563EB` (blue), light: `#EFF6FF`
  - Description: `#7C3AED` (purple), light: `#F5F3FF`
  - Discernment: `#0891B2` (cyan), light: `#ECFEFF`
  - Diligence: `#059669` (green), light: `#ECFDF5`
- Score colors: 1=`#EF4444`, 2=`#F97316`, 3=`#EAB308`, 4=`#22C55E`, 5=`#10B981`

## Report Structure

1. **Header**: Title, date, overall score (large number with level label)

2. **Overall Score Card**: Large CEFR level (e.g., "B2") with "Upper Intermediate AI Fluency" label. Include numeric score and breakdown. Add a visual CEFR scale bar (A1->C2) with a "YOU" marker highlighting the current level.

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

## Heuristic Bar Formatting (Critical)

- Label: "Detected in" (NOT "Detection rate")
- Value: "N messages" (NOT "N (X%)")
- Bar width: Scale relative to the max behavior count (e.g., if B7 has 736 matches, that's 100% width; B5 with 35 matches = 35/736 = 4.8% width)
- Projects: Label as "Strongest in" with just project names (NO percentages)
- This makes all bars look proportional and avoids small percentages looking like bad scores
