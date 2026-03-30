# CLAUDE.md — dime

This is the Python backend repo for dime, an AI agent-driven publishing pipeline. For architecture, specs, decisions, and cross-repo context, see `docs/specs/` and `docs/decisions/` (symlinked from dime-ops).

## Commands

```bash
# Dependencies
uv sync

# Run
uv run python -m dime health
uv run python -m dime start

# Quality
uv run ruff check .
uv run ruff format .
uv run pyright
uv run pytest
uv run pytest --cov
```

Always use `uv run` — never call `python` directly.

## File structure

```
dime/
  dime/                      # Main package
    __init__.py
    __main__.py              # CLI entry point
    app.py                   # FastAPI app
    config/
      settings.py            # Pydantic Settings
    agents/
      base.py
      researcher.py
      writer.py
      publisher.py
  agents/                    # ADK agent discovery
    dime_agent/
      agent.py
  tests/
  docs/                      # Symlinked to dime-ops/docs/
    specs/
    decisions/
    memory/
    issues/
  pyproject.toml
  uv.lock
```

## Coding standards

- PEP 8 enforced by ruff
- Type hints required — checked by pyright (not mypy)
- Imports in file header only, never inline
- All files end with a single newline
- Pydantic for data validation and settings
- Start simple — do not overengineer

## Gitflow rules

- Never work in `main` or `develop` directly
- All work in `feature/`, `hotfix/`, or `release/` branches
- PRs required to merge into `develop` or `main`
- Commit messages: imperative mood, present tense

## Secrets

- Secrets live in `.envrc` only — never `.env`, never committed
- `.envrc` is in `.gitignore`

## Testing

- pytest with pytest-cov
- Run `uv run pytest` before every commit
- Never disable or skip tests instead of fixing them
