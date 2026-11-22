# Overview

The ALICE MCP worker. `main.py` is the entrypoint, and MCP hosts run it over stdio to call the team server REST API.

## Directories

- `/logic`:
    - MCPServer runtime and stdio transport
    - Team server HTTP bridge
    - MCP tool handlers
- `/utils`:
    - Worker import path setup
    - Operator connection settings from server.conf