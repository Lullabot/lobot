# Connecting to Jira: details

Part of the jira skill (`SKILL.md`, "Connecting to Jira"). Read the section that `jira.py check` sent you to.

## Contents

- PyYAML
- Setting up the token
- Using Claude Code

## PyYAML

`jira.py` needs nothing beyond Python's standard library, except PyYAML for ticket plans, `docs/people.yaml`, and the structure file. The `pyyaml:` line of `check` says whether the Python running it has PyYAML. When it doesn't and the Project Brain has its own virtualenv (`.venv/` or `venv/`), `jira.py` reruns itself with that Python, so the commands in this skill work as written.

When `check` still says PyYAML is missing:

1. Install it for the PM's user, in the shell on their computer: `python3 -m pip install --user pyyaml`. Tell the PM in a line what you installed and why.
2. If pip refuses (an "externally managed" Python, as Homebrew's is), don't force it: no `--break-system-packages`, no `sudo`. Tell the PM that `jira.py` needs PyYAML and that this Python won't take packages, and ask whether to use another Python they have, or to make a virtualenv for the project in `.venv/` (add `.venv/` to the Project Brain's `.gitignore` first, and tell the PM to commit that change).
3. Run `check` again.

## Setting up the token

You do everything except the token, which only the PM touches.

1. **Get `.env` ready:**
   ```sh
   python3 .ai/general/skills/jira/jira.py setup --site SITE --email EMAIL
   ```
   Take the site from `.ai/project/jira.md` (or the address the PM opens Jira at, such as `example.atlassian.net`) and the email from the PM's `ids.email` in `docs/people.yaml`; ask only if neither has it. It makes sure `.env` is git-ignored, creates it readable only by the PM, and fills in the site and email. It never reads out or changes a token. If it says `ignore: added`, tell the PM `.gitignore` changed and should be committed. If it says `ignore: STOP`, stop and tell the PM: `.env` was committed, and any token it held must be revoked.
2. **Walk the PM through the token,** one step at a time as the guided-setup skill describes (it has the Windows steps for `.env`), in plain words like these:
   1. Open https://id.atlassian.com/manage-profile/security/api-tokens, signed in to Atlassian as yourself.
   2. Choose **Create API token**, the plain one, not the one "with scopes".
   3. Name it after the project (for example "Lobot, Example project"), pick an expiry date a few months away, and choose **Create**. Then choose **Copy**.
   4. In Finder, open the project folder and press **Cmd + Shift + .** (period) to show hidden files. Open `.env` with TextEdit.
   5. Paste the token right after `JIRA_API_TOKEN=`, with no spaces or quotes. Save and close.
   6. Tell me when it's done. Please don't paste the token into our chat.
3. **Check again** with `check`. If the PM pastes the token into the chat anyway, don't use it: ask them to delete that token on the same page and make a new one, since the chat now holds it.

A token reaches everything the PM's account can in Jira, so it belongs to one PM and one project folder. When the PM leaves the project, they delete it on the same page.

## Using Claude Code

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
