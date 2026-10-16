# Filing and writing context docs

Where everything the assistant writes in the Project Brain goes, and how to write the context docs in `docs/` that give the assistant (and a new PM) the project's context. The main context doc is the project dossier in `docs/overview/`; the dossier skill (`.ai/general/skills/dossier/SKILL.md`) applies these rules to it: its layout, standard topics, and how facts get in.

## Where things go

Every file has one home, by what it is. Use the first row that fits.

| What it is | Where | Kept by |
|---|---|---|
| A person, their role, time zone, or a username/ID | `docs/people.yaml` | people skill |
| Who is responsible for or approves an area of work | `docs/raci.yaml` | raci skill |
| A term with a meaning specific to the project | `docs/glossary.yaml` | glossary skill |
| A project decision, made or pending | `docs/decisions.yaml` (architecture decisions are ADRs in the code repo) | decision-log skill, adr skill |
| A risk, an open question (for the PM, or about the product), an action item | `docs/risks.yaml`, `docs/questions.yaml`, `docs/tasks.yaml` | risks, questions, tasks skills |
| Where things live in the project's shared Drive | `docs/sources.yaml` | drive-sources skill |
| What is true now about the project or a site | `docs/overview/` (the dossier) | dossier skill |
| A meeting transcript (source; never edited) | `docs/transcripts/` | meeting-notes skill |
| Notes from one meeting | `docs/meetings/YYYY-MM-DD-<slug>.md` | meeting-notes skill |
| What was done in a session, and why | `docs/journals/YYYY-MM-DD.md` | journal skill |
| A report: an analysis, audit, status snapshot, briefing, or list prepared for someone, true as of a date | `docs/reports/YYYY-MM-DD-<slug>.md` | see "Reports" below |
| A deliverable whose home is Drive, such as the weekly client status report | Its mapped `output` folder in Drive, not `docs/` | its skill; the PM chooses the home (drive-sources skill, "Where a deliverable lives") |
| A working file, needed only until its work is done (a ticket draft before it's posted, a diff for review, a filled template) | `tmp/` at the Project Brain root, never committed | see the working rules in `.ai/general/lobot.md` |

- **Living or dated.** Records and the dossier are living: they always say what is true now, and are corrected in place. Meetings, journals, and reports are dated: each says what was true or said on its date, and is not rewritten later.
- **Split what a file holds.** A meeting or a report often contains facts for several homes. File each fact, decision, risk, question, and task in its own home, and have the dated file refer to it (by ID or link) rather than be its only copy.
- **Nothing loose.** The top level of `docs/` holds only the records (`*.yaml`) and the kickoff checklist mirror. Don't add new files or folders there; when something fits no row above, ask the PM where it goes, and once agreed add it to `.ai/project/` as a project rule.
- **Dated names start with the date.** `YYYY-MM-DD-<slug>.md`, with a short lowercase slug, so a folder lists in time order.
- **Moving a file updates its links.** Search the Project Brain for the old path and point every link at the new one, except in past journal entries, which are never rewritten.

## Reports

A report is a snapshot: what the assistant found or prepared, as of its date, to read, share, or link from a ticket or another doc. It is not temporary, but it is not kept current either; the dossier and the records are.

- **Path:** `docs/reports/YYYY-MM-DD-<slug>.md`, dated by when its facts were gathered. Create `docs/reports/` on first use.
- **Frontmatter:** `title`, `date`, `status` (`draft`, `reviewed by <name>`, `shared with <who>`), and `sources` (what it was built from, with dates or commit hashes).
- **Open with the bottom line:** the conclusion and what's needed from whom, before the detail.
- **Don't rewrite it later.** Fix mistakes while it is still a draft. Once things change, write a new report and add one line at the top of the old one pointing to it.
- **File what it found.** Decisions, risks, questions, tasks, and lasting facts in a report also go in their homes (see the table above), with the report as their source.

## Progressive disclosure

Organize context in levels so a reader loads only what a task needs:

1. **Level 1 — index.** One screen. What it is, key facts, and a table of areas with a one-line summary and a link each. Always cheap to read; read at session start.
2. **Level 2 — topic files.** One per area (content model, features, platform, history…). Summaries, tables, and the "worth knowing" points. A few hundred lines at most.
3. **Level 3 — reference.** Exhaustive or generated detail (full field lists, inventories, extracts). Read only when a task needs specifics. Keep in a `reference/` subfolder.

Each level links down to the next. Don't repeat detail upward; summarize it.

## Every context file

- Starts with frontmatter: `title`, `status` (e.g. `draft`, `reviewed by <name>`), `sources` (what it was derived from, with a commit hash or date), `updated`.
- Marks inferences *(unverified)* until a person or authoritative source confirms them.
- States known gaps rather than guessing.
- Prefers tables and short bullets over prose.
- Links to people and glossary entries rather than redefining them.

## Generated files

- Produced by a script kept in `.ai/general/scripts/` (portable) or `.ai/project/scripts/` (project-only).
- Say at the top that they're generated, from what, when, and how to regenerate. Never hand-edit; regenerate.
- Never include secret values.
