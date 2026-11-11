---
name: project-overview
description: 'Publish and keep current the project overview page: how the project is set up and where everything lives, with links and what isn''t set up yet. Use for "is that set up?", "where is X?", "what''s our repo?", and when the setup changes.'
---

# Project overview

## Why

A PM asking "is that set?" or "where is this?" shouldn't need to know which file holds the answer, or open a terminal to find out. The setup is spread across the root `CLAUDE.md`, `docs/sources.yaml`, `.ai/project/`, git, and `.env`. The overview page, an HTML page published as a Claude artifact (never a local server), gathers it on one screen, with a link to each thing rather than its address, and lists what isn't set up yet with what to say to set it up.

## Where

| What | Where |
|---|---|
| What the page shows | `python3 .ai/general/skills/project-overview/overview.py --out tmp/overview.json`, from the Project Brain root. It reads local files only. |
| Page template | `templates/overview.html` in this skill's folder |
| The page's link | The root `CLAUDE.md` "This project" table, one row per PM: "Project overview (<PM's name>)" |

The script reports `.env` values only as set or not set (and the GitHub token's expiry date), never a token. Don't add values to its output by hand.

## Publish or update the page

1. **Gather.** Run `overview.py --out tmp/overview.json`. Use the script rather than reading the files yourself, so every run shows the same things.
2. **Fill the template.** Copy `templates/overview.html` to `tmp/overview.html`, replace `{{PROJECT_NAME}}` with the project's display name (`project.name` in the JSON) and `{{OVERVIEW_JSON}}` with the file's contents exactly as the script wrote them (it escapes `<`, so text from the records can't break the page). Check the script parses (`node --check` on the extracted script).
3. **Publish** `tmp/overview.html` as an HTML page artifact (in Claude, the Artifact tool), with no capabilities: the page is read-only and holds no database. If the assistant can't publish artifacts, answer from `overview.py` in chat and say the page needs Claude. Each PM has their own page, because it shows what they can do and only they can update it. If the root `CLAUDE.md` "This project" table has no "Project overview (<PM's name>)" row for this PM, publish a new page and add that row with its link; otherwise republish to the page that row links to, so the link stays the same. Never republish another PM's page.
4. **Check it** once after publishing: the gaps match the script's `gaps`, and the links open.

The page is the PM's own: its connections section describes the computer it was gathered on. Don't suggest sharing it.

## Answer "is that set?" and "where is this?"

1. Run `overview.py` (no `--out`) and answer from it in a line, with the link: "Yes: tickets go to Jira, space EXS ([open it](...))." or "Not yet. Say 'Map the project's Google Drive' and Lucy will do it."
2. When the PM wants the whole picture ("show me the project setup"), update the page (above) first, then open it, so it shows the setup as it is now.

If a question is about something the page doesn't show, answer from the file that holds it, and say where that is.

## Keep it current

Update the page in the same pass whenever something it shows changes: project setup finishes, the code repository is recorded, the tracker is chosen, Lucy maps or changes a Drive source, a tracker page is published, a connection is set up, a record moves to Google Sheets, or an agent is added or set up for the project.

## Rules

- **Links, not addresses.** Every item links to where it lives; the page never asks the PM to copy a URL.
- **Read-only.** Changes go through the chat and the skill that owns each setting (project-setup, drive-sources, tickets, jira, github, tasks, the agents' config). The page reflects them afterward.
- **No secrets.** Tokens, emails, and other `.env` values never reach the page, its JSON, or the chat.
