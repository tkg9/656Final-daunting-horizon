# 656Final

StageCraft: theatre production management, from script to stage.
MGT 656 (Fall 2026) final project, team daunting-horizon.

- [Project proposal](docs/proposal.md)
- [User stories](docs/user-stories.md)
- [Progress log](PROGRESS.md)

## What's here (Sprint 1 skeleton)

- **Accounts:** sign up, log in, log out (Django's built-in auth).
- **Productions:** create a production, paste in the script, edit it. You only see your own.
- **AI script breakdown:** one button sends the script to an LLM through
  [OpenRouter](https://openrouter.ai/), from the server only. It drafts characters,
  scenes, props, costumes, set pieces and cues, and the draft is saved to the database.
- **A/B test page** at `/bdcabb0`, with live counts at `/bdcabb0/stats`.
- **Seed command** for the grader accounts and a demo production.
- Pages work on phones and desktops ([Pico CSS](https://picocss.com), vendored in `static/vendor/pico`).

## Run locally

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # then fill in what you need
set -a; . ./.env; set +a
python manage.py migrate
python manage.py seed        # grader accounts + demo production
python manage.py runserver   # http://127.0.0.1:8000
```

Without `DATABASE_URL` the app uses a local SQLite file. Staging and production use Postgres.
Without `OPENROUTER_API_KEY` everything works except the AI button, which says AI isn't configured.

## Configuration

Everything is set with environment variables. Secrets are never committed.

| Variable | Needed | What it does |
|---|---|---|
| `DEBUG` | | `1` locally (default). Set to `0` on staging and production. |
| `SECRET_KEY` | when `DEBUG=0` | Django's signing key. |
| `DATABASE_URL` | when `DEBUG=0` | Postgres URL, e.g. from Neon. One database per environment. |
| `OPENROUTER_API_KEY` | for AI | OpenRouter key (Kyle explains how to get one with credits). |
| `OPENROUTER_MODEL` | | Model ID on OpenRouter. Default `anthropic/claude-sonnet-5.5`. |
| `OPENROUTER_TIMEOUT` | | Seconds to wait for the LLM. Default 60. |
| `ALLOWED_HOSTS` | | Extra hostnames, comma-separated. Render's own hostname is added automatically. |
| `SEED_ADMIN_PASSWORD`, `SEED_MEMBER_PASSWORD` | | Override the grader account passwords. |
| `LOG_LEVEL` | | Default `INFO`. Logs go to stdout. |

## Test

```sh
python manage.py test
```

Tests never call OpenRouter or any other outside service: the HTTP call is mocked,
and the test runner (`config/test_runner.py`) blanks the API key for the whole run.
GitHub Actions runs the tests against Postgres on every pull request and push to `main`,
and fails if a model change has no migration.

## Deploy

`render.yaml` defines two public Render web services, each with its own Postgres database:

| Environment | Render service | Deploys from |
|---|---|---|
| Staging | `daunting-horizon-staging` | every push to `main` |
| Production | `daunting-horizon` | the `production` branch |

To release, open a pull request from `main` into `production`.

One-time setup:

1. Create two Neon Postgres databases, one for staging and one for production.
2. Create a `production` branch from `main` on GitHub.
3. In Render: **New → Blueprint**, pick this repo. When asked, paste each service's
   `DATABASE_URL` and `OPENROUTER_API_KEY`.

Each deploy runs `build.sh`, which installs packages, collects static files, runs
migrations and runs the seed command, so the grader accounts return after any database reset.
The app listens on `$PORT`.

## Workflow

Branch, pull request, one teammate's review, merge. No direct pushes to `main`.
