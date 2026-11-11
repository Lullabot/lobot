# docs/sources.yaml format

Part of the drive-sources skill (`SKILL.md`). The full format of `docs/sources.yaml`. Read it before editing the file, and validate after every edit: `python3 .ai/general/skills/drive-sources/validate.py docs/sources.yaml`.

## Format

```yaml
# Drive sources: the project's shared drive, the folders and files it uses, and what has been processed.
# Managed by the drive-sources skill: .ai/general/skills/drive-sources/SKILL.md
# Validate after every edit: python3 .ai/general/skills/drive-sources/validate.py docs/sources.yaml
shared_drive:
  url: https://drive.google.com/drive/folders/0AbC...
  added: 2026-10-09
sources:
  contracts:
    kind: folder                       # folder | file
    url: https://drive.google.com/drive/folders/1DeF...
    purpose: reference                 # transcripts | reference | deliverable | output
    edit: locked                       # locked | ask | ok; none = read-only (see "Edit levels")
    added: 2026-10-09
    notes: "Signed SOW and change orders. Read before scope questions."
  meeting-transcripts:
    kind: folder
    url: https://drive.google.com/drive/folders/1AbC...
    purpose: transcripts
    handler: meeting-notes             # skill that processes new files
    copy_to: docs/transcripts/raw/     # save a snapshot here before handing it on
    edit: locked
    since: 2026-10-01                  # ignore files created before this date
    subfolders: false                  # also check folders inside it
    added: 2026-10-09
  status-reports:
    kind: folder
    url: https://drive.google.com/drive/folders/1GhI...
    purpose: output
    filed_by: client-status-report     # the skill that files its deliverables here; no copy in docs/
    added: 2026-10-16
  maintenance-logs:
    kind: file
    url: https://docs.google.com/spreadsheets/d/1QrS.../edit
    purpose: deliverable
    record: [docs/risks.yaml, docs/decisions.yaml, docs/questions.yaml]   # the Project Brain records it corresponds to
    tabs: ["Risks", "Decisions", "Questions"]                            # one tab per record, same order
    holds_record: true                 # optional: the Sheet is the record, the files are empty (.ai/general/records-in-sheets.md)
    edit: ask
    shared_with_client: false
    added: 2026-10-09
not_used:
  contracts: "Contracts stay in Lullabot's own Drive."   # standard items this project doesn't have, and why
processed:
  - id: 1MnO...                        # Drive file ID
    title: "Weekly sync - 2026-10-08 - Transcript"
    source: meeting-transcripts
    modified: "2026-10-08T21:14:49Z"   # Drive modifiedTime when it was handled
    processed: 2026-10-09
    result: docs/meetings/2026-10-08-weekly-sync.md
```

Field rules:

- **`shared_drive`** is the project's shared drive (or top-level project folder). Set it once; the map and the drive survey start from it. A project with several sites or programs, each with its own root folder, gives one per scope (see "Sites and programs").
- **Keys** for anything in the standard layout use the layout's key (`meeting-transcripts`, not `transcripts-folder`), so every project names the same thing the same way. Other keys are short, lowercase, and hyphenated, named for what the source is, not where it lives.
- **`url`** is the link from Drive's address bar or Share button. The ID is read from it; don't store it separately.
- **`purpose`**:
  - `transcripts`: a folder of meeting transcripts. Needs `handler: meeting-notes`.
  - `reference`: material to read and cite (SOW, specs, client docs). Changes are reported, not processed. Not edited unless its `edit` level allows.
  - `deliverable`: a Doc or Sheet the team or client works from that corresponds to a Project Brain record (`record`; a workbook holding several records lists them, with the tab for each in `tabs`): the RACI matrix, schedule, team directory, risk tracker, decision log, kickoff checklist, a running notes doc for recurring meetings (`record: docs/meetings/`; meeting-notes skill, "Recurring meetings"), or another tracker the PM designates. Mapped trackers default to `edit: ask`. The Project Brain file stays the record of truth, and the Doc or Sheet is checked for client edits so the PM can reconcile them, unless the source has `holds_record: true`: then the Sheet is the record for every record it lists and those files are empty (`.ai/general/records-in-sheets.md`). Once the Docs and Sheets connectors are available, an approved change is filed in the record first, then copied into the Doc or Sheet.
  - `output`: a folder Lucy files new Docs in. Either shareable copies of Project Brain records, one Doc per record (`record` is the `docs/` folder they come from, e.g. `docs/meetings/` for the meeting-notes folder), or deliverables that live only in Drive (`filed_by` names the skill that writes them, e.g. `client-status-report` for the status-reports folder; no `record`, because nothing is kept in `docs/`). The skill that owns the record says when to file a copy, and the record file notes its copy's link. Every copy of a record Lucy files is recorded in `processed` (its `result` is the record it was copied from), so her own copies never come up as new. Checks skip an output folder unless it also has a `handler`: some PMs drop Google Meet's Gemini notes straight into the Meeting Notes folder, so that folder then also takes `handler: meeting-notes`, `copy_to`, and `since`, like a transcripts folder.
- **`edit`** is how far the assistant may change the file or, for a folder, everything in it: `locked`, `ask`, or `ok` (see "Edit levels"). Leave it off and the source is read-only until the PM sets one. Standard items take the layout's default; the PM can change `ask` and `ok` either way, but the validator refuses to loosen a layout item that is `locked`.
- **`since`** keeps the first check from turning up years of old transcripts. Set it to the date the PM wants to start from.
- **`not_used`** lists standard layout items the PM said this project doesn't have, with the reason, so they stop coming up.
- **`processed`** holds one entry per file handled, in the order handled. `result` is the file it became (`docs/meetings/...`), or `skipped: <reason>` when the PM chose not to process it. A file edited after it was handled gets a new entry with the new `modified` when it is handled again.
