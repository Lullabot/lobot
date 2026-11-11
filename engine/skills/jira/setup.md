# Jira setup reference

Part of the jira skill (`SKILL.md`). Read the section a question needs: Jira's terms, choosing and creating a space, boards and sprints, copying a board, people and licenses, and known gotchas. Check Atlassian's current docs before describing a screen.

## Contents

- Terminology (Jira Cloud, 2025 onward)
- Choosing a space setup
- The create-space wizard (seen October 2026)
- Matching another space after creation
- How spaces, boards, and sprints relate
- Copying a board
- People and licenses (checked October 2026)
- Gotchas

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

## Copying a board

Boards are not copied with space settings. A board is a saved filter plus its configuration (columns, swimlanes, quick filters, card layout).

1. Open the source board's **⋯ menu → Copy board**.
2. Edit the copy's saved filter so it selects the new space (`project = NEWKEY`), and rename the board and filter.
3. Check the filter's sharing so the team can see it.
4. Remove or rename the board the space template created, so the team has one obvious board.

A copied board keeps its type (Scrum or Kanban). Only company-managed boards can be copied; a team-managed board has no saved filter or board configuration to copy, so match it by hand on the new space's board (columns, estimation, swimlanes, quick filters).

When a space's settings were switched after creation, its template board may show the new statuses as unmapped: map them under *Board settings → Columns* before the team starts using it.

## People and licenses (checked October 2026)

PMs ask who Jira bills for when people join or leave a project. Answer from Atlassian's current docs and the site's own billing page, not from memory: prices and rules change.

- **Access is what's billed, not use.** On monthly plans, everyone with access to Jira counts, including people who were invited and never accepted or logged in. A new person costs money from the moment they're given access, so add people when they start, not "just in case".
- **Suspended and removed users aren't billed.** In Atlassian Administration (*Directory → Users*, or *Users* on older sites, then *••• → Suspend access* or *Remove user*). Suspending keeps the person's roles and groups for when access is restored; removing drops them, and they must be invited again. Either way their work items, comments, and history stay in Jira.
- **Suspend when someone may come back** (a contractor between phases, someone on leave); remove when they're gone for good.
- **Check the count after a change.** A suspended person who still appears in the user count probably still has access through a synced directory (an identity provider such as Okta or Google). They have to be removed there too, or the sync gives their access back.
- **The PM usually can't do this.** It takes an organization admin or user access admin. Give the client's admin the list of people and the action for each (suspend or remove), and record what was done in the journal.

## Gotchas

- **Company-managed spaces need Jira admin.** Creating one requires the "Administer Jira" global permission. Without it, the option is greyed out with no explanation and only team-managed is offered. Request admin rights before starting, or have an admin create the space with shared settings and make the PM a space admin.
- **Team-managed spaces can't be converted.** Moving to company-managed means an admin creates a new space and the work items are bulk-moved into it. Story point estimates don't survive (export keys and estimates to CSV first), sprint history may be lost, work item keys change (old keys redirect), and the old space's fields, board, automation, and reports stay behind. When the goal is only to reuse a team-managed space's setup, recreate its work types and statuses in a company-managed space instead of migrating.
- **Shared settings stay linked.** A later change to a shared workflow or scheme changes every space that uses it. Before editing one, check which spaces share it, and ask the client's Jira owner before changing a scheme other teams use.
