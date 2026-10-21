---
name: questions
description: Keep the questions log (docs/questions.yaml), the list of outstanding questions, in two kinds kept apart: project questions only the PM can answer (unknown names, unclear owners, scope, schedule, process, and contract questions, values to set), and product questions the team needs a stakeholder to answer (content, copy, design, features). Use when a meeting, document, or task turns up a question the records can't answer, when the PM answers one, and when the PM asks "what do you need from me?" or "what's still open?".
---

# Questions log

## Why

Processing a meeting or mapping a project turns up questions nobody can answer but the PM: a surname, which person a role belongs to, whether a SOW is signed, what severity a risk gets. Left in chat or in a meeting's notes, they get lost. The questions log keeps them in one place, so the PM can answer them in a batch and the assistant can file each answer where it belongs.

The same work turns up product questions the team needs answered by the product owner, designer, or client. The PM doesn't answer those, but needs to see them to chase them. They go in the same log marked `about: product`, so the review desk shows them apart from the PM's own questions instead of burying them.

## Where

| What | Path |
|---|---|
| Questions log | `docs/questions.yaml` |
| Validator | `validate.py` in this skill's folder |

If `docs/questions.yaml` doesn't exist, create it from the format below with no entries. A project that still has the old markdown table (`docs/questions.md`) converts it with the Lobot tool's `migrate` (lobot skill), with the PM's approval.

## Format

```yaml
# Questions log: project questions for the PM and product questions for stakeholders (about: project | product), and their answers. Ordered by ID (Q-001, Q-002, ...); IDs are never reused.
# Managed by the questions skill: .ai/general/skills/questions/SKILL.md
# Validate after every edit: python3 .ai/general/skills/questions/validate.py docs/questions.yaml

Q-001:
  question: "Is \"Me\" in the transcript Sam Lee?"
  scope: all
  raised: 2026-10-09
  source: "docs/meetings/2026-10-08-kickoff.md"
  status: answered
  answer: "Yes (PM, 2026-10-09)."

Q-002:
  question: "What is Alex's surname? (people key is the placeholder unknown-alex)"
  scope: site-a
  raised: 2026-10-09
  source: "docs/meetings/2026-10-08-kickoff.md"
  status: open

Q-003:
  question: "Does the contact form need a phone number field?"
  about: product
  ask: "product owner"
  link: "https://github.com/example/example-site/issues/42"
  scope: site-a
  raised: 2026-10-10
  source: "docs/meetings/2026-10-09-design-review.md"
  status: open
```

| Field | Required | Holds |
|---|---|---|
| key | Yes | `Q-` plus three digits, never reused. The file is ordered by ID. |
| `question` | Yes | One question, answerable on its own: say what is missing and where the answer will go. Quoted. |
| `about` | No | `project` (the default when left out): a question for the PM. `product`: a question the team needs a stakeholder to answer (see "Two kinds of question"). |
| `ask` | No | For a product question: who answers it, as a people key or a role from the RACI. Quoted. |
| `link` | No | For a product question: the ticket where it's logged. Quoted. |
| `scope` | Yes | `all`, or a site or program key when the project declares scopes (the same keys as `docs/raci.yaml` and `docs/sources.yaml`). |
| `raised` | Yes | The date it was logged. |
| `source` | Yes | The file, meeting, or record that raised it. Quoted. |
| `status` | Yes | `open` or `answered`. |
| `answer` | When answered | The answer, with who gave it and when. A partial answer can sit on an open question. Quoted. |

Quote every text field: unquoted text containing `: ` or starting with a special character breaks YAML.

## Who does what

- **Lucy** owns the log: she adds questions from the material she processes and files answers. Adding a question is autonomous for her; it is a request for information, not a change to a record.
- **The assistant** adds questions that come up in other work, puts open ones to the PM when asked, and relays answers to Lucy.
- **The PM** answers project questions, and passes on answers to product questions (or points to where they were given, such as the ticket). An answer is only recorded from the PM (or a source the PM points to); never from silence or inference.

## Two kinds of question

The log feeds the PM's review desk, which shows each kind on its own tab. A question in the wrong kind buries the ones the PM has to answer.

- **Project** (`about: project`, or left out): questions only the PM can answer. Delivery, process, scope, schedule, the contract, who people are, and who does what (including who should answer a question nobody owns yet).
- **Product** (`about: product`): questions the team needs answered about the product (content, copy, assets, design decisions, form fields, features). They belong to the product owner or designer (check the RACI); set `ask` to who answers it. If the question is already logged on a ticket, set `link` to it and keep the discussion there. If it isn't logged anywhere, list it in the report so the assistant can offer to raise it on the right ticket. If nobody owns it, also add a project question: who should answer it.

## Adding a question

1. Decide its kind (above).
2. Check the log first; don't add a duplicate. If an open question covers it, sharpen that one.
3. Check the records the question is about (people, RACI, glossary, overview). If they answer it, it isn't a question.
4. Add the entry with the next ID and run the validator.

Meeting notes keep their own "Open questions" section for what was raised in the meeting; the questions go here, and the notes link to the log.

## Answering

1. Record the answer in the entry and set `answered`.
2. File what the answer changes, in the same pass, through that record's skill (a surname into `docs/people.yaml`, a backup into `docs/raci.yaml`, a severity into `docs/risks.yaml`), and remove any `(unverified)` marker the answer resolves.
3. If an answer is a business decision, run it through the decision-log skill's entry test; if it is a risk, it goes in the risk tracker.
4. Run the validator:
   ```sh
   python3 .ai/general/skills/questions/validate.py docs/questions.yaml
   ```

## Rules

- **Questions, not decisions.** An open question that nobody has chosen an answer to is not a pending decision-log entry. Log it here (or as a risk) until a real choice is made.
- **Never guess an answer.** Partial knowledge goes in the question ("Transcript says Halterman or Alterman"), not in the records.
- **Answered entries stay.** They are the history of how the records got their facts.
