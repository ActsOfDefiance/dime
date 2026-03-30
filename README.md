# Dime

A general-purpose AI agent-driven publishing pipeline. Dime researches topics, composes articles, generates graphics, and publishes to a static site through a pluggable adapter pattern.

Dime is not tied to any specific topic or publication. It powers [Acts of Defiance](https://github.com/ActsOfDefiance/acts-of-defiance), but can drive any content pipeline that fits the research-write-illustrate-publish workflow.

## Quick start

Prerequisites: Python 3.13+, [uv](https://docs.astral.sh/uv/), PostgreSQL, Redis

```bash
git clone git@github.com:ActsOfDefiance/dime.git
cd dime
uv sync
```

Configure secrets in `.envrc` (see [dime-ops setup](https://github.com/ActsOfDefiance/dime-ops) for full environment details):

```bash
cp .envrc.example .envrc   # then fill in your keys
direnv allow
```

Verify everything works:

```bash
uv run python -m dime health
```

## Stack

| Concern | Tool |
|---|---|
| Language | Python 3.13 |
| Package manager | uv |
| Framework | FastAPI + Google ADK |
| Database | PostgreSQL + SQLAlchemy + Alembic |
| Broker | Redis (pluggable) |
| Linting | ruff |
| Type checking | pyright |
| Testing | pytest |

## Architecture

Dime uses a 4-layer architecture with an 11-state content pipeline and 4 ADK agents (Research, Writer, ArtDirector, Image) plus a PublisherAgent. All adapters (broker, filesystem, publishing, notification) are pluggable.

See [dime-ops/docs/specs/](https://github.com/ActsOfDefiance/dime-ops/tree/develop/docs/specs) for full specs:
- [System overview](https://github.com/ActsOfDefiance/dime-ops/blob/develop/docs/specs/dime-overview.md)
- [Architecture](https://github.com/ActsOfDefiance/dime-ops/blob/develop/docs/specs/dime-architecture.md)
- [Pipeline](https://github.com/ActsOfDefiance/dime-ops/blob/develop/docs/specs/dime-pipeline.md)
- [Data model](https://github.com/ActsOfDefiance/dime-ops/blob/develop/docs/specs/dime-data-model.md)
- [Agent design](https://github.com/ActsOfDefiance/dime-ops/blob/develop/docs/specs/dime-agents.md)

## Development

```bash
uv run ruff check .          # lint
uv run ruff format .         # format
uv run pyright               # type check
uv run pytest                # test
uv run pytest --cov          # test with coverage
```

All work follows Gitflow: feature branches off `develop`, PRs required to merge.

## License

[GPLv3](LICENSE)
