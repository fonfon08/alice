import json
from logic.core import server
from logic import agent_notes, team_http
from utils import config

@server.tool(
    name="alice_auth_check",
    description="Validates the team server session using POST /auth/check.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_auth_check():
    # Confirms the bearer token still works before other tools run
    payload = team_http.team_request("POST", "/auth/check")
    status = str(payload.get("status", "")).strip().lower()

    if status and status != "success":
        message = str(payload.get("message", "auth check failed"))
        raise RuntimeError(message)

    if not payload:
        raise RuntimeError("empty response from /auth/check")

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_auth_login_info",
    description=(
        "Describes how this MCP worker authenticates to the team server. "
        "On 401 or missing credentials the operator runs ./alice.py server mcp reauth "
        "or server mcp on from the repo root, then reloads MCP. "
        "Login uses mcp.operator_key from server.conf as a single credential."
    ),
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_auth_login_info():
    # Summarises auth configuration without sending credentials to the model
    ready = bool(config.operator_key_line)
    summary = {
        "status": "success",
        "auth_mode": "operator_credentials",
        "mcp_enabled_in_conf": bool(config.enabled),
        "base_url_configured": bool(config.base_url),
        "operator_key_configured": ready,
        "can_authenticate": ready and config.enabled,
        "login_endpoint": "/auth/login",
        "operator_enable_cmd": agent_notes.operator_note("enable_cmd"),
        "operator_reauth_cmd": agent_notes.operator_note("reauth_cmd"),
        "note": agent_notes.operator_note("instructions", mcp_enabled=config.enabled),
    }
    return json.dumps(summary, indent=2, ensure_ascii=False)