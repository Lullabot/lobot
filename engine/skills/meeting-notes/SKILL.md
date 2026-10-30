---
name: meeting-notes
description: Turn a meeting transcript into derived meeting notes (docs/meetings/), after cleaning it with the transcript-cleanup skill, propose tasks, decision log entries, and context-doc updates, and flag risks and ADR candidates for follow-up. Use when the PM drops a transcript, asks to process/summarize a meeting, or asks what happened in a call.
---

# Meeting notes

## Why

Transcripts are long and noisy. The notes file is what the team and the assistant actually read later: what the meeting was about, who owes what, and what changed in our understanding of the project. Processing also keeps the context docs (people, glossary, overview) current, and makes sure risks and decisions raised in passing don't get lost.

## Where

| What | Path |
|---|---|
| Raw transcripts (never edit; git-ignored by default) | `docs/transcripts/raw/` |
| Cleaned transcripts, the ones notes cite and the Project Brain commits | `docs/transcripts/` (transcript-cleanup skill) |
| Derived notes, one per meeting | `docs/meetings/YYYY-MM-DD-<slug>.md` |
| Meeting type templates | `types/` in this skill's folder |
| Project task routing (where tasks go, labels) | `.ai/project/task-management.md` |
| Shareable copy for the team, one Google Doc per meeting | The `meeting-notes` folder in `docs/sources.yaml` (Project Management > Meeting Notes, next to Meeting Transcripts; one per scope) |

## Meeting types

Different meetings need different attention. Each type file says what to extract and how to lay out the notes.

| Type file | Use for |
|---|---|
| `types/general.md` | Default. Onboarding, kickoffs, syncs, status calls, anything without a more specific type. |

Ask the PM for the meeting type if it isn't stated. Record the PM's label (e.g. `onboarding`) in the notes' `type` and the template used in `template`. When a meeting doesn't fit a template well, say so and propose a new type file rather than stretching the general one. New types go here and in `types/`, designed with the PM.

## Workflow

1. **Locate the source.** Find the raw transcript in `docs/transcripts/raw/`. Note its format (Gemini notes markdown, plain text, WebVTT), date, title, and length. If the file contains a machine-written summary (e.g. "Notes by Gemini"), treat it as a hint only; the transcript is the source.
2. **Clean it** with the transcript-cleanup skill, up to its draft (`tmp/<slug>.clean.md`). Its cut list joins this skill's review (below), and the cleaned transcript is written to `docs/transcripts/` once the PM approves. Work from the cleaned draft from here on, and cite its timestamps.
3. **Load the type file** and `.ai/project/task-management.md`. If the project has no task-management file, ask the PM where tasks go and create it.
4. **Read the whole cleaned transcript**, in chunks if large. Don't summarize from the first half.
5. **Resolve names and terms as you read.**
   - Speakers and people mentioned: people skill. Transcript labels may be misspelled or differ from the directory (`Joshua` vs. `Josh`); match on `aka`. Never guess who an unknown name is.
   - Terms and likely mistranscriptions: glossary skill. When you correct a mistranscription in the notes, use the glossary term; if the match is uncertain, keep the original in quotes with `(unverified)`.
6. **Extract** what the type file asks for. Attribute statements to the person who made them. Cite the transcript timestamp for action items and flags so the PM can check them.
7. **Write the notes file** from the type file's template, `status: draft`.
8. **Present one review list** to the PM (see Review below): write it into the notes file's `## Review` section, one numbered line per item, then add the items to the review desk and open it (tracker-pages skill, "Review desk"). Without tracker pages, show the list in chat. Change nothing outside the notes file until the PM approves, except adding the PM's own actions to the task list (tasks skill) and the open questions to the questions log, each marked with its kind and who answers it (questions skill, "Kinds of question"), which are autonomous.
9. **Apply what was approved** in one pass: write the cleaned transcript to `docs/transcripts/` with the approved cuts (transcript-cleanup skill) and point the notes' `source` at it, file the PM's approved tasks per `.ai/project/task-management.md` and put each link in its task-list row, add decision log entries with the decision-log skill, edit context docs with their own skills (run validators), including the dossier topics the meeting adds facts to (dossier skill), and record task links, entry IDs, and doc changes back in the notes file. Mark each review line approved, changed, or dropped. Set `status: reviewed by <PM name>`.
10. **File the shareable copy** in Drive (see below), add its link to the notes' frontmatter as `drive_copy:`, and record the copy in `docs/sources.yaml` `processed` (source: the meeting-notes folder, result: the notes file).
11. **Journal** one Log entry linking the notes file, plus `#people`, `#risk`, `#decision` tags as applicable.

## Gemini notes

Google Meet's Gemini notes are one Doc with the summary, decisions, and next steps on one tab and the transcript on another. When the source is a Gemini notes Doc, the summary already exists and the team reads it there, so don't write another one:

- **Snapshot the whole Doc** (both tabs) to `docs/transcripts/raw/` as usual, and clean only the transcript tab (transcript-cleanup skill, `--from`). The transcript tab is the source; Gemini's summary is a hint that is often wrong (misattributed speakers, proposals reported as agreed, mistranscribed names).
- **Write a short record** in `docs/meetings/` instead of the full notes: the usual frontmatter plus `gemini_notes: <link>`, one line saying the summary and action items are Gemini's, then only **Corrections to Gemini's notes** (each with a transcript quote), the **Flags** table, and **Context updates**. No TL;DR, overview, or action-items table.
- **Review and apply** as usual (steps 7 and 8). The Gemini Doc is already in Drive, so file no shareable copy.

## Shareable copy in Drive

Reviewed notes also go to the project's shared drive, so the team can read them without the Project Brain. The file in `docs/meetings/` stays the record; the Drive copy is a snapshot of it.

- **Where.** The `meeting-notes` source in `docs/sources.yaml` for the meeting's scope: the Meeting Notes folder in Project Management, next to Meeting Transcripts. If it isn't mapped, offer to map or create it (drive-sources skill) and file the copy once the PM says yes.
- **When.** After the PM has reviewed the notes (`status: reviewed by ...`). Never file a draft.
- **What.** A new Google Doc (upload Markdown and let Drive convert it) titled `YYYY-MM-DD <meeting title>`. Start with one line: date, a link to the transcript in Drive (or its title when it was never in Drive), and "Notes reviewed by <PM name>". Then the notes' TL;DR, overview, action items, flags, and open questions. Leave out the frontmatter, the "Context updates" section, and links to Project Brain files (they don't open in Drive); write a record ID instead (`R-002`, `Q-012`).
- **Who reads it.** Anyone with access to the folder. The source's `shared_with_client` says whether the client can: when it is `false`, file the notes as they are; when it is `true` or not set, check the copy for anything meant only for Lullabot (internal risk commentary, account or pricing notes) and ask the PM before filing it.
- **Once Docs can be edited.** When the assistant has a connector that edits Google Docs, switch to one Doc per meeting with two tabs, the way Gemini's meeting notes are laid out: **Summary** (the copy described above) and **Transcript** (the full transcript). Confirm the switch with the PM first, and leave copies filed earlier as they are unless the PM asks to convert them.
- **Changes.** If the notes change after filing, file the change in the same Doc when the connector can edit it; otherwise tell the PM the copy is out of date. Never delete or move an old copy.

## Rules

- **Speakers, not attendees.** A transcript only shows who spoke. List them as `speakers`; never claim attendance. If the PM knows others attended silently, they can add them.
- **Stated vs. inferred.** The notes report what was said. Anything the assistant infers (meaning of a vague reference, who an action belongs to) is marked *(unverified)*.
- **No assistant opinions.** Risks, concerns, and decisions are flagged only when a speaker raised them. If the assistant notices a risk nobody named, raise it in chat during review; it goes in the notes only if the PM confirms, attributed to the PM.
- **Flag, don't fabricate.** When a meeting mentions a risk or architecture choice without enough detail for a full record, flag it as a follow-up task rather than writing a thin entry. When the project has a skill for that record type and the meeting gives enough detail, propose a full entry instead.
- **Decisions go to the decision log.** Run each decision in the meeting through the decision-log skill's entry test. Review the candidates with the PM in the review list and log the approved ones in the same pass, not as follow-up tasks. When nobody can confirm who approved one, log it as `pending`; never infer approval from silence. Put the entry ID in the notes' flags table. If the PM isn't available, follow the decision-log skill: log what clearly passes, and create a follow-up task for anything you aren't sure about. Architecture choices are not log entries: run them through the adr skill's entry test. One that passes and has been made is proposed in the review list as a draft ADR pull request; one that isn't decided yet, or that the PM can't review now, becomes a follow-up task.
- **Action items to tasks.** An action item is something a person said they'll do or find out: the PM's own actions, and non-design work or answers someone else committed to. Design work and design decisions owned by the design team (revising a wireframe, reworking a listing, showing designs at the next review, walking the client through a design artifact) are not action items: they go in the work breakdown (work-breakdown skill). All action items go in the notes' action-items table, whoever owns them. Only the PM's own one-off actions go in the task list (`docs/tasks.yaml`, tasks skill, "Only the PM's own one-off actions"); information the work is waiting on becomes a question (questions skill), and development work belongs in tickets. The PM's items and the follow-up flags also become tasks in the task manager, unless the project's task-management file says otherwise.
- **One fact, one home.** Notes link to people and glossary entries rather than redefining them. Facts about the project and its sites (the current site, audiences, content, data, migration, systems) go into the dossier (dossier skill), citing the notes file and timestamp; the notes keep only a short summary.
- **No secrets or personal chatter.** Leave out credentials, personal life details, and small talk. The cleaned transcript has already cut most of them; anything it kept that shouldn't be in the notes is a cut to add, not something to quietly leave out.

## Review

Show the PM one list, grouped, every item with a one-line reason and a transcript timestamp where relevant:

1. **Transcript cuts:** the list from the transcript-cleanup skill's `check`, with the share of words removed and any facts held in sensitive cuts. Sensitive cuts show their kind and reason, never the removed words.
2. **Tasks to create:** title, project/section, priority, labels, assignee, description summary. Follow the task-management file's conventions.
3. **Context doc changes:** people (new entries, new facts, IDs), RACI (people named to a role or area, and anyone acting outside their recorded role, per the raci skill), glossary (new terms, corrected meanings, new `aka`), dossier (facts added or corrected per site topic file, open gaps closed), work breakdown (items added or changed, each change stated exactly; already applied when the work breakdown is autonomous, otherwise proposed; work-breakdown skill).
4. **Decision log entries:** each proposed entry in full (decision, justification, driver, approver, status, tags), per the decision-log skill.
5. **Flags:** risks, ADR candidates, open questions, and how each will be followed up.
6. **Questions for the PM:** unknown people, uncertain terms, unclear owners. Whatever the PM doesn't answer during review is added to the questions log (questions skill), and the notes' open questions link to it.

The PM approves, edits, or drops items in one pass. Apply only what was approved.
