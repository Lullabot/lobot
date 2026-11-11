---
name: drive-sources
description: Map the project's shared Google Drive in docs/sources.yaml, check it for new or changed files, and read files in place. Use to set up Drive, for "anything new in Drive?" or "process the latest transcripts", at session start, and before using a Drive file.
---

# Drive sources

## Why

Every Lullabot client project has its own shared drive, and most project material lives there: Meet transcripts, SOWs, status reports, and the trackers the client sees. Exporting each file before the assistant can use it is slow, and the copy goes stale. This skill keeps two things in `docs/sources.yaml`:

- **Where things are.** The shared drive, and each folder or file the project uses, under the same key on every project (from the standard layout). A new PM, or a PM moving between projects, finds the same things in the same places.
- **What has been handled.** Every file already processed, so "what's new?" has a reliable answer and nothing is filed twice.

## Rules

- **Ask before scanning.** Mapping the shared drive starts with the PM's go-ahead, every time. Checking already-mapped sources doesn't need one.
- **Changes in Drive follow Lucy's autonomy.** Creating a folder or blank file is a change in the client's drive, so it is its own autonomy area in Lucy's project config (junior by default). At junior, she names exactly what she'll create and where, and waits for the PM's yes on each item.
- **Never delete, move, rename, or share in Drive,** and never change permissions. Ask the PM to do it.
- **Records stay local; Drive gets only `output` folders.** Notes, logs, and records are written to `docs/`. The only things written into Drive are the Docs a skill files in a mapped `output` folder: copies of a record (reviewed meeting notes) or deliverables whose home is that folder (client status reports), until the Docs and Sheets connectors are available; then existing files are changed only at their edit level ("Edit levels"), such as a running notes doc that gets a new entry after each reviewed meeting.
- **Nothing is processed without the PM.** A check reports; the PM chooses what to process or skip.
- **Ledger, not timestamps.** "New" means not in `processed`. Never infer that a file was handled from its date.
- **No secrets in snapshots.** If a file contains credentials or keys, don't save a snapshot of it. Tell the PM and work from Drive directly.
- **Say when you can't see something.** If a mapped source can't be opened, report it by key and link. Don't drop it from the map.

## Where

| What | Path |
|---|---|
| Source map and processed list | `docs/sources.yaml` |
| Standard shared drive layout | `layout.yaml` in this skill's folder |
| Validator | `validate.py` in this skill's folder |
| What was built from a file | `cited.py` in this skill's folder (see "Check for new and changed files") |
| Snapshots of transcripts read from Drive (raw; git-ignored by default) | `docs/transcripts/raw/` (the source's `copy_to`) |

If `docs/sources.yaml` doesn't exist (projects installed before this skill), create it with the header comment from `format.md`, `sources: {}`, `not_used: {}`, and `processed: []`.

## Who does what

- **Lucy** owns `docs/sources.yaml` and does the Drive work: mapping the shared drive, checking sources, reading files, saving snapshots, and filing them. She uses the Drive connector whenever the assistant has one.
- **The assistant** briefs Lucy for the start-of-session check (report only; `.ai/general/lobot.md`, "Start-of-session routine"), runs it itself when agents can't run or Lucy can't reach Drive, and relays Lucy's questions to the PM. If Lucy can't reach Drive in this assistant, the assistant reads the files, saves the snapshots, and briefs her with the local paths, Drive IDs, and `modified` values.
- **The PM** says where things live, approves changes to the map, and chooses what gets processed.

When Lucy runs as a subagent she can't talk to the PM mid-run. "Lucy asks" means she returns the question in her report, and the assistant puts it to the PM and briefs her again with the answer.

## Needs

- **The Google Drive connector.** Tool names differ by assistant; the steps below name what each call does. If no Drive connector is available, say so once, skip the Drive steps, and fall back to files the PM drops in `docs/transcripts/raw/`. Never ask the PM to export a file you could read once the connector is set up; tell them which connector would remove that step.
- **Access through the PM's own Google account.** Only what that account can open is visible. A file missing from a check may not be shared with the PM.
- **Reading Docs and Sheets; editing only trackers, never sales documents.** The Drive connector reads files and can create folders, blank files, and new Docs, but it can't edit what is inside a Doc or Sheet. Until the Google Docs and Sheets connectors are available, records stay in the Project Brain (`docs/`). With them, a file is edited only at the edit level its entry gives it (see "Edit levels"); the `contracts` folder (Sales Docs: SOWs, change orders, MSAs, proposals) is `locked` and never edited, whatever the PM asks (`.ai/general/lobot.md`, "Never edit sales documents"). The exception is an `output` folder (see `purpose`): Lucy files new Docs there, either copies of a Project Brain record (the record stays the source of truth) or deliverables whose only home is that folder (see "Where a deliverable lives").

## Format

The full format of `docs/sources.yaml`, with every field, is in `format.md` in this skill's folder. Read it before editing the file, and validate after every edit:

```sh
python3 .ai/general/skills/drive-sources/validate.py docs/sources.yaml
```

## Edit levels

Every Drive file Lobot might change has one of three levels, set by the PM in its entry (or its folder's). They only matter once the assistant has a connector that edits Docs or Sheets; until then nothing is edited in place, and creating folders, blank files, and Docs in `output` folders follows "Rules" below.

| Level | Meaning | Defaults |
|---|---|---|
| `locked` | Never edited, commented on, moved, or replaced, even when the PM asks. Covers everything inside a locked folder, at any depth. | `contracts` (Sales Docs), `meeting-transcripts` |
| `ask` | Each change is proposed with its exact text and made only after the PM approves it. | Trackers: kickoff checklist, maintenance logs, Roster & RACI, and any schedule or other tracker the PM maps |
| `ok` | Changed as its record's skill says, with the change listed in the session report for the PM to review afterward. Best kept for internal files; the validator warns on a client-shared one. | None |

Before editing any Drive file:

1. **Find its level:** its own entry, or else the entry of the mapped folder it sits in (check the file's parents). The strictest level that applies wins.
2. **Sales documents are always `locked`.** An SOW, change order, MSA, proposal, or estimate is locked wherever it lives, mapped or not (`.ai/general/lobot.md`, "Never edit sales documents"). Say so and stop.
3. **`ask` or `ok`:** an edit copies a change already filed in the file's Project Brain record, when it has one, and follows that record's skill.
4. **No level: ask first, then log it.** Treat the file as read-only. Ask the PM whether it may be edited and at which level, then map it ("Add or change a source") with that `edit`, so the question isn't asked again. A file the PM won't open to edits is mapped `edit: locked`.

## Sites and programs

Most projects have one root folder and never declare `scopes`. When a project covers several sites or programs, each with its own root folder in Drive (typically one per SOW), declare them the way the raci skill does and give each its own root:

```yaml
scopes:
  site-a: "Site A"
  site-b: "Site B"
shared_drive:
  site-a:
    url: https://drive.google.com/drive/folders/1AbC...
    added: 2026-10-09
  site-b:
    url: https://drive.google.com/drive/folders/1XyZ...
    added: 2026-10-09
sources:
  contracts@site-a:
    kind: folder
    url: https://drive.google.com/drive/folders/1DeF...
    purpose: reference
    added: 2026-10-09
  meeting-transcripts:              # no @scope: one folder shared by every scope
    kind: folder
    # ...
not_used:
  status-reports@site-b: "Site B gets status in the shared weekly report."
```

- **Scope keys** are short, lowercase, and hyphenated, with a quoted display name. Use the same scope keys as `docs/raci.yaml` when it declares scopes.
- **`<key>@<scope>`** is a source (or `not_used` entry) for that scope only. The part before `@` follows the usual key rules, so `contracts@site-a` is still the standard `contracts` item. A key with no `@scope` covers every scope.
- **Every standard item is accounted for per scope**, by a scoped entry, an unscoped one, or `not_used`. The validator lists `<key>@<scope>` for anything still open.
- `processed` entries name the full source key (`meeting-transcripts@site-a`).

## Map the shared drive

Run this when a project is set up, when `docs/sources.yaml` has no `shared_drive`, when the PM asks to map or tidy the drive, or when the standard layout has items the project hasn't accounted for. Ask before scanning, then follow `mapping.md` in this skill's folder, including its paired sales folder section (always `locked`).

## Check for new and changed files

Run this when the PM asks, during the start-of-session routine (report only; process nothing without the PM), and before a task that relies on a mapped source.

1. Read `docs/sources.yaml`. If it has no sources, skip the check silently.
2. **Folders** (skip `output` folders that have no `handler`): use the Drive connector's search with `parentId = '<folder id>'`, following page tokens until the list is complete. Ask for metadata only (no content snippets). With `subfolders: true`, repeat for each child folder.
   - New: files whose ID is not in `processed`, created on or after `since`. Filter by ID, not by date alone: a transcript moved into the folder late keeps its original created date.
   - Changed: files in `processed` whose current `modifiedTime` is later than the latest `modified` recorded for them.
   - A shortcut (`application/vnd.google-apps.shortcut`) points at another file. Get its metadata to find the target; if the target can't be read, list it as a question for the PM.
3. **Files** (skip `project-journal`: it changes every week and is read when the PJE is drafted): get each file's metadata and compare `modifiedTime` with its latest `processed` entry. A file with no entry has never been read.
4. **Find what each changed file fed.** For every file listed as changed, run:
   ```sh
   python3 .ai/general/skills/drive-sources/cited.py ID [ID ...]
   ```
   It lists what was built from the earlier version (the `result` of each `processed` entry) and every dossier file whose `sources` cite it, directly or through those results or a snapshot of it, with the lines of the facts that cite it. Use the script rather than searching by hand, so every check finds the same things.
5. **Report** in one short list per source: title, date, and why it's listed (new, changed, can't read). Under a changed file, add what `cited.py` found in a line or two (for example "feeds the meeting notes of 2026-10-08 and 6 facts in site A's data.md"), so the PM knows which facts may now be stale. Say nothing else when there's nothing new.

## Process new files

Only after the PM says which files to process.

1. **Read the file** with the Drive connector's read tool. Google Docs come back as Markdown, Sheets as CSV with every tab, Slides as plain text. Read the whole file; for a long transcript, read in chunks rather than summarizing from the first part.
2. **Save a snapshot** when the source has `copy_to`: write the content unchanged to `<copy_to>/YYYY-MM-DD-<slug>.md` (meeting date, slug from the title), with this frontmatter first:
   ```yaml
   ---
   drive_id: 1MnO...
   drive_url: https://docs.google.com/document/d/1MnO.../edit
   title: "Weekly sync - 2026-10-08 - Transcript"
   modified: "2026-10-08T21:14:49Z"
   retrieved: 2026-10-09
   ---
   ```
   The snapshot keeps the Project Brain usable without Drive access (portability rule). Never edit it afterwards; to refresh it, write a new snapshot. A transcript snapshot is raw: it goes in `docs/transcripts/raw/`, which is git-ignored by default, and the cleaned copy the Project Brain commits is made from it (transcript-cleanup skill, which meeting-notes runs first).
3. **Run the handler** skill (e.g. meeting-notes) on the snapshot, then record the file in `processed` with the resulting path as `result`. For a file processed again because it changed, also recheck every fact `cited.py` listed against the new version, and change the ones it no longer supports as the dossier skill's "Add facts" says.
4. **Skipped files:** when the PM says to skip a file, record it with `result: "skipped: <reason>"` so it stops coming up.

For `reference` and `deliverable` sources, read the file when a task needs it and cite it by title and link. When one has changed, recheck the facts `cited.py` lists against the new version with the PM, then record a `processed` entry, so the next check reports only newer edits.

## Mirror a Sheet locally

When a Google Sheet needs a local copy in `docs/` (the kickoff checklist, until the assistant can edit Sheets), follow `mirror-sheet.md` in this skill's folder.

## Add or change a source

1. Get the link from the PM. Confirm the file or folder opens with the Drive connector (metadata only) and note its title and type.
2. If it's a standard layout item, use the layout's key and fields. Otherwise ask what it's for (purpose) and its edit level ("Edit levels"; read-only if the PM doesn't want it edited), and for a transcript folder, which date to start from.
3. Lucy proposes the entry; the PM approves it; Lucy adds it in alphabetical order by key and runs the validator:
   ```sh
   python3 .ai/general/skills/drive-sources/validate.py docs/sources.yaml
   ```
   (Requires PyYAML: `pip install pyyaml`.)
4. **The project journal doc** (the weekly entry for Lullabot leadership, project-journal-entry skill) is mapped as `project-journal`: `kind: file`, `purpose: reference`, and a note that it is internal to Lullabot. It usually lives in Lullabot's own Drive, not the client's: never create it in, copy it to, or link it from the client's shared drive.
5. To stop using a source, delete its entry and leave its `processed` entries; the validator warns about them but keeps them as history.

## Where a deliverable lives

Every deliverable has one home, chosen by the PM. The first time a skill produces a new kind of deliverable on the project, Lucy names Lobot's default home for it and asks whether to override it, following `deliverables.md` in this skill's folder. It is filed there and nowhere else.
