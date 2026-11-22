# Overview

Raw logic of the MCP worker: `core.py` runs the MCPServer (MCP SDK v2), `team_http.py` talks to the team server over HTTPS, `handlers.py` loads all `logic/functions/*.py` tools, and `logic/functions/registry.md` maps routes to tool names.