---
name: tasks
description: Keep the action-item list (docs/tasks.md), every follow-up that came out of meetings and documents, the PM's own and the ones others owe, with owner, due date, and status. Use when a meeting or document produces action items, when the PM asks what's on their plate or who owes what, when someone finishes or drops an item, and before chasing anyone for a follow-up.
---

# Tasks

## Why

Action items are written into each meeting's notes, and then they scatter: the PM's own go to a task manager (when one is connected), and the ones others owe live only in old notes files. Nobody can then see what is late or who to chase. The task list keeps every open action item in one place, the PM's and everyone else's, so the PM can work their own and follow up on the rest.

## Where

| What | Path |
|---|---|
| Task list | `docs/tasks.md` |
| Validator | `validate.py` in this skill's folder |
| Where the PM's tasks go (tool, project, sections) | `.ai/project/task-management.md` |

If `docs/tasks.md` doesn't exist (projects installed before this skill), create it from the format below with an empty table.

## Format

```markdown
---
title: Task list
status: active
updated: 2026-10-14
---
# Task list

Open action items first. ...

| ID | Task | Owner | Scope | Due | Status | Source | Link |
|---|---|---|---|---|---|---|---|
| T-002 | Send the homework list to the client | Sam Lee | site-a | 2026-10-16 | open | docs/meetings/2026-10-08-kickoff.md (00:41:10) |  |
| T-001 | Share sample data files | Ana Ruiz | all |  | waiting | docs/meetings/2026-10-08-kickoff.md (00:12:30) |  |
```

- **ID** is `T-` and three digits, never reused.
- **Task** is one action, starting with a verb, clear without opening the source.
- **Owner** is a name from `docs/people.yaml` (several separated by commas), or a team ("Client team"). Mark an owner the source didn't state with `(unverified)`.
- **Scope** is `all`, or a site or program key (the same keys as `docs/raci.yaml`).
- **Due** is a date (`YYYY-MM-DD`) or blank. A date worked out from something vague ("by end of week") gets `(derived)` in the Task.
- **Status** is `open`, `waiting` (blocked on someone else), `done`, or `dropped`.
- **Source** is the meeting notes file and timestamp, or the record that raised it.
- **Link** is the task in the task manager, once the PM's own item has been filed there.
- Open and waiting rows first, then done and dropped. No `|` inside a cell; it breaks the table.

## Who does what

- **Lucy** adds the action items from the material she processes (meeting-notes skill), one row per item in the notes' action-items table. Adding a row is autonomous for her: it repeats what the source says.
- **The assistant** files the PM's own items in the task manager per `.ai/project/task-management.md` and puts the link in the row. While the project has no task manager connected, the row is the task.
- **The PM** closes, drops, or re-dates items. Others' items are closed when the PM or a source says they're done, never from silence.

## Changing a row

1. Find the row by ID or by text; don't add a duplicate. If a later meeting repeats an item, add the new source to the row.
2. Set the status, due date, or owner. A done or dropped row gets who said so and when, in the Task (`... Done, PM 2026-10-15.`).
3. Update `updated` in the frontmatter and run the validator:
   ```sh
   python3 .ai/general/skills/tasks/validate.py docs/tasks.md
   ```

## Rules

- **Every action item, one home.** The notes keep their action-items table as the record of the meeting; the task list is where status lives. Don't track status in the notes.
- **Waiting is not done.** An item stays open until someone says it's done.
- **Done rows stay.** They are the history of who did what.
