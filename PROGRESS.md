# Progress

Shared log for the team. Add lines; don't rewrite other people's. Update it in
the same pull request as your work.

## Now

One line per person: who is working on what.

- Abercrombie35: finishing the Sprint 1 checklist (staging deploy, production service, GitHub Project)

## Done

Newest first: date, who, what, PR.

- 2026-11-19, Abercrombie35, Rest of the skeleton: sign-up, productions, AI script breakdown via OpenRouter (mocked in tests), Pico CSS layout, demo data in seed, stdout logging, staging + production in render.yaml, first draft of user stories, PR TBD
- 2026-11-11, tkg9, Sprint 1 skeleton: Django, accounts, A/B page, seed, tests

## Decisions

Decision, reason, date.

- Django + Postgres (Neon) on Render free tier: course default, free, built-in accounts and test runner. 2026-11-11
- Cloudflare not used for the database: its database is SQLite and the course requires Postgres or MySQL. 2026-11-11
- OpenRouter called with Python's standard library (urllib), no SDK: one small module (`productions/llm.py`), nothing extra to install, easy to mock. 2026-11-19
- Pico CSS, vendored in `static/`: mobile-friendly with almost no classes, and no CDN to depend on. 2026-11-19
- Production deploys from a `production` branch, released by pull request from `main`. Staging deploys every push to `main`. 2026-11-19
- Seed command moved from `abtest` to the new `accounts` app, since it now also creates demo data. 2026-11-19

## Blocked / questions

- First user stories: draft in docs/user-stories.md, needs team review, then one issue per story
- Neon databases (staging + production) and Render blueprint setup: whoever owns the Render account
- OpenRouter key with credits from Kyle; confirm the default model ID on openrouter.ai/models
- Team GitHub Project with iterations for all four sprints
