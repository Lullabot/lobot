# Ticket plans

Part of the tickets skill (`SKILL.md`). The format of a ticket plan, the one tracker-neutral file a batch of tickets is drafted in before it is previewed (ticket-preview skill), approved, and sent with the tracker's skill.

## Ticket plans

Tickets that come in a batch, such as the `ready` items of the work breakdown, are drafted as one **ticket plan**: a YAML file with the same shape whichever tracker the project uses. Pepper drafts it, the PM reviews it on the ticket preview page (ticket-preview skill) and approves it, and the tracker's skill checks it against the tracker and sends it. Show the plan on that page before asking for approval, and again after every change.

- **Where:** `docs/work/tickets/YYYY-MM-DD-<slug>.yaml`. After sending, `PLAN.created.json` beside it records the ticket each `ref` became.
- **The tracker's own names.** Work types, labels, statuses, and extra fields use the names the tracker uses, from its project file: the structure file `.ai/project/jira/<SPACE>.yaml` for Jira (jira skill), `.ai/project/github.md` for GitHub (github skill). If that file is missing or doesn't have what a ticket needs, say so rather than guessing.
- **Everything else is neutral:** titles and descriptions follow this skill, and people are people-directory keys, turned into usernames or account IDs only when the plan is sent.

```yaml
destination: Jira, space ABC          # the human-review stamp (.ai/general/human-review.md); never sent
sources: [docs/work/site/search.md]
status: draft                         # approved_by: and approved_at: are added on the PM's approval
tracker: jira                         # jira or github, as recorded in .ai/project/tickets.md
project: ABC                          # a Jira space key, or a GitHub OWNER/REPO
items:
  - ref: search-epic                  # a new ticket: a name used only in this plan
    type: Epic                        # the tracker's work type or issue type
    title: Event search
    description: |                    # markdown, to this skill's standards
      ## Description
      …
  - ref: date-filter
    type: Story
    parent: search-epic               # a ref earlier in the plan, or an existing ticket
    title: Add an event date filter to the news listing
    labels: [search]
    assignee: doe-jane                # people-directory key
    blocked_by: [date-index]          # refs or existing tickets; `blocks:` works the same way
    fields:                           # anything else, under the tracker's own field names
      Story point estimate: 3
    description: |
      …
  - key: ABC-7                        # an existing ticket ("#123", quoted, on GitHub): only what's given changes
    status: In Progress
    comment: |                        # markdown, posted as a comment
      …
```

| Key | Means |
|---|---|
| `ref` or `key` | A new ticket (a name used only in this plan) or an existing one. Every item has exactly one. |
| `type`, `title`, `description` | The ticket itself. |
| `parent` | Its parent: a ref earlier in the plan, or an existing ticket. One parent per ticket (see Links). |
| `labels`, `assignee` | As the team uses them. A list given for an existing ticket replaces the whole list. |
| `blocks`, `blocked_by` | Dependencies, as lists of refs or tickets. Other relationships the tracker has go under `links:` in its own wording (`- relates to: ABC-9`). |
| `status` | The status to move it to after creating or updating it. |
| `comment` | A comment to post. |
| `fields` | Any other field, under the tracker's own name for it. |

Sending a plan to Jira: the jira skill's "Sending". It's checked first, with every problem coming back as a question; it's sent only once the PM has approved it and it's stamped; and a run that stops partway can be run again without making anything twice. GitHub has no way to send a plan yet: tell the PM, and if they ask, create the tickets one at a time with the github skill's "Writing".
