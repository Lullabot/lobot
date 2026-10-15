---
name: tracker-pages
description: Publish and keep in sync the PM's tracker pages: hosted pages (Claude artifacts with a shared database) for the risk tracker, decision log, RACI matrix, questions log, and kickoff checklist, and the review desk that gathers everything needing the PM's attention in tabs, where the PM reviews and edits records outside the chat. Use when the PM asks to see, pull up, list, or review a record that has a page or a page template (open questions, risks, decisions, RACI, a kickoff checklist, tasks), when the PM asks for the dashboard or what needs their attention (the review desk is the dashboard), when the PM asks for a page, tracker, or dashboard for a Project Brain record, after processing a new file or transcript (to open the review desk), during the start-of-session routine and session close (to file what the PM changed on a page), and whenever a record with a page changes.
---

# Tracker pages

## Why

Records in `docs/` are the source of truth, but a YAML file is a poor place for a PM to set a risk's severity, answer twenty questions, or check who is accountable for what on site B. A tracker page shows one record as a working screen. The PM edits there; the assistant files those edits back into the Project Brain through each record's skill, so the rules (sources, approvals, validators) still apply.

## Needs

The assistant must be able to publish a hosted page with a shared database and read and write that database (in Claude: the Artifact tool with the `db` capability, and the ArtifactData tool). Without that, say so once and keep working from the files.

## Pages

Templates are in `templates/` in this skill's folder. Each has a `CONFIG` object and `{{…}}` placeholders at the top.

| Template | Record | Collections | PM can |
|---|---|---|---|
| `risks.html` | `docs/risks.yaml` | `risks/<R-###>` | Set severity, status, next step; add a risk |
| `decisions.html` | `docs/decisions.yaml` | `decisions/<D-###>` | Set status and approver; propose a decision (marked as a proposal) |
| `raci.html` | `docs/raci.yaml` (people from `docs/people.yaml`) | `roles`, `rows`, `meta/info`, `requests` | View the matrix (Responsibility, then R, A, C, I with the people in each cell, grouped by area) per scope, or one page per site; request a change (no direct edits: RACI changes need a source) |
| `questions.html` | `docs/questions.yaml` | `questions/<Q-###>` | Answer, reopen, add a question |
| `checklist.html` | `docs/kickoff-checklist[-<scope>].md` (drive-sources skill, "Mirror a Sheet locally") | `kickoff/<scope or all>/tasks` | Set status and note; mark rows copied into the Sheet |
| `review.html` | The review desk: several records, one tab each (see "Review desk") | `review`, `questions`, `tasks`, `risks`, `decisions`, `checklist`, `meta/info` | Approve, change, or drop Lucy's proposals; answer questions; set task status and dates; set risk severity, status, next step; settle pending decisions; set checklist status; add a question, task, or risk |

## Publish a page

1. Copy the template to a file in `tmp/` and fill it: `{{PROJECT_NAME}}` (the project's display name), `{{SCOPES_JSON}}` (the scopes from `docs/raci.yaml` or `docs/sources.yaml` as JSON, or `{}` on a single-site project; always replace it, or the script won't run), for the review desk `{{PM_NAME}}` (the PM's name as in `docs/people.yaml`), and for the checklist `{{SCOPE_KEY}}`, `{{SHEET_URL}}`, `{{SHEET_TITLE}}`, `{{SHEET_TAB}}`. Check the script parses (`node --check` on the extracted script) before publishing.
   For the RACI page, two `CONFIG` options: `site` set to a scope key makes a page for that site alone (no switcher; the title names the site), `showRoles: false` shows only people's names in the matrix (the roles list under it keeps each role as the reference), and `responseWindows: false` drops the "No response window" flags on a project that has chosen not to track them. On a multi-site project the PM can have one RACI page per site, all from the one `docs/raci.yaml`. Seed each with only its site's data (rows for `all` and that scope, each role's `people` for that scope, and that scope alone in `meta/info`), because anyone who can open a page can read its whole database. A record change then updates every page it appears on.
2. Publish it with capabilities `{"db": {}, "user": {}}`. The page starts private; tell the PM to share it from the page if the team should see it.
3. Seed the database from the record, one document per entry, in one batch. Fields keep their record names except that pages use camelCase (`next_step` is `nextStep`, `confirmed_by` is `confirmedBy`, `needed_by` is `neededBy`). A risk's `risk` is shown as it is, and its `description` on a page is the description followed by its updates, one per line as `<date>: <note>`; an edit to the page's description that only adds a line is filed as a new update. For every editable field, also store the value as it is in the file under `synced` (`synced: {severity, status, nextStep}` for a risk). Never seed invented example rows.
4. Read the collection back once (and once as a view-only user) to confirm it loaded.
5. Add the page to the root `CLAUDE.md` "This project" table: record, link. Pages live in one person's account, so the link is recorded but the record stays in `docs/`.

## Show a record

When the PM asks to see a record that has a template above, in any wording ("pull up my open questions", "show me the risks", "where's the RACI?"), the page is the answer, not a table in chat.

1. **Find the page** in the root `CLAUDE.md` "This project" table.
2. **Check it first.** Read its database and list anything waiting to be filed (see "Keep them in sync"), so the PM knows the page and the file differ.
3. **Open it** (in Claude: the Artifact tool's `open` action). If the record has a template but no page yet, publish it ("Publish a page"), then open it.
4. **Summarize in chat**, briefly: counts, and the few items most likely to need the PM's attention first. Don't reprint the whole record.

If the assistant can't open pages, answer from the file and say the page link is in the root `CLAUDE.md`. A record with no template (people, glossary, journal, meetings) is answered from the file.

## Review desk

The review desk is the PM's one stop for everything that needs them, and what "the dashboard" means. The record pages above show one whole record each; the desk shows only what needs attention across all of them, one tab each, with a count on every tab. It is the PM's internal tool: don't suggest sharing it.

| Tab | Seeded from | What goes in |
|---|---|---|
| Lucy's proposals | The review list of each meeting notes file still `status: draft` (meeting-notes skill, "Review"), and any other proposal Lucy returned for approval | One document per item: `id` (the notes file name and the item number, e.g. `2026-10-14-site-walkthrough-3`), `kind` (Task, People, RACI, Glossary, Dossier, Decision, Risk, ADR), `item` (the proposal in full, with its reason), `source` (the notes file), `ref` (timestamp), `scope`, `decision` and `note` (blank) |
| Questions | `docs/questions.yaml` | Every entry, as on the questions page |
| My tasks, Others owe | `docs/tasks.yaml` (tasks skill) | Every entry, with `mine: true` when the PM is the owner, plus `due`, `status`, `link`, and a blank `note` |
| Risks | `docs/risks.yaml` | Every entry, as on the risk page |
| Decisions | `docs/decisions.yaml` | Pending entries only, with `driver`, `approver`, `neededBy` |
| Checklists | Each `docs/kickoff-checklist[-<scope>].md` | Every row, `id` `<scope>-<row>`, with `scope`, `row`, `task`, `status`, `note` |

Every document gets `synced` for its editable fields (`decision`, `note` for a proposal; `status`, `due`, `note` for a task; `status`, `approver` for a decision; `status`, `note` for a checklist row), like the record pages. `meta/info` holds `processed` (a list of `{title, file}` for what was just processed) and `at` (the date), shown at the top of the page.

**After processing a new file or transcript** (meeting notes, a Drive source, a document Lucy filed):
1. Write the review list into the notes file, as the meeting-notes skill says, and add its items to the `review` collection.
2. Sync every tab from the files, set `meta/info`, and file anything already waiting on the page first.
3. Open the review desk and say in one line what's new on it (for example "7 proposals, 3 new questions, 2 tasks for you"). The PM works through it there instead of a long list in chat.

**Filing a proposal decision.** `approve` applies the item as proposed; `change` applies it with the PM's note; `drop` leaves it out. Apply them as meeting-notes step 8 says (approval is the PM's; never infer it from an untouched item), record the outcome in the notes file's review list, then delete the proposal's document. When a notes file has no undecided items left, it can be set to reviewed.

On a project without the review desk, publish it the first time Lucy finishes processing a file, then open it.

**Filing on a schedule.** The page tells the PM to ask Claude to "process the review desk changes", and suggests a scheduled task. When the PM wants one, create it with the assistant's scheduled-task tools if it has them; otherwise give the PM a prompt to schedule themselves: work in the Project Brain, follow `.ai/general/lobot.md`, run this skill's sync on every page in the root `CLAUDE.md`, file each change through its record's skill (decided proposals as meeting-notes step 8 says), turn anything unclear into a question rather than guessing, update `synced`, run the validators, journal it, change nothing when nothing is waiting, and never commit, push, or send anything outside the Project Brain. The PM's computer must be on at that time if the Project Brain is a folder on it.

## Keep them in sync

**Page to Project Brain.** At the start of a session (after the drive-sources check) and at session close, read each page's database. Anything waiting to be filed shows up as:
- a field that differs from its `synced` value (an edit),
- a document with `synced: null` (an item added on the page),
- an open document in the RACI page's `requests`,
- a proposal on the review desk with a `decision`.

List them for the PM in one short list per page. Then file each through its record's skill, at Lucy's autonomy for that record: an edit to a junior area is a proposal until the PM approves it (the PM making the edit on the page counts as the PM's request, not as approval of anything the assistant infers from it). After writing the file, update the document's `synced` to match (or close the request), so the page's waiting list clears.

**Project Brain to page.** Whenever a record with a page changes (a new risk, an answered question, a RACI update), update the page's documents and their `synced` values in the same pass.

**Conflicts.** The file wins. If a page edit and a file change disagree, don't overwrite either: ask the PM.

## Rules

- **The file is the record.** Pages are views and inboxes. Nothing on a page is part of the project's history until it is filed.
- **No secrets on a page**, and nothing beyond work contact details about people.
- **Page structure is the template's.** To change how a page works for every project, change the template here; a one-off tweak for one project goes in `.ai/project/`.
