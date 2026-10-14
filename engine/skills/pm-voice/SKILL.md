---
name: pm-voice
description: Write drafts in the PM's own voice, and learn that voice. Use whenever the assistant drafts something the PM will send or publish as themselves (status updates, client email, Slack posts, tickets, agendas, proposals), when the PM says "learn my voice" or points to writing samples, when the PM edits or rewrites a draft, and when a new PM joins the project.
---

# PM voice

## Why

Anything the PM sends goes out under their name. A draft that sounds like the assistant, or like nobody, costs the PM a rewrite and can cost them credibility with the client. Every PM writes differently, so Lobot ships a neutral base voice and learns each PM's real voice from their own writing, one approved change at a time. A PM's voice is theirs on every project, so it is kept in their personal profile (pm-profile skill), with only what differs on a given project kept in that project.

## Where

| What | Where |
|---|---|
| Base voice, used until a PM has a profile | `base-voice.md` in this skill's folder |
| Template for a new profile | `template.md` in this skill's folder |
| The PM's own voice, on every project | `~/.lobot/voice.md` (see the pm-profile skill for the folder's rules) |
| What differs on this project (a client's register, a team's norms), one file per PM | `.ai/project/voice/<people-key>.md`, keyed like `docs/people.yaml` (`lastname-firstname`). Holds only the differences. |

## Which voice to use

1. **Work out who the draft is for.** A draft is written as the PM it will go out under. If it's unclear which PM that is (co-PMs, a handoff, a new session), match the git user or the people directory, and ask if that doesn't settle it.
2. **Build their voice in layers**, each one overriding the one before where they disagree:
   1. `base-voice.md`;
   2. `~/.lobot/voice.md`, if it exists, can be read, and belongs to this PM (pm-profile skill, "Reading it");
   3. `.ai/project/voice/<people-key>.md`, if it exists.

   If the draft goes out under someone other than the person at this computer (a co-PM, a handoff), skip layer 2 and use their project file. With no profile in layer 2 or 3, use the base voice and offer once per session to learn the PM's voice.
3. **Fit the context.** The profile's "By context" section says how the PM writes each kind of thing (tickets, client email, team chat) and for each audience (a client executive, the dev team). Use the section that matches the draft; a project file's section beats the personal one. The voice stays the PM's; only the register changes.
4. **No assistant personality** in a draft. Lobot's personality (`.ai/general/personality.md`) is for talking to the PM, never for writing as them.

## Drafting rules

- **Facts first, voice second.** Voice never changes a fact, date, number, or commitment, and never adds one.
- **Never invent quotes or attributions.** If the PM's style uses quotes (a quote of the week, a client's own words), use real ones with their source, or leave a marked placeholder: `[QUOTE: source needed]`.
- **Mark what to verify.** After the draft, list the names, dates, figures, and links the PM should check before sending.
- **Follow the profile's "Avoid" list strictly.** It is usually the quickest way a draft stops sounding like the PM.
- **Disclosure.** Lullabot policy requires disclosing substantially AI-written published content (articles, thought leadership, proposals). For those, say so to the PM and offer to work as an editor on their outline or draft instead.

## Learn from samples

When the PM says "learn my voice" or points to their writing:

1. Ask for, or find, 3 to 10 pieces the PM wrote themselves and sent: status updates, client emails, Slack posts, tickets. Prefer recent work and a mix of audiences. Drafts the assistant wrote and the PM barely touched are not samples.
2. Read them and note patterns, each with the sample it came from: length, structure, openings and sign-offs, formality, humor, recurring phrases, words they never use, how they deliver bad news, how they ask for decisions.
3. Write a proposed profile from `template.md`. Keep only patterns seen in at least two samples; note single sightings as "possible".
4. Show the PM the profile, with one or two lines of sample evidence per trait. Save it only once they approve. Never infer approval from silence.
5. Save the general traits to `~/.lobot/voice.md` and anything specific to this project to the project file, asking where anything unclear belongs (pm-profile skill, "Saving to it"). The evidence you showed the PM stays in the chat: the personal file gets no excerpts from project material.
6. Log it in the journal (without the excerpts).

A PM can also bring a writing-style profile from another tool. Treat it as a sample set: map it onto the template, confirm it with the PM, and save it the same way. The files in `~/.lobot/` and the Project Brain are the source of truth, not the other tool.

## Learn from edits

When the PM edits, rewrites, or rejects a draft:

1. Compare the draft with what they actually sent or kept.
2. Separate **voice** changes (wording, tone, length, structure) from **content** changes (facts, scope, what to say). Only voice changes belong in the profile.
3. If the voice change is a pattern rather than a one-off, propose one line for the profile ("Avoid: 'circle back'. Seen in 2 edits.") at the end of your reply, and say where it would go: everywhere, or just this project, and for every kind of writing or only one ("Tickets: no greeting"). One proposal per edit, at most.
4. Apply it only when the PM approves, in the place they chose, and add it to that file's change log with the date.

Don't propose a change from a single edit when the reason could just be that day's context. Wait for it to repeat, or ask.

## Keeping profiles honest

- **Refine, don't accumulate.** When a new trait contradicts an old one, replace the old line and log the change.
- **Excerpts stay short** (one or two sentences) and contain no secrets or personal data. Never copy whole emails into a profile. Excerpts from project material go only in the project file; `~/.lobot/voice.md` describes traits without quoting project work.
- **New contexts as they come up.** When the PM's voice differs for a kind of writing the profile doesn't cover yet, add a heading for it under "By context" rather than bending another section to fit.
- **A profile belongs to its PM.** On a handoff the new PM brings their own `~/.lobot/voice.md` and gets their own project file; the old project file stays for reference with `status: former`.
- **Older projects.** A project set up before the personal profile may hold a PM's whole voice in `.ai/project/voice/`. The pm-profile skill's "Bringing it along" moves the general part to `~/.lobot/voice.md`.
