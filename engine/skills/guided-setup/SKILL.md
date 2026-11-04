---
name: guided-setup
description: Walk a PM who isn't technical through setup they have to do themselves, one step at a time - a GitHub or Jira token, finding and editing the hidden .env file, and connecting the project folder or their ~/.lobot profile folder to the session - on a Mac or Windows. Use when a task can't go ahead because access is missing (no GitHub login or token, Jira token missing or refused, an agent reports it can't reach the tracker, ~/.lobot can't be read), when the project overview lists something to set up, and when the PM asks how to set one of these up.
---

# Guided setup

## Why

Some setup only the PM can do: a token is theirs alone, and a folder is connected from their own computer. Most PMs don't live in a terminal, and "paste it into `.env`" means nothing to someone who has never seen a hidden file. When access is missing, the PM shouldn't hit a dead end ("Pepper can't reach GitHub") and have to work out the fix alone. The assistant names what's missing, offers to help, and walks them through it one step at a time.

The click-by-click steps for each token stay in their own skills (github, project-setup, jira). This skill is how to walk a PM through them, plus the steps those skills leave out: hidden files, editing `.env`, and connecting folders.

## Offer, don't stop

When a task can't go ahead because something isn't set up, say so in one line, say what setting it up would make possible, and offer to walk the PM through it:

> I can't reach GitHub from here yet, so I can't create that ticket. Setting it up takes about five minutes and lets me create and update tickets for you from now on. Want me to walk you through it?

| What you see | What's missing | Walkthrough |
|---|---|---|
| github skill's `gh-setup.sh` says `token: missing`, `brain-state.sh` says `no-login`, or Pepper reports she has no GitHub tools | A GitHub token | "GitHub token" |
| `gh-setup.sh` says `auth: failed …` | A working token: expired, missing a scope, or not authorized for the org | "GitHub token", after naming the likely cause |
| `jira.py check` says `missing` or `refused` | A Jira token | "Jira token" |
| The pm-profile skill can't read `~/.lobot/` | The profile folder connected to the session (or created) | "Connect a folder" |
| The project folder isn't in the session | The project folder connected | "Connect a folder" |
| The project overview lists one of these under what isn't set up | That item | The matching walkthrough |

- **When an agent reports missing access,** the assistant makes the offer: agents can't talk to the PM mid-run (`.ai/general/delegation.md`). Keep the agent's other results; once access works, rerun only the part that needed it.
- **Offer once per thing per session.** If the PM says not now, carry on with what can be done without it (Pepper can still draft a ticket plan) and say what's waiting.
- **Fix what's yours first.** Anything that is a command (`gh-setup.sh`, `jira.py setup`, creating `.env`, checking `.gitignore`) the assistant runs before the walkthrough starts. The PM only does what needs them: their browser, their accounts, their own computer's windows.

## How to walk someone through it

1. **Set it up in one message.** What we're doing, why, roughly how long, and what they'll need ("a browser where you're signed in to GitHub").
2. **Know their computer.** Work it out from the project folder's path (`/Users/…` is a Mac, `C:\…` is Windows) and give only that computer's steps. Ask only if you can't tell.
3. **One step per message, then wait.** Each step says what to do, with the exact words on the button or menu in **bold**, and what they should see after. Wait for "done" before the next. Two small steps can share a message if they happen on the same screen.
4. **Plain words.** Explain a term the first time it comes up, in a sentence, and not again. The terms most walkthroughs need:
   - **Token:** a password made for one tool. You can set it to expire, and cancel it without changing your real password.
   - **`.env`:** a small text file in the project folder that holds your tokens. It stays on your computer and is never saved to GitHub.
   - **Hidden file:** a file whose name starts with a dot. A Mac hides these unless you ask to see them.
   - **Scope** or **permission:** what a token is allowed to do.
   - **SSO:** your organization's sign-in. A token has to be approved for it before it works on the organization's repositories.
5. **Never ask for the token.** It goes from the website straight into `.env`, and never into the chat, a screenshot, or an email. If the PM pastes it into the chat anyway, don't use it; walk them through cancelling it and making a new one.
6. **Check it worked.** Run the check (`gh-setup.sh`, `jira.py check`, reading the folder) and say what it means in plain words: "GitHub knows it's you." Then go back to the task that was waiting.
7. **When they're stuck,** ask what they see on the screen. A screenshot helps, as long as the token isn't on it. If the screen doesn't match the steps, believe the PM: the website may have changed. Check the vendor's current help pages and adjust, and offer to report the out-of-date step to Lobot (lobot-feedback skill).
8. **Let them stop.** If they need to stop (an admin has to approve something, they ran out of time), say where you left off and what's left, and pick it up next time it comes up. Nothing secret goes in the notes.

## Walkthroughs

### Find and edit `.env`

Most token walkthroughs end here. Before you start, make sure `.env` exists (the github skill's `gh-setup.sh` or the jira skill's `jira.py setup` creates it) and tell the PM the name of the folder it's in.

**Mac**

1. Open the project folder in Finder.
2. Press **Cmd + Shift + .** (period). Files whose names start with a dot appear, slightly faded. Pressing it again hides them.
3. Right-click (or Control-click) `.env` and choose **Open With**, then **TextEdit**. If TextEdit isn't in the list, choose **Other…** and pick it from Applications. Don't double-click: the Mac may open it in an app that doesn't let you type.
4. Put the cursor right after the `=` on the line named in the walkthrough (`GH_TOKEN=`, `JIRA_API_TOKEN=`) and paste with **Cmd + V**. No spaces, quotes, or new lines around it.
5. Save with **Cmd + S** and close the window. If TextEdit asks about the file type or offers to add `.txt`, choose to keep `.env` as it is.

**Windows**

1. Open the project folder in File Explorer. Windows shows `.env` already: it only hides files marked hidden, not names that start with a dot.
2. Turn on file name extensions, so a stray `.txt` would show: Windows 11, **View**, **Show**, **File name extensions**; Windows 10, the **View** tab, tick **File name extensions**.
3. Right-click `.env` and choose **Open with**, then **Notepad** (on Windows 11 it may be under **Show more options** or **Choose another app**).
4. Paste with **Ctrl + V** right after the `=`, with no spaces or quotes.
5. Save with **Ctrl + S**, not Save As. If the file now shows as `.env.txt`, rename it back to `.env` and confirm the warning.

Then check it yourself: the file is still called `.env`, and its line has a value (read whether the line is filled, never the value).

### GitHub token

1. Run the github skill's `gh-setup.sh` first, and act on anything it says about `.gitignore`.
2. Decide which token. Use the classic token in the github skill's "Connecting GitHub" unless the organization blocks classic tokens or the PM prefers a fine-grained one; then use "A fine-grained token for one repository" in the project-setup skill. Don't make the PM choose: tell them which one and why, in a sentence.
3. Walk them through that skill's steps, one per message, with these additions:
   - **Signing in.** If GitHub asks them to confirm their password or a code first, that's expected.
   - **The name and expiry.** Suggest both. Explain that a short expiry is safer, and that you'll remind them before it runs out.
   - **Copy it now.** GitHub shows the token once. If they leave the page before copying it, make a new one; that's fine.
   - **SSO.** With a classic token, the **Configure SSO** step is what lets it reach the organization's repositories. Easy to miss, so ask them to do it before leaving the page.
   - **Waiting for approval.** A fine-grained token may say it's pending: an organization owner has to approve it. Use the project-setup skill's draft for the request, and stop there for now.
4. "Find and edit `.env`" to paste it after `GH_TOKEN=`, and the expiry date after `GH_TOKEN_EXPIRES=` (as `YYYY-MM-DD`).
5. Run `gh-setup.sh` again. `auth: ok as <login>` means it worked; say so, then go back to the waiting task. If it says `auth: failed`, the github skill names the cause; the usual ones are a missed SSO step, a missing scope, or a stray space in `.env`.

### Jira token

1. Run `jira.py setup` as the jira skill's "Setting up the token" says. It fills in the site and email, so the PM only adds the token.
2. Walk them through the token steps in that section, one per message. Its step for opening `.env` is the Mac one; on Windows, use "Find and edit `.env`" above.
3. Run `jira.py check`. If it says `blocked`, the token is fine but this session can't reach Jira: follow the jira skill's "Using Claude Code".

### Connect a folder

The session can only see folders the PM has connected. Two come up: the project folder, and the personal profile folder `~/.lobot` in their home folder (pm-profile skill).

If the assistant can ask for access to a folder itself (Cowork can, for a folder that already exists), do that: the PM only approves the prompt on their computer. Otherwise, walk them through it:

**Claude Cowork, Mac**

1. In the Claude desktop app, in this task, choose **Add folder**.
2. The project folder: find it the usual way and choose **Open**.
3. `~/.lobot`: in the window that opens, press **Cmd + Shift + G**, type `~/.lobot`, and press **Return**, then choose **Open**. (It's a hidden folder, so it doesn't show up by browsing. **Cmd + Shift + .** shows hidden folders in this window too.)
4. If the window says the folder doesn't exist, the PM hasn't saved a profile yet. Finder won't make a folder whose name starts with a dot, so have Claude Code make it: in the Claude desktop app, choose **Code** at the top, then **Local** under the message box, open the project folder, and type "Create the folder ~/.lobot". Then come back to this task and connect it as in step 3.

**Claude Cowork, Windows**

1. In the Claude desktop app, in this task, choose **Add folder**.
2. The project folder: find it the usual way and choose **Select Folder**.
3. `~/.lobot`: click the address bar at the top of the window, type `%USERPROFILE%\.lobot`, press **Enter**, then choose **Select Folder**.
4. If it doesn't exist: type `%USERPROFILE%` in the address bar instead, choose **New folder**, and name it `.lobot`. If Windows refuses the name (older versions of Windows 10 do), type `.lobot.` with a dot at the end, and Windows keeps `.lobot`. Then select it.

**Claude Code** sees the project folder it was opened in. For `~/.lobot`, it asks each time it reads outside the project; to stop it asking, offer to add `~/.lobot` to `permissions.additionalDirectories` in `~/.claude/settings.json` for the PM, with their approval of the change. Create `~/.lobot` with a command if it doesn't exist; Claude Code can.

Then check: list the folder. For `~/.lobot`, carry on with the pm-profile skill (a new folder is empty, so it offers to start the profile).

## Hard limits

- Never ask for, read out, print, or copy a token, and never have the PM paste one anywhere but their own `.env`.
- Never ask the PM to open a terminal or run a command. Commands are the assistant's job.
- Never change a security or organization setting for the PM, or tell them to turn off a protection (SSO, an approval, a firewall rule) to get past a step. If the organization says no, use the project-setup skill's access ladder.
- Never walk a PM through giving a token more access than the task needs.
