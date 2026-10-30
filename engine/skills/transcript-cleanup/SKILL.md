---
name: transcript-cleanup
description: Clean a raw meeting transcript into the copy the Project Brain commits. Small talk and sensitive passages (personal, health, HR, other clients, credentials, internal matters) are removed and marked, fillers are dropped, and each speaker turn becomes one timestamped paragraph. Raw transcripts stay local in docs/transcripts/raw/. Use before writing meeting notes from a transcript (the meeting-notes skill runs it first), when the PM drops a transcript or asks to clean one, and before committing anything in docs/transcripts/.
---

# Transcript cleanup

## Why

Raw transcripts are full of small talk and filler, and sometimes hold things that shouldn't stay in the project's git history forever: someone's health, pay or HR matters, another client's business, a password read aloud. They also take up context every time they're read. The cleaned transcript is the copy the Project Brain commits, and what the meeting notes, the assistant, and the team read later. The raw one stays on the PM's computer, and in Drive for Meet calls.

The model never rewrites the transcript. A script splits it into numbered turns. Lucy lists which turns, or exact passages inside a turn, to remove and why. The PM approves that list, and the script makes the cuts. Every word left is as recorded, apart from standalone um, uh, er and ah, so the cleaned copy can be quoted and cited like the original.

## Where

| What | Path |
|---|---|
| Raw transcripts, as recorded (never edited; git-ignored by default) | `docs/transcripts/raw/` |
| Cleaned transcripts (committed) | `docs/transcripts/`, same file name as the raw one |
| Working files: turns, edits, draft | `tmp/` |
| Script | `transcript.py` in this skill's folder |
| Who can read this Project Brain, and what else it cuts | `.ai/project/transcript-cleanup.md` (see "Before the first cleanup") |

`docs/transcripts/raw/2026-10-28-weekly-sync.md` becomes `docs/transcripts/2026-10-28-weekly-sync.md`.

## Raw transcripts stay out of git

By default the Project Brain's `.gitignore` lists `/docs/transcripts/raw/`, so only cleaned transcripts are committed. Each PM decides whether their project follows this. Lobot asks when an update brings it (lobot skill, "Migrate"), as two separate choices:

1. Keep raw transcripts out of git from now on. This is the default.
2. Move raw transcripts that were committed before into `raw/`. They stop being tracked, but git history still has them.

A choice the PM declines is recorded in `.ai/project/declined-migrations.yaml`.

- `transcript.py verify docs/transcripts` reports raw transcripts still at the top level, and a missing ignore line. If it reports either and neither choice is recorded as declined, put the question in your report for the assistant to ask the PM. Never move, untrack, or delete committed transcripts yourself; the migration does that.
- A raw transcript exists only where it was saved. For a Meet call, Drive keeps the original. A file the PM dropped in exists only on this computer: say so, and suggest adding it to the project's Drive transcripts folder.

## What to cut

There are two kinds of cut, with different rules.

**Banter.** Cut it only when it carries nothing about the project. When unsure, keep it.

| `kind` | What |
|---|---|
| `small-talk` | Greetings, weekends, weather, sports, jokes and chat unrelated to the work |
| `audio` | "Can you hear me?", screen sharing, waiting for people to join, connection trouble |
| `off-topic` | Tangents about other work or unrelated subjects |

Never cut these as banter: dates, availability ("I'm out next week"), who is joining or leaving the team, decisions, commitments, risks, opinions on the work, questions, or reactions to a proposal. An "mm-hmm" after "does that work?" stays.

**Sensitive.** Always cut it, even when it says something useful.

| `kind` | What |
|---|---|
| `personal` | Family, relationships, home life, personal plans beyond plain availability |
| `health` | Illness, medical appointments, conditions, reasons for leave |
| `hr` | Pay, performance, hiring and firing, complaints about a colleague |
| `other-client` | Another client's name, projects, or business. A passing mention that names no client and gives no detail that would identify one ("we're kicking off another project next month") isn't other-client: keep it when it says something about capacity or timing |
| `credential` | Passwords, keys, tokens, account details read aloud |
| `internal` | Lullabot-only matters: rates, margins, budget burn, estimates, sales, staffing plans. Cut only when someone outside Lullabot may read the Project Brain (see "Before the first cleanup") |

When a sensitive passage holds a project fact ("I'm having surgery, so I'm out Nov 3 to 14"), cut it whole and put the fact in the cut's `fact` field in neutral words ("Sam is out Nov 3–14"). The PM decides whether that fact goes into a record. Never paraphrase it back into the transcript.

Cut the smallest span that removes the problem. When the rest of a turn is about the work, cut a passage inside the turn rather than the whole turn.

`.ai/project/transcript-cleanup.md` says who can read this Project Brain, which decides how much `internal` cuts, and lists anything else this project cuts (a codename, a topic the client asked to keep off the record). It can't switch off the other sensitive kinds.

## Before the first cleanup

If `.ai/project/transcript-cleanup.md` doesn't exist, ask the PM before marking any cuts (Lucy returns the question in her report; the assistant asks): **who can read this Project Brain, now or later?** Lullabot only, or might the client, contractors, or a future vendor get access? On an internal project, `internal` cuts staffing, estimates, budgets and sales talk that the team needs, so the answer matters. Write the file with the answer:

```markdown
# Transcript cleanup: project settings

Readers: Lullabot only        # or: Lullabot and the client (or whoever else)
Internal: keep                # keep: don't cut internal matters (Lullabot-only readers)
                              # cut: cut them (anyone outside Lullabot may read it)
Also cut:
- (anything else this project keeps out of the record, or "nothing")
```

With `Internal: keep`, internal matters stay unless they're also another kind (another client's business, someone's pay). When the readers change, the PM updates the file. Transcripts cleaned before keep their cuts; `verify` lists them so the PM can decide which to reclean from their raw copies.

## Workflow

1. **Find the raw transcript** in `docs/transcripts/raw/`: a snapshot from Drive (drive-sources skill) or a file the PM dropped in. If the PM put it somewhere else in the Project Brain, move it into `raw/` first. Moving isn't editing.
2. **Prepare** the turns:
   ```sh
   python3 .ai/general/skills/transcript-cleanup/transcript.py prepare docs/transcripts/raw/<file> --out tmp/<slug>.turns.md
   ```
   Add `--title "<meeting title>"` and `--date YYYY-MM-DD` when the raw file doesn't carry them (a Zoom or dropped-in file; Drive snapshots do). For a Gemini notes Doc, which starts with a summary, the script starts after the "Transcript" heading on its own and says so. If it warns that it found no transcript heading, or picked the wrong place, pass `--from "<text of the heading>"`. The summary stays in Drive.

   Check what it prints. Compare the speaker list with who was on the call. A warning that a speaker label appears inside other turns usually means a speaker the parser didn't recognize, whose lines were merged into someone else's. When the speakers look wrong, stop: report the parse problem (it's a Lobot bug worth reporting with the lobot-feedback skill) rather than cleaning a misattributed transcript.
3. **Mark the cuts.** Read every turn, in chunks for a long meeting, and write `tmp/<slug>.edits.yaml`:
   ```yaml
   cuts:
     - turns: T001-T004              # one turn, or a range cut whole
       kind: audio
       why: Audio check while people joined
     - turns: T017
       text: "How did the move go?"  # an exact passage inside one turn, copied from the turns file
       kind: small-talk
       why: Asked about a move
     - turns: T042
       text: "I've got surgery on the 3rd, so I'm out until the 14th."
       kind: health
       why: Medical detail
       fact: Sam is out Nov 3–14
   topics:                           # optional headings, where the conversation changes subject
     - at: T005
       title: Content freeze date
   ```
   A topic title names the subject in a few words and draws no conclusions. One every 5 to 15 minutes is usual; short calls need none.
4. **Check:**
   ```sh
   python3 .ai/general/skills/transcript-cleanup/transcript.py check tmp/<slug>.turns.md tmp/<slug>.edits.yaml
   ```
   It prints how many words were spoken, how many fillers it dropped, and how many words the cuts remove, each as a share of the words spoken. Fix every error. For each line under "Check these in the kept text", either cut it or keep it and say why in the review (a work email address, a budget figure the client discussed openly).
5. **Review with the PM.** Show the list `check` prints, grouped as banter, sensitive, and facts from sensitive cuts, along with the share of words the cuts remove. On the review desk, a sensitive cut shows only its kind and reason, never the removed words; the PM can ask to see them in chat (`check --show`). When meeting-notes runs this skill, the cut list is the first group of its review, so the PM approves everything in one pass. No autonomy level skips this review: a passage that gets committed stays in git history. Approval is never inferred from silence.
6. **Write.** Before approval, write a draft to read and work from:
   ```sh
   python3 .ai/general/skills/transcript-cleanup/transcript.py write tmp/<slug>.turns.md tmp/<slug>.edits.yaml --out tmp/<slug>.clean.md
   ```
   After approval, apply the PM's changes to the edits file and write the cleaned transcript:
   ```sh
   python3 .ai/general/skills/transcript-cleanup/transcript.py write tmp/<slug>.turns.md tmp/<slug>.edits.yaml --out docs/transcripts/<file> --reviewed-by "<PM name>"
   ```
7. **Verify** with `transcript.py verify docs/transcripts`. Fix errors and pass warnings on to the PM.
8. **File approved facts** with their own skills, e.g. availability in the people directory (people skill).

## The cleaned file

```markdown
---
title: Weekly sync
date: 2026-10-28
cleaned: 2026-10-29
reviewed_by: Jane Doe
raw: docs/transcripts/raw/2026-10-28-weekly-sync.md   # local only
drive_url: https://docs.google.com/document/d/...     # when it came from Drive
format: timed text
speakers: [Jane Doe, Sam Lee]
removed: {audio: 1, small-talk: 2, health: 1}
readers: Lullabot only                                # from .ai/project/transcript-cleanup.md
internal: keep
words: {spoken: 9120, cleaned: 7480}
---
# Weekly sync

*[audio and setup, 00:00:00–00:02:40]*

## [00:02:40] Content freeze date

**[00:02:40] Jane Doe:** We need the content freeze before the 15th.

**[00:03:05] Sam Lee:** That works if QA starts the week after. [removed: health]
```

- Each speaker turn is one paragraph, starting with its timestamp and the speaker label exactly as the transcript gives it. Matching labels to people is the meeting-notes skill's job. A long turn carries an inline `[hh:mm:ss]` at least every two minutes.
- Timestamps match the raw transcript, so a citation to the cleaned file also finds the passage in the original.
- A marker replaces each cut: `*[small talk, 00:10:12]*` for whole turns, `[…]` for a passage of banter inside a turn, and `[removed: <kind>]` for a sensitive passage. A marker names the kind, never what was said.
- `readers` and `internal` record the project's setting when it was cleaned. When the setting changes, `verify` lists the transcripts cleaned under the old one, so the PM can decide which to reclean.
- `words` counts the words spoken in the raw transcript (not its timing lines or a Gemini summary) and what's left after fillers and cuts.

## Rules

- **Cut, never paraphrase.** Every kept word is from the transcript. Only the script changes the text.
- **The raw transcript is read-only.** Never edit or delete it. To change the cuts, prepare from the raw transcript again, edit the edits file, and write with `--force`. If the raw transcript is gone, say so; never edit a cleaned transcript by hand.
- **Commit only cleaned transcripts.** Before the Project Brain is saved to git, `verify docs/transcripts` must pass. A draft, or a file with no `reviewed_by`, is never committed.
