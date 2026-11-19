---
name: save
description: 'Commit each finished process (a transcript processed, page changes filed) on its own, with a message saying what was done and from what, and push the Project Brain to its repository. Use when a process starts or ends, for "save", "commit", or "push", and at session close.'
---

# Save

The Project Brain is a git repository, and its history is the project's paper trail. A folder on one computer is lost with that computer, so commits are what keep the work, and the push to the private repository is what keeps it off the PM's laptop. One commit per finished process means anyone (the PM, the next PM, an assistant) can see what was done, from what, and when, and can undo one piece of work without touching another.

The PM never needs a terminal: the assistant does the git work, in plain language. If the Project Brain isn't in git yet or has no GitHub repository, use the project-setup skill first. If it isn't in git and the PM doesn't want it to be, everything here except the commits still applies (process markers, the journal). Run git in the same shell as `gh` (in Cowork, the shell on the PM's computer), from the Project Brain root.

## Before the first git command in a session

1. **Cowork: ask for delete permission.** Git deletes its own temporary lock files, which a connected folder blocks until the PM allows deleting there. Without it, git leaves lock files behind that break the next git command, the PM's own included. Ask once per session for the Project Brain folder, and tell the PM it also allows other deletes in that folder for the session. If they decline, don't run git commands that write; say what's left unsaved.
2. **Set who the commits are from.** Check `git config user.name` and `git config user.email`. The shell often has no git settings of its own (Cowork's always starts empty), so if either is empty, set both for this repository only with `git config user.name` and `git config user.email`, no `--global`. Take them from, in order: the owner in the PM's personal profile (`~/.lobot/`, pm-profile skill), the PM's entry in the people directory, or the PM, asked once. Tell the PM in one line. They're saved in the Project Brain's `.git/config`, which isn't committed, so each PM's copy keeps its own.

Follow any saving preference in the PM's profile (for example, a Project Brain kept in a synced folder that the PM doesn't commit).

## One process, one commit

A **process** is one piece of work with a beginning and an end: processing a transcript into notes and records, filing the changes the PM made on a tracker page, a drive-sources check that filed new files, drafting a status report, a ticket plan, a Lobot update, the journal's session close. A single edit the PM asks for ("add Sam's GitHub username") is a process of its own.

- **Commit when the process finishes,** after its validators pass and its journal Log line is written, so the line goes in the same commit. No approval is needed: the commit stays on the PM's computer until it's pushed. Tell the PM in one line ("Saved: Process the 14 November client meeting").
- **A process that waits on the PM** (a review list on the review desk, a question) commits what stands on its own before the wait ("Draft notes for the 14 November client meeting, 9 items for review"), then commits the rest when it finishes.
- **Never mid-step.** Files that would fail a validator, a transcript `verify` reports as a draft, and anything half-written stay out until they're done.
- **Only this process's files.** Stage by name the files the process touched, never with `git add -A` or `git add .`. Check `git status` first: changes this process didn't make (the PM's own edits, another session's work) stay unstaged and are left for their own commit. If `.env` or any other secret shows up as a change, stop (github skill, "Token safety").
- **Transcripts:** when the commit includes `docs/transcripts/`, run `python3 .ai/general/skills/transcript-cleanup/transcript.py verify docs/transcripts` first. Commit no transcript it reports as a draft or raw unless the PM chose to keep raw transcripts in git (transcript-cleanup skill).
- **The assistant commits, agents don't.** When Lucy or Pepper finishes a piece of work, the assistant commits it from their report.
- **Never rewrite history.** No amend, rebase, reset, or squash on `main`. A mistake is fixed in a new commit that says what it corrects.

## Process markers

A process that writes more than one file, or waits on the PM, keeps a marker while it's open: `tmp/processes/<YYYY-MM-DD>-<slug>.md`. It's how a later session, or the cleanup skill, finds work that was never finished. Write it when the process starts, tick steps as they finish, and delete it once the last commit is made.

```markdown
---
process: Process the 14 November client meeting
skill: meeting-notes
started: 2026-11-14
sources: [docs/transcripts/raw/2026-11-14-client-weekly.md]
files: [tmp/2026-11-14-client-weekly.clean.md]
---
- [x] Cleaned draft: tmp/2026-11-14-client-weekly.clean.md
- [x] Notes: docs/meetings/2026-11-14-client-weekly.md (committed a1b2c3d)
- [ ] Waiting on: the PM's review of 9 items on the review desk
- [ ] Apply approved items, file the Drive copy, journal
```

`files:` lists the working files in `tmp/` the process still needs; nothing clears them while the marker is open. `tmp/` is never committed, so the marker is a working note for this computer only; the commits and the journal are the record.

## Commit messages

Write for someone reading the history a year from now, who wasn't there.

```
Process the 14 November client meeting

From the cleaned transcript of the client weekly (docs/transcripts/2026-11-14-client-weekly.md).

- Notes: docs/meetings/2026-11-14-client-weekly.md, reviewed by Jane Doe
- Decisions: D-012 recorded (launch moves to March)
- Questions: Q-031 added (who owns the SSO setup), Q-027 answered
- Tasks: 2 added to docs/tasks.yaml
- Dossier: hosting facts added to the main site's infrastructure topic
- Waiting: R-004 update proposed on the review desk

Skill: meeting-notes
```

- **Subject:** what was done, in plain language, imperative, under 72 characters. Lobot updates use "Update Lobot to x.y.z".
- **Body:** what it was built from (sources, with paths or links), then one line per record or file changed, with entry IDs and who approved what, then anything still waiting. Leave the body out for a one-line edit whose subject says it all.
- **Trailer:** `Skill: <name>` of the skill that ran the process, last, after a blank line. The cleanup skill reads it.
- Names as they appear in the people directory. No secrets, and nothing from a sensitive transcript cut.

## Getting changes and pushing

Prefer HTTPS with the `GH_TOKEN` loaded by the github skill's `gh-env.sh`. In Cowork, the shell on the PM's computer usually has no SSH key, so an `origin` that starts with `git@github.com:` fails there with "Host key verification failed". Don't change `origin` (the PM's own tools may use SSH); pass the HTTPS address instead:

```sh
source .ai/general/skills/github/gh-env.sh
url="https://github.com/OWNER/REPO.git"   # origin's repo, over HTTPS
git -c credential.helper= -c credential.helper='!gh auth git-credential' pull --ff-only "$url" main
git fetch -q "$url" main:refs/remotes/origin/main     # so status compares against the right origin/main
git -c credential.helper= -c credential.helper='!gh auth git-credential' push "$url" HEAD:main
```

The token is passed by `gh` for that one command. Never put it in a URL, `.git/config`, or a credential store.

- **Straight to `main`.** The Project Brain is the PM's working record, not shared code: no branches or pull requests for it. Pull requests are only for changes to Lobot itself (lobot skill) and for ADRs in the code repository (adr skill).
- **Pull before the first commit of a session,** so the commits land on top of a teammate's saves. If git refuses because of uncommitted changes, commit them first (as their own process) and pull again; never stash, reset, or discard them.
- **Push only with the PM's yes:** when they ask, or under a standing approval they gave (project-setup skill, "Keeping it saved", or a scheduled job they set up to push). Before pushing, list the commits it will send (`git log --oneline origin/main..HEAD`) in a line or two.
- If a pull can't fast-forward (someone else saved changes too), stop and explain it to the PM in plain terms. Never force-push, rebase, or reset without their explicit approval. Commits keep piling up locally in the meantime, which is safe.
- **When the push is blocked here** (Cowork answers 403 with "Cowork blocked this request … not git push"), the commits are safe on the PM's computer. Say how many are waiting and that the PM has to push them by hand, either way:
  - **GitHub Desktop:** open the Project Brain (the first time, File > Add Local Repository and choose its folder), then click **Push origin**.
  - **Terminal:** go to the Project Brain folder and run `git push origin main`.

  Don't look for another way around the block. If the push is refused there because GitHub has newer saves, the PM pulls first (**Fetch origin**, then **Pull origin** in GitHub Desktop) and pushes again.
- No GitHub repository yet: commit anyway, and offer to finish setup (project-setup skill) once per session.
