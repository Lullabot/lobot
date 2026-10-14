# Working on Lobot

Instructions for an AI assistant (or a person) changing this repository. For what Lobot is and how projects use it, read `README.md`, then `engine/lobot.md`.

## This repository is public

Never put a client's name, people, project details, internal URLs, or credentials in any file, commit message, issue, or pull request. When a change comes out of work on a real project, describe it in general terms.

## What ships where

| Path | Reaches | Notes |
|---|---|---|
| `engine/` | Every project, on its next update, as `.ai/general/` | Must work on any project. Paths written inside these files are the installed ones (`.ai/general/...`, `docs/...`), never `engine/...`. |
| `scaffold/` | New projects only, once | Existing projects never receive changes here. If they need one, say in the commit body what they have to do by hand. `{{PROJECT_NAME}}`, `{{PROJECT_KEY}}`, and `{{DATE}}` are filled in on install. `gitignore` has no dot because npm drops `.gitignore`; the tool restores it. |
| `tools/lobot.js` | Runs through `npx`; not copied into projects | No dependencies. |
| `tools/migrations.json` | Read by the tool's `status`, `update`, and `migrate` | Steps a breaking change needs in a project's own files (see "Breaking" below). |
| Everything else | Nobody | Repository docs, release config, this file. |

## Rules

- **Keep `package.json` free of dependencies, devDependencies, and a `prepare` script.** Projects run this straight from GitHub with `npx`; any of those would make every run install packages.
- **Never edit `version` in `package.json` or anything in `CHANGELOG.md`.** Releases write both (see below).
- **One skill per folder:** `engine/skills/<name>/SKILL.md`, with `name` matching the folder and a `description` that says when to use it. Skills that keep a record file ship a validator and are tested against an empty file.
- **Agent names and personalities follow one pattern.** A named agent gets an alliterative name plus a role that fits ("Lucy the Librarian", "Pepper the Process Wrangler"), so it's easy to remember who does what. Its `personality.md` follows Lobot's format: a namesake from film, TV, or books, an inspiration table (what they take, what they leave behind), and the traits left behind become hard limits.
- **Everything about an agent lives under `engine/agents/`:** the definition is `<name>.md`, supporting files go in `<name>/`. Only the definition is copied to `.claude/agents/`, so no other `.md` file may sit directly in `engine/agents/`. Project settings for an agent belong in `scaffold/.ai/project/agents/<name>/`.
- **Keep the map current.** Adding, renaming, or removing a rule, skill, agent, or record file means updating `engine/lobot.md` (directory map, working rules), `engine/delegation.md` (roster) when an agent changes, and `README.md` if the commands or layout changed.
- **Rules are refined, not accumulated.** Edit an instruction in place; don't append a contradiction.

## Commits and releases

Every push to `main` is released automatically from its commit messages, so the message decides the version. Use Conventional Commits: `type(scope): summary`.

- **Scope** says what changed: `engine`, `scaffold`, or `tool`. A commit with one of these scopes always releases at least a patch. Leave the scope off for changes nothing receives (this file, the README, CI).
- **Type:** `feat` for something new (minor), `fix` for a correction (patch), `docs` or `refactor` for rewording and restructuring (patch when scoped), `ci` and `test` for the pipeline.
- **Breaking:** add `!` after the scope (`feat(engine)!: ...`) when existing projects must change something to keep working, and say what in the body. Until 1.0, a breaking change releases as a minor version (`.releaserc.json`); the `!` still matters, because it puts the change first in the PM's "What's new" report. When Lobot reaches 1.0, set the `breaking` rule back to `major`. If the change is a move, a text replacement, a deletion, a markdown table record turned into YAML (`convert`, with a converter in `TABLE_CONVERTERS` in `tools/lobot.js`), or links pointed at a renamed record (`relink`) in the project's own files (`.ai/project/`, `.claude/`, `docs/`), also add it to `tools/migrations.json` in the same commit, so the assistant can make it with the PM's approval. Each step must be safe to run twice and must check the files rather than the version. Test it with `status`, `migrate --dry-run`, and `migrate` on a project installed from the previous version.
- **Write the summary for a PM.** It becomes the release note that projects show their PM in the "What's new" report on update. Say what they can now do or what changed for them.
- One logical change per commit. Reference an issue with `Closes #12` in the body.

Propose the commit message; the maintainer commits and pushes unless they ask you to. The release adds its own commit to `main`, so make sure the checkout is up to date before editing.

## Test before proposing a commit

```sh
node tools/lobot.js init /tmp/lobot-test --name "Test Project" --key TST   # fresh install
node tools/lobot.js status /tmp/lobot-test                                 # should report nothing to change
```

Then check whatever the change touches: run a changed validator against the empty file in the test project, confirm a new skill is linked in `.claude/skills/`, and for a change to the tool, run `update` against a test project installed from the previous version.

To try a change on a real project before it is pushed, apply this checkout to it:

```sh
node tools/lobot.js update /path/to/project
```

## Working with GitHub

The github skill (`engine/skills/github/SKILL.md`) is written for projects: it connects a PM's Project Brain to GitHub. This section is for working on this repository. The skill's scripts work from here too and use this checkout's own git-ignored `.env`.

**Connect.** From the repository root, in the shell that runs git (in Cowork, the shell on the maintainer's computer, not the cloud workspace):

```sh
bash engine/skills/github/gh-setup.sh
```

Act on its output as the skill's "Connecting GitHub" describes, and follow its "Token safety". The token must also be able to write to this repository: a classic token needs the `repo` scope; a fine-grained one needs `Lullabot/lobot` under repository access, with Contents (and Pull requests, to open them) set to "Read and write". `auth: ok` only proves the token can read, so check that it can push before relying on it:

```sh
source engine/skills/github/gh-env.sh
url=https://github.com/Lullabot/lobot.git
git -c credential.helper= -c credential.helper='!gh auth git-credential' push --dry-run "$url" HEAD:refs/heads/main
```

A 403 ("Permission … denied") means the token can't write; say which setting to change and stop. (`gh api repos/Lullabot/lobot --jq .permissions.push` reports the account's access, not the token's, so it isn't a check.)

**Fetch and push over HTTPS**, in the same shell after sourcing `gh-env.sh`, without changing `origin` (it may use SSH, which Cowork's shell can't):

```sh
git -c credential.helper= -c credential.helper='!gh auth git-credential' fetch "$url" +main:refs/remotes/origin/main
git -c credential.helper= -c credential.helper='!gh auth git-credential' push "$url" BRANCH:refs/heads/BRANCH
```

- In Cowork, ask once per session for delete permission on the checkout before the first git command; without it git leaves lock files that break the next command.
- Push only when the maintainer asks. Pushing `main` releases (see "Commits and releases"), so name every unpushed commit it would release before asking.
- Fetch before editing and before pushing. If `main` moved, stop and say what changed rather than merging, rebasing, or force-pushing.

## Changes that start in a project

When this repository is connected to a session alongside a project, make general changes here in `engine/`, then apply them to the project with the command above. If a general change was made in the project's `.ai/general/` instead (Lucy's general corrections log is the usual case), copy it here, strip anything project-specific, and commit it; the project's next update then finds nothing to overwrite.
