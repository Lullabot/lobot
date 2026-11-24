---
name: pm-profile
description: Read and update the PM's personal profile in ~/.lobot/ (voice and preferences that follow them across projects) and each PM's technical comfort with git and the command line. Use at session start, when the PM states a lasting preference ("always", "from now on"), when an approved change needs saving, and before giving a PM steps to do themselves.
---

# PM profile

## Why

A PM's working style doesn't change when they change projects. How they write, how chatty they want Lobot to be, and how they like a status update laid out would otherwise be relearned on every project, because each Project Brain only knows what's in its own folder. The personal profile keeps those things in the PM's home folder, where every project they open can read them.

## Where

| What | Where |
|---|---|
| The PM's voice: how they write, overall and by context (tickets, client email, team chat) | `~/.lobot/voice.md` (see the pm-voice skill) |
| The PM's preferences: Lobot's settings, formats, and working habits | `~/.lobot/preferences.md`, from `template.md` in this skill's folder |
| How comfortable each PM on the project is with git and the command line, and which git tool they use | `.ai/project/pms.md`, one section per PM (see "Technical comfort"), with the PM's own default in `~/.lobot/preferences.md` |
| Anything that only applies to one project | `.ai/project/voice/<people-key>.md` and the project's own rule files, never `~/.lobot/` |

`~` is the home folder of the person at the computer (`%USERPROFILE%` on Windows). Create `~/.lobot/` the first time the PM approves saving something there.

The profile belongs to that person, not to the project. Lobot's portability rule still holds: a project must work fully without it, and nothing about the project may live only there.

## Reading it

At the start of a session, read `~/.lobot/preferences.md` if it exists. Apply its Lobot settings as the session's starting settings, and its other sections wherever they fit. Read `~/.lobot/voice.md` when drafting as the PM (pm-voice skill).

**Check whose profile it is.** The frontmatter names its owner. If that person isn't the PM you're working for (a co-PM's computer, a shared machine), don't use it, and say so once.

**When it can't be read**, say so in one line and carry on with the project's files and the defaults. This happens when the assistant can only see the project folder:

- **Claude Code** asks before reading outside the project. To stop it asking, the PM can add `~/.lobot` to `permissions.additionalDirectories` in `~/.claude/settings.json`.
- **Claude Cowork** can see it only if the PM connects the `~/.lobot` folder to the session. It's a hidden folder and may not exist yet; the guided-setup skill's "Connect a folder" walks the PM through both.
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

## Technical comfort

Some PMs push from a terminal every day, and some have never opened one. Lobot does the git and command work itself whenever it can, but sometimes the PM has to do a step themselves: the assistant's tool blocks a push (Cowork does), a login only they can make, an app only they can install. Those instructions are only useful at the PM's own level. A step-by-step walkthrough wastes a fluent PM's time, and a bare command strands a PM who has never seen a terminal.

### The settings

| Setting | Values |
|---|---|
| `terminal` | How comfortable they are on the command line: `step-by-step`, `checklist`, or `fluent` (below) |
| `git` | How comfortable they are with git itself (commit, push, pull, a refused push): the same three levels |
| `git app` | What they use to work with git on their own: `GitHub Desktop`, `terminal`, another app by name (VS Code, Tower), or `none yet` |

| Level | Who it fits | How Lobot gives instructions |
|---|---|---|
| `step-by-step` | New to it, or would rather not learn it | One step per message, then wait. Exact button and menu names in **bold**, what they'll see after each step, and every term explained in a sentence the first time (guided-setup skill, "How to walk someone through it"). Plain words for git: "send your saved work up to GitHub" for push, "get the latest from GitHub" for pull; name the git word only where the screen shows it (GitHub Desktop's **Push origin** button). Never a terminal command unless they chose the terminal. |
| `checklist` | Knows the basics and follows written steps | All the steps in one numbered list, commands in copyable blocks, and a short note on anything they haven't done before. Git's own words, explained once if new. |
| `fluent` | Uses it daily | The command or menu path and why it's needed, in a line. No walkthrough unless they ask. |

Until a PM has a setting, use `step-by-step` with GitHub Desktop: it's the safe default for a PM, and an experienced one will say so quickly.

**Something new to their level.** When a task asks for more than a PM's level has covered (a `checklist` PM's first refused push, a `step-by-step` PM installing GitHub Desktop), drop to step-by-step for that task, explain what's happening and why, and go back to their level after. Offer once to raise a level when they say they've got it; don't lower one because of a single slip.

### Where it's kept

**In the project**, in `.ai/project/pms.md`, so the assistant knows how to work with each PM on this project, and two PMs working together can see each other's settings (a fluent PM pairing with a step-by-step one knows which app the other uses and how much to explain). It's a rule file at the top of `.ai/project/`, so it's read at the start of every session. One section per PM, keyed by their people directory entry:

```markdown
# PMs on this project

How the assistant gives git and command-line instructions to each PM (pm-profile skill, "Technical comfort"). Work preferences only; nothing personal.

## Jane Doe (doe-jane)

- terminal: step-by-step
- git: step-by-step
- git app: GitHub Desktop
- updated: 2026-11-24
```

**In the PM's personal profile** as well, under "Technical comfort" in `~/.lobot/preferences.md`, so their next project starts from it instead of asking again. Saving it there follows "Saving to it" like any other preference.

The project file wins where the two disagree (a PM can be fluent at home and want steps on a client's unfamiliar setup). A PM who'd rather not have their setting in the project's files can keep it in their profile only; then Lobot asks again on a computer where the profile can't be read.

### Knowing which PM it is

Match the person at the computer to a section: the owner of `~/.lobot/preferences.md`, then the commit identity (`git config user.email`) against the people directory, then the PM the root `CLAUDE.md` names. If two PMs could match, or none does, ask once: "Is this Jane?" Keep to that PM's settings for the session.

### Asking

The first session with a PM who has no setting in the project or their profile, ask once, in one short message, near the end of the opening brief and never ahead of anything urgent:

> So I give you instructions at the right level when you need to do something yourself: how comfortable are you with the command line, and with git? And when you work with git on your own, do you use GitHub Desktop, the terminal, or something else, or haven't you needed to yet?

Map the answer to the levels, tell the PM what you took it as in a line ("Got it: step-by-step, GitHub Desktop"), and save it to the project file with their yes (and offer the profile, as above). If they skip it, use the default and ask again only when they first need to do something themselves. A PM can change it any time ("I'm fine with the terminal now"); refine the line in place and update `updated:`.

### Hard limits

- It decides how instructions are written, never what Lobot will do. A fluent PM still approves every push, and the hard rules apply at every level.
- Never record anything but these settings in `.ai/project/pms.md`: no judgments ("not technical"), no personal details.
- Never ask a PM to run a command you can run yourself, whatever their level.

## Bringing it along

- **First project with Lobot, or a new computer.** If there is no `~/.lobot/`, offer once to set it up: start `preferences.md` from the template with Lobot's default settings, and have the pm-voice skill offer to learn the PM's voice.
- **A project with an older, project-only voice profile.** If `.ai/project/voice/` has an approved profile for this PM and `~/.lobot/voice.md` doesn't exist, offer once to promote it: copy the general traits into `~/.lobot/voice.md` (stripped, as above, with no excerpts), and leave only what is specific to this project in the project's file.
- **Handoff.** The new PM brings their own profile. Nothing in `~/.lobot/` is needed for the handoff, and the outgoing PM's profile isn't copied into the project. The new PM gets their own section in `.ai/project/pms.md` ("Technical comfort"); the outgoing PM's section goes when their people directory entry turns `former`.
