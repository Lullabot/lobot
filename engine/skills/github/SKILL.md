---
name: github
description: Work with the project's GitHub repo and GitHub Projects through the gh CLI — read and update issues, PRs, and project boards. Use whenever a task involves GitHub issues, pull requests, project status, sprint/board reporting, or GitHub usernames.
---

# GitHub

## Why

Lullabot projects track work in GitHub issues and GitHub Projects. `gh` gives the assistant the same view the team has, from both Claude Code and Cowork, with one set of commands.

## Project config

Repo, project board numbers, and field/option IDs for **this** project live in `.ai/project/github.md`. Read it before any GitHub task. If it doesn't exist, create it (see "Discovering a project's setup" below) and ask the PM to confirm.

## Setup (every shell)

Run this at the start of **every** shell command that uses `gh` (each Cowork shell call is a fresh process):

```sh
source .ai/general/skills/github/gh-env.sh
```

In Cowork, run `gh` in the shell on the PM's computer (the one with the Project Brain folder mounted), from the Project Brain root. Not the cloud workspace's shell: it has its own `gh` with an unrelated `GH_TOKEN`, it can't see the PM's `.env`, and its proxy blocks the GraphQL API that `gh project` commands use. If `gh` reports "command not found" or a bad token, first check you're in the right shell and sourced this script.

Source it directly in the same shell that runs `gh`. Don't pipe it (`source … | sed`) or wrap it in `( … )`: that runs it in a subshell, and `PATH` and `GH_TOKEN` are lost (symptom: `gh: command not found`). Don't fall back to `gh auth login` or a device-code login; if the script can't authenticate, report why.

It works for both tools:

| Tool | Auth | What the script does |
|---|---|---|
| Claude Code on the PM's machine | PM's own `gh auth login` (token in OS keychain) | Nothing; uses the installed, logged-in `gh`. |
| Cowork / cloud sandbox | Personal access token in the Project Brain's gitignored `.env` (`GH_TOKEN=`) | Installs `gh` into `~/.local/gh` if missing, loads `GH_TOKEN` from `.env`. |

Token: classic PAT, scopes `repo`, `project`, `read:org`, SSO-authorized for the org, short expiry. See `.env.example`.

Check with `gh auth status`. If it fails, or `gh` isn't installed, follow "Connecting GitHub" below rather than retrying.

## Connecting GitHub

Use this when the PM asks to set up or connect GitHub, or when the check above fails. Run from the Project Brain root:

```sh
bash .ai/general/skills/github/gh-setup.sh
```

It's safe to run again. It makes sure `.env` is git-ignored (adding it to `.gitignore` if not), installs `gh` if missing, and checks the login. Without a login, it creates `.env` from `.env.example` with owner-only permissions. It never prints the token. Act on its output:

- **`ignore: added …`**: tell the PM `.gitignore` changed and should be committed.
- **`ignore: STOP …`**: `.env` is tracked by git. Stop and tell the PM; any token it ever held must be revoked.
- **`token: missing`**: walk the PM through creating a token, then run the script again once they say it's in:
  1. Open https://github.com/settings/tokens/new (Settings → Developer settings → Personal access tokens → Tokens (classic)).
  2. Name it for the project and tool (for example "Lobot, Cowork"), set a short expiration, and tick the `repo`, `project`, and `read:org` scopes.
  3. Generate it. If the org uses SSO, choose **Configure SSO** next to the token and authorize it for the org.
  4. Open `.env` at the top of the Project Brain folder (in Finder, Cmd+Shift+. shows hidden files) and paste the token right after `GH_TOKEN=`, with no quotes or spaces. Save.
  5. Tell the assistant it's done. Never paste the token into the chat.
- **`auth: failed …`**: name the likely cause from the message and stop; don't retry in a loop.
- **`auth: ok as <login>`**: confirm with a read-only call on the project's repo (`gh issue list -R OWNER/REPO --limit 1`). If `.ai/project/github.md` is missing, continue with "Discovering a project's setup".

If the PM pastes a token into the chat anyway, don't use it: it's now in the conversation history. Ask them to revoke it and make a new one.

## Token safety

- Never print, echo, log, or copy the token. Never run `gh auth token`.
- If command output could contain it, redact `gh[pousr]_…` before showing it.
- Never write the token anywhere except the PM's own `.env`.

## Reading (no approval needed)

```sh
gh issue list -R OWNER/REPO --state open --limit 50
gh issue view 123 -R OWNER/REPO --comments
gh pr list -R OWNER/REPO --state open
gh pr view 456 -R OWNER/REPO
gh project item-list N --owner ORG --limit 500 --format json   # default limit is 30
gh project field-list N --owner ORG --format json
```

- Use `--format json` / `--json` with `-q` (jq) to filter rather than reading full dumps.
- For board summaries (counts by status, what's in progress, what's stale), pull `item-list` JSON once and aggregate it.
- Cite issues and PRs as `#123` with links when reporting to the PM.

## Writing (approval required)

Anything the team or client can see is a write: creating, editing, commenting on, labeling, assigning, or closing issues/PRs; adding items to a project; changing a project field (status, priority, dates).

1. Show the PM exactly what will change (issue, field, old → new, or the full comment text).
2. Wait for explicit approval, unless the PM's request is itself the instruction ("move #612 to Done").
3. Make the change, then confirm with a link.

Creating an issue under an epic, on a board:

```sh
gh issue create -R OWNER/REPO --type Task --title "…" --body-file body.md   # prints the URL
gh api -X POST repos/OWNER/REPO/issues/EPIC/sub_issues -F sub_issue_id="$(gh api repos/OWNER/REPO/issues/N --jq .id)"
gh api -X POST repos/OWNER/REPO/issues/N/dependencies/blocked_by -F issue_id="$(gh api repos/OWNER/REPO/issues/BLOCKER --jq .id)"
gh project item-add BOARD --owner ORG --url ISSUE_URL
```

Sub-issue and dependency calls take the issue's numeric `id`, not its number.

Setting project fields needs IDs from `.ai/project/github.md`:

```sh
gh project item-edit --project-id PROJECT_NODE_ID --id ITEM_ID \
  --field-id FIELD_ID --single-select-option-id OPTION_ID
```

Never: merge PRs, push code, create/delete branches, change repo or project settings, or delete anything. Those are for the dev team.

One exception: the adr skill (`.ai/general/skills/adr/SKILL.md`) adds an ADR file on its own branch and opens a draft pull request for it, with the PM's approval. It touches nothing else in the repo and never merges.

## People

GitHub usernames for assignees, reviewers, and @mentions come from the people directory (people skill), `ids.github`. Never guess a username. When a new username surfaces for an existing person, add it there.

## Journal

Log meaningful GitHub changes the assistant made (status moves, issues created) and anything learned about how the team uses the board.

## Discovering a project's setup

When `.ai/project/github.md` is missing or stale:

```sh
gh api graphql -f query='{repository(owner:"ORG",name:"REPO"){projectsV2(first:10){nodes{number title url closed}}}}'
gh project view N --owner ORG --format json
gh project field-list N --owner ORG --format json
```

Also check for org-level issue fields. These are set on the issue itself, not on a board, and an org may use them instead of a board's own Priority field:

```sh
gh api orgs/ORG/issue-fields --jq '.[] | {id, name, data_type, options: [.options[]? | {id, name}]}'
gh api repos/OWNER/REPO/issues/N --jq .issue_field_values   # what an issue has set
```

Set one with the option's name (not its ID):

```sh
echo '{"issue_field_values":[{"field_id":FIELD_ID,"value":"Medium"}]}' \
  | gh api -X POST repos/OWNER/REPO/issues/N/issue-field-values --input -
```

Record the repo, each board (number, title, purpose, URL, node ID), the Status/Priority/Size fields with option IDs, and any org issue fields with option IDs. When a board and the org both have a field with the same name (Priority is common), look at recent issues to see which one the team fills in, and note in `.ai/project/github.md` which one to use.

## Handoff

When a PM rolls off: delete their `.env` token line and revoke the token in GitHub settings. The next PM follows `README.md` setup with their own token.
