# Prompts

Requests for the coding agent. Anyone on the team can add one; the agent picks
them up in batches and records the outcome in [LOG.md](LOG.md).

## Adding a prompt

1. Copy [TEMPLATE.md](TEMPLATE.md) to `prompts/YYYY-MM-DD-<github-username>-<short-slug>.md`,
   e.g. `2026-11-18-Lasya1106-cue-list.md`.
2. Fill it in. One request per file; say what "done" looks like.
3. Add a row to [LOG.md](LOG.md) with status `new`.
4. Open a pull request (or commit to a branch and ask for it to be merged).

Don't edit a prompt once it's `in progress`; add a new one instead.

## Statuses

| Status | Meaning |
|---|---|
| `new` | Added, not yet picked up |
| `in progress` | Being worked on; the PR column links the branch or PR |
| `done` | Shipped; the PR column links the merged PR |
| `needs info` | Blocked on a question, written in Notes |
| `declined` | Won't do; reason in Notes |
