# Zenkai Bot Runtime

This directory contains the executable Discord bot package and its tests.

## Source

- `zenkai/core/` — Discord, configuration, logging, database, cache, scheduler, permissions
- `zenkai/features/` — independent feature modules
- `tests/` — unit and integration tests

## Canonical Project Notes

- `../Zenkai-Vault/01-Projects/Zenkai-Project.md`
- `../Zenkai-Vault/01-Projects/Zenkai-Execution-Plan.md`
- `../Zenkai-Vault/04-Operations/Bot-Setup.md`
- `../Zenkai-Vault/02-Architecture/Zenkai-Architecture.md`

## Verify

```bash
uv pip install --python .venv/bin/python -e ".[dev]"
.venv/bin/python -m zenkai --help
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/mypy zenkai
```

Set `DISCORD_TOKEN` in a local `.env` before running `.venv/bin/python -m zenkai`.
