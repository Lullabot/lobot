---
name: jira
description: Guide the PM through setting up and running Jira Cloud — spaces, boards, workflows, work types, sprints, and permissions — using current Atlassian terminology and docs, and read and write work items through Jira's API (search, view, create in bulk, edit, link, move, comment). Use whenever a task involves Jira configuration, auditing or cleaning up a Jira site, creating or copying a space or board, choosing between Jira options, explaining what a Jira screen is asking for, connecting Jira, or reading, creating, updating, or linking Jira work items.
---

# Jira

## Why

Lullabot PMs set Jira up for clients, often without being Jira admins, and Atlassian changes Jira's names and screens often. This skill turns "what is this screen asking me?" into a clear answer and a short list of steps, without trusting outdated knowledge. It also gives the assistant a plain way to read and write work items, so a backlog drafted in the Project Brain doesn't have to be typed into Jira by hand.

## Project config

The site, the reference space to copy from, and this project's conventions live in `.ai/project/jira.md`. Read it before any Jira task. If it doesn't exist, create it as you learn the setup (see "Project file" below) and ask the PM to confirm.

## How to help

1. **Find out what the PM is looking at.** Ask for the screen's title and options, or a screenshot, before giving steps. Don't describe screens from memory.
2. **Check current Atlassian docs** (support.atlassian.com, community.atlassian.com) for anything about menus, labels, or where an option lives. Say when you couldn't confirm a step, so the PM checks it in Jira.
3. **Recommend first, then explain.** Name the option to pick, then why in one or two lines. Point out choices that are hard to undo (space type, shared settings) before the PM makes them.
4. **Record what you learn.** Project facts go in `.ai/project/jira.md`. Lessons that would help on any project go under "Gotchas" here, proposed to Lobot (see the lobot skill).

## Terminology (Jira Cloud, 2025 onward)

Atlassian renamed core concepts in 2025. Older docs, plugins, and APIs still use the old names.

| Now | Was | Notes |
|---|---|---|
| Space | Project | Same thing, renamed to match Confluence. The API and JQL still say `project`. |
| Work item | Issue | |
| Work type | Issue type | Epic, Story, Task, Bug, Subtask, … |
| Company-managed space | Classic project | Settings (workflows, work types, fields) come from shared schemes. Can share settings with other spaces. |
| Team-managed space | Next-gen project | Settings belong to the space alone. Cannot share settings. |

## Choosing a space setup

- **Reusing another space's setup** (workflow, work types, fields) requires a **company-managed** space that shares settings with another **company-managed** space, on a paid plan (Standard or higher). Team-managed spaces can be neither the source nor the target.
- **Template:** Scrum for sprints, backlog, and sprint reports; Kanban for continuous flow with no sprints. When sharing settings, the template mostly decides the starting board; the workflow and work types come from the shared space.
- **When the source is team-managed,** its setup can't be shared. Recreate its work types and statuses by hand in the wizard's configuration step (keep the old space's settings open in another tab), then make the new company-managed space the reference future spaces share from.

## The create-space wizard (seen October 2026)

Jira's wizard changes; compare what the PM sees with this and update it when it differs.

1. **Pick a template** (e.g. Scrum), then **Name your space** (step 1 of 4): name, how the space is managed (company- or team-managed; company-managed is disabled without Jira admin), key, and the chosen template. No option to share settings appeared on this step.
2. **Let's set up your space** (step 2 of 4): a required **Configuration** with three cards, each editable: **Work types** (default Epic, Story, Bug, Task), **Statuses** (default To Do, In Progress, Done), and **Views** (Summary, Timeline, Board, Backlog, Calendar, List, Forms, Development, Docs). A wand icon suggests a configuration and a reset icon restores the defaults. **Start with sample work items** is a toggle; leave it off for real projects.
3. Steps 3 and 4: not yet recorded.

## Matching another space after creation

A company-managed space's settings are a set of separate schemes. Pointing a space at another space's workflow scheme does not change its work types, screens, or fields; each is switched on its own. To make a new company-managed space match another one (useful when the wizard offers no shared-settings option), accept the wizard's defaults, then in **Space settings** switch each scheme to the one the other space uses:

1. **Work types:** *Work items → Types → Actions → Use a different scheme* (Atlassian's docs say *Work types*; the settings menu said *Work items → Types* in October 2026), then pick the other space's work type scheme. Do this first: the workflow and screen schemes are mapped per work type. A space switched in the other order shows the other space's workflow but still has its own work types until this is done.
2. **Workflows:** *Workflows → Switch scheme*, then pick the other space's workflow scheme.
3. **Screens** and **Fields:** switch to the other space's screen scheme and field configuration scheme the same way, so the same fields show up on the same forms.
4. Check **Permissions** and **Notifications**, which are also schemes, and leave them as they are unless the PM wants them matched.

Switching is easiest before the space has work items; afterward, Jira asks how to map existing items' work types and statuses. Every switched scheme is now shared, so a later change to it affects both spaces (see Gotchas).

## How spaces, boards, and sprints relate

- **A space holds work items and settings; a board is a view.** A company-managed board shows whatever its saved filter selects, from any number of spaces, including team-managed ones. Its location (the space it sits under) only decides where it appears in navigation, not what it shows; the filter doesn't even have to include that space.
- **A team-managed board shows only its own space.** To combine spaces on one board, the board must be company-managed.
- **Sprints belong to every board that shows their items.** On company-managed boards, a sprint started on one Scrum board appears on any other Scrum board whose filter includes the same work items. Plan sprints on one board per team; use Kanban boards for views that span teams, since they show status without taking part in sprints.
- **Mixing space types on one board has costs.** A team-managed space's statuses are its own, even when names match, so each must be mapped to a column (and new ones mapped as they appear). The two space types also use different estimate fields, so points from one don't count on a board estimating with the other, and velocity and burndown undercount.
- **For numbers across spaces,** a dashboard built on filters copes with mixed spaces better than board reports. On Jira Premium, Plans (formerly Advanced Roadmaps) roll several spaces into one view, with limits for team-managed spaces.

**Example.** A client has a PLATFORM space for shared work and one space per site built on it (SITEA, SITEB). A Kanban board located in PLATFORM with the filter `project in (SITEA, SITEB) ORDER BY Rank ASC` and one swimlane per site (*Configure board → Swimlanes → Queries*, `project = SITEA`, …) shows all site work without PLATFORM's own items, while each site keeps planning its sprints on its own Scrum board. This shows how the pieces combine; it is not a layout to recommend by default.

## Auditing a Jira site

To clean up or unify a site, document what exists before deciding what to keep. The PM's screenshots of these admin pages (*Settings → Work items* unless noted) cover it, in this order:

1. **Spaces** (*Settings → Spaces*): key, name, type, lead. Team-managed spaces have no schemes and show up nowhere else below.
2. **Workflow schemes:** the **Active** section maps each space to a workflow per work type; the **Inactive** section lists schemes no space uses, which are the easiest to remove.
3. **Workflows:** the **Active** tab shows which spaces and schemes use each workflow and when it last changed; **Inactive** lists workflows no scheme uses.
4. **Each active workflow:** its diagram, for statuses and transitions.
5. **Statuses:** every status, its category, and how many workflows use it.
6. **Work types**, then **Work type schemes**, which shows the spaces using each scheme.
7. Boards and fields, if the cleanup covers them.

**Atlassian's connector (Rovo MCP server, October 2026)** reads what each space uses: spaces, statuses, work types, boards, and a space's full workflows (`getJiraWorkflows`, in the `manage_jira` group, which a Jira admin must turn on). It reads no workflow or work type schemes and nothing unused, so inactive schemes, old copies, and unused statuses still need the admin-page screenshots.

**Record it as a decision workbook**, one tab per entity (spaces, workflow schemes, workflows, statuses, work type schemes, work types) and one grid tab per relationship (users of a thing down the left, the things used across the top, TRUE where one uses the other). The PM sets **Keep**, **Unsure**, or **Removable** on spaces only; every other row suggests its own from the rows that use it (Keep if anything kept uses it, Unsure if only unsure ones do, otherwise Removable), with an Override column and a warning when a Removable item is still used by something kept. Built-in items are always Keep; leave the Default work type scheme's grid row blank so it doesn't keep every type. A status whose Jira usage count is higher than the workflows mapped in the grid stays Unsure until the unmapped workflows are Removable. Build it as an .xlsx with plain formulas (INDEX/MATCH, SUMPRODUCT) so it converts to Google Sheets, and let the PM import it (*File → Save as Google Sheets*, then *Insert → Checkbox* on the grids): uploading through the Drive connector puts the whole file in one call and is slow and fragile.

Things to expect:

- **Scheme names lie.** Schemes named "… Software Simplified Workflow Scheme" ("Generated by Jira Software … managed internally") keep that name after an admin points them at a shared workflow. Go by the workflow they map to, not the name.
- **Copies pile up.** Switching a space's scheme leaves its old one inactive, and Jira saves "Copy of …" schemes from unpublished drafts when a scheme is deactivated. Inactive schemes and workflows with no spaces are usually safe to remove, after the PM confirms.
- **"Unassigned Types"** in a scheme is the workflow for every work type not listed separately.
- **Built-in workflows can't be removed.** Workflows marked **READ-ONLY** with a "Dec 31, 1969" date (e.g. *jira*, the default, and *Builds Workflow*) are Jira system workflows: list them as such and leave them.
- **Backups look like copies.** An inactive "Copy of X" or "Backup of X" with the same date as X's last change is usually a backup someone made before editing X.
- **Statuses are freed last.** The Statuses page counts every workflow that uses a status, inactive ones included, and a status can be deleted only when that count is zero. Remove unused workflows first, then the statuses they leave behind.
- **Check each status's category.** Reports and boards go by category (To Do, In Progress, Done), not by name. A testing or pre-release status in Done counts as finished before it ships; a Blocked status in To Do counts as not started.
- **The Default work type scheme lists every work type.** A type that appears only there isn't used by any space unless a space is on the Default scheme. The Work types page's "Related schemes" also lists unused schemes, so read the Work type schemes page, which shows the spaces using each one, before saying what a space has.
- **Hierarchy level decides what can be a parent.** Epic is 1, standard types 0, subtasks -1. A custom type described as "contains epics" (e.g. Initiative) does nothing as a parent unless it sits at level 2, which needs Jira Premium.

## Copying a board

Boards are not copied with space settings. A board is a saved filter plus its configuration (columns, swimlanes, quick filters, card layout).

1. Open the source board's **⋯ menu → Copy board**.
2. Edit the copy's saved filter so it selects the new space (`project = NEWKEY`), and rename the board and filter.
3. Check the filter's sharing so the team can see it.
4. Remove or rename the board the space template created, so the team has one obvious board.

A copied board keeps its type (Scrum or Kanban). Only company-managed boards can be copied; a team-managed board has no saved filter or board configuration to copy, so match it by hand on the new space's board (columns, estimation, swimlanes, quick filters).

When a space's settings were switched after creation, its template board may show the new statuses as unmapped: map them under *Board settings → Columns* before the team starts using it.

## Gotchas

- **Company-managed spaces need Jira admin.** Creating one requires the "Administer Jira" global permission. Without it, the option is greyed out with no explanation and only team-managed is offered. Request admin rights before starting, or have an admin create the space with shared settings and make the PM a space admin.
- **Team-managed spaces can't be converted.** Moving to company-managed means an admin creates a new space and the work items are bulk-moved into it. Story point estimates don't survive (export keys and estimates to CSV first), sprint history may be lost, work item keys change (old keys redirect), and the old space's fields, board, automation, and reports stay behind. When the goal is only to reuse a team-managed space's setup, recreate its work types and statuses in a company-managed space instead of migrating.
- **Shared settings stay linked.** A later change to a shared workflow or scheme changes every space that uses it. Before editing one, check which spaces share it, and ask the client's Jira owner before changing a scheme other teams use.

## Connecting to Jira

Use the first connection that works. Find out yourself: don't ask the PM which one they have, and don't ask them to run anything.

1. **Atlassian's connector.** If this session has Atlassian's Jira tools, use them for reading and for single approved changes. They sign in as the PM through their browser, with nothing to set up in the folder. Plans still go through `jira.py`, which is what matches field names and values to Jira.
2. **`jira.py`, here.** From the Project Brain root, in the shell on the PM's computer:
   ```sh
   python3 .ai/general/skills/jira/jira.py check
   ```
   Act on its last line, once; don't retry in a loop:

   | It says | Meaning | Next |
   |---|---|---|
   | `jira: ok as <name>` | Connected. | Carry on. |
   | `jira: missing …` | No token in this folder yet. | "Setting up the token" below. |
   | `jira: blocked …` | This shell can't reach Jira. Cowork is blocked until the organization allows the PM's Jira site. | "Using Claude Code" below. |
   | `jira: refused …` | Jira turned the token down. Usually it expired, or the email isn't the PM's Atlassian login. | Check the email in `.env`, then a new token ("Setting up the token", from step 2). |
   | `jira: unreachable …` | The site name is wrong, or the network is down. | Compare `JIRA_SITE` with the address the PM opens Jira at; otherwise try later. |

### Setting up the token

You do everything except the token, which only the PM touches.

1. **Get `.env` ready:**
   ```sh
   python3 .ai/general/skills/jira/jira.py setup --site SITE --email EMAIL
   ```
   Take the site from `.ai/project/jira.md` (or the address the PM opens Jira at, such as `example.atlassian.net`) and the email from the PM's `ids.email` in `docs/people.yaml`; ask only if neither has it. It makes sure `.env` is git-ignored, creates it readable only by the PM, and fills in the site and email. It never reads out or changes a token. If it says `ignore: added`, tell the PM `.gitignore` changed and should be committed. If it says `ignore: STOP`, stop and tell the PM: `.env` was committed, and any token it held must be revoked.
2. **Walk the PM through the token,** in plain words like these:
   1. Open https://id.atlassian.com/manage-profile/security/api-tokens, signed in to Atlassian as yourself.
   2. Choose **Create API token**, the plain one, not the one "with scopes".
   3. Name it after the project (for example "Lobot, Example project"), pick an expiry date a few months away, and choose **Create**. Then choose **Copy**.
   4. In Finder, open the project folder and press **Cmd + Shift + .** (period) to show hidden files. Open `.env` with TextEdit.
   5. Paste the token right after `JIRA_API_TOKEN=`, with no spaces or quotes. Save and close.
   6. Tell me when it's done. Please don't paste the token into our chat.
3. **Check again** with `check`. If the PM pastes the token into the chat anyway, don't use it: ask them to delete that token on the same page and make a new one, since the chat now holds it.

A token reaches everything the PM's account can in Jira, so it belongs to one PM and one project folder. When the PM leaves the project, they delete it on the same page.

### Using Claude Code

When `check` says `blocked`, Jira can't be reached from this session. Keep going with everything that doesn't need Jira (Pepper writes plans from the structure file), and hand the Jira steps to Claude Code, which runs on the PM's own computer and network:

1. Tell the PM what needs Jira and why, in one line.
2. Give them these steps, with the request already filled in:
   1. In the Claude desktop app, choose **Code** at the top, next to Chat and Cowork.
   2. Under the message box, choose **Local**, then the folder button, **Open folder…**, and pick this project's folder.
   3. Type: "_the request_". For example: "Check the Jira connection", "Update the Jira structure for SPACE", or "Validate the Jira plan docs/work/tickets/2026-11-03-search.yaml, ask me about anything it flags, and send it once I approve."
   4. If Claude Code asks before running a command, the Jira ones start with `python3 .ai/general/skills/jira/jira.py`.
3. Claude Code reads the same `.env`, so a token set up once works in both. If `check` there says `missing`, it follows "Setting up the token".
4. Back in this session, pick up from what Claude Code left in the folder: the structure file, and `PLAN.created.json` beside a sent plan.

If the PM would rather stay in Cowork, their organization's admin can allow the Jira site (`*.atlassian.net`) in Claude's admin settings, under Capabilities.

### After connecting

Record the site and spaces in `.ai/project/jira.md`, and each team member's account ID as `ids.jira` in `docs/people.yaml` (look them up with `users`).

## How work gets into Jira

Lucy lays out the work, Pepper turns it into a plan file, and the assistant sends it from wherever Jira can be reached (Claude Code, or Cowork once the site is allowed):

1. **Jira → Pepper.** Where Jira is reachable, `structure SPACE` writes `.ai/project/jira/SPACE.yaml`: the space's work types and levels, each type's required and optional fields under the names people see in Jira, each field's kind and allowed values, statuses, link types, sprints, and open epics. Pepper writes plans from it without needing Jira. Regenerate it before a new batch of work, and whenever the space's setup changes.
2. **Pepper writes the plan.** From the work the PM approved (work-breakdown skill), Pepper drafts a plan file in `docs/work/tickets/YYYY-MM-DD-<slug>.yaml` (format below), following the tickets skill for titles and descriptions. The PM reviews it there.
3. **Validate and settle questions.** `validate` checks the plan against Jira and lists every problem at once, as questions: a field the type doesn't have, a value Jira doesn't allow, a missing required field, a parent at the wrong level, an unknown person or sprint. Answer what you can from the structure file and the records; ask the PM the rest, then fix the plan and validate again.
4. **Approve and send.** The PM approves the final plan and it's stamped; `apply` sends it. A change to a stamped plan needs a new approval.
5. **Record the keys.** `apply` writes `PLAN.created.json` beside the plan (ref → key). Lucy copies the keys into the work items' **Tickets.** and marks them `ticketed`.

## Reading (no approval needed)

```sh
J=".ai/general/skills/jira/jira.py"
python3 $J structure SPACE             # writes .ai/project/jira/SPACE.yaml for Pepper (--out - to print it)
python3 $J spaces                      # key, name, company- or team-managed
python3 $J types SPACE                 # work types and hierarchy level (epic 1, standard 0, subtask -1)
python3 $J fields SPACE TYPE           # one type's fields: name, kind, required, field ID, allowed values
python3 $J link-types                  # how each link type reads ("A blocks B")
python3 $J users "name or email"       # account IDs, for docs/people.yaml
python3 $J search 'project = SPACE AND statusCategory != Done ORDER BY rank' --limit 100
python3 $J view SPACE-123 --comments   # fields, links, children, and the description as markdown
python3 $J transitions SPACE-123       # statuses it can move to now
```

Add `--json` for Jira's raw response, and filter that rather than reading it whole.

## Plan files

A plan is YAML. Name fields exactly as the structure file does (case doesn't matter) and give values the way a person would; the script finds each field's ID and turns the value into what Jira's API expects.

```yaml
destination: Jira, space SPACE          # the human-review stamp: checked by the script, never sent
sources: [docs/work/site/search.md]
status: draft
# approved_by: and approved_at: added on the PM's approval
space: SPACE                            # default for every item
items:
  - ref: search-epic                    # required on new items: a name used only in this plan
    type: Epic
    summary: Event search
    Team: 0f1e2d3c-…                    # a required field from the structure file
    description: |                      # markdown, converted to Jira's format
      ## Description
      …
  - ref: date-filter
    type: Story
    parent: search-epic                 # a ref earlier in the plan, or a key (SPACE-12)
    summary: Add an event date filter to the news listing
    labels: [search]
    assignee: doe-jane                  # people-directory key with ids.jira
    Story point estimate: 3
    Discipline: [Back end, Front end]
    Sprint: Sprint 5
    description: |
      …
    links:
      - is blocked by: date-index       # a link's wording (structure file), then a ref or key
  - key: SPACE-7                        # an existing item: only the fields given change
    labels: [search, phase-2]           # lists replace the whole list; an empty value clears a field
    transition: In Progress             # a status or transition name
    comment: |                          # markdown
      …
```

The plan's own keys are `ref`, `key`, `type`, `space`, `parent`, `links`, `transition`, and `comment`. Every other key is a field. A field can also go under `fields:` (for example, by its ID when two fields share a name; the structure file shows the ID then).

| Kind (structure file) | Write it as |
|---|---|
| text, url | Plain text. Summary is at most 255 characters. |
| long text | Markdown. `@key` becomes a mention for anyone in `docs/people.yaml` with `ids.jira`; checkboxes become Jira action items. |
| number | A number. |
| date, datetime | `2026-11-03`, or `2026-11-03 14:00` (UTC unless an offset is given). |
| option, version | One of the listed values. |
| options, versions, components | A list of listed values, or one comma-separated line. |
| option / child | `Parent / Child`, as listed. |
| person, people | People-directory keys (or a list of them). |
| labels | A list, or one comma-separated line; no spaces inside a label. |
| sprint | An active or future sprint's name, as listed. |
| team | The team's ID from Jira. |
| other | The value as Jira's API expects it, under the field's ID. |

A field that is in Jira but not on the create screen is set right after the item is created; Jira checks that value only then, so `validate` flags it. Hierarchy is checked: an item's parent is one level up (a story under an epic, a subtask under a story or task), and a subtask must have one.

## Sending

```sh
python3 $J validate docs/work/tickets/2026-11-03-search.yaml        # questions, or a summary of what will happen
python3 $J apply docs/work/tickets/2026-11-03-search.yaml --dry-run # every request it would send, sending nothing
python3 $J apply docs/work/tickets/2026-11-03-search.yaml           # creates, updates, then links, moves, and comments
```

- Every write follows "Making changes" below and `.ai/general/human-review.md`. `apply` refuses a plan until it has `approved_by` and `approved_at`; `validate` and `--dry-run` work on any plan.
- `apply` validates first and sends nothing if anything is wrong. Items are created in order; links are made after every item exists, so they can point forward.
- If a run stops partway (Jira refused one item), fix the plan and run it again: what `PLAN.created.json` records is skipped.
- After a link, the script reads it back and warns if Jira shows it the other way round.
- Check the first item of a new kind in Jira, and report anything that renders or maps wrong to Lobot (lobot skill).

Single changes, once approved, don't need a plan file:

```sh
python3 $J link SPACE-3 blocks SPACE-4
python3 $J transition SPACE-3 "In Review"
python3 $J comment SPACE-3 tmp/comment.md     # a draft's frontmatter is left out
```

Each takes `--dry-run`. `python3 $J adf FILE.md --back` shows offline how a markdown file will read in Jira.

## Making changes

Anything the team or client can see is a change: creating or editing spaces, boards, filters, workflows, schemes, permissions, or work items.

1. Say exactly what will change and in which space or board.
2. Wait for the PM's approval, unless their request is itself the instruction.
3. Make it with `jira.py` (above) or, for settings the API doesn't cover, through the browser, and confirm the result with links afterward.

Never delete a space, board, filter, or scheme, or change permissions for anyone but the PM's own team, without the PM explicitly asking for that action.

## Project file

`.ai/project/jira.md` records:

- Site URL and who the client's Jira admins are (by people-directory key, not by name in this file).
- Spaces: name, key, type (company- or team-managed), template, and purpose. When a project has several sites, one space per site, with the site it covers.
- The reference space new spaces copy settings from, and its shared schemes.
- Boards: name, space, type, and saved filter.
- Conventions: work types in use, workflow statuses, sprint length and naming, labels, components.
- Which work types the team uses for what (epics per feature area, stories, tasks), and which fields it fills in. The fields themselves, their kinds and allowed values, are in the generated `.ai/project/jira/<SPACE>.yaml` (`jira.py structure`); don't copy them here.

## Journal

Log Jira changes the PM made with your help (space created, board copied, workflow changed), work items created or changed through `jira.py` (how many, which space, the plan's parent keys, who approved), and anything learned about how the client uses Jira.
