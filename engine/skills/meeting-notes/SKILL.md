---
name: meeting-notes
description: Turn a cleaned meeting transcript into notes in docs/meetings/, file them for the team straight away (a Doc per meeting, a running-doc entry for recurring meetings), then propose the tasks, decisions, and facts it yields for review. Use when the PM drops a transcript or asks what happened in a meeting.
---

# Meeting notes

## Why

Transcripts are long and noisy. The notes file is what the team and the assistant actually read later: what the meeting was about, who owes what, and what changed in our understanding of the project. Processing also keeps the context docs (people, glossary, overview) current, and makes sure risks and decisions raised in passing don't get lost.

**The summary and the records are separate.** A summary reports what was said, so it needs no approval: it's filed for the team as soon as it's written. What the meeting changes in the project's records (tasks, decisions, risks, questions, people, glossary, dossier, work breakdown) is proposed for the PM's review, and only what's approved is filed. The cleaned transcript's cuts are part of that review, because a transcript once committed stays in git history. The one exception: a summary going where the client or other outside people can read it waits for the PM's check (see "Who reads it").

## Where

| What | Path |
|---|---|
| Raw transcripts (never edit; git-ignored by default) | `docs/transcripts/raw/` |
| Cleaned transcripts, the ones notes cite and the Project Brain commits | `docs/transcripts/` (transcript-cleanup skill) |
| Derived notes, one per meeting | `docs/meetings/YYYY-MM-DD-<slug>.md` |
| Meeting type templates | `types/` in this skill's folder |
| Project task routing (where tasks go, labels) | `.ai/project/task-management.md` |
| Shareable copy for the team, one Google Doc per meeting | The `meeting-notes` folder in `docs/sources.yaml` (Project Management > Meeting Notes, next to Meeting Transcripts; one per scope) |
| Recurring meetings and how each one's notes are shared | `.ai/project/meeting-notes.md` (see "Recurring meetings") |
| Running notes doc for recurring meetings, a dated entry per meeting | A Google Doc mapped in `docs/sources.yaml`; by default `<KEY> Recurring Meeting Notes` in the Meeting Notes folder, one tab per kind of recurring meeting |

## Meeting types

Different meetings need different attention. Each type file says what to extract and how to lay out the notes.

| Type file | Use for |
|---|---|
| `types/general.md` | Default. Onboarding, kickoffs, syncs, status calls, anything without a more specific type. |

Ask the PM for the meeting type if it isn't stated. Record the PM's label (e.g. `onboarding`) in the notes' `type` and the template used in `template`. When a meeting doesn't fit a template well, say so and propose a new type file rather than stretching the general one. New types go here and in `types/`, designed with the PM.

## Workflow

1. **Locate the source** and start a process marker for the meeting (save skill, "Process markers"). Find the raw transcript in `docs/transcripts/raw/`. Note its format (Gemini notes markdown, plain text, WebVTT), date, title, and length. If the file contains a machine-written summary (e.g. "Notes by Gemini"), treat it as a hint only; the transcript is the source.
2. **Clean it** with the transcript-cleanup skill, up to its draft (`tmp/<slug>.clean.md`). Its cut list joins this skill's review (below), and the cleaned transcript is written to `docs/transcripts/` once the PM approves. Work from the cleaned draft from here on, and cite its timestamps.
3. **Load the type file** and `.ai/project/task-management.md`. If the project has no task-management file, the task manager is Lobot's own list; ask the PM once whether they'd rather use another one (tasks skill, "Task managers") and create the file.
4. **Read the whole cleaned transcript**, in chunks if large. Don't summarize from the first half.
5. **Resolve names and terms as you read.**
   - Speakers and people mentioned: people skill. Transcript labels may be misspelled or differ from the directory (`Joshua` vs. `Josh`); match on `aka`. Never guess who an unknown name is.
   - Terms and likely mistranscriptions: glossary skill. When you correct a mistranscription in the notes, use the glossary term; if the match is uncertain, keep the original in quotes with `(unverified)`.
6. **Extract** what the type file asks for. Attribute statements to the person who made them. Cite the transcript timestamp for action items and flags so the PM can check them.
7. **Write the notes file** from the type file's template, with `status: draft` and `review: open`.
8. **File the notes for the team** right away, without waiting for review: a standalone meeting gets its own Doc in the Meeting Notes folder (see "Notes in Drive"); a recurring meeting is shared the way its row in `.ai/project/meeting-notes.md` says: an entry in its running doc, its own Doc, or both (see "Recurring meetings"). Where a decision, risk, or question is still proposed, say "proposed" instead of a record ID. Add the links to the notes' frontmatter (`drive_copy:`, `running_doc:`), record each in `docs/sources.yaml` `processed`, and set `status: shared`. A Doc that outside people can read waits for the PM's check of that copy first ("Who reads it"); the other copies don't wait for it.
9. **Present one review list** to the PM (see Review below): the records the meeting changes, not the summary. Write it into the notes file's `## Review` section, one numbered line per item, then add the items to the review desk and open it (tracker-pages skill, "Review desk"). Without tracker pages, show the list in chat. Change no record until the PM approves, except adding the PM's own actions to the task list (tasks skill) and the open questions to the questions log, each marked with its kind and who answers it (questions skill, "Kinds of question"), which are autonomous. Then commit the notes and those additions before waiting (save skill).
10. **Apply what was approved** in one pass: write the cleaned transcript to `docs/transcripts/` with the approved cuts (transcript-cleanup skill) and point the notes' `source` at it, file the PM's approved tasks per `.ai/project/task-management.md` and put each link in its task-list row, add decision log entries with the decision-log skill, edit context docs with their own skills (run validators), including the dossier topics the meeting adds facts to (dossier skill), and record task links, entry IDs, and doc changes back in the notes file. Mark each review line approved, changed, or dropped. Set `review: done by <PM name> (YYYY-MM-DD)`. When this changes what the filed notes say (a record ID in place of "proposed", a decision the PM dropped, a passage the PM added to the cuts), correct the Doc and the running-doc entry in place ("Changes").
11. **Journal** one Log entry linking the notes file, plus `#people`, `#risk`, `#decision` tags as applicable.
12. **Commit** the processed meeting as one commit, listing the records it changed and who approved them (save skill), and delete its process marker.

## Gemini notes

Google Meet's Gemini notes are one Doc with the summary, decisions, and next steps on one tab and the transcript on another. When the source is a Gemini notes Doc, the summary already exists and the team reads it there, so don't write another one:

- **Snapshot the whole Doc** (both tabs) to `docs/transcripts/raw/` as usual, and clean only the transcript tab (transcript-cleanup skill, `--from`). The transcript tab is the source; Gemini's summary is a hint that is often wrong (misattributed speakers, proposals reported as agreed, mistranscribed names).
- **Write a short record** in `docs/meetings/` instead of the full notes: the usual frontmatter plus `gemini_notes: <link>`, one line saying the summary and action items are Gemini's, then only **Corrections to Gemini's notes** (each with a transcript quote), the **Flags** table, and **Context updates**. No TL;DR, overview, or action-items table.
- **File, review, and apply** as usual (steps 8 to 10). The Gemini Doc is already in Drive, so file no Doc of your own. A recurring meeting whose notes go in a running doc still gets its entry there straight away, written from Gemini's summary as corrected in the short record, with the Gemini Doc as its source.

## Notes in Drive

The notes go to the project's shared drive as soon as they're written, so the team can read them without the Project Brain. The file in `docs/meetings/` stays the record; the Drive copy is a snapshot of it. It's the detailed version of the meeting; a recurring meeting's running-doc entry is the overview.

- **Where.** The `meeting-notes` source in `docs/sources.yaml` for the meeting's scope: the Meeting Notes folder in Project Management, next to Meeting Transcripts. If it isn't mapped, offer to map or create it (drive-sources skill) and file the copy once the PM says yes.
- **When.** Right after the notes file is written (step 8), before the review. The PM reviews the records the meeting yields, not the summary.
- **What.** A new Google Doc (upload Markdown and let Drive convert it) titled `YYYY-MM-DD <meeting title>`. Start with one line: date, a link to the transcript in Drive (or its title when it was never in Drive), and "Summary drafted by Claude from the transcript", so readers know it's AI-written and unreviewed. Then the notes' TL;DR, overview, action items, flags, and open questions. Leave out the frontmatter, the "Context updates" section, and links to Project Brain files (they don't open in Drive); write a record ID instead (`R-002`, `Q-012`).
- **Who reads it.** Anyone with access to the folder. The source's `shared_with_client` says whether the client can: when it is `false`, file the notes as they are; when it is `true` or not set, check the copy for anything meant only for Lullabot (internal risk commentary, account or pricing notes), show it to the PM, and file it once they OK it (`.ai/general/human-review.md`). This is the only check a summary waits for.
- **Once Docs can be edited.** When the assistant has a connector that edits Google Docs, switch to one Doc per meeting with two tabs, the way Gemini's meeting notes are laid out: **Summary** (the copy described above) and **Transcript** (the full transcript). Confirm the switch with the PM first, and leave copies filed earlier as they are unless the PM asks to convert them.
- **Changes.** If the notes change after filing, file the change in the same Doc when the connector can edit it; otherwise tell the PM the copy is out of date. Never delete or move an old copy.

## Recurring meetings

Teams used to one running doc for a weekly meeting want to scroll back to last time, not open a new Doc each week. For a recurring meeting the PM chooses how its notes are shared: one Doc per meeting (the detailed notes, above), a running doc with a dated entry for each meeting (the overview), or both. Either way the Project Brain keeps one notes file per meeting in `docs/meetings/`; that file stays the record, and the running doc is a copy of it, like the Drive copy.

### The project's recurring meetings

`.ai/project/meeting-notes.md` lists them. Create it the first time one comes up:

```markdown
# Meeting notes: <KEY>

## Recurring meetings

| Meeting | Matches | Audience | Share as | Running doc | Tab |
|---|---|---|---|---|---|
| Team Huddle | Titles starting "Team huddle" | Internal | running | recurring-meeting-notes | Team Huddle |
| Schedule Review | "Schedule review" | Internal | both | recurring-meeting-notes | Schedule Review |
| Design and Strategy Sync | "Design sync", "Strategy sync" | Client | running | recurring-meeting-notes-client | Design and Strategy Sync |
```

- **Meeting:** its name. The notes file names it in `series:`.
- **Matches:** how to recognize it: titles, or other signs the PM gives.
- **Audience:** `Internal` (Lullabot only) or who else attends (`Client`, a vendor).
- **Share as:** `copies` (one Doc per meeting, as for any meeting), `running` (an entry in the running doc), or `both`.
- **Running doc:** the key of the doc's entry in `docs/sources.yaml`; `—` for `copies`.
- **Tab:** the doc's tab for this meeting, or `—` when entries go straight in the doc.

### Spotting a recurring meeting

A meeting is recurring when its title matches a row. With no row yet, it may be one when it shares its title with an earlier notes file, its invite repeats, or the PM says so. Then ask the PM once, as a review item ("Questions for the PM"): share its notes as one Doc per meeting, in a running doc with a new dated entry each time, or both? For a running doc, settle where it goes (below), then add the row. A meeting with no row is shared as a copy, as before.

### Where the running doc goes

The PM can point to a Doc or a folder they already use. Otherwise say Lobot's default and ask about an override, as for any deliverable (drive-sources skill, "Where a deliverable lives"):

- **Internal meetings:** one `<KEY> Recurring Meeting Notes` Doc in the Meeting Notes folder, with a tab for each kind of recurring meeting, named for it ("Team Huddle", "Schedule Review"). Each tab is laid out as in "The tab" below. Its key is `recurring-meeting-notes`.
- **Meetings with outside people:** a separate running doc, never the internal one, because the audience decides who may read it. Ask the PM which folder those people can open (usually one shared with the client) and whether meetings with the same audience share the doc, one tab each. Key it `recurring-meeting-notes-<short name>`. Who can open the doc is the PM's to set: Lucy never shares it or changes its permissions.
- **How it's organized** depends on the tool, and the PM can override the default. In Google Docs, ask whether the PM wants a tab per kind of meeting (the default), sub-tabs (one per meeting under an audience, or one per year in a long-running meeting), or a doc per meeting with no tabs. In another tool, ask how it groups pages or sections, and note the answer in the row.

Map the doc in `docs/sources.yaml` as a `deliverable` file with `record: docs/meetings/`, `shared_with_client` for its audience, and `edit: ok` when it's internal or `edit: ask` when outside people can read it (drive-sources skill). Creating it, and adding a tab, follow Lucy's autonomy for Drive changes. If the Docs connector can't add a tab, ask the PM to add one with the meeting's name, then fill it in.

### Adding an entry

As soon as the notes file is written (step 8), and only with a connector that edits Google Docs. Without one, file a copy for this meeting and tell the PM the running doc needs that connector.

1. **Read the doc** (the meeting's tab). Look for a heading with the meeting's date: someone may have added it ahead of time with an agenda. If there's none, add the date heading just below the divider (see "The tab"), above the latest entry, so the newest meeting comes first. The header above the divider is the PM's: never change it.
2. **Write the entry under that heading**, in the layout below. Never change earlier entries or text someone else wrote: an agenda already there stays as written and is the entry's Agenda. Write against the revision you just read, so someone else's edit in the meantime stops the write instead of being overwritten; then read again and retry.
3. **Read it back,** check it, add the doc's link (to the tab) to the notes' frontmatter as `running_doc:`, and record it in `docs/sources.yaml` `processed` (source: the running doc's key, result: the notes file).

#### The tab

Top to bottom:

1. **Title,** Heading 1: the meeting's name and "Running Notes" ("Team Huddle Running Notes", "Breath Alcohol Running Notes"). No intro paragraph: the title says what the tab is.
2. **Header** (optional): content the PM keeps there for every meeting, such as a short schedule table or links to docs the meeting refers to, under Heading 2s ("Schedule"). The PM defines it; when setting up a new tab, ask whether it needs one.
3. **Divider:** a horizontal line, with no label, between the header (or the title) and the entries. The Docs API can't insert a horizontal line, so set a bottom border on the empty paragraph after the header instead, or ask the PM to add one with Insert > Horizontal line. Either one is the divider.
4. **Entries,** newest first: the date as a Heading 2 ("October 29, 2026"), and each part of the entry as a Heading 3 under it, in the order below.

#### The entry

1. **Attendees:** a bulleted list, one person per bullet: who spoke, plus anyone the PM or the invite confirms was there. Under the list, one plain line says where the list comes from ("Speakers; attendance not confirmed", "From the invite and transcript").
2. **Agenda** (only when there was one): the agenda written ahead of time, or the one stated at the start of the meeting.
3. **Notes:** short bullets of what was discussed, one per topic, like minutes but quick to scan for the gist.
4. **Decisions:** a numbered list, each with what was decided, who made it, what it changes, and its decision log ID, or "proposed" until the PM approves it.
5. **Action items:** a checklist (Docs' checkbox list, so people can tick items off), only the key follow-ups that sit outside the regular workflow and people's usual jobs, each starting with its owner, then the action and any deadline or key detail. Not every "I'll look into it", and not ticket work. The full list stays in the notes file. Write the owner as a person mention (smart chip; the Docs API's `insertPerson` with their email from the people directory) when they are on the project team or have an account that can open the doc, so the chip links to them; otherwise write their name as plain text. Check who can open it with the doc's (or its shared drive's) permissions; never share the doc to make a mention work.
6. A last line: **Source:** a link to the transcript or recording in Drive (they stay their own files in the Meeting transcripts folder), or to the Gemini notes Doc; a link to the meeting's own Doc when it has one ("Full notes"); and "Summary drafted by Claude from the transcript".

The Drive copy's content rules apply: no frontmatter, Context updates, or links to Project Brain files (write record IDs instead), and when outside people can read the doc, check the entry for anything meant only for Lullabot and ask the PM before filing it ("Who reads it").

**Changes.** If the notes change after their entry was filed (the review usually changes a few: record IDs, a dropped decision, a new cut), correct that entry in place, at the doc's edit level, and nothing else in the doc. Someone else's edits to the doc (usually the next meeting's agenda) are expected: a check reports the doc as changed, and the agenda is picked up when that meeting is processed.

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

The review covers what the meeting changes in the project's records. The summary isn't in it: it was filed at step 8, and the PM corrects it by saying what's wrong, like any filed notes.

1. **Transcript cuts:** the list from the transcript-cleanup skill's `check`, with the share of words removed and any facts held in sensitive cuts. Sensitive cuts show their kind and reason, never the removed words.
2. **Tasks to create:** title, project/section, priority, labels, assignee, description summary. Follow the task-management file's conventions.
3. **Context doc changes:** people (new entries, new facts, IDs), RACI (people named to a role or area, and anyone acting outside their recorded role, per the raci skill), glossary (new terms, corrected meanings, new `aka`), dossier (facts added or corrected per site topic file, open gaps closed; a correction that contradicts a cited fact is a review item, not a change, per the dossier skill's "Contradictions"), work breakdown (items added or changed, each change stated exactly; already applied when the work breakdown is autonomous, otherwise proposed; work-breakdown skill).
4. **Decision log entries:** each proposed entry in full (decision, justification, driver, approver, status, tags), per the decision-log skill.
5. **Flags:** risks, ADR candidates, open questions, and how each will be followed up.
6. **Questions for the PM:** unknown people, uncertain terms, unclear owners. Whatever the PM doesn't answer during review is added to the questions log (questions skill), and the notes' open questions link to it.

The PM approves, edits, or drops items in one pass. Apply only what was approved.
