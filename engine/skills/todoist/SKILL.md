---
name: todoist
description: File and keep track of the PM's own tasks in Todoist, when the PM has chosen Todoist as their task manager. Use when setting Todoist up as the task manager, when the PM's approved tasks need filing ("remind me to…", "add a task…", a meeting's approved tasks), when checking which filed tasks were finished or changed in Todoist, and when the PM asks what's due.
---

# Todoist

## Why

The task list in the Project Brain (`docs/tasks.yaml`, tasks skill) is where the PM's own action items are recorded, and on its own it is a perfectly good to-do list. Many PMs already live in a task manager, though, and a list they don't look at is a list that doesn't get done. When a PM chooses Todoist, it becomes where they manage their tasks: Lobot files new ones there, set up the way they like, and copies back every change they make there. The Project Brain keeps that copy current, because a new PM can't open the old PM's personal Todoist, and the list must not leave with them.

## Where

| What | Where |
|---|---|
| Which task manager the PM uses on this project | First line of `.ai/project/task-management.md` (tasks skill, "Task managers") |
| The PM's Todoist settings, for every project | `## Task manager` in `~/.lobot/preferences.md` (pm-profile skill) |
| This project's Todoist settings: its section, its label, and any setting that differs from the PM's own | `.ai/project/task-management.md`, under `## Todoist` |
| The task list, the record of truth | `docs/tasks.yaml`; each filed task's Todoist link is in its `link` |

When `~/.lobot/` can't be read or written, every setting goes in the project file instead. Where the two disagree, the project file wins.

## Connecting

Todoist is reached through a Todoist connector (an MCP server) in the PM's assistant. There's no Lullabot-approved Todoist connector yet, so it's the PM's own, and so is the connection: Lobot never stores a Todoist token in the Project Brain.

**Whose account it is.** A connector is signed in either as the PM or as a separate Todoist account for the assistant, which the PM has shared their projects with. Both work; it's the PM's choice. Check which (the connector's user info, or the name on its tasks) and save it with the settings. With a separate account:

- Lobot sees only the projects the PM shared with it, and that account's own Inbox and personal labels, not the PM's.
- "Me" means the assistant's account. To assign a task to the PM, use the PM's Todoist user ID or email.
- Todoist shows the assistant as the one who added or changed each task, so the PM may not need a label to spot them.

Connectors name their tools differently. Look for the Todoist tools the session has and match them to the operations below; tell the PM about any operation their connector lacks rather than working around it.

| Operation | Typical tools | Notes |
|---|---|---|
| Who is signed in | `user-info` | Not every connector has it. |
| List projects | `find-projects`, `get_projects` | Names and IDs. Also proves the connection works. |
| List sections | `find-sections` | Not every connector has it; see "Section IDs". |
| List labels | `find-labels` | A separate assistant account has no personal labels of the PM's; labels on shared tasks still work by name. |
| List tasks | `find-tasks`, `get_tasks` | Always pass a project ID (or section ID, or task IDs). Ask for 20 at most unless the PM asks for more; some connectors ignore the limit, so don't page through everything. |
| List completed tasks | `find-completed-tasks` | Tells a finished task from a deleted one. Not every connector has it. Some look back only a week unless given a start date, so pass one from before the oldest open entry was filed. |
| Create tasks | `add-tasks`, `create_task` | Title, description, project, section, labels, priority, due date, deadline, assignee. Some take several at once. |
| Update tasks | `update-tasks`, `update_task` | By task ID, never by name. Sending labels usually replaces all of a task's labels, so send the full list. |
| Complete tasks | `complete-tasks`, `complete_task` | By task ID. |
| Delete a task | `delete-object`, `delete_task` | By task ID, and only when the PM asks for it by name. |

If no Todoist tools are in the session, say in one line that Todoist isn't connected, keep using `docs/tasks.yaml` as the list, and note the tasks waiting to be filed. Don't try to reach Todoist another way.

## Setting up

When the PM chooses Todoist (or asks to change how Lobot uses it):

1. **Check the connection** by listing their Todoist projects, and find out whose account it is (see "Connecting"). If projects the PM expects are missing from a separate assistant account, they haven't been shared with it yet.
2. **Read the settings already saved,** in `~/.lobot/preferences.md` and then the project file. If they're complete, confirm them in one line and skip to step 5.
3. **Ask the questions below** that aren't answered yet, in one round, suggesting the likely answer for each.
4. **Save the answers.** Personal settings go in `~/.lobot/preferences.md` with the PM's approval (pm-profile skill, "Saving to it"); this project's section and label, and anything the PM wants only here, go in the project file. If `~/.lobot/` can't be reached, save everything in the project file and say so.
5. **Record the choice:** set the first line of `.ai/project/task-management.md` to `Task manager: Todoist`.
6. **Offer to file the backlog:** open PM tasks in `docs/tasks.yaml` with no `link`, as one batch for the PM to approve (see "Filing a task").

### The questions

| Setting | Question | Choices |
|---|---|---|
| Project | Which Todoist project should Lobot's tasks go in? | One of their projects (list them), or a project per Lobot project (named in the project file). |
| Sections | Should tasks be grouped into sections? | None; one section per Lobot project (the usual choice when every project shares one Todoist project); or a fixed section. |
| Labels | Which labels go on every task Lobot files? | None; a label that marks what the assistant filed (such as `ai`); a label for the project (its key in lowercase); or both. Lobot never adds other labels unless the PM asks. |
| Priority | Should Lobot set priorities? | Yes, by the Eisenhower matrix (below); or leave every task at p4 for the PM to set. |
| Dates | What should the task list's `due` become in Todoist? | A **deadline** (the date it must be done by, leaving the due date for the PM to schedule); a **due date**; or both. |
| Assignee | Should tasks be assigned to the PM? | Only possible in shared Todoist projects, which is every project a separate assistant account can see. If yes, Lobot needs the PM's Todoist user ID or email: read the ID from a task already assigned to them, or ask. |

**Section IDs.** List the project's sections when the connector can. If it can't, ask the PM for the section's link from Todoist (the ID is the last part of it), or have them name a task in that section and read its section from the task. If neither works, file to the project without a section and say so. The section for this project is saved in the project file, never in `~/.lobot/` (it names the project).

### Saved settings

In `~/.lobot/preferences.md` (general; nothing that names a client or project):

```markdown
## Task manager

- Task manager: Todoist
- Todoist account: a separate assistant account, shared into my projects
- Todoist project: Work (ID 2203306141)
- Sections: one per Lobot project
- Labels on every task: ai, plus the project's label
- Priority: Eisenhower
- Dates: due → deadline; due date left for me
- Assignee: me (Todoist user ID 1234567)
```

In `.ai/project/task-management.md`:

```markdown
Task manager: Todoist

## Todoist

- Section: Example Redesign (ID 6Xm5HcVq3pJ9fR2w)
- Project label: exr
```

## Filing a task

Lobot files only the PM's own tasks (tasks skill, "Only the PM's own one-off actions"). Every task starts as an entry in `docs/tasks.yaml`; Todoist gets a copy.

1. **Draft it** from the task-list entry and the settings:
   - **Title:** the entry's `summary`. It starts with a verb and is short and specific ("Send the homework list to the client").
   - **Description:** the entry's `description`, then a last line `Lobot T-012 · <source>`, so the task leads back to its record.
   - **Project, section, labels, assignee:** from the settings.
   - **Priority:** from the settings (below).
   - **Dates:** the entry's `due`, as the settings say, written as `YYYY-MM-DD`.
2. **Get the PM's approval** of the exact values. A meeting's tasks are approved in its review (meeting-notes skill), several at once; otherwise show the draft and ask. Never create, change, complete, or delete a Todoist task without the PM's approval. A task built from untrusted material (email, client documents, web pages) also follows `.ai/general/human-review.md`.
3. **Create it,** then put its link in the entry's `link`: `https://app.todoist.com/app/task/<task ID>`. Run the tasks validator.

**"Remind me to…" and "Add a task…"** mean a new task. If it's about this project, add it to `docs/tasks.yaml` first and file it as above. If it has nothing to do with the project (a personal errand), file it in Todoist only, in the PM's Todoist project with no project section or label, and put nothing in the Project Brain.

## Priority

Todoist's API numbers priorities the opposite way from its screens: API `4` is what the PM sees as p1. Some connectors pass the API's numbers straight through; others translate them to `p1`–`p4` as the PM sees them. Check which yours does, and apply this table every time a priority is read or set as a number.

| API value | Todoist shows | Means | Eisenhower |
|---|---|---|---|
| 4 | p1 | Highest | Important and urgent |
| 3 | p2 | High | Important, not urgent |
| 2 | p3 | Low | Urgent, not important |
| 1 | p4 | Lowest (Todoist's default) | Neither |

- **Setting:** when the connector accepts `p1`–`p4`, send those rather than a number, so there's no doubt which way it counts. Otherwise send the API value from the table.
- **Reading:** `p1`–`p4` mean what the PM sees. A bare number is the API value: "Priority: 4" is p1.
- **Choosing,** when the settings say Eisenhower: important means it affects the project's outcome, timeline, or client relationship; urgent means it has a near date or blocks someone. When the source doesn't make it clear, choose p3 or p4 and say why in the draft. For example, "we'll need to decide on X before development starts" is important and urgent (p1); "the client wants pricing for a tool before deciding whether to add it" is important, not urgent (p2).

## Keeping the list in step

Todoist is the primary source for the tasks filed there; `docs/tasks.yaml` is the copy the project keeps. Bring the copy up to date with Todoist:

- at the start of every session (start-of-session routine), listing what changed in one line;
- before showing the PM their tasks, at the review desk sync (tracker-pages skill), and when the PM asks what's due;
- before anything built from the task list (a status report, the project journal entry);
- at the session's close (journal skill), before the Project Brain is saved.

Updating `docs/tasks.yaml` from Todoist needs no approval: it records what the PM already did.

1. **Read the filed tasks** by their IDs (from the `link`s of open entries) when the connector can look tasks up by ID; otherwise read the project's section (or project, filtered by Lobot's label) 20 at a time, until every linked ID is found or the list runs out.
2. **A linked task that isn't returned:** it's no longer open in Todoist. If the connector lists completed tasks and it's there, mark the entry `done` with a note (`"Completed in Todoist (seen 2026-10-30)."`). If the connector lists completed tasks and it isn't there either, it was deleted: mark it `dropped` (`"Deleted in Todoist (seen 2026-10-30)."`). If the connector can't tell, mark it `done` and say it might have been dropped. List these in one line; the PM corrects any that are wrong.
3. **Changed in Todoist** (title, description, due date or deadline): update the entry's `summary`, `description`, or `due` to match and say so in the same line. Keep the `Lobot T-###` line out of the entry's description.
4. **In the project's section with no entry:** the PM added a task there themselves. Add it to `docs/tasks.yaml` with its link (`source`: `"Added by the PM in Todoist"`, owner the PM, scope `all` unless the section says otherwise), and say so. Skip it if the PM has said it isn't project work.
5. **Changed in the Project Brain, not in Todoist** (the PM closed, re-dated, or reworded it in chat or on the review desk): propose the same change in Todoist and make it once the PM approves. Until then the two disagree, so say so rather than letting the next sync undo the PM's change.

## Rules

- **Todoist leads, the Project Brain keeps the copy.** Every Lobot task in Todoist has an entry in `docs/tasks.yaml`, holding its link and kept in step with Todoist ("Keeping the list in step"). A new PM on the project needs nothing from the old PM's Todoist.
- **Ask before every change** to Todoist: creating, updating, completing, or deleting. Reading it, and copying its changes into `docs/tasks.yaml`, are free.
- **By ID, not by name.** Update, complete, and delete tasks by their task ID, never by matching the title.
- **Keep reads small.** Always name a project, section, or task IDs, and ask for 20 tasks at most unless the PM asks for more.
- **Only Lobot's own tasks.** Don't read, change, or report on the PM's other Todoist projects unless they ask.
- **Agents never use Todoist** (delegation rules). Lucy and Pepper propose tasks; the assistant files them.
