---
name: work-breakdown
description: Lay out the work a project will build, by site and feature area, before any of it becomes tickets. Lucy keeps the breakdown in structured Markdown in docs/work/, from the dossier, meetings, and email, and proposes changes as new material arrives. Use when the PM asks to define, break down, scope, or plan the work, asks what's planned or ready for a site, or when a transcript, email, or document describes something the team will build or changes something already planned.
---

# Work breakdown

## Why

The dossier says what is true about a site; the task list says who owes what. Neither says what the team will build. The work breakdown does: the work worked out in plain language, with its sources, before anyone writes a ticket, so tickets come from a reviewed plan rather than from memory.

Turning ready items into tickets is not settled yet (see "Not settled yet"). This skill covers laying out the work and keeping it current.

## Files

| Path | What it is |
|---|---|
| `docs/work/<site>/index.md` | The site's areas at a glance: one row per area with its file, its items, item counts by status, and a one-line summary. |
| `docs/work/<site>/<area>.md` | One feature area (a group of related work) and its items. |
| `docs/work/shared/` | Work several sites share (hosting, sign-in, platform setup, theme, launch). Same layout. |

`<site>` is the dossier's site folder name (`docs/overview/sites/<site>/`); a single-site project uses one folder named for the project. `<area>` is a short lowercase slug. Lucy keeps these files; the PM reviews them.

## Areas

Organize each site by feature area, the way the client and the team talk about the site: a search tool, a content section, a data feed, the migration. The first time, Lucy proposes the areas for each site and the shared ones from the dossier and asks the PM to confirm them before writing any items. Add, merge, or rename areas with the PM's approval.

## Area file

```markdown
---
title: "<Site>: <Area>"
area: <area slug>
updated: YYYY-MM-DD
status: draft (Lucy, YYYY-MM-DD)
sources:
  dossier: docs/overview/sites/<site>/
  walkthrough: docs/meetings/YYYY-MM-DD-<slug>.md
---
# <Area>

Two or three sentences: what this area is for and who it serves. Link the dossier topic it comes from rather than repeating it.

### W-001: <Short title, a deliverable>

`status: draft · scope: <scope> · milestone: <milestone> · discipline: <back end, front end, design, content, strategy, QA>`

**Goal.** Who needs this and why, in one or two sentences.

**Included.**
- What the work covers, concretely.

**Acceptance notes.**
- Rough, testable outcomes. They become acceptance criteria when the item is ticketed.

**Open questions.**
- What's unknown, with Q-### when it's in the questions log.

**Depends on.** W-###, R-###, D-###, T-### (or "none").

**Sources.** Short keys from the frontmatter with timestamps or sections (`walkthrough 00:12:34`), emails by sender, subject, and date.

**Tickets.** Ticket keys, once they exist.
```

- **IDs** are `W-###`, one sequence for the whole project, never reused. When an item is split, it keeps its ID for one part and the other takes the next number.
- **Meta line:** `scope` is a scope key from the project's records (`all` for shared work); `milestone` names the contract or schedule milestone the work belongs to; `discipline` lists who does it.
- **Leave out empty sections**, except Sources, which every item has.
- **One item is one deliverable** someone could demo. Smaller pieces are for the tickets.
- **Inferences are marked** *(unverified)*. Work no source asked for is never added: propose it to the PM as an `idea` with the reason.
- **Scope check.** If an item isn't in the contract or a client request, say so in its Open questions so it's settled before it's ticketed.

## Statuses

| Status | Means | Set by |
|---|---|---|
| `idea` | Named; little detail yet. | Lucy |
| `draft` | Outlined; open questions may remain. | Lucy |
| `ready` | The PM approved it to become tickets. | The PM only |
| `ticketed` | Its tickets exist; the ticket system is now the source of truth and the item keeps only their keys. | Lucy, once the keys are known |

## Keeping it current

- **First pass from the records.** Lucy builds it from the dossier (content, data, migration, design, plan topics), meeting notes, decisions, questions, and risks, after the PM confirms the areas.
- **As material arrives.** When a transcript, email, or document describes something to build or changes an item, Lucy proposes the new or changed items with that material's other proposals (in a meeting's review list, as kind `Work breakdown`). Facts still go to the dossier first; items link to them rather than repeating them.
- **Exact changes.** A proposal names the items and says what changes in each (a line added to Included, an open question, a new item in full), so the PM approves exactly what will be written.
- **Index stays current.** Every change to an area file updates that site's `index.md` counts and summary.
- **Review in small batches**, area by area. Only the PM moves an item to `ready`.

## Not settled yet

Still being worked out in real use. Don't treat these as rules yet:

- How items become tickets. For now: Pepper drafts a ticket plan from `ready` items (tickets skill, "Ticket plans") for the tracker the PM chose, and the item's **Tickets.** gets the keys from the plan's `PLAN.created.json` once it's sent. Still open: which issue types items map to (an epic per area, a story per item, tasks below), and how many tickets one item usually becomes.
- An import file (such as CSV) for ticket systems without a connector, and its columns.
- How much detail an item needs before a PM is willing to mark it `ready`.

Note what worked and what didn't in the journal with the tag `#work-breakdown`, so this skill can be refined from it.

## Validate

`python3 .ai/general/skills/work-breakdown/validate.py` checks every area file in `docs/work/`: item IDs unique across the project, a meta line with a known status and a scope, Sources on every item, and keys on every `ticketed` item. Run it after every change.
