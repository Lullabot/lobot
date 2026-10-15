---
name: project-setup
description: Put the Project Brain under version control on GitHub and keep the PM connected to it. Creates the private repository for a new project, attaches one to a folder that has none, helps a PM join a project that already has one, and works out what to do when GitHub access is blocked. Use when the PM starts a project, says "set up the repo", "put this on GitHub", "back up the Project Brain", "join" or "take over" a project, when the Project Brain has no git repository or no remote, or when creating, pulling, or pushing the repository fails with a permission, token, or approval error.
---

# Project setup

## Why

A Project Brain only works as a handoff if the next PM can get all of it: a private repository in the org, kept current, and a PM who can reach it without knowing git. This skill does that work in plain language. When GitHub says no, it finds the next route instead of stopping.

The Project Brain holds transcripts and a people directory, which is client data. It lives in a private repository in the org, never in a personal account or on another service, whatever the obstacle.

## Where

Run everything from the Project Brain root, in the same shell as `gh` (in Cowork, the shell on the PM's computer). Source `.ai/general/skills/github/gh-env.sh` first, and follow the github skill's "Token safety" and "Before the first git command in a session" (delete permission, commit identity).

| What | Where |
|---|---|
| Where this Project Brain stands | `bash .ai/general/skills/project-setup/brain-state.sh` (changes nothing) |
| The repository, and anything left to do | "Project Brain repository" in `.ai/project/github.md` |
| Org and repository name | Org `Lullabot`, wherever the code lives. The name is the code repository's name plus `-pm`: code in `Lullabot/example-site` (or a client's org) gives `Lullabot/example-site-pm`. Only if the project truly has no code repository, use the project key in lowercase plus `-pm` (`exu-pm`). If the PM names another, use theirs. |
| When the PM's token expires | `GH_TOKEN_EXPIRES=YYYY-MM-DD` in `.env`, beside the token. It's the PM's own, so it stays out of git with them. |

## Find out where things stand

Run `brain-state.sh` and read it. Look things up; don't ask the PM what the script can tell you. Its last line, `state:`, picks the next step:

| `state:` | Meaning | Next |
|---|---|---|
| `no-git` | The folder isn't under version control | Create the repository |
| `no-remote` | Git, but no GitHub repository | Create the repository (skip `git init`) |
| `no-login` | A repository is set, but `gh` has no working login | The github skill's "Connecting GitHub", then run the script again |
| `no-access` | GitHub refuses to read or save the repository (`remote:` or `push-check:` says why) | Access ladder |
| `behind` | GitHub has saves this copy doesn't | Pull first (github skill); if it can't fast-forward, stop and explain |
| `unsaved` | The repository is empty (`remote: empty`), or this copy has changes or saves GitHub doesn't | First save if it's empty; otherwise save as the github skill does |
| `saved` | This copy and GitHub match | Nothing to do |

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

If a call still fails, the `X-Accepted-GitHub-Permissions` header names what's missing, and it wins over this list. The PM pastes the token into `.env` as the github skill describes, and the expiry date as `GH_TOKEN_EXPIRES=` on the next line. Never ask for the token in chat. If the org requires approval, GitHub tells the PM the token is pending.

**Request to an org admin (rung 3).** A draft for the PM to send, not to send for them:

> Could you create a private repository in the Lullabot org named example-site-pm, empty (no README), and give me write access? It holds my working files for the project: meeting notes, decisions, risks, and a people directory. There is no code in it. Nothing else is needed.

**Request to approve a token.** Give the PM these points for whoever reviews it, to put in their own words:

- What it's for: saving the project's working files to one private repository (and, if asked for, reading and updating issues on one code repository).
- Scope and permissions: the exact list, with one line of reason each.
- How it's kept: in a git-ignored `.env` readable only by the PM, never printed, logged, or put in a remote address.
- What the assistant won't do: merge, force-push, delete, or change repository or organization settings. Every change others can see waits for the PM's approval.
- How it ends: it expires on the date set, and is revoked in GitHub when the PM rolls off.

## Join a project

For a PM taking over or joining a project that already has a repository. Their folder is empty, so this skill and the github skill aren't in it yet: read them from Lobot's repository (https://github.com/Lullabot/lobot, `engine/skills/`) until the repository is pulled.

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
5. **Hand over**: run the start-of-session routine, then recap the journal from the latest handoff entry.

## Keeping it saved

Once the repository is connected, ask the PM once: "Want me to save and push the Project Brain at the end of every session, or only when you ask?" Nothing runs in the background, so "automatic" means at wrap-up.

- **At wrap-up (their yes is the standing approval):** after the journal closes, commit what changed (staged by name, with the summary shown in a line) and push. If the push can't fast-forward, stop and explain, as the github skill says.
- **Only when asked:** follow the github skill, offering at the end of a session that changed files.

It's the PM's own habit, so save the answer in their personal profile (pm-profile skill), never in the project's files, which the next PM shares. If the profile can't be read, ask again at wrap-up. Don't push anything else, and never push the code repository.

## Record it

Add this to `.ai/project/github.md` (create the file if it's missing), and refine it in place when it changes. Only what's true for every PM goes here: no tokens, expiry dates, or personal preferences.

```markdown
## Project Brain repository

- Repository: Lullabot/example-site-pm (private)
- Pending: none
```

Use `Pending:` for anything unfinished ("waiting for an admin to create the repository, requested 2026-10-15"). While it isn't "none", offer to continue at the start of each session. Log the setup in the journal: the repository, which rung worked, and anything pending. Never the token.

## Hard limits

- Never create or change a repository to public, and never use a personal account, another host, or a different cloud drive as the fallback.
- Never put a token in a remote address, `.git/config`, the chat, a file other than the PM's `.env`, or a command's output.
- Never use `gh auth login` or a device-code login (the github skill's rule), and never change organization settings or other people's repositories.
- Never create a repository, ask for access on the PM's behalf, or push without the PM's approval of what you're about to do.
- Never force-push, rebase, or reset without the PM's explicit approval.
