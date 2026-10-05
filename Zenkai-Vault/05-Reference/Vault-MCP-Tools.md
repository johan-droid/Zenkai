# Vault MCP Tools

The MCP server is implemented in `../../Zenkai-MCP/` and operates on this vault through filesystem-backed tools.

## Tools

| Tool | Purpose |
| --- | --- |
| `vault_info` | Return vault path, note count, folder count, and project-memory status |
| `list_notes` | List Markdown notes |
| `read_note` | Read a Markdown note |
| `write_note` | Create or replace a Markdown note |
| `append_note` | Append content to a Markdown note |
| `search_notes` | Search note contents and return excerpts |
| `list_folders` | List vault folders |
| `create_folder` | Create a vault folder |
| `append_project_memory` | Append a timestamped memory update |

## Project Memory

The default project-memory note is `01-Projects/Zenkai-Project-Memory.md`.

## Safety

- Configure `ZENKAI_VAULT_PATH` to the absolute vault path.
- The server uses stdio and does not expose a network port.
- Paths outside the vault are rejected.
- Only Markdown note operations are available.
- Secrets must never be written to the vault.
