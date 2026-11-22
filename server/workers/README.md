# Overview

Folder related to the workers.

## Directories

- `/alicescripts`:
    - AliceScript worker; `main.py` is the entrypoint
    - Monitors the database for changes and runs operator scripts
- `/mcp_server`:
    - MCP worker; `main.py` is the entrypoint
    - stdio bridge for AI hosts against the team server REST API