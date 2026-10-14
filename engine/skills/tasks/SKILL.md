---
name: tasks
description: Keep the action-item list (docs/tasks.yaml), every follow-up that came out of meetings and documents, the PM's own and the ones others owe, with owner, due date, and status. Use when a meeting or document produces action items, when the PM asks what's on their plate or who owes what, when someone finishes or drops an item, and before chasing anyone for a follow-up.
---

# Tasks

## Why

Action items are written into each meeting's notes, and then they scatter: the PM's own go to a task manager (when one is connected), and the ones others owe live only in old notes files. Nobody can then see what is late or who to chase. The task list keeps every open action item in one place, the PM's and everyone else's, so the PM can work their own and follow up on the rest.

## Where

| What | Path |
|---|---|
| Task list | `docs/tasks.yaml` |
| Validator | `validate.py` in this skill's folder |
| Where the PM's tasks go (tool, project, sections) | `.ai/project/task-management.md` |

If `docs/tasks.yaml` doesn't exist, create it from the format below with no entries.

## Format

```yaml
# Task list: every action item, the PM's own and the ones others owe. Ordered by ID (T-001, T-002, ...); IDs are never reused.
# Managed by the tasks skill: .ai/general/skills/tasks/SKILL.md
# Validate after every edit: python3 .ai/general/skills/tasks/validate.py docs/tasks.yaml

T-001:
  task: "Share sample data files"
  owner: "Ana Ruiz"
  scope: all
  status: done
  source: "docs/meetings/2026-10-08-kickoff.md (00:12:30)"
  note: "Files arrived 2026-10-14 (PM, 2026-10-15)."

T-002:
  task: "Send the homework list to the client"
  owner: "Sam Lee"
  scope: site-a
  due: 2026-10-16
  status: open
  source: "docs/meetings/2026-10-08-kickoff.md (00:41:10)"
```

| Field | Required | Holds |
|---|---|---|
| key | Yes | `T-` plus three digits, never reused. The file is ordered by ID. |
| `task` | Yes | One action, starting with a verb, clear without opening the source. Quoted. |
| `owner` | Yes | A name from `docs/people.yaml` (several separated by commas), or a team ("Client team"). Mark an owner the source didn't state with `(unverified)`. Quoted. |
| `scope` | Yes | `all`, or a site or program key (the same keys as `docs/raci.yaml`). |
| `due` | No | The date it's due. A date worked out from something vague ("by end of week") is noted in `note` as derived. |
| `status` | Yes | `open`, `waiting` (blocked on someone else), `done`, or `dropped`. |
| `source` | Yes | The meeting notes file and timestamp, or the record that raised it. A later meeting that repeats the item is added here. Quoted. |
| `link` | No | The task in the task manager, once the PM's own item has been filed there. |
| `note` | When done or dropped | Who said it was done or dropped, and when; or anything else the PM added. Quoted. |

Quote every text field: unquoted text containing `: ` or starting with a special character breaks YAML.

## Who does what

- **Lucy** adds the action items from the material she processes (meeting-notes skill), one entry per item in the notes' action-items table. Adding an entry is autonomous for her: it repeats what the source says.
- **The assistant** files the PM's own items in the task manager per `.ai/project/task-management.md` and puts the link in the entry. While the project has no task manager connected, the entry is the task.
- **The PM** closes, drops, or re-dates items. Others' items are closed when the PM or a source says they're done, never from silence.

## Changing an entry

1. Find the entry by ID or by text; don't add a duplicate. If a later meeting repeats an item, add the new source to it.
2. Set the status, due date, or owner. A done or dropped entry gets who said so and when, in `note`.
3. Run the validator:
   ```sh
   python3 .ai/general/skills/tasks/validate.py docs/tasks.yaml
   ```

## Rules

- **Every action item, one home.** The notes keep their action-items table as the record of the meeting; the task list is where status lives. Don't track status in the notes.
- **Waiting is not done.** An item stays open until someone says it's done.
- **Done entries stay.** They are the history of who did what.
