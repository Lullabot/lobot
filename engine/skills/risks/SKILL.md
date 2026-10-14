---
name: risks
description: Keep the risk tracker (docs/risks.yaml), the project's risks with a short summary, severity, status, the people who confirmed them, a next step, and dated updates. Use when a meeting or document raises a risk, when something changes an existing risk, when the PM sets a severity or closes a risk, and when the PM asks what could go wrong or what the open risks are.
---

# Risk tracker

## Why

Risks come up in passing: a launch date over the holidays, a data feed nobody has built, a contract that isn't signed. Unless each one is written down with who raised it, how bad it is, and what happens next, it gets lost until it turns into a problem. The risk tracker keeps them in one place, and its dated updates show how each risk developed, so the PM can report on it and act early.

## Where

| What | Path |
|---|---|
| Risk tracker | `docs/risks.yaml` |
| Validator | `validate.py` in this skill's folder |

If `docs/risks.yaml` doesn't exist, create it from the format below with no entries. A project that still has the old markdown table (`docs/risks.md`), or entries whose `risk` is a long text from an earlier version, converts them with the Lobot tool's `migrate` (lobot skill), with the PM's approval; dated additions in the old risk text become updates, and the rest is split into a short `risk` and a `description`. The short version is taken from the start of each risk, so reread them with the PM and reword any that read badly.

## Format

```yaml
# Risk tracker: project risks, each confirmed by a named person. Ordered by ID (R-001, R-002, ...); IDs are never reused.
# Managed by the risks skill: .ai/general/skills/risks/SKILL.md
# Validate after every edit: python3 .ai/general/skills/risks/validate.py docs/risks.yaml

R-001:
  risk: "Launch window falls over the holidays"
  description: "The client's funding depends on launching by year end, which leaves no slack if the launch slips past the holidays."
  scope: all
  severity: High
  status: Open
  raised: 2026-10-08
  source: "docs/meetings/2026-10-08-kickoff.md (00:31:10)"
  confirmed_by: "Sam Lee, Ana Ruiz"
  next_step: "PM and Sam Lee to agree a launch date with the client."
  updates:
    - date: 2026-10-14
      source: "Schedule Sheet"
      note: "The schedule marks the last two weeks of December as a change freeze."
```

| Field | Required | Holds |
|---|---|---|
| key | Yes | `R-` plus three digits, never reused. The file is ordered by ID. |
| `risk` | Yes | A short summary of the risk, one line of at most 80 characters, that makes sense on its own in a list ("Launch window falls over the holidays"). Quoted. |
| `description` | No | What could go wrong and why it matters, as first confirmed. Keep it to the risk itself; later developments go in `updates`. Leave it out when the summary says it all. Quoted. |
| `scope` | Yes | `all`, or a site or program key (the same keys as `docs/raci.yaml`). |
| `severity` | Yes | `High`, `Medium`, `Low`, or `TBD` until the PM sets it. |
| `status` | Yes | `Open`, `Monitoring` (no action needed now, watching it), or `Closed`. |
| `raised` | No | The date it was first raised. |
| `source` | Yes | Where it was raised: meeting notes file and timestamp, document, or who stated it. Quoted. |
| `confirmed_by` | Yes | The people who confirmed it is a risk, by name, comma-separated. Quoted. |
| `next_step` | When open | Who does what next. Quoted. |
| `updates` | No | Dated developments, oldest first: `date`, `note`, and `source` when it isn't obvious. Add an update rather than rewriting `description`. |

Quote every text field: unquoted text containing `: ` or starting with a special character breaks YAML.

## Who does what

- **Lucy** proposes new risks and updates from the material she processes (meeting-notes skill), only when a speaker or document raised them, with a quote or timestamp. Writing them is junior for her by default: she proposes, the PM approves.
- **The assistant** raises a risk it notices that nobody named in chat; it goes in the tracker only if the PM confirms it, attributed to the PM.
- **The PM** confirms risks, sets severity and status, and closes them.

## Changing the tracker

1. Check the tracker first; a new development of an existing risk is an update to it, not a new risk.
2. Add or change the entry. A new risk gets the next ID and `severity: TBD` unless the PM set one; add a question to the questions log for the severity if the PM isn't there to set it.
3. Closing a risk: set `status: Closed` and add an update saying why, who decided, and when.
4. Run the validator:
   ```sh
   python3 .ai/general/skills/risks/validate.py docs/risks.yaml
   ```

## Rules

- **Confirmed, not inferred.** A risk is listed only when a named person raised or confirmed it. Never infer a risk from silence or from the assistant's own reading.
- **Updates, not rewrites.** The history of a risk is its updates. Correct a mistake in place, but add new facts as updates.
- **Short summaries.** `risk` names the risk; `description` explains it. If the summary needs a second sentence, move it to the description.
- **Closed risks stay.** They show what was managed.
