# MCP Server

This folder holds utility files for setting up the ALICE MCP server.

- `stdio_template.json`: Cursor/JSON config for MCP over stdio
- `http_template.json`: Cursor/JSON config for MCP over Streamable HTTP
- `vars.sh`: helper script that prints stdio command and HTTP host/port/path/access_token/url from server.conf

# Where is the MCP server?

The `server/mcp` folder is only for helpers. All MCP server logic lives under `server/workers/mcp_server`.

# Tutorials

If you want to integrate the ALICE MCP server with a tool or agent, see:

- https://nukerat.com/docs/mcp/