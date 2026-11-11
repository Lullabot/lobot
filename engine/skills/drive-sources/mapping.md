# Mapping the shared drive

Part of the drive-sources skill (`SKILL.md`). Steps for mapping a project's shared drive against the standard layout (`layout.yaml`), and for its paired sales folder. The skill's rules apply throughout, starting with: ask before scanning.

## Map the shared drive

Run this when a project is set up, when `docs/sources.yaml` has no `shared_drive`, when the PM asks to map or tidy the drive, or when the standard layout has items the project hasn't accounted for (not in `sources` and not in `not_used`). The goal is a complete map that matches the standard layout.

1. **Ask before scanning.** Never scan the drive without the PM's go-ahead. Lucy offers once, briefly: what she'll look at (the top level of the shared drive, names and types only, nothing inside the files) and what she'll come back with. If the PM hasn't given the shared drive's link, ask for it.
2. **If the PM says yes, scan the top level** of the shared drive, or of each scope's root. Search for files whose parent is the root's ID, metadata only (no content snippets), following page tokens until the list is complete. Shared drives are usually small; if the top level has more than about 50 items, report the count and ask which folders to look in. Look one level deeper only into a folder the PM points to, or one that matches a layout folder other items name as their `parent` (e.g. Project Management), or whose name matches a layout item's `look_for`.
3. **Match it against `layout.yaml`.** For each standard item not yet in `sources` or `not_used`, compare names, case-insensitively, against its `name` and `look_for`, and check that the kind matches (folder or file). An item with a `parent` is expected there (`root` is the top level); a match somewhere else is still a match, but say where it is. Then report back in three short lists:
   - **Likely matches to confirm:** "Is *Meet Recordings* the meeting-transcripts folder?"
   - **Missing:** standard items with no match. The contracts folder is never created; it is the paired sales folder (below). For each other item, offer to create it with the layout's `name`, with `<KEY>` replaced by the project key from the root `CLAUDE.md` (a folder, or a blank Doc or Sheet per `file_type`) in its `parent` (at the root for `root`, inside the parent folder otherwise, creating that first if it's missing too; at the root when there is no `parent`), to record where it actually lives if it's elsewhere, or to mark it not used.
   - **Unrecognized:** top-level items that match nothing. Ask whether any should be mapped, and what each is for.
4. **If the PM says no to the scan, ask instead.** List the standard items not yet accounted for, with each one's `why`, and ask where each lives (a link), whether it should be created, or whether the project doesn't use it. Record what the PM answers; ask about the rest another time rather than repeating the whole list.
5. **Record the answers.** Lucy writes the entries (keys and fields from `layout.yaml`, plus `added`, with `@<scope>` when the project has scopes), the `shared_drive` link (or each scope's) if it's new, and any `not_used` reasons, then runs the validator. For a transcript folder, ask which date to start from (`since`).

## The paired sales folder

Most projects have two folders in Drive: the **sales folder**, where the Sales team keeps the SOWs, change orders, estimates, and pricing, and the **project folder** (the shared drive or project root mapped here), where the production team works. The sales folder usually lives elsewhere (often a Clients folder for the client) and is linked into the project folder's top level with a shortcut. It is the project's `contracts` source.

- **Finding it.** When mapping the drive, check the top level for shortcuts and read each one's target. A shortcut to a folder holding SOWs or change orders, or one named like the `contracts` item, is the sales folder: map the target folder (not the shortcut) as `contracts`, and note where it lives.
- **When there's no shortcut,** ask the PM for the sales folder's link rather than creating a Contracts folder. Once it's mapped, ask the PM to add a shortcut to it from the project folder's top level (in Drive: right-click the sales folder, Organize, Add shortcut), since the Drive connector can't create shortcuts.
- **Everything in it is locked** (`.ai/general/lobot.md`, "Never edit sales documents"), including estimates and pricing models. Those are internal to Lullabot: read them for hours and budget, and never quote them in anything the client sees.
- A project with no separate sales folder (contracts kept in the project folder, or not shared with the PM) maps whatever holds the SOWs, or records why in `not_used`.
