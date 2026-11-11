---
name: jira
description: Guide Jira Cloud setup (spaces, boards, workflows, work types, sprints, permissions, licenses) from current Atlassian docs, and read and write work items through Jira's API. Use for any Jira question, audit, setup, connection, or work item change.
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
4. **Record what you learn.** Project facts go in `.ai/project/jira.md`. Lessons that would help on any project go under "Gotchas" in `setup.md`, proposed to Lobot (see the lobot skill).

## Setup questions

Jira's terms, setting up or copying a space or board, how spaces, boards, and sprints relate, people and licenses, and known gotchas are in `setup.md` in this skill's folder. Read the section the question needs.

## Auditing a Jira site

When the PM asks to audit or clean up a Jira site, follow `audit.md` in this skill's folder.

## Connecting to Jira

Use the first connection that works. Find out yourself: don't ask the PM which one they have, and don't ask them to run anything.

1. **Atlassian's connector.** If this session has Atlassian's Jira tools, use them for reading and for single approved changes. They sign in as the PM through their browser, with nothing to set up in the folder. Ticket plans still go through `jira.py`, which is what matches field names and values to Jira.
2. **`jira.py`, here.** From the Project Brain root, in the shell on the PM's computer:
   ```sh
   python3 .ai/general/skills/jira/jira.py check
   ```
   Act on its last line, once; don't retry in a loop:

   | It says | Meaning | Next |
   |---|---|---|
   | `jira: ok as <name>` | Connected. | Carry on. |
   | `jira: ok …` ending in `but PyYAML missing …` | Connected, but this Python can't read or write YAML, so `structure` and YAML ticket plans won't work. | "PyYAML" in `connecting.md`. |
   | `jira: missing …` | No token in this folder yet. | "Setting up the token" in `connecting.md`. |
   | `jira: blocked …` | This shell can't reach Jira. Cowork is blocked until the organization allows the PM's Jira site. | "Using Claude Code" in `connecting.md`. |
   | `jira: refused …` | Jira turned the token down. Usually it expired, or the email isn't the PM's Atlassian login. | Check the email in `.env`, then a new token ("Setting up the token" in `connecting.md`, from step 2). |
   | `jira: unreachable …` | The site name is wrong, or the network is down. | Compare `JIRA_SITE` with the address the PM opens Jira at; otherwise try later. |

### After connecting

Record the site and spaces in `.ai/project/jira.md`, and each team member's account ID as `ids.jira` in `docs/people.yaml` (look them up with `users`).

## How work gets into Jira

When the project's tracker is Jira (tickets skill, "Which tracker"), Lucy lays out the work, Pepper turns it into a ticket plan, and the assistant sends it from wherever Jira can be reached (Claude Code, or Cowork once the site is allowed):

1. **Jira → Pepper.** Where Jira is reachable, `structure SPACE` writes `.ai/project/jira/SPACE.yaml`: the space's work types and levels, each type's required and optional fields under the names people see in Jira, each field's kind and allowed values, statuses, link types, sprints, and open epics. Pepper drafts ticket plans from it without needing Jira. Regenerate it before a new batch of work, and whenever the space's setup changes.
2. **Pepper drafts the ticket plan.** From the work the PM approved (work-breakdown skill), Pepper drafts a ticket plan in `docs/work/tickets/YYYY-MM-DD-<slug>.yaml` (tickets skill, "Ticket plans"; Jira's part below). The PM reviews it there.
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
python3 $J sprint SPACE                # active sprint: dates, days left, unfinished items that are blocked or stale (--stale DAYS, default 7)
```

Add `--json` for Jira's raw response, and filter that rather than reading it whole.

## Ticket plans in Jira

Pepper drafts tickets as a ticket plan (tickets skill, "Ticket plans"), with `tracker: jira` and the space key as `project`. For Jira:

- `type` is one of the space's work types, and `key` is a work item key (`ABC-12`).
- Under `fields:`, name fields exactly as the structure file does (case doesn't matter) and give values the way a person would. The script finds each field's ID and turns the value into what Jira's API expects. When two fields share a name, the structure file shows the field's ID; use that instead.
- `parent` must be one level up: a story or task under an epic, a subtask under a story or task. A subtask must have one.
- `status` is a status or transition name from the work type's workflow; `blocks` and `blocked_by` use Jira's Blocks link; any other link goes under `links:` in the structure file's wording (`- relates to: ABC-9`).
- An empty value on an existing item clears that field.

| Kind (structure file) | Write it as |
|---|---|
| text, url | Plain text. A title is at most 255 characters. |
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

A field that is in Jira but not on the create screen is set right after the item is created; Jira checks that value only then, so `validate` flags it.

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

Single changes, once approved, don't need a ticket plan:

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
