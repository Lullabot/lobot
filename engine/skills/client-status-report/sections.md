# Optional sections

The menu for building a project's status report template (client-status-report skill, "Set up the report"). The default template covers what every client needs. These are the additions and changes PMs have found useful; offer them one group at a time, with the question in each group's heading, and add only what the PM picks. Each entry says where its content comes from, so the drafting step knows what to gather.

## Who reads it, and how long should it be?

Ask this first: it decides the rest. A sponsor who skims needs a short report that ends at Key dates. Product owners and editors often want the detail, which belongs at the end (an appendix) so the first page stays short.

- **Contents.** A linked table of contents after the summary. Worth it once the report runs past two pages, usually because of an appendix. Source: the template's headings.

## How do you show overall status?

- **Status color.** A line under the summary: 🟢 On track, 🟡 At risk, or 🔴 Off track, with one line on why when it changes. The PM picks the color every week; the assistant only suggests a change, with reasons. Source: the PM, last week's color, open High risks and slipped dates.
- **Week number.** "Week N" in the date line, counted from the date in the settings. Helps long engagements and clients who count weeks.

## How should progress be organized?

Pick one; the default is a single list.

- **By workstream.** One short block per workstream (development, content migration, training…), each a sentence or two. Suits programs with parallel teams. Source: as Progress, sorted by workstream.
- **By discipline.** Strategy, Design, Development, Content. Suits design and build phases where each discipline has its own deliverables.
- **By site or scope.** One block per scope, for a multi-site project that sends one report. Source: as Progress, split by the scope keys in `docs/sources.yaml`.
- **Workstream status tables.** Instead of bullets, a table per workstream grouped as Completed this week, In progress, Blocked, and Up next, with a status column (✅ Complete, 🔄 In progress, 🔄 In review, 🚫 Blocked, or a target date). Keep each row to one line of plain language, not a ticket title. Source: the sprint board or ticket system (jira or github skill), journals.
  ```markdown
  | Timeframe | Item | Status |
  | :-- | :-- | :-- |
  | **Completed this week** |  |  |
  |  | Plain-language item | ✅ Complete |
  | **In progress** |  |  |
  |  | Plain-language item | 🔄 In review |
  | **Up next** |  |  |
  |  | Plain-language item | October 21 |
  ```

## What about the sprint and the tickets?

- **Sprint.** Under Key dates: the current sprint's name and week ("Sprint 12, week 2"), with links to the board and timeline. Source: the ticket system.
- **Release notes appendix.** At the end, under a heading of its own: what was deployed this week, what is done and waiting for the next release, and other completed work, each ticket as its key and title with one line in plain language saying what changed for the client ("Editors can add icon lists to landing pages."), plus which sites it affects on a multi-site platform. Group by work type (stories, tasks, bugs) when lists get long. Source: the ticket system (jira or github skill) for the window, and the release or changelog tooling the team uses. The outcome line comes from the ticket's acceptance criteria; ask the PM when a ticket has none.
  ```markdown
  ## Released this week

  1. [KEY-123](link) Ticket title
     Sites: **Site A, Site B**
     *What changed, in one sentence a client editor would understand.*

  ## Done, waiting for the next release

  ## Other work completed
  ```

## Do you want forecasts?

- **Forecast.** Open work over time and a projected completion date for the next milestone, based on the team's recent throughput (for example a four-week rolling average of items finished), per discipline or workstream, with two or three bullets reading the chart: who's ahead, who's behind, and what it means for the date. Valuable in the run-up to a launch; noisy otherwise. Charts follow the dataviz guidance where the assistant has it; the numbers come from a script, never mental arithmetic. Source: the ticket system's created and resolved dates.
- **Priorities.** A short list of the current epics or initiatives in priority order, flagging any change since last week and any conflicting priorities. Source: the ticket system, decisions.

## Anything else the client should see?

- **Decisions this week.** Decisions made in the window, each in one line with who approved it. Source: `docs/decisions.yaml` (made in the window, and agreed for the client to see).
- **Key insights and developments.** A few bullets of interpretation that no other section carries: a pattern the team noticed, a need that's emerging, a direction being weighed, a lesson worth keeping. Each says why it matters and whether it needs anything yet ("a planning-horizon item, not urgent"). Source: journal Thoughts, meeting notes, the PM.
- **Budget and hours.** Hours or budget used against the plan, as of the report's date. Only when the contract or the client expects it, and only figures the PM supplies or approves. Source: the PM.
- **Dashboard link.** A closing line linking the project's progress dashboard. Source: settings.

## Rename or drop a default section

Any default section can be renamed (for example "Accomplishments this week" for Progress) or dropped (for example Team availability, when the client tracks a shared calendar). Keep Summary, Risks and issues, and Needs your attention unless the PM insists: they are what a client acts on.
