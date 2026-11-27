# Progress

Shared log for the team. Add lines; don't rewrite other people's. Update it in
the same pull request as your work.

## Now

One line per person: who is working on what.

- 

## Done

Newest first: date, who, what, PR.

- 2026-11-27, tkg9, Sign in with Google on the login page
- 2026-11-18, Baggs99, script breakdown calls OpenRouter; talented-moose added to the roster
- 2026-11-18, tkg9, staging and production live on Render with separate Neon databases
- 2026-11-18, tkg9, US-1/US-2 shipped and US-3 started: productions, script scenes, rule-based breakdown (#5)
- 2026-11-18, tkg9, prompts folder and log (#4)
- 2026-11-11, tkg9, Sprint 1 skeleton: Django, accounts, A/B page, seed, tests

## Decisions

Decision, reason, date.

- Django + Postgres (Neon) on Render free tier: course default, free, built-in accounts and test runner. 2026-11-11
- Cloudflare not used for the database: its database is SQLite and the course requires Postgres or MySQL. 2026-11-11
- Separate Neon branches for staging and production, auto-delete off. 2026-11-18
- AI breakdown behind one function; rule-based first, LLM next. 2026-11-18

## Blocked / questions

- Course nicknames still missing for Lasya1106 and msomoyeeta. Baggs99 is talented-moose.
- Team to review the drafted user stories (docs/user-stories.md)
- GitHub Project board needs the `project` scope on the gh token
