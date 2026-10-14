---
name: pm-profile
description: Read and update the PM's personal profile in ~/.lobot/, which follows them from project to project. Use at the start of every session, when the PM sets a preference they want kept ("always", "from now on", "I prefer"), when they turn a Lobot setting and want it as their default, and when a voice or preference change is approved and needs a place to be saved.
---

# PM profile

## Why

A PM's working style doesn't change when they change projects. How they write, how chatty they want Lobot to be, and how they like a status update laid out would otherwise be relearned on every project, because each Project Brain only knows what's in its own folder. The personal profile keeps those things in the PM's home folder, where every project they open can read them.

## Where

| What | Where |
|---|---|
| The PM's voice: how they write, overall and by context (tickets, client email, team chat) | `~/.lobot/voice.md` (see the pm-voice skill) |
| The PM's preferences: Lobot's settings, formats, and working habits | `~/.lobot/preferences.md`, from `template.md` in this skill's folder |
| Anything that only applies to one project | `.ai/project/voice/<people-key>.md` and the project's own rule files, never `~/.lobot/` |

`~` is the home folder of the person at the computer (`%USERPROFILE%` on Windows). Create `~/.lobot/` the first time the PM approves saving something there.

The profile belongs to that person, not to the project. Lobot's portability rule still holds: a project must work fully without it, and nothing about the project may live only there.

## Reading it

At the start of a session, read `~/.lobot/preferences.md` if it exists. Apply its Lobot settings as the session's starting settings, and its other sections wherever they fit. Read `~/.lobot/voice.md` when drafting as the PM (pm-voice skill).

**Check whose profile it is.** The frontmatter names its owner. If that person isn't the PM you're working for (a co-PM's computer, a shared machine), don't use it, and say so once.

**When it can't be read**, say so in one line and carry on with the project's files and the defaults. This happens when the assistant can only see the project folder:

- **Claude Code** asks before reading outside the project. To stop it asking, the PM can add `~/.lobot` to `permissions.additionalDirectories` in `~/.claude/settings.json`.
- **Claude Cowork** can see it only if the PM connects the `~/.lobot` folder to the session.
- Other assistants vary. If one can't reach it, the PM can say "use my profile from <path>" or paste it in.

Offer the fix once per session, not on every draft.

**When the project has settings of its own** (a project voice profile, a rule in `.ai/project/`), they win where the two disagree. The project's files are about this project; the profile is the PM's defaults.

## Saving to it

Nothing is written to `~/.lobot/` without the PM's approval, and approval is never inferred from silence.

1. **Ask where it belongs.** When a preference or voice change is approved, ask: "Save this for you everywhere, or just for this project?" Suggest the likely answer: habits of the PM's (wording, formats, settings) go everywhere; anything about this client, team, or project stays in the project.
2. **Strip it before saving.** The profile travels between clients, so it never holds client or project names, people's names, internal URLs, quotes from project material, or anything confidential. Write the trait in general terms ("Client executives get a three-line summary first"), not the instance ("The VP at the client wants...").
3. **Refine, don't accumulate.** Replace a line that the new one contradicts; don't add both. Add a dated line to the file's change log.
4. **Tell the PM what changed** in one line, with the file.

## Learning preferences

- When the PM says "always", "from now on", "I prefer", or "stop doing", that's a candidate. Ask where to save it (above).
- When the PM changes a Lobot setting ("humor to 10"), it lasts the session. If they make the same change in a later session, offer once to make it their default.
- When the PM keeps reshaping the same kind of output (a status format, how a briefing is ordered), propose the pattern once it repeats. One proposal at a time, at the end of a reply.
- New kinds of preference get their own heading in the file as they come up. The template is a starting point, not a limit.

## Bringing it along

- **First project with Lobot, or a new computer.** If there is no `~/.lobot/`, offer once to set it up: start `preferences.md` from the template with Lobot's default settings, and have the pm-voice skill offer to learn the PM's voice.
- **A project with an older, project-only voice profile.** If `.ai/project/voice/` has an approved profile for this PM and `~/.lobot/voice.md` doesn't exist, offer once to promote it: copy the general traits into `~/.lobot/voice.md` (stripped, as above, with no excerpts), and leave only what is specific to this project in the project's file.
- **Handoff.** The new PM brings their own profile. Nothing in `~/.lobot/` is needed for the handoff, and the outgoing PM's profile isn't copied into the project.
