---
name: tickets
description: Standards for writing and organizing tickets in GitHub and Jira, covering titles, descriptions, acceptance criteria, types and labels, links, workflow states, comments, and board hygiene. Use whenever drafting, rewriting, triaging, or auditing tickets, drafting a comment or pull request description for the PM, or reporting on a board.
---

# Tickets

## Why

The ticket system is the team's shared memory of what is being built and why. A clear ticket saves a developer a meeting; a messy board hides risk until it's late. These standards keep tickets readable by everyone who touches them: developers, designers, the client, and the next PM.

Project conventions in `.ai/project/tickets.md` override anything here. When that file doesn't exist and a convention matters (labels, workflow, definition of done), work out what the team already does from the board, write it up there, and ask the PM to confirm.

## Vocabulary

"Ticket" is the neutral word, and the one to use with the PM. In each system, use that system's own term:

| System | Term | Notes |
|---|---|---|
| GitHub | Issue; pull request (PR) | On a GitHub Projects board, issues, PRs, and draft issues are all "items". |
| Jira Cloud | Work item | Called "issue" in Jira Data Center, in JQL (`issuetype`), and in the API. Many people still say "issue". |

Refer to tickets by key: `#123` in GitHub, `PROJ-123` in Jira. Link them in reports.

## Titles

- Say what the ticket delivers or what is wrong, specifically enough to find it in a search a month from now.
- Features and tasks: start with a verb and name the outcome. "Add event date filter to the news listing", not "Filters".
- Bugs: the symptom and where it happens. "Search returns no results when the query has an apostrophe", not "Search broken".
- Keep it short (about 70 characters). Detail goes in the description.
- Don't put the type, priority, or status in the title ("BUG:", "URGENT") when the system has a field for it.

## Descriptions

Write for a developer who wasn't in the meeting. Start from the project's issue template for the ticket type (in GitHub, `.github/ISSUE_TEMPLATE/`), keep its headings, and add the common sections below where they apply. Drop sections that would be empty.

### Order

```markdown
## Description            (or the template's equivalent: Summary, Context and What, steps to reproduce)
## Design concerns        only when the ticket questions or departs from the design
## Questions
## Resources              only when there are external links
## Out of scope           only when it prevents a likely misunderstanding
## Acceptance criteria    always last above the divider
---
## Implementation notes   only when the project uses them
```

**Description.** Why this work exists, who asked for it, and the change described as behavior, not implementation. Bugs add **Steps to reproduce**, **Expected**, **Actual**, and **Environment** (URL, browser, role, data), plus a screenshot or recording when there is one.

**Acceptance criteria.** Testable statements as checkboxes; each passes or fails with no judgment calls. Merge like items into one line and cut anything another line already covers; aim for five or fewer. More than that usually means the ticket should be split. State the requirement, not a proposed fix that hasn't been approved: "Donate Now's text meets 4.5:1 contrast, using colors the designer approves", not "Donate Now uses black text". If criteria need technical knowledge you don't have, draft what you can, mark the gap, and ask the developer. Never invent technical detail.

### Common sections (any ticket type)

**Design concerns.** Add when a ticket questions or departs from the design, limited to accessibility violations you can verify against a specific WCAG criterion, privacy or personal-data problems, and functional gaps (a state, screen, or behavior the design doesn't cover). Leave subjective or unverifiable concerns (a font that looks small, a color you don't like) for user acceptance testing. Developers and PMs suggest; the designer decides (with a design file, there is always a designer who made the call, even when roles vary by project). A numbered list, one item per concern: a bold title that states the problem, then one paragraph with what and why (numbers and the WCAG criterion for accessibility), who raised it, and the suggestion with who made it.

```markdown
1. **Donate Now color contrast ratio is too low**
The comp has white text on green, a 2.27:1 contrast ratio. WCAG 2.2 AA requires 4.5:1 for text (1.4.3), so many visitors with low vision can't read it. Raised by @pm-handle. @dev-handle suggests the design system's primary button, black text on the same green (9.25:1).
```

Credit the person who actually raised it. Every concern also gets a question (below) so its resolution is tracked.

**Questions.** Everything that must be answered before the ticket is ready, as checkboxes, each starting with the @username of the person who has the authority to answer (from the people directory; never guess a username). Business, copy, and naming questions go to the client; design questions go to the designer, or, when the designer isn't on the ticket system, to the client lead to get the designer's decision. Follow the list with this line:

```markdown
*Please update the description, acceptance criteria, and implementation notes as questions are answered.*
```

While questions are open, set the ticket to the status and assignee the project uses for that (in `.ai/project/tickets.md` or `.ai/project/github.md`; often a research or review status, assigned to the client lead). When every box is checked and the ticket reflects the answers, it can move to the team's ready state.

**Resources.** External links only: designs, documents, recordings. Parent, epic, blocking, and blocked-by tickets go in the system's relationship fields (GitHub sub-issues and dependencies; Jira parent and issue links), not in the body.

### Implementation notes (optional per project)

When developers rely on coding agents, ask the PM whether the project's issue templates should end with a `---` divider and an **Implementation notes** section. Above the divider is the work; below it, how to build it, written short enough for a developer to skim and specific enough for an agent to follow:

- the branch to start from and where the pull request goes;
- existing code, components, and config to reuse, by path or name;
- conventions that apply (where config lives, frameworks to use or avoid);
- what not to touch;
- how to verify (commands, preview checks).

Read the code before writing them, and keep design choices out: anything that changes what users see belongs in Design concerns until the designer approves it. Don't make this standard for every project.

### Keeping it current

- Don't use first person (I, we, my, our) for something someone else said or decided: the ticket posts under the PM's account, so it reads as theirs. Cite the person ("decided by @handle", "@handle suggests") or use the passive voice ("This ticket assumes ...").
- When scope changes in a comment thread, update the description and note the change with a date, so readers don't have to reconstruct it from comments.
- Client-visible tickets contain no internal notes, budget talk, or Project Brain paths.

## Size

One ticket is one deliverable that one person can finish and that can be tested on its own. When a ticket bundles several, propose splitting it into child tickets under a parent (GitHub sub-issues; a Jira epic or parent work item). When two tickets describe the same work, propose closing the newer one as a duplicate, linking the original, and carrying over anything it adds.

## Types, labels, and fields

- Use the team's existing taxonomy. Never invent a label; propose one to the PM with the reason.
- Prefer a real field over a label: issue types and work item types, priority, components, sprint, estimate. Labels are for what has no field.
- A few labels per ticket at most. A label that's on everything means nothing.
- Fields that drive reports (status, assignee, sprint, estimate) must be right. A wrong field is worse than an empty one.

## Links

- **Ticket to pull request.** GitHub: "Closes #123" (or Fixes, Resolves) in the PR description links it and closes the issue on merge. Jira: put the key (`PROJ-123`) in the branch name, PR title, or commit message so it appears in the development panel.
- **Parent and child.** Every child has exactly one parent. Don't link the same work into two hierarchies.
- **Dependencies.** "Blocks" / "is blocked by" when one can't finish before the other. "Relates to" is weak; use it only when nothing stronger fits.
- **Decisions.** When a decision affecting a ticket was made elsewhere (meeting, chat), add a short comment saying what was decided, by whom, and when. Tell the assistant so it can be recorded in the decision log too.

## Workflow

- Status reflects reality. A ticket is "In Progress" when someone is working on it, not when it's planned.
- One owner. The assignee is the person responsible for the next step. Don't assign someone without their or their lead's agreement.
- Don't skip states the team uses (for example, moving straight to Done past review or QA) without saying why in a comment.
- Done means the team's definition of done (in `.ai/project/tickets.md`). Merged is not necessarily done.
- Reopen with a comment that says what failed and how to see it.

## Comments

Every comment should do one job: answer a question, ask one, record a decision, explain a status change, or hand off. Then stop.

- Lead with the point. Put any background after it.
- @mention only the people who need to act, and say what you need from each and by when.
- Ask specific questions. Not "any update?" but "Is the API change still on track for Thursday's build, or should we move PROJ-123 to next sprint?"
- No "+1", "bump", or comments that only restate the status field.
- Long thread? Post a dated summary of where things stand and what's open, and update the description.
- Never edit someone else's comment. Correct your own with a visible note, not a silent rewrite.
- Comments posted under the PM's account are drafted in their voice (pm-voice skill).

## Pull request paperwork

You don't review code. You do make sure each PR:

- links its ticket (see Links);
- has a description that says what changed, why, and how to test it;
- has a reviewer requested, per the team's rules;
- moves its ticket to the right status when it opens and after it merges.

## Hygiene audit

When asked to audit a board or sprint, check for:

- **Stale:** no update in longer than the team's threshold (`.ai/project/tickets.md`; default 7 days for "In Progress" and "In Review").
- **Unowned:** in progress or review with no assignee or reviewer.
- **Unclear:** no description or acceptance criteria in a "Ready" column or the current sprint.
- **Orphaned:** open PRs with no linked ticket; tickets marked done with an open PR, or open with a merged one.
- **Duplicates** and tickets that belong under an existing parent.
- **Overload:** one person with more in progress than the team's limit.

Report findings ranked by how much they slow the team down, with keys and links, and a proposed fix for each. Don't fix anything without approval unless the area is autonomous.

## Approvals

Anything the team or client can see is a change and follows the github skill's approval rules (and the jira skill's, when the project has one): show the exact change, wait for explicit approval, make it, confirm with a link. Reading is always free.
