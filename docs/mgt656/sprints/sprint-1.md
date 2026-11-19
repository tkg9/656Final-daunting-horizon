# Sprint 1: walking skeleton

**Goal:** get the whole pipeline working end to end (app, database, staging
deploy, tests) before building StageCraft features.

## What shipped

- Django app with user accounts on Postgres (PR #1), plus sign-up
- Seed command for the grader accounts and a demo production: `python manage.py seed`
- A/B test page at `/bdcabb0` and live stats at `/bdcabb0/stats`, listing all five team nicknames
- Productions: create one, paste in the script, edit it
- AI feature: the script breakdown, drafted by an LLM through OpenRouter from the server
- Mobile-friendly pages with Pico CSS
- Tests for A/B counting, the seed command, accounts, productions and the AI breakdown.
  OpenRouter is always mocked, and GitHub Actions runs the tests on Postgres for every pull request (PR #2)
- 12-factor setup: config and secrets in environment variables, database URL, logs on stdout,
  `$PORT`, migrations
- Two Render services in `render.yaml`: staging deploys from `main`, production from `production`

## What works on staging

- TODO: staging URL, `/login`, `/bdcabb0`, `/bdcabb0/stats`, AI breakdown with the OpenRouter key

## Working with agents

TODO: one concrete thing that worked or didn't, and what we changed.

## Backlog changes for next sprint

- First draft of the user stories is in [docs/user-stories.md](../../user-stories.md),
  for the team to review before creating issues.
- TODO: team GitHub Project with iterations for all four sprints.
