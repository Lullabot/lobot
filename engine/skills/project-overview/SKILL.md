---
name: project-overview
description: Publish and keep current the project overview page, the PM's one place to see how the project is set up and where everything lives - project name and short name, the Project Brain and code repositories, the ticket tracker, the project's library (its records and folders in the Project Brain, in Google Drive, and on this computer), tracker pages, connections, the agents, and what isn't set up yet - each with a link to where it lives. Use when the PM asks whether something is set up or where something is ("is the Jira space set?", "where are the transcripts?", "what's our repo?"), asks for the project's setup or overview, at the end of project setup, and whenever something the page shows changes.
---

# Project overview

## Why

A PM asking "is that set?" or "where is this?" shouldn't need to know which file holds the answer, or open a terminal to find out. The setup is spread across the root `CLAUDE.md`, `docs/sources.yaml`, `.ai/project/`, git, and `.env`. The overview page, an HTML page published as a Claude artifact (never a local server), gathers it on one screen, with a link to each thing rather than its address, and lists what isn't set up yet with what to say to set it up.

## Where

| What | Where |
|---|---|
| What the page shows | `python3 .ai/general/skills/project-overview/overview.py --out tmp/overview.json`, from the Project Brain root. It reads local files only. |
| Page template | `templates/overview.html` in this skill's folder |
| The page's link | The root `CLAUDE.md` "This project" table, row "Project overview" |

The script reports `.env` values only as set or not set (and the GitHub token's expiry date), never a token. Don't add values to its output by hand.

## Publish or update the page

1. **Gather.** Run `overview.py --out tmp/overview.json`. Use the script rather than reading the files yourself, so every run shows the same things.
2. **Fill the template.** Copy `templates/overview.html` to `tmp/overview.html`, replace `{{PROJECT_NAME}}` with the project's name and `{{OVERVIEW_JSON}}` with the file's contents, unchanged. Check the script parses (`node --check` on the extracted script).
3. **Publish** `tmp/overview.html` as an HTML page artifact (in Claude, the Artifact tool), with no capabilities: the page is read-only and holds no database. If the assistant can't publish artifacts, answer from `overview.py` in chat and say the page needs Claude. The first time, publish it as a new page and add a "Project overview" row with its link to the root `CLAUDE.md` "This project" table. After that, republish to the same page, so the link stays the same.
4. **Check it** once after publishing: the gaps match the script's `gaps`, and the links open.

The page is the PM's own: its connections section describes the computer it was gathered on. Don't suggest sharing it.

## Answer "is that set?" and "where is this?"

1. Run `overview.py` (no `--out`) and answer from it in a line, with the link: "Yes: tickets go to Jira, space EXS ([open it](...))." or "Not yet. Say 'Map the project's Google Drive' and Lucy will do it."
2. If the answer differs from the published page, update the page (above), then open it.
3. Otherwise open the page when the PM wants the whole picture ("show me the project setup").

If a question is about something the page doesn't show, answer from the file that holds it, and say where that is.

## Keep it current

Update the page in the same pass whenever something it shows changes: project setup finishes, the code repository is recorded, the tracker is chosen, Lucy maps or changes a Drive source, a tracker page is published, a connection is set up, a record moves to Google Sheets, or an agent is added or set up for the project.

## Rules

- **Links, not addresses.** Every item links to where it lives; the page never asks the PM to copy a URL.
- **Read-only.** Changes go through the chat and the skill that owns each setting (project-setup, drive-sources, tickets, jira, github, tasks, the agents' config). The page reflects them afterward.
- **No secrets.** Tokens, emails, and other `.env` values never reach the page, its JSON, or the chat.
