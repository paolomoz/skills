# Skills

Personal collection of reusable Claude Code skills, extracted from real project work.

## Process

1. While working in another project, recognize a reusable pattern
2. Come back to this repo and formalize the skill
3. Each skill gets its own directory under `skills/` with a `SKILL.md` file

## Skill format

```
skills/
└── your-skill-name/
    └── SKILL.md
```

`SKILL.md` uses YAML front matter for metadata, followed by the instructions:

```markdown
---
name: your-skill-name
description: What this skill does and when to use it.
---

# Skill Name

## Instructions

...
```

See `skills/_template/SKILL.md` for a starting point.

## Adding a new skill

1. Create a new directory under `skills/` with a descriptive name
2. Add a `SKILL.md` following the template format
3. Register it in `.claude-plugin/marketplace.json` under the appropriate plugin category
