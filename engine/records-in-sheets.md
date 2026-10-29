# Records that live in Google Sheets

A record (the risk tracker, decision log, or questions log) normally lives in its `docs/` file, and tracker pages or Sheets show copies of it. When the assistant can edit Google Sheets, the PM can move a record into Sheets instead, so each item lives in one place. This file says how that works. It overrides what a skill says about reading and writing the record's file.

## When a record lives in Sheets

`docs/sources.yaml` maps the Sheet that holds it as a `deliverable` with `holds_record: true`: usually the standard Maintenance Logs workbook, which holds all three records in a Risks, a Decisions, and a Questions tab (`record` lists the files, `tabs` names the tab for each), or a project's own Sheet for one record (`record` set to the file). A project with several sites has one per site, or one for the project. `holds_record` applies to every record the Sheet lists. Then:

- **The Sheets are the record.** The `docs/` file holds no entries, only a header pointing to the Sheets. It stays, so validators and links keep working, and so the record can move back if the Sheets connector goes away.
- **Wherever a skill says to read or write that file, use its Sheets.** Read every Sheet that holds the record (`get_values` on the whole tab, the record's tab in a workbook). Write rows with the Sheets connector.
- **Column mapping.** Each Sheet's columns map to the record's fields. The mapping is project-specific and lives in the root `CLAUDE.md` "Project rules". Fields with no column of their own get one, to the right of the template's columns; nothing is dropped.
- **IDs** stay `R-###`, `D-###`, `Q-###`, unique across every Sheet that holds the record and across its archive. Before adding an item, take the highest ID in all of them and add one. Never reuse an ID.
- **Sites.** An item for one site goes in that site's Sheet. A project-wide item (`all`, or a decision that applies to every site) goes in every site's Sheet, as identical rows: change all of them in the same pass.
- **Approvals don't change.** The record's own skill still says what is autonomous and what the PM approves (questions are added autonomously; new risks and decisions are proposals). The Sheet's `edit` level covers changing existing rows. Never delete a row; close, answer, or deprecate it.
- **Checks.** There is no validator for a Sheet. After writing, read the rows back and check them against the skill's field rules (required fields, allowed statuses, dates).
- **Edits by others.** People edit the Sheets directly. Read before writing, and never overwrite a cell someone changed since your last read without asking the PM.

## Review desk and tracker pages

The review desk keeps the record's tabs, with no items, and shows a link to each Sheet that holds it (tracker-pages skill, "Review desk"). Record pages for that record (risks, decisions, questions pages) are retired.

## Moving a record into Sheets

1. Reconcile: every entry in the file is in its Sheet(s), field for field, with any missing columns added. Fix gaps before going further.
2. Archive the file's entries: copy the file to `docs/archive/<record>-<date>.yaml`.
3. Empty the file: keep only a header naming the Sheets and this file.
4. Set `holds_record: true` on each Sheet's source (it then covers every record that Sheet lists, so move them all at once), and record the mapping in the root `CLAUDE.md`.
5. Clear the record's collections on the review desk and set the Sheet links (tracker-pages skill).
6. Journal it.

## Moving a record back

If the Sheets connector is no longer available: export each Sheet, rebuild the file from the rows (using the mapping), run the validator, remove `holds_record`, and reseed the pages. The Sheets go back to being copies.
