---
name: tasks
description: Keep the PM's own to-do list (docs/tasks.yaml): one-off actions only the PM will do, with due date and status. Not development work (tickets), routine team work, information the work is waiting on (questions), or risk next steps. Use when a meeting or document gives the PM an action, when the PM asks what's on their plate, and when the PM finishes or drops an item.
---

# Tasks

## Why

Action items come out of every meeting and document, but most of them already have a home: development work is in the ticket tracker, design work in the work breakdown, routine team work in the team's own habits and meetings, and waiting on someone for information in the questions log. The task list is the PM's own to-do list: the one-off actions only the PM will do, so they don't get lost among everyone else's. Other people's action items stay in the meeting notes' action-items table, the record of who agreed to what.

## Where

| What | Path |
|---|---|
| Task list | `docs/tasks.yaml` |
| Validator | `validate.py` in this skill's folder |
| Which task manager the PM uses, and its settings for this project | `.ai/project/task-management.md` (see "Task managers") |

If `docs/tasks.yaml` doesn't exist, create it from the format below with no entries.

## Format

```yaml
# Task list: the PM's own one-off actions. Ordered by ID (T-001, T-002, ...); IDs are never reused.
# Managed by the tasks skill: .ai/general/skills/tasks/SKILL.md
# Validate after every edit: python3 .ai/general/skills/tasks/validate.py docs/tasks.yaml

T-001:
  summary: "Share sample data files"
  owner: "Ana Ruiz"
  scope: all
  status: done
  source: "docs/meetings/2026-10-08-kickoff.md (00:12:30)"
  note: "Files arrived 2026-10-14 (PM, 2026-10-15)."

T-002:
  summary: "Send the homework list to the client"
  description: "Data samples, brand materials, analytics access, and key dates, as promised on the kickoff call."
  owner: "Sam Lee"
  scope: site-a
  due: 2026-10-16
  status: open
  source: "docs/meetings/2026-10-08-kickoff.md (00:41:10)"
```

| Field | Required | Holds |
|---|---|---|
| key | Yes | `T-` plus three digits, never reused. The file is ordered by ID. |
| `summary` | Yes | One action, starting with a verb, short enough to skim (under 100 characters): what, not every detail. Quoted. |
| `description` | No | The detail the summary leaves out: what exactly, the parts of a list, context, related record IDs. Quoted. |
| `task` | Older entries | The single field tasks had before `summary` and `description`; it reads as the summary. Split it into the two fields when the task is next edited, and never add both. |
| `owner` | Yes | A name from `docs/people.yaml` (several separated by commas), or a team ("Client team"). Mark an owner the source didn't state with `(unverified)`. Quoted. |
| `scope` | Yes | `all`, or a site or program key (the same keys as `docs/raci.yaml`). |
| `due` | No | The date it's due. A date worked out from something vague ("by end of week") is noted in `note` as derived. |
| `status` | Yes | `open`, `waiting` (blocked on someone else), `done`, or `dropped`. |
| `source` | Yes | The meeting notes file and timestamp, or the record that raised it. A later meeting that repeats the item is added here. Quoted. |
| `link` | No | The task in the task manager, once the PM's own item has been filed there. |
| `note` | When done or dropped | Who said it was done or dropped, and when; or anything else the PM added. Quoted. |

Quote every text field: unquoted text containing `: ` or starting with a special character breaks YAML.

## Who does what

- **Lucy** adds the PM's own one-off actions from the material she processes (meeting-notes skill), phrased as what the PM does, and turns information the work is waiting on into questions instead (questions skill). Adding an entry is autonomous for her; other people's action items stay in the notes.
- **The assistant** files the PM's own items in the PM's task manager (see "Task managers") and puts the link in the entry. With Lobot as the task manager, the entry is the task.
- **The PM** closes, drops, or re-dates items. Others' items are closed when the PM or a source says they're done, never from silence.

## Task managers

The task list always keeps the project's copy, so it survives a change of PM. The PM chooses where they manage their own tasks, and the choice is the first line of `.ai/project/task-management.md`:

| Task manager | First line | How |
|---|---|---|
| Lobot (the default) | `Task manager: Lobot` | The entries in `docs/tasks.yaml`, shown on the review desk (tracker-pages skill). Nothing is filed anywhere else. |
| Todoist | `Task manager: Todoist` | Todoist is where the PM manages the tasks filed there, and the entries follow it: the todoist skill (`.ai/general/skills/todoist/SKILL.md`) files each approved task and copies every change made in Todoist back here. |

When the file or its first line is missing, the task manager is Lobot; ask the PM once whether they'd rather use another one, and record the answer. Never assume a task manager because its connector is in the session. A PM who uses the same task manager everywhere can keep the choice and its settings in their profile (`## Task manager` in `~/.lobot/preferences.md`, pm-profile skill); the project file still records it, so the project shows where its tasks went.

## Changing an entry

1. Find the entry by ID or by text; don't add a duplicate. If a later meeting repeats an item, add the new source to it.
2. Set the status, due date, or owner. A done or dropped entry gets who said so and when, in `note`.
3. Run the validator:
   ```sh
   python3 .ai/general/skills/tasks/validate.py docs/tasks.yaml
   ```

## Rules

- **Only the PM's own one-off actions.** File an item only when the PM has something to do that isn't already tracked elsewhere, phrased as what the PM does ("Request GA for all three sites"); the owner is the PM. Don't file:
  - **Development work.** It goes in the ticket tracker.
  - **Routine team work and meeting prep.** Known, recurring work (logging hours, planning a review that's on the calendar) and anything a scheduled meeting covers.
  - **Waiting on someone for information.** That's a question with `ask` and `needed_by` (questions skill), not a task, and never a task that only says to get an answer.
  - **Next steps on a risk.** They stay on the risk (risks skill).
  - **Other people's action items.** They stay in the meeting notes' action-items table.
- **Every action item, one home.** The notes keep their action-items table as the record of the meeting; the task list is where status lives. Don't track status in the notes.
- **Waiting is not done.** An item stays open until someone says it's done.
- **Done entries stay.** They are the history of who did what.
