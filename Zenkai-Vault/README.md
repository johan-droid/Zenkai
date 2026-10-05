# Zenkai Vault

This folder is the Obsidian vault for the Zenkai project. It is the canonical location for project memory, architecture, execution plans, operational notes, decisions, and reusable templates.

## Start Here

- [[Home]]
- [[01-Projects/Zenkai-Project]]
- [[01-Projects/Zenkai-Project-Memory]]
- [[02-Architecture/Zenkai-Architecture]]
- [[01-Projects/Zenkai-Execution-Plan]]
- [[04-Operations/Bot-Setup]]
- [[05-Reference/Vault-MCP-Tools]]

## Folder Layout

| Folder | Purpose |
| --- | --- |
| `00-Inbox` | Unprocessed ideas and incoming notes |
| `01-Projects` | Active project notes, plans, and memory |
| `02-Architecture` | System design and technical architecture |
| `03-Decisions` | Architecture decision records |
| `04-Operations` | Setup, deployment, runbooks, and maintenance |
| `05-Reference` | Tooling and technical reference |
| `06-Meetings` | Meeting notes and discussion records |
| `07-Logs` | Dated operational and development logs |
| `08-Templates` | Reusable note templates |
| `09-Archive` | Inactive historical material |

## Writing Rules

- Keep one canonical document per topic.
- Append project memory through the `append_project_memory` MCP tool.
- Record architectural decisions in `03-Decisions` with an ADR filename.
- Never store Discord tokens, API keys, passwords, or other secrets in the vault.
- Keep the runtime package in `Zenkai-Bot/` and the MCP package in `Zenkai-MCP/`.
- Link notes with Obsidian wiki links when possible.
