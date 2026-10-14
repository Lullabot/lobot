---
name: dossier
description: Build and keep the project dossier in docs/overview/, a set of linked files (project index, one folder per site, topic files, reference detail) that holds everything known about the project and each site, including the background of a site being migrated or rebuilt. Use when the PM asks a question about the project or a site ("how does X get onto the site?", "what do we know about Y?"), when processed meetings, research, or answered questions add facts, when a site or program starts, and when the PM asks to write, update, or review the overview.
---

# Project dossier

## Why

Meeting notes are a diary: each one holds what was said that day, and a fact learned in week one is buried by week six. Records like risks, questions, and the RACI each hold one kind of thing. Nothing else holds the whole picture of a site: what it is today, who uses it, how its content gets there, what is moving, what is changing, and what is still unknown.

The dossier does. It is the detailed, current account of the work, written so the assistant (or a new PM) can answer a question about the project by reading two or three short files instead of every transcript. It points to the records and notes rather than copying them, and every fact in it says where it came from.

## Where

| What | Path |
|---|---|
| Project index (Level 1, read at session start) | `docs/overview/index.md` |
| Project-wide topic files (engagement, plan, platform…) | `docs/overview/<topic>.md` |
| One folder per site, program, or product | `docs/overview/sites/<site>/` |
| Site index (Level 1 for the site) | `docs/overview/sites/<site>/index.md` |
| Site topic files (Level 2) | `docs/overview/sites/<site>/<topic>.md` |
| Exhaustive or generated detail (Level 3) | `reference/` under the folder it belongs to |
| Templates | `templates/` in this skill's folder |
| Validator | `validate.py` in this skill's folder |

A project with one site still gets `sites/<site>/`, so every project reads the same. `<site>` is a short lowercase slug (`breath-alcohol`). When the project declares scopes (in `docs/raci.yaml` or `docs/sources.yaml`), each site index names its `scope`; one scope can hold several sites. The progressive-disclosure rules in `.ai/general/context-docs.md` apply to every file here.

## Levels

1. **Project index.** One screen: what the project is, the engagement, a **Sites** table (site, scope, one-line status, link), plan and dates, systems, an **Areas** table for project-wide topic files, and known gaps.
2. **Site index.** One screen per site: what the site is and who owns it, the kind of work (new build, migration, rebuild, "lift and shift"), current status, a **Topics** table linking each topic file with a one-line summary, the risks, questions, and decisions that concern the site (by ID), and known gaps.
3. **Topic files.** The detail. A few hundred lines at most; when a topic outgrows that, split it or move the exhaustive part to `reference/`.
4. **Reference.** Inventories, field lists, extracts, page lists. Generated where possible (see context-docs).

## Standard site topics

Write a topic when there is material for it; until then, list it under the site index's known gaps. Add other topics when a site needs them (a site with a public API gets `api.md`).

| File | Holds |
|---|---|
| `current-site.md` | **Background of the site being migrated or rebuilt.** Its purpose and history, who built and runs it, the platform and hosting, how content gets there today (by hand, feeds, scripts), size and inventory (pages, documents, records, years of data), how people reach it, what works, pain points, and anything that must not be lost. Skip only for a site that has no predecessor. |
| `audiences.md` | Audiences in priority order, what each comes to do, top tasks, and how they reach the site. |
| `content.md` | The new site's content and features: pages, content types, search tools, documents, and what is kept, dropped, merged, or new, with the reason. Requested features and changes. |
| `data.md` | Data sources and integrations: what feeds the site, from where, how often, formats, who owns each step, volumes, and retention. |
| `migration.md` | What moves and how: scope and cutoffs, volume, content mapping, cleanup, manual versus scripted work, redirects, and the order of work. |
| `design.md` | Brand and look-and-feel requirements, accessibility requirements, and platform constraints on design. |

## Writing rules

- **Cite every fact.** Each bullet or table row ends with its source in parentheses, using a short label from the file's `sources` frontmatter plus a locator: `(walkthrough 00:28:54)`, `(SOW §3)`, `(Q-012)`. The `sources` map gives each label its path or URL. A fact with no source doesn't go in.
- **Stated vs. inferred.** Write what a source says. Anything inferred is marked *(unverified)* until a person or authoritative source confirms it. Never guess to fill a gap; list it under known gaps or add it to the questions log.
- **Point, don't copy.** People are linked by their `docs/people.yaml` key or named; terms come from the glossary; risks, questions, and decisions are cited by ID (`R-002`, `Q-036`, `D-004`); research notes and meeting notes are linked. Summarize them in a line where it helps the reader; never duplicate their content.
- **Current, with history where it matters.** The dossier says what is true now. When a fact changes, edit it in place and keep the earlier value only when the change itself matters ("estimated 5,000 PDFs at kickoff; about 1,660 after the 5-year cut (walkthrough 00:28:54)").
- **Summaries go up, detail goes down.** An index holds one line per topic. Don't repeat a topic file's detail in the index.
- **No secrets, no personal data** beyond work contact details. Sample records, test results, or anything about members of the public stay out, even when a meeting showed them.

## Frontmatter

```yaml
---
title: Breath Alcohol: the current site
status: draft            # or "reviewed by <name> (YYYY-MM-DD)"
updated: 2026-10-14
sources:
  kickoff: docs/meetings/2026-10-08-kickoff.md
  walkthrough: docs/meetings/2026-10-14-site-walkthrough.md
  pdf-research: docs/research/pdf-accessibility.md
# site index files only:
site: breath-alcohol
scope: bacr
---
```

## Workflows

### Start a site's dossier

When a site or program starts (kickoff, a new SOW), or when the project has none yet:

1. Create `sites/<site>/index.md` from `templates/site-index.md`, and add the site to the project index's Sites table.
2. Seed it from what exists: the SOW, kickoff and walkthrough notes, research notes, the records. Write `current-site.md` first for a migration or rebuild.
3. Run the validator and present the files to the PM for review.

### Add facts

Facts reach the dossier from:
- **Meeting notes.** When processing a meeting, record its facts in the dossier topics they belong to and list the files changed in the notes' "Context updates". (At junior autonomy, propose them in the review list instead.)
- **Research notes** in `docs/research/` and documents in Drive: summarize the findings in the topic they affect and link the note.
- **Answered questions.** When the PM answers a question that fills a gap, update the topic and remove the gap.

Each time, update `updated`, add the source to `sources`, and run the validator.

### Answer a question about the project

1. Read the project index, then the site index, then the topic file the question points to.
2. Answer from the dossier and cite the file (and its source, when the PM may want to check).
3. If the dossier doesn't answer it but a meeting note or record does, answer from that source and propose adding the fact to the dossier.
4. If nothing answers it, say so, and add it to the questions log when only the PM can answer.

### Review

Before a milestone, or when the PM asks, check each site's dossier against the newest meetings and records: facts that changed, gaps now filled, risks and questions closed, files over the size limit. Present the changes as one list.

## Validate

```sh
python3 .ai/general/skills/dossier/validate.py docs/overview
```

It checks frontmatter, that every local source path exists, that every file is linked from the index above it, that relative links resolve, and that each site names a declared scope.

## Who does what

- **Lucy** owns the dossier and writes it without approval by default: she starts site folders, organizes and records facts as material arrives (meetings, research, answers, documents), and keeps sources and gaps current. When she is unsure how to interpret something (what a speaker meant, which of two accounts is right, whether a hedged remark is a fact), she records the fact as *(unverified)* or leaves it out and asks through the questions log. A PM can lower this to junior in `.ai/project/agents/lucy/config.md`.
- **The assistant** reads it to answer the PM's questions, and asks Lucy (or proposes to the PM) when a fact should be added.
- **The PM** reviews it; a file's `status` records who reviewed it and when.
