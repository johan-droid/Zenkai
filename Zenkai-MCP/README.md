# Zenkai Vault MCP

Filesystem-backed MCP server for the `Zenkai-Vault` Obsidian vault.

## Install and run

From the repository root:

```bash
uv run --project Zenkai-MCP zenkai-vault-mcp
```

Set `ZENKAI_VAULT_PATH` when the vault is outside the repository:

```bash
ZENKAI_VAULT_PATH=/absolute/path/to/Zenkai-Vault uv run --project Zenkai-MCP zenkai-vault-mcp
```

The server communicates over MCP stdio. It does not start a network service and does not execute commands.

## Tools

- `vault_info` — vault path and note/folder counts
- `list_notes` — list Markdown notes
- `read_note` — read one Markdown note
- `write_note` — create or replace one Markdown note
- `append_note` — append content to one Markdown note
- `search_notes` — search note contents and return matching excerpts
- `list_folders` — list vault folders
- `create_folder` — create a folder inside the vault
- `append_project_memory` — append a timestamped memory update to the project memory note

## Safety

- All paths are resolved and confined to the configured vault.
- Only `.md` files can be read or written through note tools.
- Writes are atomic and limited to 2 MB per note.
- Search results and errors never escape the vault root.
- The server has no delete or arbitrary command tool.

## MCP client configuration

Use `config.example.json` as a template. The command should point to the installed or project-local server and set an absolute `ZENKAI_VAULT_PATH`.
