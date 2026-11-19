# Sprint 2: development

**Goal:** production running with its own database, the first user stories
shipped through pull requests, and the AI feature started.

## What shipped

- Production environment: https://daunting-horizon.onrender.com, with its own
  Neon database branch, separate from staging
  (https://daunting-horizon-staging.onrender.com)
- US-1, create a production: the creator becomes director; members see only
  productions they belong to ([#5](https://github.com/tkg9/656Final-daunting-horizon/pull/5))
- US-2, paste a script: split into scenes at ACT/SCENE headings; only
  directors and stage managers can edit ([#5](https://github.com/tkg9/656Final-daunting-horizon/pull/5))
- US-3 started, AI script breakdown: `productions/breakdown.py` asks
  OpenRouter for the characters in each scene when `OPENROUTER_API_KEY` is
  set, and parses the script text when the key is missing or the call fails.
  Tests mock the HTTP call and never hit OpenRouter.
- `prompts/` folder and log, so any teammate can queue work for the coding
  agent and see when it's done ([#4](https://github.com/tkg9/656Final-daunting-horizon/pull/4))
- 22 tests, run against Postgres on every pull request

## What works on staging and production

Log in as either grader account, open **My productions**, open **Demo
production**, view its two scenes, and click **Draft a script breakdown**.
`/bdcabb0` and `/bdcabb0/stats` work on both.

## Working with agents

The agent wrote the scene splitter and its tests first, then the views.
Writing the tests first surfaced a choice we hadn't made: what happens to
text before the first SCENE heading. We decided it becomes scene 1 rather than
being dropped. Connection strings went from the Neon console to Keychain to
Render without being pasted into chat or committed.

## Backlog changes for next sprint

- Finish US-1: invite members by email with a role
- US-3: ask the model for props, costumes, set pieces, and cues
- US-4 to US-7: casting, rehearsals, attendance, the actor view
