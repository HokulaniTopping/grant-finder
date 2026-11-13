---
name: pr-prep
description: Use when a Grant Finder change is ready to become a pull request. Checks the branch, scope, and project checks, then drafts the PR title and description.
---

# PR Prep

Use this skill once the code for one change is written and before you open the pull request.

## Workflow

1. **Branch.** Confirm the current branch is not `master` and is named `feature/<short-name>` or `skill/<short-name>`. If you are on `master`, stop and create the right branch first. Never commit straight to `master`.
2. **Scope.** Run `git diff master...HEAD --stat` and `git status`. The change should do one thing. Flag any unrelated files, such as stray documents, `.env` files, `__pycache__/`, or edits outside the change's purpose, and remove them before continuing.
3. **Layout.** Confirm the code sits where `AGENTS.md` says it should: business rules in `app/rules.py`, routes only in `app/main.py`, AI logic in `app/agent.py`.
4. **Checks.** Run each one and record the result:
   - `uv run pytest`
   - `uv run ruff check`
   - `uv run mypy`
   - `uv run python -c "import app.main"` (the app still starts)

   If a check fails, fix it before opening the PR. Do not open a PR with failing checks.
5. **Tests.** For a feature, confirm there are new or updated tests for the normal case, the failing case, and any missing or edge-case input.
6. **Draft the PR.** Use the template below. Write the title as `Add <thing>`. Report the actual check output, not what you expect it to be.
7. **Open it.** Push the branch and open the PR with `gh pr create`, using the drafted title and body.

## PR description template

```markdown
## What
<One or two sentences on what the change does. List the new behavior if there are several outcomes.>

## Why
<The requirement it meets. Cite `docs/proposal.md` when you can.>

## Out of scope
<What this PR deliberately leaves for later. Leave this section out if nothing applies.>

## How it was verified
- <New tests and what they cover>
- `uv run pytest`: <result>
- `uv run ruff check`: <result>
- `uv run mypy`: <result>
```

Keep the description short enough to read in a minute. A reviewer should know what changed, why, and how it was checked without opening the code.
