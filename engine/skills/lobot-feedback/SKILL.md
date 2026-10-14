---
name: lobot-feedback
description: Notice ways Lobot itself could be better (a bug, a missing rule, a correction that applies to any project) and offer to report them as an issue on Lobot's repository. Use when the PM corrects an agent in a way that would help every project, a skill, template, script, or rule misbehaves or is missing something, a workaround for Lobot's own behavior comes up twice, or the PM says "report that to Lobot" or "file an issue for Lobot".
---

# Lobot feedback

## Why

Lobot gets better when the people using it on real projects tell its maintainers what works and what doesn't. Training an agent or hitting a rough edge is exactly when a PM learns something every other project could use. This skill makes that easy: the assistant notices the opportunity, offers to report it, and does the writing. The PM only approves.

## Notice

Watch for these during any task, including when training an agent:

- The PM corrects an agent or the assistant and the lesson is not about this project (it would apply to any Lullabot project). Log the correction as the agent's instructions say, then consider reporting it.
- A skill, template, page, script, or validator fails, gives a wrong result, or does something the PM has to work around.
- A rule is missing, unclear, or contradicts another one, and the assistant had to guess.
- The same project-specific workaround for Lobot's own behavior is needed a second time.
- A change was made in `.ai/general/` (see the lobot skill, "Local changes").

Skip anything about the project itself (its people, its clients, its tools). That belongs in `.ai/project/` or `docs/`, not in Lobot.

## Offer

- Wait for a natural pause, after the task at hand is done. Never interrupt work to suggest a report.
- Make one short offer per topic, naming the problem and what you'd ask Lobot to change: "That correction applies to any project. Want me to report it to Lobot?"
- If the PM says no, don't offer that topic again this session. If several things come up in a session, offer them together at the end, not one by one.
- An agent can't ask the PM (see `delegation.md`). It lists candidates in its report, and the assistant makes the offer.

## Draft

1. Find the installed Lobot version (`.ai/general/.lobot-version`).
2. Check for an existing report, so Lobot's maintainers don't get duplicates:

   ```sh
   gh issue list -R Lullabot/lobot --state all --search "KEYWORDS" --limit 10
   ```

   If one matches, offer to add a comment to it instead (what you saw, in general terms).
3. Write the issue in general terms. Lobot's repository is public: no client or project names, no people, no URLs, no ticket numbers, no credentials, and no quotes from meetings or documents. Describe what happened in plain, general terms ("a list of product questions was put on the PM's desk") rather than who said what.

   ```markdown
   Title: one line saying what should change, e.g. "Lucy: only put questions on the PM's list that the PM can answer"

   **Lobot version:** 0.15.1
   **What happened:** What the assistant or agent did, and what the PM expected instead.
   **Suggested change:** The rule, fix, or addition, naming the file in `engine/` when known (this project's `.ai/general/<path>` is Lobot's `engine/<path>`).
   **Why it matters:** What it costs the PM today.
   ```
4. Pick one label: `bug` for something broken, `enhancement` for something to add or change, `documentation` for wording.

## File

Anything visible to other people needs the PM's approval (see the github skill, "Writing"). Show the PM the exact title, label, and body, say it will be posted under their GitHub account, and wait for a yes.

1. With `gh` working (github skill, "Setup"), create it:

   ```sh
   gh issue create -R Lullabot/lobot --title "…" --label enhancement --body-file issue.md
   ```

   If GitHub refuses the label, because the PM can't set labels there, create it again without `--label`. Delete `issue.md` afterwards.
2. Without `gh` or a login, give the PM the finished text to paste at https://github.com/Lullabot/lobot/issues/new, or a prefilled link built from the URL-encoded title and body. Anyone with a GitHub account can open an issue on a public repository.
3. Give the PM the issue's link. Journal it with `#brain-kit` (what was reported and the link).
4. Keep a general correction in the project's corrections log until a Lobot release brings it in. The update then makes the local note redundant.

## Never

- Never post, comment, or label without the PM's approval of the exact text.
- Never open a pull request from a Project Brain with this skill. A change that is ready to go back as a pull request follows the lobot skill's "Contribute".
- Never use someone else's token without telling the PM whose account the issue will appear under.
