---
name: project-setup
description: Choose where the Project Brain is kept (a private GitHub repository, or a folder in the project's Lullabot shared drive that Drive backs up) and keep the PM connected to it. Sets up the shared-drive home or moves a Project Brain there, creates the private repository for a new project, attaches one to a folder that has none, helps a PM join a project that already has one, and works out what to do when GitHub access is blocked. Use when the PM starts a project, says "set up the repo", "put this on GitHub", "back up the Project Brain", "join" or "take over" a project, "keep it in the shared drive", when the Project Brain has no git repository or no remote, when it sits in a synced folder, or when creating, pulling, or pushing the repository fails with a permission, token, or approval error.
---

# Project setup

## Why

A Project Brain only works as a handoff if the next PM can get all of it: kept current, backed up, and reachable without knowing git. It lives in one of two places, both owned by Lullabot: the project's shared drive, synced by Google Drive for desktop, or a private repository in the org. This skill does that work in plain language. When GitHub says no, it finds the next route instead of stopping.

The Project Brain holds transcripts and a people directory, which is client data. It lives in the project's Lullabot shared drive or a private repository in the org, never in a personal account or on another service, whatever the obstacle.

## Where

Run everything from the Project Brain root, in the same shell as `gh` (in Cowork, the shell on the PM's computer). Source `.ai/general/skills/github/gh-env.sh` first, and follow the github skill's "Token safety" and "Before the first git command in a session" (delete permission, commit identity).

| What | Where |
|---|---|
| Where this Project Brain stands | `bash .ai/general/skills/project-setup/brain-state.sh` (changes nothing) |
| The repository, and anything left to do | "Project Brain repository" in `.ai/project/github.md` |
| Org and repository name | Org `Lullabot`, wherever the code lives. The name is the code repository's name plus `-pm`: code in `Lullabot/example-site` (or a client's org) gives `Lullabot/example-site-pm`. Only if the project truly has no code repository, use the project key in lowercase plus `-pm` (`exu-pm`). If the PM names another, use theirs. |
| When the PM's token expires | `GH_TOKEN_EXPIRES=YYYY-MM-DD` in the PM's token file, beside the token. It's the PM's own, so it stays out of git and Drive with them. |

## Choose a home

A Project Brain lives in one of two homes. Ask the PM once, when the project starts or when `brain-state.sh` says `no-git`, and recommend the shared drive when the project has one:

| Home | Backup and history | Handoff | Needs |
|---|---|---|---|
| **The project's shared drive** | Drive saves every change as it happens and keeps earlier versions of each file for a while (Google's help says 30 days); deleted files go to the shared drive's trash | The next PM is given access to the shared drive | Google Drive for desktop. No git, no GitHub repository, no token for saving |
| **A private GitHub repository** | Every save is a commit, kept for good | The next PM is given access to the repository | Git, `gh`, and a GitHub token (the rest of this skill) |

The shared drive is simpler; GitHub keeps a full history and works without Drive for desktop. GitHub Projects and ADRs need a GitHub token either way.

## Keep it in the shared drive

The shared drive must be the project's own, in Lullabot's Google Workspace, and no one outside Lullabot may be able to open it: everything in the Project Brain syncs, raw transcripts and the people directory included, with no `.gitignore` to leave anything out. If the client or a contractor outside Lullabot has access to the drive, or the project has no shared drive, use GitHub instead. Never a PM's own My Drive, a personal account, or another sync service.

**Set it up** (a new project, or `state: no-git` with the PM choosing the shared drive):

1. **Find the folder.** The project's folder in the shared drive, as Google Drive for desktop shows it on the PM's computer (on a Mac, under `~/Library/CloudStorage/GoogleDrive-<email>/Shared drives/`). The Project Brain is a folder inside it named `.<key>-lobot` in lowercase (`.exu-lobot`), so it sits beside the project's other folders without crowding them.
2. **Say what you'll do and wait for a yes**: "I'll keep the Project Brain in the EXU shared drive, at `.exu-lobot`. Drive will back it up, so there's no GitHub repository. Everyone who can open the drive can read it. OK?"
3. **Put it there.** Install Lobot into that folder (lobot skill), or have the PM move an existing Project Brain folder there in Finder or File Explorer. In Cowork, the PM connects the new folder to the session.
4. **Make it available offline** so scripts read it at full speed: in Finder or File Explorer, right-click the folder, choose **Google Drive** (or **Offline access**), then **Available offline**.
5. **Point `drive` at the shared drive:** `ln -sfn .. drive` from the Project Brain root. Relative, so it works on every PM's computer.
6. **Record it** in `.ai/project/brain-home.md` (see "Record it"). Scripts read this file to keep tokens out of the synced folder, since the folder's path doesn't show it's a shared drive in every tool.
7. **Check tokens.** Run `brain-state.sh`: `state: shared-drive` means it's set. If it shows `env-warning:`, act on it as the github skill's "Connecting GitHub" says. The PM's tokens live in `~/.lobot/<key>.env` from now on (github skill, "The PM's token file").
8. Publish or update the project overview (project-overview skill).

**Moving from GitHub to the shared drive** (`state: shared-drive-git`, or the PM asks):

1. Save first: commit and push everything as the github skill says, so GitHub holds the last version.
2. The PM moves the folder into the shared drive (step 3 above), then steps 4 to 7.
3. Offer to remove the Project Brain's `.git` folder. Drive can damage a git repository it syncs, and with the folder in Drive git isn't needed. It needs the PM's approval and, in Cowork, delete permission on the folder. Never touch `repo/`, the code repository's own clone.
4. The GitHub repository stays as it is, as an archive. Archiving or deleting it is the PM's decision, made in GitHub; Lobot never changes repository settings.
5. Update "Project Brain repository" in `.ai/project/github.md` to say it's archived and where the Project Brain lives now, and log the move in the journal.

**Working in it:**

- **One PM at a time.** Drive syncs files, not changes: two people editing the same file at once leaves conflict copies. When two PMs share a project, agree who keeps the Project Brain, or check for duplicate files (`name (1).md`) at the start of a session and ask before merging them.
- **Nothing to commit.** Skip every commit, pull, and push step in other skills (Lobot's "Save the Project Brain" rule). "Keeping it saved" doesn't apply.
- **Links.** Drive for desktop may not sync links (`drive`, `.claude/skills/`) to other computers. If they're missing, recreate them: `ln -sfn .. drive`, and `npx --yes github:Lullabot/lobot link` for the skills.
- **Undoing a change.** In Drive on the web, right-click a file, **File information**, **Manage versions** (for files that aren't Google Docs), or restore it from the shared drive's trash.

## Find out where things stand

Run `brain-state.sh` and read it. Its `home:` line says where the folder is (`shared-drive`, `synced`, or `local`) and `env-file:` where the PM's tokens are read from. Look things up; don't ask the PM what the script can tell you. Its last line, `state:`, picks the next step:

| `state:` | Meaning | Next |
|---|---|---|
| `no-git` | The folder isn't under version control | "Choose a home", then the shared-drive setup or "Create the repository" |
| `no-remote` | Git, but no GitHub repository | Create the repository (skip `git init`) |
| `no-login` | A repository is set, but `gh` has no working login | The github skill's "Connecting GitHub", then run the script again |
| `no-access` | GitHub refuses to read or save the repository (`remote:` or `push-check:` says why) | Access ladder |
| `behind` | GitHub has saves this copy doesn't | Pull first (github skill); if it can't fast-forward, stop and explain |
| `unsaved` | The repository is empty (`remote: empty`), or this copy has changes or saves GitHub doesn't | First save if it's empty; otherwise save as the github skill does |
| `saved` | This copy and GitHub match | Nothing to do |
| `shared-drive` | Kept in the project's shared drive, with no git | Nothing to do: Drive is the backup. Act on any `env-warning:` line |
| `shared-drive-git` | In the shared drive, but still a git repository | "Moving from GitHub to the shared drive", from step 3 |
| `synced-other` | In a synced folder that isn't a shared drive (a My Drive, Dropbox, OneDrive, iCloud) | Tell the PM it can't stay there; offer the project's shared drive or GitHub ("Choose a home") |

If the PM wants to join an existing project, go to "Join a project" instead.

When `token-expires` is two weeks away or less, tell the PM and walk them through a replacement before it runs out.

## Create the repository

1. **Check the name.** `suggested-repo` says what it was based on. If it came from the project key because no code repository was found, look in the root `CLAUDE.md` and ask the PM which code repository the project uses before falling back: every project should have one, even if it isn't cloned into `repo/` yet. If `suggested-repo-exists` is yes, don't create or push anything: ask whether this is the same project (then "Join a project") or a new one that needs another name, such as with the year (`example-site-2027-pm`).
2. **Say what you'll do and wait for a yes**: "I'll create the private repository Lullabot/example-site-pm and save this Project Brain to it. OK?" Never create a public one.
3. **Start git** if `state` was `no-git`: `git init -b main`. Confirm `.env` is ignored (`git check-ignore -q .env`); if it isn't, run the github skill's `gh-setup.sh`, which adds it.
4. **Create the repository**, empty. Don't use `--source` or `--push`: they rely on the shell's own git login, which Cowork's shell doesn't have.

   ```sh
   gh repo create Lullabot/example-site-pm --private --description "Project Brain for EXU"
   git remote add origin https://github.com/Lullabot/example-site-pm.git
   ```

5. Go to "First save". If the create fails, keep what's done (the local repository is fine) and go to "Access ladder".

## First save

1. Read `git status --short` and confirm `.env` isn't in it.
2. Stage by name, not with `git add -A`: `.ai`, `.claude`, `docs`, `CLAUDE.md`, `README.md`, `.env.example`, `.gitignore`, and `AGENTS.md` or `.agents` if they exist. Show the PM what's included in a line or two.
3. Commit ("Set up the Project Brain with Lobot x.y.z", using the installed version) and push with the command in the github skill's "Saving the Project Brain". The repository is empty, so skip the pull before it: there's nothing to get yet.
4. Tell the PM the repository's address and that the next PM can join from it. Then "Keeping it saved" and "Record it".
5. Publish the project overview (project-overview skill), or update it if the project has one, so the PM can see what's set up and what's left.

## Access ladder

Start at rung 1 and go down only when a step fails. Say in a sentence or two what happened and what comes next, then continue. Don't loop on a failure, and don't try to get around a policy.

| Rung | When it applies | What you do | What the PM does |
|---|---|---|---|
| 1. Classic token | The PM has a classic token (the github skill's scopes, SSO-authorized) and may create private repositories in the org | Create and save as above | Approves the plan |
| 2. PM creates the repository | Classic tokens are blocked, or the PM's token can't create repositories, but the PM can in GitHub's own screens | Gives the name and the clicks: github.com, **+**, **New repository**, owner Lullabot, the name, **Private**, nothing else ticked (no README). Then a fine-grained token for that one repository (below) | Creates the repository and the token |
| 3. An admin creates it | The PM can't create repositories in the org (Lullabot isn't offered as an owner, or private isn't allowed) | Drafts the request below | Sends it and waits |
| 4. Local only | No GitHub access yet | The local repository and commits are enough. Records what's pending (see "Record it") and offers to finish at the start of a later session | Nothing, for now |

Don't ask for a fine-grained token that can create repositories. It would need administration rights across the org's repositories, which is the kind of token a security team refuses, and rung 2's two minutes of clicking does the same job.

**What GitHub says, and where it points:**

| Message (match the meaning, not the wording) | It means | Next |
|---|---|---|
| The org forbids access by a classic token | The org has restricted classic tokens | Rung 2 |
| The resource is protected by the org's SAML or SSO | The token isn't authorized for the org's single sign-on | The PM opens the token in GitHub, chooses **Configure SSO**, and authorizes Lullabot. Then try the same rung again |
| "Resource not accessible by personal access token" (403) | A fine-grained token lacks a permission, or isn't set to the right owner or repository | Rerun the call as `gh api -i`, read `X-Accepted-GitHub-Permissions`, and ask the PM to add exactly what it names |
| 403 or 404 on creating a repository, with a token that works elsewhere | The PM may not be allowed to create repositories in the org | Ask the PM to try **New repository** in GitHub: if Lullabot is offered as an owner, rung 2; if not, rung 3 |
| The token works for the PM's own account but the org's repositories are refused, soon after the PM made it | A fine-grained token waiting for an owner's approval (GitHub shows it as pending on the token's page) | Nothing is broken. Say who has to approve it, offer the request text, and work locally meanwhile (rung 4) |
| 401, "Bad credentials", or an expired token | Expired, revoked, or mistyped | Walk the PM through a new token |

**A fine-grained token for one repository.** Walk the PM through github.com, Settings, Developer settings, Personal access tokens, Fine-grained tokens, Generate new token:

- Name it for the project and tool ("EXU Project Brain, Cowork") and set an expiry as short as is practical.
- Resource owner **Lullabot**. If Lullabot isn't listed, the org usually isn't allowing fine-grained tokens, which an admin has to change: rung 3.
- Repository access **Only select repositories**: just the Project Brain repository.
- Permissions: Contents read and write (Metadata read comes with it).
- Add only what a feature needs, when the PM asks for it: Issues and Pull requests (read and write) on the code repository for tickets and ADRs, and the organization's Projects permission for boards. Each one is something the token's approver has to accept, so don't ask for more at once.

If a call still fails, the `X-Accepted-GitHub-Permissions` header names what's missing, and it wins over this list. The PM pastes the token into their token file as the github skill describes, and the expiry date as `GH_TOKEN_EXPIRES=` on the next line. Never ask for the token in chat. If the org requires approval, GitHub tells the PM the token is pending.

**Request to an org admin (rung 3).** A draft for the PM to send, not to send for them:

> Could you create a private repository in the Lullabot org named example-site-pm, empty (no README), and give me write access? It holds my working files for the project: meeting notes, decisions, risks, and a people directory. There is no code in it. Nothing else is needed.

**Request to approve a token.** Point the reviewer to `.ai/general/reference/security.md` (or its copy on GitHub, https://github.com/Lullabot/lobot/blob/main/engine/reference/security.md), which explains all of Lobot's access. For the token itself, give the PM these points to put in their own words:

- What it's for: saving the project's working files to one private repository (and, if asked for, reading and updating issues on one code repository).
- Scope and permissions: the exact list, with one line of reason each.
- How it's kept: in a git-ignored `.env` readable only by the PM, never printed, logged, or put in a remote address.
- What the assistant won't do: merge, force-push, delete, or change repository or organization settings. Every change others can see waits for the PM's approval.
- How it ends: it expires on the date set, and is revoked in GitHub when the PM rolls off.

## Join a project

**Kept in the shared drive** (`.ai/project/brain-home.md` says so, or the PM says the Project Brain is in the project's drive): the PM needs access to the shared drive (whoever manages it gives it) and Google Drive for desktop. Connect the `.<key>-lobot` folder to the session, make it available offline, recreate the links if they're missing ("Working in it"), then steps 3 to 5 below. Tokens go in `~/.lobot/<key>.env` as the github and jira skills set them up.

**Kept on GitHub:** for a PM taking over or joining a project that already has a repository. Their folder is empty, so this skill and the github skill aren't in it yet: read them from Lobot's repository (https://github.com/Lullabot/lobot, `engine/skills/`) until the repository is pulled.

1. **Get the repository** from the PM (name or address), and an empty folder connected to the session.
2. **Pull it**, depending on what the computer has:
   - **`gh` already logged in** (Claude Code on the PM's own computer): `gh repo clone Lullabot/NAME .`
   - **Otherwise** (Cowork): the token has to come first, and it lives in the folder. Create `.env` with `GH_TOKEN=` and `GH_TOKEN_EXPIRES=` lines, owner-only (`chmod 600 .env`), and walk the PM through a token as in rung 2 (or a classic one, if the org allows them). Once they've pasted it in, pull with git alone, reading the token from `.env` for this one command:

     ```sh
     git init -b main
     git remote add origin https://github.com/Lullabot/NAME.git
     git -c credential.helper= -c 'credential.helper=!f() { echo username=x-access-token; echo "password=$(sed -n "s/^GH_TOKEN=//p" .env | tail -1)"; }; f' pull origin main
     git check-ignore -q .env && echo ".env is ignored"
     ```

     The repository's `.gitignore` ignores `.env`. If the check doesn't print, stop before anything is committed.
   - **If it's refused**, the PM needs access to the repository. Whoever owns it or an org admin gives it; draft the request as in rung 3.
3. **Set up what git leaves out**, one at a time, asking before each:
   - `repo/`: clone the code repository named in the root `CLAUDE.md`;
   - the PM's personal profile in `~/.lobot/` (pm-profile skill).
4. **Check the Lobot version** (lobot skill) and offer an update if one is waiting.
5. **Hand over**: run the start-of-session routine, then recap the journal from the latest handoff entry, and publish the joining PM's own project overview (project-overview skill), since its connections are theirs.

## Keeping it saved

Not for a shared-drive Project Brain: Drive saves it as it changes.

Once the repository is connected, ask the PM once: "Want me to save and push the Project Brain at the end of every session, or only when you ask?" Nothing runs in the background, so "automatic" means at wrap-up.

- **At wrap-up (their yes is the standing approval):** after the journal closes, commit what changed (staged by name, with the summary shown in a line) and push. If the push can't fast-forward, stop and explain, as the github skill says.
- **Only when asked:** follow the github skill, offering at the end of a session that changed files.

It's the PM's own habit, so save the answer in their personal profile (pm-profile skill), never in the project's files, which the next PM shares. If the profile can't be read, ask again at wrap-up. Don't push anything else, and never push the code repository.

## Record it

**Shared drive:** create `.ai/project/brain-home.md`, the file the scripts read:

```markdown
# Where this Project Brain lives

- Home: shared drive
- Folder: Shared drives/Projects/Example Client/.exu-lobot
- Backup: Google Drive (version history and trash); no git
```

Log the setup in the journal. If the project had a GitHub repository, also update `.ai/project/github.md` as "Moving from GitHub" says.

**GitHub:** add this to `.ai/project/github.md` (create the file if it's missing), and refine it in place when it changes. Only what's true for every PM goes here: no tokens, expiry dates, or personal preferences.

```markdown
## Project Brain repository

- Repository: Lullabot/example-site-pm (private)
- Pending: none
```

Use `Pending:` for anything unfinished ("waiting for an admin to create the repository, requested 2026-10-15"). While it isn't "none", offer to continue at the start of each session. Log the setup in the journal: the repository, which rung worked, and anything pending. Never the token.

## Hard limits

- Never create or change a repository to public, and never use a personal account, another host, or a cloud drive other than the project's Lullabot shared drive. The shared drive is a home the PM chooses, not a way around a GitHub refusal: offer it only if the PM hasn't ruled it out, and never for a drive anyone outside Lullabot can open.
- Never run `git init` in a shared-drive Project Brain, and never put a token file in one.
- Never put a token in a remote address, `.git/config`, the chat, a file other than the PM's `.env`, or a command's output.
- Never use `gh auth login` or a device-code login (the github skill's rule), and never change organization settings or other people's repositories.
- Never create a repository, ask for access on the PM's behalf, or push without the PM's approval of what you're about to do.
- Never force-push, rebase, or reset without the PM's explicit approval.
