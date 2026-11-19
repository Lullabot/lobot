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

## Dated updates

A record whose entries carry dated updates (the risk tracker's `updates`) keeps them on their own **Updates** tab, right after the record's tab, one row per update: `ID | Date | Update | Source`, oldest first within each item, Source blank when there isn't one. A long history in one cell is hard to read in a Sheet, and the Sheet may be shared with the client. The record's tab shows the updates through three formulas, each written once in row 2 so it fills the column; never type in those columns:

- **Last updated:** the newest update's date, or the date identified when there are none.
  `=MAP(A2:A, I2:I, LAMBDA(id, d, IF(id="", "", IFERROR(MAX(FILTER(Updates!B2:B, Updates!A2:A=id)), d))))`
- **Latest update:** the newest update as `<date>: <note>` (ties go to the row lower down).
  `=MAP(A2:A, LAMBDA(id, IF(id="", "", IFERROR(LET(f, SORT(FILTER({Updates!B2:B, Updates!C2:C}, Updates!A2:A=id), 1, TRUE), TEXT(INDEX(f, ROWS(f), 1), "m/d/yyyy")&": "&INDEX(f, ROWS(f), 2)), ""))))`
- **Update history:** a link to the Updates tab with the count. `<gid>` is the Updates tab's `sheetId`.
  `=MAP(A2:A, LAMBDA(id, IF(id="", "", LET(n, COUNTIF(Updates!A2:A, id), IF(n=0, "No updates", HYPERLINK("#gid=<gid>", n&IF(n=1, " update", " updates")))))))`

The letters are the standard Risk Log's (A is the ID, I the date identified); the project's mapping in the root `CLAUDE.md` says where its columns sit. To add an update, add a row at the bottom of the Updates tab; never write update text on the record's tab. A project-wide item's updates go in every site's Sheet. A link can't filter a tab, so readers filter the Updates tab's ID column to see one item's history.

## Moving updates onto an Updates tab

A workbook made before the Updates tab keeps every update in one cell, one per line as `<date>: <note> (Source: ...)`. When the PM approves the move (it changes a Sheet the client may see), do this in each Sheet that holds the record:

1. Read the record's tab and count each item's update lines.
2. Add the Updates tab right after it: headers ID, Date, Update, Source; frozen header row; the workbook's banding and header style; wrapped text; the record tab's date format on Date; and a filter.
3. Fill it with a formula, never by retyping. In A2, with O as the old updates column:
   `=ARRAYFORMULA(LET(L, FLATTEN(IFERROR(Risks!A2:A&"¦"&SPLIT(Risks!O2:O, CHAR(10), FALSE, TRUE))), X, FILTER(L, REGEXMATCH(L, "^R-\d+¦\d{4}-\d{2}-\d{2}: ")), HSTACK(REGEXEXTRACT(X, "^(R-\d+)¦"), DATEVALUE(REGEXEXTRACT(X, "¦(\d{4}-\d{2}-\d{2}): ")), REGEXEXTRACT(X, "¦\d{4}-\d{2}-\d{2}: (.*?)(?: \(Source: .*\))?$"), IFERROR(REGEXEXTRACT(X, " \(Source: (.*)\)$"), ""))))`
4. Check the result against step 1: the same number of rows and the same dates for each item, sources split off, and Source blank where an update had none. A line that doesn't start with a date is left out, so fix it in the old cell first.
5. Paste the tab over itself as values (a `copyPaste` with `PASTE_VALUES`), so it no longer depends on the old column.
6. On the record's tab, clear the old updates column and the Last updated values below the header. Rename the old column Latest update and add Update history next to it with the same format. Write the three formulas, and widen Latest update.
7. Read both tabs back: Last updated matches its old values, each item's count matches, and nothing shows an error.
8. Update the column mapping in the root `CLAUDE.md`, mention the Updates tab in the Sheet's `notes` in `docs/sources.yaml` (`tabs` still lists one tab per record), and journal it.

## Review desk and tracker pages

The review desk keeps the record's tabs, with no items, and shows a link to each Sheet that holds it (tracker-pages skill, "Review desk"). Record pages for that record (risks, decisions, questions pages) are retired.

## Moving a record into Sheets

1. Reconcile: every entry in the file is in its Sheet(s), field for field, with any missing columns added., and each dated update a row on the Updates tab ("Dated updates"). Fix gaps before going further.
2. Archive the file's entries: copy the file to `docs/archive/<record>-<date>.yaml`.
3. Empty the file: keep only a header naming the Sheets and this file.
4. Set `holds_record: true` on each Sheet's source (it then covers every record that Sheet lists, so move them all at once), and record the mapping in the root `CLAUDE.md`.
5. Clear the record's collections on the review desk and set the Sheet links (tracker-pages skill).
6. Journal it.

## Moving a record back

If the Sheets connector is no longer available: export each Sheet, rebuild the file from the rows (using the mapping, with each item's updates from the Updates tab), run the validator, remove `holds_record`, and reseed the pages. The Sheets go back to being copies.
