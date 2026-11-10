---
name: lobot-health
description: Check Lobot's instruction files for context bloat and rules likely to slip (oversized files, long skill descriptions, broken references, duplicated text, overgrown corrections logs). Use when the PM asks for a health check or says Lobot seems slow, forgetful, or ignored a rule.
---

# Lobot health

Every instruction file Lobot loads costs context, and a rule buried in a long file, repeated in two places, or contradicted by another is the one that gets missed. This skill measures that and turns it into fixes. The PM never needs a terminal: the assistant runs the check.

## Rules

- **Report, don't rewrite.** `.ai/general/` is Lobot's copy and is replaced on update: never fix it in place. Findings there go back to Lobot with the lobot-feedback skill.
- **Project files change only with the PM's approval** of each change: the root `CLAUDE.md`, `.ai/project/`, and the project's corrections logs.
- **Numbers come from the script**, never from reading the files and estimating.

## Run the check

1. From the Project Brain root, run `python3 .ai/general/skills/lobot-health/health.py --json`. If the assistant has no shell, say so in one line and stop.
2. **Judgment pass.** The script can't tell whether two rules disagree. Read the files it lists under `always_loaded_files`, the project's rule files, and each pair it flags under `duplicates`, and note any two instructions that contradict each other or a rule the PM reported as ignored (see below).
3. **Report** in chat, short:
   - One line of measurements: always-loaded tokens, rule-file tokens, skill listing size, against their budgets.
   - Findings grouped as **This project** (files the PM owns) and **Lobot** (`.ai/general/`), most costly first, each with the fix in one line.
   - Contradictions from step 2, quoting both rules with their files.
4. **This project:** offer the fixes and make the ones the PM approves (below).
5. **Lobot:** offer once to report the Lobot findings with the lobot-feedback skill, as one report.

## Fixes for project files

| Finding | Fix |
|---|---|
| Root `CLAUDE.md` too long | Keep the project's name, its "This project" table, and rules the assistant must know before reading anything else. Move the rest to a rule file in `.ai/project/`, or to a project skill when it applies to one kind of task. |
| Rule file too long | Split it by task; move steps that apply to one kind of task into a project skill (lobot skill, "New project skills"). |
| Corrections log overgrown | For each settled lesson, propose a line in the agent's project config or the skill it corrects, then remove it from the log. General lessons go to Lobot (lobot-feedback). |
| Contradiction | Ask the PM which rule stands; edit the losing one in place rather than adding a third. |
| Missing `.claude/skills/` link | Relink skills (lobot skill, "New project skills"). |

## When a rule was ignored

When the PM says the assistant skipped a rule, find where the rule lives and check, in order:

1. **Was it loaded?** A rule in a skill counts only once that skill is open; a rule the task needed before the skill opened belongs in the file that opens it.
2. **Is it buried?** In the middle of a long paragraph, or far down a long file. Rules the assistant must not miss go first, one per line.
3. **Does another file say otherwise,** or repeat it in different words?
4. **Can a script check it?** A rule that must hold every time is safer as a check in the script that does the work than as a sentence.

Report the cause in one line and propose the fix the same way as above.

## Budgets

The budgets are at the top of `health.py`, with the reason for each. They follow Anthropic's guidance for instruction files and skills: keep what loads every session short, keep `SKILL.md` under 500 lines with detail in reference files, keep each description to what the skill does and when to use it, and give long reference files a contents list.
