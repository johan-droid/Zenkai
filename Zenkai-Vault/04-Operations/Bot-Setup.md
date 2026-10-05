---
tags: [zenkai, operations, setup]
created: 2026-09-24
updated: 2026-09-24
---

# Bot Setup

The executable Python project is `../../Zenkai-Bot/`.

## Requirements

- Python 3.12+
- PostgreSQL 15+ for production
- Redis for shared cache and scheduler state when configured
- Discord application with `bot` and `applications.commands` scopes
- Privileged intents approved when required by enabled features

## Environment

```bash
cd ../../Zenkai-Bot
cp .env.example .env
```

Set at minimum:

```text
DISCORD_TOKEN=your_bot_token
DATABASE_URL=sqlite+aiosqlite:///./zenkai.db
```

Optional keys:

```text
REDIS_URL=redis://localhost:6379/0
GUILD_ID=optional_development_server_id
AI_PROVIDER=none
AI_API_KEY=
AI_MODEL=
LOG_LEVEL=INFO
ENVIRONMENT=development
```

Never commit `.env` or place credentials in this vault.

## Install

```bash
cd ../../Zenkai-Bot
uv venv .venv
uv pip install --python .venv/bin/python -e ".[dev]"
```

## Verify

```bash
.venv/bin/python -m zenkai --help
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/mypy zenkai
```

## Run

```bash
.venv/bin/python -m zenkai
```

The bot registers the `/ping` canary command during startup. Discord global command propagation can take time; `GUILD_ID` enables development guild sync.

## Source Map

- `zenkai/core/` — shared infrastructure
- `zenkai/core/discord/` — Discord client and command registry
- `zenkai/features/` — independent feature modules
- `tests/` — unit and integration tests
- `../01-Projects/Zenkai-Execution-Plan.md` — phased delivery plan
