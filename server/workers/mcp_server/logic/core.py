import logging
import sys
from mcp.server import MCPServer
from logic import agent_notes
from utils import config

logger = logging.getLogger("mcp_server.core")
config.load_settings()
server = MCPServer(
    "alice",
    instructions=agent_notes.operator_note("instructions", mcp_enabled=config.enabled),
)

def setup_logging():
    # Sends worker diagnostics to stderr so stdio stays JSON-RPC clean
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s | mcp_server | %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

def main():
    # Boots MCP tools, then stdio or Streamable HTTP from mcp.mode
    setup_logging()
    config.load_settings()

    if not config.enabled:
        logger.warning(agent_notes.operator_note("disabled"))

    from logic.handlers import register_all_tools
    from logic.http import run_http

    register_all_tools()
    mode = str(config.mode or "stdio").strip().lower()
    if mode not in ("stdio", "http"):
        logger.error("invalid mcp.mode %s; use stdio or http", mode)
        return
    if mode == "http":
        run_http()
        return
    logger.info("MCP stdio transport started")
    server.run(transport="stdio")
