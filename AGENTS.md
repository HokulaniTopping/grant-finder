# Instructions for coding agents

Grant Finder is an app that helps small Hawaii nonprofits find and track grant opportunities that fit their mission, location, and eligibility requirements.

The full proposal is in `docs/proposal.md`.

## Layout

- `app/main.py`: FastAPI routes and the page. No business rules here.
- `app/agent.py`: AI logic and output models for grant matching.
- `app/rules.py`: business rules in plain Python.
- `docs/proposal.md`: project proposal and product requirements.

## Commands

```bash
uv run fastapi dev app/main.py
uv run pytest
uv run ruff check
uv run mypy
```

## Important constraints

- Keep the app skeleton working before adding real grant logic.
- Do not commit secrets or `.env` values to Git.
- Use clear, testable business rules rather than vague behavior.
- The project should help nonprofits find relevant grants, explain why the match fits, and track application progress.
