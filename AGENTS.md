# Zenkai Agent Instructions

## Vault Access

Use the `zenkai-vault` MCP server for project memory and documentation updates.

Start with:

- `Home.md`
- `01-Projects/Zenkai-Project.md`
- `01-Projects/Zenkai-Project-Memory.md`
- `01-Projects/Zenkai-Execution-Plan.md`
- `02-Architecture/Zenkai-Architecture.md`

Use `search_notes` before creating a new note. Use `read_note` before updating an existing note. Prefer `append_note` for logs and `append_project_memory` for meaningful project milestones, decisions, status changes, and implementation results.

## Repository Boundaries

- Keep runtime source in `Zenkai-Bot/`.
- Keep the MCP server in `Zenkai-MCP/`.
- Keep project documentation and memory in `Zenkai-Vault/`.
- Update the execution plan when work starts, completes, or becomes blocked.
- Do not duplicate canonical documents.
- Do not store Discord tokens, API keys, passwords, or other secrets in the vault.

## Safe Changes

Before changing source, inspect the relevant vault notes and follow the architecture. After a meaningful change, update project memory with the decision, verification result, and next step. Do not claim a feature is complete until its definition-of-done requirements are verified.
