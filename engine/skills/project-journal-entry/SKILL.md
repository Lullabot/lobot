---
name: project-journal-entry
description: Draft the PM's weekly Project Journal Entry (PJE) for Lullabot leadership from the daily journals and the last entry in the project's journal doc. Use when the PM asks for their PJE, journal entry, weekly entry, or weekly status for leadership, and when they paste or point to a past entry.
---

# Project journal entry

## Why

Every week each Lullabot PM writes a Project Journal Entry (PJE) for leadership: how the project is doing, what went wrong, where there may be more work, and what other projects could use. Account managers read it to keep a pulse on the account; others read it to spot problems they can help with and work worth sharing. The daily journals (journal skill) already hold the week, so the assistant drafts the entry from them and the PM spends their time correcting it, not writing it from scratch.

## Who reads it

| Reader | What they look for |
|---|---|
| The project's account manager (primary) | Status, problems with the client relationship, and opportunities for more work |
| The architecture lead | Architecture problems to escalate, and solutions other projects could reuse |
| The principal PM or CS lead | Requests for CS resources, and PM problems where advice would help |
| A partner PM, on a project run alongside a CS or LSM project | Anything that affects the shared work |

The names for this project are in its settings file (below), looked up in `docs/people.yaml`. Write so each reader finds their part fast: a problem that needs one of them says so and names them.

## Where

| What | Path |
|---|---|
| The journal doc | A Google Doc per project, newest entry at the top, usually in Lullabot's own Drive rather than the client's. It is the only record of past entries: read it, don't copy it into the Project Brain. Lucy records its link in `docs/sources.yaml` as the `project-journal` source (drive-sources skill). |
| This week's draft | `tmp/project-journal-entry.md`, a working file the PM copies into the journal doc. Cleared at session close like everything in `tmp/`. |
| Entry template | `template.md` in this skill's folder |
| Project settings: account manager, other readers, due day | `.ai/project/project-journal-entry.md`, created from `settings-template.md` in this skill's folder on first use |

## The entry

Sections, in this order. Each is a few short bullets in the first person. A quiet week gets one line ("No new problems."), never an empty heading.

| Section | What goes in it | Where it comes from |
|---|---|---|
| **Status** | 🟢 Green (on track), 🟡 Yellow (at risk; needs attention), or 🔴 Red (off track; needs leadership's help). When it changes from last week, one line on why. | The PM, confirmed every week (see step 6) |
| **Progress & Milestones** | What got done or moved: launches, demos, deliveries, process changes that stuck, team changes. Outcomes, not a task list. | Journal Summary and Log lines, decisions recorded in `docs/decisions.yaml` in the window, meeting notes |
| **Problems/Risks** | What's in the way or worrying: client friction, blockers, risks, process trouble, budget or timeline pressure. Say what's being done about each, and who is needed if it's a reader. For a slipped date or a scope change, say whether it's still inside what pays for the work (the funding deadline, the SOW's hours or budget): that tells leadership how worried to be. | Log lines tagged `#risk` or `#blocker`, Open threads, risks added or updated in `docs/risks.yaml`, problems still open from the last PJE |
| **Opportunities** | New chances beyond the current scope that the account manager may not know about yet: an extension, new work, a renewal signal, a Lullabot tool or service the client could use. | Log lines tagged `#opportunity`, opportunities still open from the last PJE |
| **Things to Share with the Group** | What other projects could use: a reusable tool, a pattern, a contrib candidate, a process experiment, a lesson. Also news that affects Lullabot beyond this project (spare budget, a team member freeing up). | Log lines tagged `#share`, Thoughts |
| **Other Notes** | Anything worth saying that fits nowhere else. Optional: leave the heading out when there is nothing. | Thoughts, the PM |

## What belongs in the entry

The readers are Lullabot leadership, not the delivery team. Every bullet has to pass one test: **would a reader act on it, change how they see the project or account, or reuse it?** If not, it stays out, however true or important it is to the team.

| Leave out | Unless |
|---|---|
| Code-level issues already tracked in the issue tracker: security findings, bugs, tech debt, permissions | It needs a reader's help, or it has become an account problem (the team or client disagree about fixing it and the PM is mediating, or it leaves real exposure) |
| Internal problems the team already recognizes and is working through, that no reader can help with | They are stuck and need someone above the team |
| The opinions of the client's own staff or end users (people a level below our client contacts) | One line as a signal of whether the work is landing ("the volunteers who will use it were receptive"), with no detail |
| Staffing, hours, and schedule the account manager and the PMs who need it already know | It changed in a way leadership doesn't know about, or needs a decision |
| One-off workarounds for a situation that shouldn't have happened, however clever | Never in Things to Share; mention the work in Progress if it moved the project |
| Asks the PM is already making of leadership somewhere else ("I'm raising it at the roundtable", a staffing request) | The entry is where the ask is made |
| Work already planned with the client, owned by another Lullabot team (such as more sites coming onto a shared platform), or already in a drafted or pending SOW, proposal, or estimate | It's news to the account manager, or the client's interest in it changed (a signal to sign, expand, or drop it); ask the PM before listing it as an opportunity |
| SOW terms, assumptions, and fixed dates the account manager already knows (a launch date that holds whatever content is ready, a cap on hours) | Something has put them at risk, or they changed |

Call out generously anything that could lead to more work: an idea the client is excited about, a phase that was tabled, a backlog the client wants. Those are what the account manager reads for.

## Draft a PJE

1. **Settings.** Read `.ai/project/project-journal-entry.md`. If it doesn't exist, create it from `settings-template.md` and ask the PM for the account manager, then the rest when it matters. Look people up with the people skill.
2. **Find the journal doc.** Look up the `project-journal` source in `docs/sources.yaml`. If it isn't there, ask the PM for the doc's link and have Lucy add it (drive-sources skill, "Add or change a source"), so next week starts from it.
3. **Read the last PJE.** It is the newest entry at the top of the journal doc. Read it with the Drive connector (read only). Without a connector, ask the PM to paste it. Its date starts the window and its contents are what carries forward. If its date is today, the PM has already written this week's entry; ask before drafting another.
4. **Set the window.** Read every daily journal dated after the last PJE, up to today. Use the last PJE's date, not "the last seven days", so a skipped week isn't lost. With no journals in the window, say so and draft from the records and the PM's answers.
5. **Gather.** From the window: journal Summaries, Log lines (by tag), Thoughts, and Open threads; risks and decisions added or changed; meeting notes. From the last PJE: its status, and every problem and opportunity still open. Carry each of those forward with what changed ("Still waiting on the hosting decision; nudged again Tuesday"), drop it if it's resolved (and say so once, in Progress), or ask the PM if the journals don't say.
6. **Propose the status.** Start from last week's color. Suggest a change only with reasons from the window (a new high-severity risk, a missed milestone, a blocker past a week, client escalation), and give them. The PM picks the color; never change it without asking, and ask even when nothing points to a change.
7. **Draft in the PM's voice** (pm-voice skill), using the "By context" section for project journal entries if the profile has one. If the PM has no voice profile, their past entries in the journal doc are the best samples there are; offer once to learn their voice from them. Keep the entry short: leadership reads a dozen of these.
8. **Review with the PM.** Apply "What belongs in the entry" before showing anything, and drop any bullet that only restates the SOW, a pending proposal, or something else the account manager already has. Write the draft to `tmp/project-journal-entry.md` from `template.md` and show it in chat as one fenced `markdown` code block, so the PM can copy and paste it as is (Google Docs takes it with Edit › Paste from Markdown). Show every revised draft the same way. After the block, list what to check before it goes out: names, dates, numbers, the status color, and anything said about the client or a teammate. Nothing goes into the entry that the PM hasn't seen; an observation of the assistant's own (a risk, a pattern) is raised in chat and goes in only if the PM confirms it, in the PM's words.
9. **Publish.** If the assistant can edit Google Docs, offer to add the entry at the top of the journal doc, and do it only after the PM approves the final text. Otherwise show the approved text again as one fenced `markdown` code block for the PM to copy into the doc: the dated heading, the section headings, and bullets, nothing else. The draft is finished once it's in the doc, so the session close can clear it. If the PM then edits the entry in the doc, read it back: file new facts in their records (step 10), and offer voice traits from the edits (pm-voice skill).
10. **File and log.** A problem, risk, decision, or task that came up while drafting and isn't in its record yet goes there with its skill, with the journal or meeting it came from as its source. Add a journal Log line: `- Drafted the project journal entry for YYYY-MM-DD. Why: weekly report to leadership.`

## Writing rules

- First person, short bullets, one idea each. Lead with what happened, not the effort.
- Candid. This is an internal report: say plainly what's frustrating or at risk, but keep it professional about the client and never blame a teammate.
- Name people as they are in `docs/people.yaml`, and credit teammates for their work.
- Never invent progress, problems, or numbers to fill a section; one line saying there's nothing new is fine.
- No secrets, credentials, or client data beyond what leadership needs to know.
- Once an entry is in the journal doc, corrections go in the next week's entry.
