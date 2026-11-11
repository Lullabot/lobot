# Where a deliverable lives

Part of the drive-sources skill (`SKILL.md`).

## Where a deliverable lives

Everything the assistant produces has one home, and the PM chooses it. Lobot has a default home for each kind of deliverable (a folder in the standard layout, or a path in `docs/` from "Where things go" in `.ai/general/context-docs.md`), and the PM can choose another. Lucy settles it the first time a skill produces that kind of deliverable on the project (for example, the first client status report), and whenever the PM asks to move one.

1. **Say the default.** Name the deliverable, Lobot's default home for it, and why, in one or two lines: "Status reports go in a *Status reports* folder inside Project Management in the shared drive, one Doc per week. That folder is their only copy; last week's report is read from there."
2. **Ask about an override.** "Use that, or put them somewhere else?" The PM can point to an existing folder, have Lucy create the default (at her autonomy level for Drive changes), or say the project doesn't produce it (`not_used`, with the reason).
3. **Record it** in `docs/sources.yaml` under the layout key, with the scope when the project has scopes, and run the validator. A home in Drive for a deliverable kept only there is an `output` folder with `filed_by`. If the item was mapped before with an older purpose (the validator warns), update it now with the PM's approval.
4. **Keep to it.** From then on the skill files that deliverable there and nowhere else: no second copy in `docs/`, and no copy in Drive of something whose home is `docs/` unless the PM asked for one (as with meeting notes). If the PM moves the home later, Lucy updates the entry; files already filed stay where they are unless the PM moves them.
