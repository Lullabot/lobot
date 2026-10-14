# Changelog

## [0.16.0](https://github.com/Lullabot/lobot/compare/v0.15.1...v0.16.0) (2026-10-14)

### Added

* **engine:** the assistant now offers to report Lobot bugs and lessons from training agents as issues ([db592d2](https://github.com/Lullabot/lobot/commit/db592d23eb16cce524bd8cc5670628524b7f39ae))

## [0.15.1](https://github.com/Lullabot/lobot/compare/v0.15.0...v0.15.1) (2026-10-14)

### Fixed

* **engine:** review desk cards are easier to scan, with each item's details down the left and sources and IDs as a footnote under the buttons ([6a6226f](https://github.com/Lullabot/lobot/commit/6a6226f1ee1463e240238aa44aa8f09574954bd5))

## [0.15.0](https://github.com/Lullabot/lobot/compare/v0.14.0...v0.15.0) (2026-10-14)

### ⚠ BREAKING CHANGES

* **engine:** each risk is now a short one-line summary with the detail in a separate description, and your existing risks are split for you

### Added

* **engine:** each risk is now a short one-line summary with the detail in a separate description, and your existing risks are split for you ([d1a3b56](https://github.com/Lullabot/lobot/commit/d1a3b5604c60f1b1001f2d962f26ce64fefd83ef))
* **tool:** migrations can shorten a long text field and move the detail to a description ([c5d2065](https://github.com/Lullabot/lobot/commit/c5d206508ef40085fc8d1bda65236d99c153887c))

## [0.14.0](https://github.com/Lullabot/lobot/compare/v0.13.0...v0.14.0) (2026-10-14)

### ⚠ BREAKING CHANGES

* **engine:** questions, risks, and tasks are now kept as YAML like the decision log, risks get their own skill with a dated history, and your existing files are converted for you

### Added

* **engine:** questions, risks, and tasks are now kept as YAML like the decision log, risks get their own skill with a dated history, and your existing files are converted for you ([bffaf0a](https://github.com/Lullabot/lobot/commit/bffaf0a99bc86dea8ddd7e3fa0be8d6817f35c0e))
* **tool:** updates can now convert a record kept as a table to YAML and fix the links to it, with your approval ([be5ec8b](https://github.com/Lullabot/lobot/commit/be5ec8b087ad748f22d8e2dfdd0be6f756bea2ac))

## [0.13.0](https://github.com/Lullabot/lobot/compare/v0.12.0...v0.13.0) (2026-10-14)

### Added

* **engine:** a review desk page gathers everything that needs you (Lucy's proposals, questions, your tasks, what others owe, risks, pending decisions, checklists) and opens after each processed transcript; a new task list tracks every action item, yours and others' ([84760e6](https://github.com/Lullabot/lobot/commit/84760e6410cd46c1e6fb2929f45d4df015b4a10a))

## [0.12.0](https://github.com/Lullabot/lobot/compare/v0.11.1...v0.12.0) (2026-10-14)

### Added

* **engine:** Lucy keeps a project dossier: one folder per site with its background, audiences, content, data, and migration, so questions about the project are answered from cited files instead of old meeting notes ([2063848](https://github.com/Lullabot/lobot/commit/2063848b9b0a19884a27ac920210b5a87867ba67))

## [0.11.1](https://github.com/Lullabot/lobot/compare/v0.11.0...v0.11.1) (2026-10-14)

### Fixed

* **engine:** the local dashboard is withdrawn again; it reached 0.11.0 by mistake, and tracker pages remain the place to see your records outside the chat ([148b284](https://github.com/Lullabot/lobot/commit/148b2847adf0eb56489be20651b40fa014c6e7c6))

## [0.11.0](https://github.com/Lullabot/lobot/compare/v0.10.0...v0.11.0) (2026-10-14)

### Added

* **engine:** browse every project record as tabs on a local, read-only dashboard ([48496a7](https://github.com/Lullabot/lobot/commit/48496a727974db2987ca2dab87f0c788993bb55d))

## [0.10.0](https://github.com/Lullabot/lobot/compare/v0.9.0...v0.10.0) (2026-10-14)

### Added

* **engine:** the assistant now saves the Project Brain to git for you ([614e5f1](https://github.com/Lullabot/lobot/commit/614e5f1308ef8db81f0794eb99bd6c35bca1cf83))
* **engine:** your writing voice and preferences now follow you to every project ([1f8126c](https://github.com/Lullabot/lobot/commit/1f8126cff351099e017b1ebd44de66155705d06a))

### Changed

* **engine:** tracker pages are now the one place to see your records outside the chat; the local dashboard is retired for now ([d1f70f1](https://github.com/Lullabot/lobot/commit/d1f70f1661ea29d3c7e8064aadbcc94e6685ba44))

## [0.9.0](https://github.com/Lullabot/lobot/compare/v0.8.0...v0.9.0) (2026-10-14)

### Added

* **engine:** add Pepper, the process wrangler, for GitHub and Jira tickets ([abceb67](https://github.com/Lullabot/lobot/commit/abceb67fdf1454a5d806ba5eb8f907448a1820dc))

## [0.8.0](https://github.com/Lullabot/lobot/compare/v0.7.0...v0.8.0) (2026-10-14)

### Added

* **engine:** ask your assistant to "connect GitHub" and it sets up gh and tells you where to paste your token ([c2af233](https://github.com/Lullabot/lobot/commit/c2af2333ca8e5ce6befeccf75eec9bac2afec560))

### Maintenance

* ignore local .env file ([17efcf7](https://github.com/Lullabot/lobot/commit/17efcf7127f74db64ccc9c7b0d0346dfa0110296))

## [0.7.0](https://github.com/Lullabot/lobot/compare/v0.6.0...v0.7.0) (2026-10-14)

### Added

* **engine:** browse every project record as tabs on a local, read-only dashboard ([5e79026](https://github.com/Lullabot/lobot/commit/5e79026ef0c9aadca1c8b465938d23f82282d737))
* **engine:** file reviewed meeting notes as Google Docs in the shared drive, and correct Gemini notes instead of rewriting them ([d156919](https://github.com/Lullabot/lobot/commit/d156919ce6818ccabfcea639cd498348a7f78b61))
* **engine:** get step-by-step help setting up and running Jira, checked against Atlassian's current docs ([23265e5](https://github.com/Lullabot/lobot/commit/23265e582d7cd6edb90e2f43e335a7ea85d89e82))
* **engine:** keep one log of the questions only you can answer, and file each answer where it belongs ([79153b6](https://github.com/Lullabot/lobot/commit/79153b6096c2a874165635382a9bb61572e0ceb5))
* **engine:** review and edit the risks, decisions, RACI, questions, and kickoff checklist on shared tracker pages ([b285314](https://github.com/Lullabot/lobot/commit/b285314816bd7fd0d29fe5b855d0008aa42b5d5b))

## [0.6.0](https://github.com/Lullabot/lobot/compare/v0.5.0...v0.6.0) (2026-10-09)

### Added

* **engine:** Generate checklist artifact in Claude. ([79d3418](https://github.com/Lullabot/lobot/commit/79d3418b312beacda069a2a3ae9e078e16aad875))

## [0.5.0](https://github.com/Lullabot/lobot/compare/v0.4.1...v0.5.0) (2026-10-09)

### Added

* **engine:** Support multiple sites or scopes in a single project ([acf78df](https://github.com/Lullabot/lobot/commit/acf78dfb7f5a249d5e9b202d2f2a9fd392d9b596))

## [0.4.1](https://github.com/Lullabot/lobot/compare/v0.4.0...v0.4.1) (2026-10-09)

### Fixed

* **tool:** stop status and update crashing on release notes ([b644754](https://github.com/Lullabot/lobot/commit/b644754161b8e9977b58167677406af5eb38332e))
* **tool:** stop status and update crashing on release notes ([ac08355](https://github.com/Lullabot/lobot/commit/ac0835571393120402e896a0be0908e753d6a9d3))

## [0.4.0](https://github.com/Lullabot/lobot/compare/v0.3.0...v0.4.0) (2026-10-09)

### Added

* **engine:** keep a RACI matrix of who is responsible, accountable, consulted, and informed for each area of work ([e65efe0](https://github.com/Lullabot/lobot/commit/e65efe0ff54314faf1e06cff1306e7e72c7b7c40)), closes [#3](https://github.com/Lullabot/lobot/issues/3)
* **engine:** read meeting transcripts and project documents straight from the shared Google Drive ([a4f1bec](https://github.com/Lullabot/lobot/commit/a4f1bec7b596d13d86c6ab0fea816dde56d680d7)), closes [#4](https://github.com/Lullabot/lobot/issues/4)

## [0.3.0](https://github.com/Lullabot/lobot/compare/v0.2.0...v0.3.0) (2026-10-08)

### ⚠ BREAKING CHANGES

* **engine:** Lucy's project settings move from .ai/project/agents/lucille/
to .ai/project/agents/lucy/. After updating, the assistant lists the steps and
makes them with your approval (npx --yes github:Lullabot/lobot migrate). The
update removes the old agent from .claude/agents/ itself.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012mpBMPzP4HsC8vSDXv9MPS

### Added

* **engine:** rename the librarian to Lucy and give her a full personality profile ([e52feb0](https://github.com/Lullabot/lobot/commit/e52feb000feb2fa65ec86b01c3a0819c8595e2ae))
* **tool:** make the project-side steps of a breaking change for you ([6943ed8](https://github.com/Lullabot/lobot/commit/6943ed84fe7d4a54faf505cd3d08e872f984ef24))
* **tool:** show what's new after an update ([9e95987](https://github.com/Lullabot/lobot/commit/9e959870c38fb09588d2a78d3eb4ce70c6a69615))

### Fixed

* **tool:** remove agents Lobot no longer ships from .claude/agents ([373572b](https://github.com/Lullabot/lobot/commit/373572bee1297abf2d80dc1ccebadce980de12e5))

## [0.2.0](https://github.com/Lullabot/lobot/compare/v0.1.0...v0.2.0) (2026-10-08)

### Added

* **engine:** add Lobot personality and pm-voice skill ([0c87552](https://github.com/Lullabot/lobot/commit/0c875520f10cc72d155a5e394a533d2f1724b0da))

### Fixed

* **tool:** point to the Lullabot/lobot repository ([99a5946](https://github.com/Lullabot/lobot/commit/99a59460bc1a85815df31a602e89d9ee6e22d816))

### Wording and documentation

* add contributor rules and project workflow ([999bb8e](https://github.com/Lullabot/lobot/commit/999bb8e0cc676f01f020cc8c07d205c524936716))

## 0.1.0 (2026-10-07)

First version, extracted from the first Project Brain.

- **Engine:** the general rules, shared glossary, research, scripts, and skills (adr, decision-log, github, glossary, journal, meeting-notes, people), unchanged from the source project.
- **Engine, new:** `lobot.md` holds the directory map, start-of-session routine, and working rules that used to live in each project's `CLAUDE.md`, so they update with Lobot.
- **Engine, new:** the `lobot` skill, so a PM can say "update Lobot" and the assistant checks the version, updates, and prepares contributions.
- **Engine, moved:** everything about an agent now lives under `agents/`. Lucille's definition is `agents/lucille.md` (copied to `.claude/agents/` on install and update), and her personality and general corrections log are in `agents/lucille/`. `delegation.md` describes the layout.
- **Scaffold, moved:** an agent's project settings live in `.ai/project/agents/<name>/` (`config.md`, `corrections.md`).
- **Scaffold:** short `CLAUDE.md` that points to `lobot.md`, `README.md`, `.env.example`, `.gitignore`, Lucille and ADR project config, empty `docs/` records.
- **Tool:** `npx github:KeyboardCowboy/lobot` with `init`, `status`, `update`, and `link`. No separate clone needed.
- **Skill discovery:** every skill in `.ai/general/skills/` and `.ai/project/skills/` is linked into `.claude/skills/` (and `.agents/skills/` with `--harnesses claude,agents`), so assistants that discover skills on their own find them.
