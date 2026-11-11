# Directory map

Where everything in a Project Brain lives and who maintains it. Read it when unsure where something lives or belongs; for where a new file goes, `.ai/general/context-docs.md` ("Where things go") decides.

| Path | What it is | Who maintains it |
|---|---|---|
| `README.md` | Human-facing overview, per-tool setup (Claude Code, Cowork, others), handoff steps. | PM |
| `CLAUDE.md` | Entry point. Names the project, points here, and lists what is specific to this project. Keep it short. | PM + assistant |
| `.ai/` | Instructions for the assistant: rules and skills. | PM + assistant |
| `.ai/general/` | Lobot: how the assistant operates as a PM assistant on **any** project. A copy of the Lobot engine at the version in `.ai/general/.lobot-version`. Must contain nothing project-specific. | Lobot (see "Changing Lobot") |
| `.ai/general/lobot.md` | Loaded every session: hard rules, start-of-session routine, which skill to use when, working rules. | Lobot |
| `.ai/general/personality.md` | How the assistant (Lobot) sounds when talking to the PM: tone, proactiveness, humor, adjustable settings. Applies to conversation only, never to records or drafts in the PM's voice. | Lobot |
| `.ai/general/glossary.yaml` | Shared glossary: Drupal, Lullabot tooling, and Agile terms that mean the same on any project. | Lobot |
| `.ai/general/reference/` | Pages read only when needed: this directory map, and pages for people outside the project, e.g. `security.md` (what Lobot needs access to and why, for a security team). | Lobot |
| `.ai/general/research/` | Reference research behind the skills (e.g. industry criteria for ADRs, decision logs, risk registers, RACI). Suggestions in it are not rules until a PM adopts them. | Lobot |
| `.ai/general/human-review.md` | The security rule for what leaves the Project Brain: which sources are trusted, and how anything built from untrusted material is drafted, approved by a person, stamped, and sent exactly as approved. | Lobot |
| `.ai/general/context-docs.md` | Where everything in `docs/` goes (living records vs. dated files, reports, naming), and how to write context docs (progressive disclosure, frontmatter, generated files). | Lobot |
| `.ai/general/pages.md` | Steps and rules shared by the read-only pages Lobot publishes (weekly and daily boards, ticket preview). | Lobot |
| `.ai/general/records-in-sheets.md` | How the risk tracker, decision log, and questions log live in Google Sheets instead of their `docs/` files when the PM moves them there: IDs, sites, approvals, and moving in and back. | Lobot |
| `.ai/general/delegation.md` | Roster of named agents and the rules for handing work to them (routing, briefs, approvals, sequencing). | Lobot |
| `.ai/general/agents/` | Named agents. `<name>.md` is the agent's definition, which Lobot copies to `.claude/agents/`, where Claude looks for it. `<name>/` holds its supporting files, e.g. Lucy the librarian's personality and general corrections log. The roster is in `delegation.md`. | Lobot |
| `.ai/project/agents/<name>/` | An agent's settings for this project: `config.md` (autonomy levels, sources) and `corrections.md` (project corrections log). | PM |
| `.claude/skills/`, `.agents/skills/` | Links to every skill in `.ai/general/skills/` and `.ai/project/skills/`, so assistants that discover skills on their own find them. Made by Lobot; the skills themselves live in `.ai/`. | Lobot |
| `.ai/general/scripts/` | Helper scripts that work on any project (e.g. `drupal_config_inventory.py`). | Lobot |
| `.ai/project/` | How the assistant helps on **this** project only (project conventions, client norms, workflows). | PM + assistant |
| `.ai/project/github.md` | The project's repo, GitHub Project boards, field and option IDs (used by the github skill), and where the Project Brain's own repository stands (project-setup skill). | PM + assistant |
| `.ai/project/tickets.md` | Which tracker the project's tickets go to (the PM's choice), and the team's ticket conventions: labels, types, workflow, definition of done, stale threshold (used by the tickets skill). | PM + assistant |
| `.ai/project/jira.md` | The project's Jira site, spaces, reference space and shared schemes, boards, and conventions (used by the jira skill). | PM + assistant |
| `.ai/project/jira/<SPACE>.yaml` | Generated: a Jira space's work types, fields (names, kinds, allowed values), statuses, link types, sprints, and open epics, so Pepper can draft ticket plans for Jira without reaching it (jira skill, `jira.py structure`). Never hand-edited. | Assistant |
| `.ai/project/adr.md` | The project's ADR setup: ADR directory, base branch, branch naming, technical lead (used by the adr skill). | PM + assistant |
| `.ai/project/client-status-report.md` | The header, readers, due day, scopes, and file name for the weekly client status report (used by the client-status-report skill). | PM + assistant |
| `.ai/project/client-status-report/template.md` | The project's own status report template, when the PM built one; it replaces the skill's default. | PM + assistant |
| `.ai/project/project-journal-entry.md` | The account manager, other readers, and due day for the weekly project journal entry (used by the project-journal-entry skill). | PM + assistant |
| `.ai/project/voice/` | One file per PM (`<people-key>.md`) with how their voice differs on this project (a client's register, a team's norms), layered over their personal voice. See the pm-voice skill. | PM + assistant |
| `~/.lobot/` | Outside the Project Brain, in the PM's home folder: their personal profile (`voice.md`, `preferences.md`, including their task manager settings), shared by every project they work on. Nothing project-specific. See the pm-profile skill. | PM + assistant |
| `.ai/project/meeting-notes.md` | The project's recurring meetings: how to recognize each, its audience, whether its notes are shared as one Doc per meeting, a running doc, or both, and which running doc and tab (meeting-notes skill, "Recurring meetings"). | PM + assistant |
| `.ai/project/transcript-cleanup.md` | Who can read this Project Brain (which decides whether internal matters are cut from transcripts) and anything else this project cuts. Asked before the first cleanup (transcript-cleanup skill). | PM + assistant |
| `.ai/project/declined-migrations.yaml` | Lobot migrations the PM chose not to apply, so they stop coming up (lobot skill, "Migrate"). Written by Lobot's `migrate --decline`. | Lobot tool |
| `.ai/project/task-management.md` | Which task manager the PM uses on this project (first line: `Task manager: Lobot`, the default, or `Todoist`), and that task manager's settings for this project (tasks skill). | PM |
| `docs/` | Context artifacts: the material the assistant reads to do tasks (people, glossary, notes, derived summaries, journal). | Assistant, reviewed by PM |
| `docs/overview/` | Project dossier: `index.md` (read first) → one folder per site (`sites/<site>/`: index, topic files such as the current site's background, audiences, content, data, migration) → `reference/` (exhaustive or generated detail). Every fact cites its source. See the dossier skill. | Lucy, reviewed by PM |
| `docs/people.yaml` | Canonical people directory: active participants, roles, timezones, third-party usernames/IDs. See the people skill. | Assistant |
| `docs/glossary.yaml` | Project glossary: terms with a meaning specific to this project (client acronyms, internal names, jargon). Overrides the shared glossary on conflicts. See the glossary skill. | Assistant |
| `docs/raci.yaml` | RACI matrix: who is Responsible, Accountable, Consulted, and Informed for each area of work, agency and client, per site or program. See the raci skill. | Assistant, reviewed by PM |
| `docs/decisions.yaml` | Decision log: project decisions, made and pending (decision, justification, driver, approver, status). See the decision-log skill. Empty when the log lives in Sheets (`.ai/general/records-in-sheets.md`). | Assistant, reviewed by PM |
| `docs/questions.yaml` | Questions log: outstanding questions in four kinds (project questions only the PM can answer, product questions for a stakeholder, technical questions for developers or client IT, housekeeping checks for the Project Brain), with who answers each, its priority, its status, when it is needed by, and the answers. See the questions skill. Empty when the log lives in Sheets (`.ai/general/records-in-sheets.md`). | Lucy, answered by PM |
| `docs/risks.yaml` | Risk tracker: project risks with severity, status, who confirmed them, next step, and dated updates. See the risks skill. Empty when the tracker lives in Sheets (`.ai/general/records-in-sheets.md`). | Lucy, reviewed by PM |
| `docs/tasks.yaml` | Task list: the PM's own one-off actions from meetings and documents, with due date and status (not dev work, routine team work, questions, or risk next steps). See the tasks skill. | Lucy, closed by PM |
| `docs/work/` | Work breakdown: what the team will build, one folder per site plus `shared/`, an index and one Markdown file per feature area of `W-###` items, each with its status (idea, draft, ready, ticketed) and sources. See the work-breakdown skill. | Lucy, reviewed by PM |
| `docs/sources.yaml` | The project's shared Google Drive (one root per site or program when it has several), where its standard folders and files live (transcripts, contracts, client-facing Sheets), the link to the internal project journal doc, and the files already processed. See the drive-sources skill. | Lucy, reviewed by PM |
| `docs/kickoff-checklist.md` | Local mirror of the project's kickoff checklist Sheet (one per site or program when there are several), kept until the assistant can edit Sheets. See the drive-sources skill. | Assistant, synced by PM |
| `docs/transcripts/` | Cleaned meeting transcripts: small talk and sensitive passages cut and marked, one timestamped paragraph per speaker turn. What meeting notes cite, and the only transcripts committed by default. See the transcript-cleanup skill. | Lucy, reviewed by PM |
| `docs/transcripts/raw/` | Raw meeting transcripts: files the PM drops in and snapshots of transcripts read from Drive (source; never edit). Git-ignored by default, so they stay on the PM's computer. | PM + Lucy |
| `docs/meetings/` | Derived meeting notes (`YYYY-MM-DD-<slug>.md`) from transcripts: TL;DR, overview, action items, flags, with a link to the transcript. A recurring meeting still gets one file per meeting here, even when the team reads its notes in a running doc. See the meeting-notes skill. | Assistant, reviewed by PM |
| `docs/journals/` | Daily journal (`YYYY-MM-DD.md`): what was done, why, decisions, attributed thoughts. See the journal skill. | Assistant, reviewed by PM |
| `docs/reports/` | Dated reports (`YYYY-MM-DD-<slug>.md`): analyses, audits, status snapshots, and briefings, true as of their date and linkable from tickets and other docs. Not kept current; see context-docs. | Assistant, reviewed by PM |
| `repo/` | The project's code repository (its own git repo, not tracked by the Project Brain). Read-only for PM work unless explicitly asked; ADRs are added through the adr skill on their own branch and pull request. | Dev team |
| `tmp/` | Working files needed only until their work is done: a ticket draft before it's posted, a diff or extract for the PM to review, a template being filled before it's published. Never committed (it holds its own `.gitignore`) and cleared when the session closes. | Assistant |
| `Claude outputs/` | Files the Claude app saves on its own (CSV exports, markdown copies of answers). Treated like `tmp/`: never committed (listed in the root `.gitignore`), checked when the session closes. | Claude app |

Within `.ai/general/` and `.ai/project/`, rules live as markdown files at the top level and skills live in a `skills/<skill-name>/SKILL.md` folder. After adding a project skill, link it so assistants discover it (see the lobot skill).
