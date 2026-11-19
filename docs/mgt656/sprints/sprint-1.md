# Sprint 1: walking skeleton

**Goal:** get the whole pipeline working end to end (app, database, staging
deploy, tests) before building StageCraft features.

## What shipped

- Django app with user accounts on Postgres ([#1](https://github.com/tkg9/656Final/pull/1))
- Seed command for the grader accounts: `python manage.py seed`
- A/B test page at `/bdcabb0` and live stats at `/bdcabb0/stats`
- Unit tests for A/B counting and the seed command, run by GitHub Actions
  against Postgres on every pull request ([#2](https://github.com/tkg9/656Final/pull/2))
- Team roster in `team.yaml` and on the A/B page ([#3](https://github.com/tkg9/656Final/pull/3))

## What works on staging

Staging: https://daunting-horizon-staging.onrender.com (Render free tier,
Neon Postgres). Checked live: `/login/` with both grader accounts,
`/bdcabb0` (one button, kudos or thanks), a click redirecting back without a
new impression, and `/bdcabb0/stats` returning `preferred`.

## Working with agents

The agent wrote the A/B tests before deploying, which caught the redirect
rule (a click must not count a new impression) locally. What didn't work:
its first push was rejected because the GitHub token lacked the `workflow`
scope, so CI landed in a separate PR. We now grant scopes up front and keep
CI changes in their own small PRs.

## Backlog changes for next sprint

First user stories drafted in [docs/user-stories.md](../../user-stories.md)
(US-1 to US-9); US-1 to US-3 move into Sprint 2.
