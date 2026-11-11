# Mirror a Sheet locally

Part of the drive-sources skill (`SKILL.md`).

## Mirror a Sheet locally

Until the assistant can edit Sheets, a deliverable Sheet that tracks work (the kickoff checklist) gets a local mirror at its `record` path. The assistant keeps the mirror current as work happens; the PM copies the changes into the Sheet. With scopes, each scope gets its own mirror: add `-<scope>` before the extension (`docs/kickoff-checklist-site-a.md`).

1. **Create the mirror.** Read the Sheet and copy the tracking tab into a Markdown table, with this frontmatter:
   ```yaml
   ---
   drive_url: https://docs.google.com/spreadsheets/d/1QrS.../edit
   title: "EXU Kickoff tasks"
   tab: "New Project Checklist"
   modified: "2026-10-09T19:43:26Z"   # Sheet modifiedTime when last synced
   synced: 2026-10-09
   ---
   ```
   Columns: `Row | Task | Status | Notes`. `Row` is the Sheet's row number, so the PM can find it. Copy each task word for word, using the Sheet's own status values. Copy only the tracking tab; read reference tabs (agendas, examples) in Drive when needed.
   **A tracker page, where the assistant can publish one.** Offer the tracker-pages skill's `checklist.html` page per mirror: the rows with a status picker and a note field, plus a "to copy into the Sheet" queue of rows whose status differs from the Sheet's, with a "Copied" button. Seed it from the Sheet; it stores per row `row`, `task`, `status`, `sheetStatus` (what the Sheet says), and `note`. The PM works in the page; the assistant reads it back and rewrites the mirror file from it whenever it touches the checklist and at session close, because the page lives in one person's account and the mirror keeps the Project Brain portable. Put the page's link in the mirror's frontmatter as `tracker:`.
2. **Update it as work happens.** Change a row's Status and add a short note with the evidence (a file, a meeting, a link). Never reword, add, or remove tasks; those are the PM's edits in the Sheet. A task the PM rules out gets the status `Not applicable` until the PM deletes it from the Sheet.
3. **Hand changes back.** When asked, or when rows have changed since `synced`, list each change as `Row 9: Not started → Done (note)` for the PM to apply.
4. **Resync.** When the PM says the Sheet is updated, or the check shows it changed, read it again and rewrite the mirror from it. The Sheet wins; a row the mirror changed that the Sheet doesn't reflect yet is listed as a question, not overwritten silently. Update `modified` and `synced`, and record a `processed` entry for the Sheet.
5. **Retire it** once the assistant can edit Sheets: from then on, changes go straight into the Sheet with the PM's approval, and the mirror is deleted.
