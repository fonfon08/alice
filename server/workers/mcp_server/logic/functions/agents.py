import json
from logic.core import server
from logic import team_http

def build_agent_post_body(raw):
    # Parses and validates agent POST JSON (create or usage) before the team server
    if isinstance(raw, dict):
        body = raw
    else:
        text = str(raw or "").strip()

        if not text:
            raise ValueError("agent_body must be a non-empty JSON object string")

        try:
            body = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"agent_body must be valid JSON: {exc}") from exc

        if not isinstance(body, dict):
            raise ValueError("agent_body must decode to a JSON object")

    action = str(body.get("type") or "").strip()

    if action == "create":
        config = body.get("config")
        if not isinstance(config, dict):
            raise ValueError("create agent_body requires config object")
        name = str(config.get("name") or "").strip()
        if not name:
            raise ValueError("create agent_body.config.name is required")
        typ = str(config.get("type") or "deepseek").strip()
        if typ not in ("deepseek", "custom"):
            raise ValueError('create agent_body.config.type must be "deepseek" or "custom"')
        return body

    if action == "usage":
        for field in ("model", "id", "message"):
            if not str(body.get(field) or "").strip():
                raise ValueError(f"usage agent_body requires {field}")
        context = body.get("context")
        if context is not None and not isinstance(context, list):
            raise ValueError("usage agent_body.context must be a list when provided")
        return body

    raise ValueError('agent_body.type must be "create" or "usage"')

def build_agent_patch_body(raw):
    # Parses PATCH /api/agents/{tag} JSON with a config object
    if isinstance(raw, dict):
        body = raw
    else:
        text = str(raw or "").strip()

        if not text:
            raise ValueError("config_body must be a non-empty JSON object string")

        try:
            body = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"config_body must be valid JSON: {exc}") from exc

        if not isinstance(body, dict):
            raise ValueError("config_body must decode to a JSON object")

    config = body.get("config")

    if config is None and "name" in body:
        config = body

    if not isinstance(config, dict):
        raise ValueError("config_body requires config object")

    name = str(config.get("name") or "").strip()

    if not name:
        raise ValueError("config_body.config.name is required")

    typ = str(config.get("type") or "deepseek").strip()

    if typ not in ("deepseek", "custom"):
        raise ValueError('config_body.config.type must be "deepseek" or "custom"')

    return {"config": config}

@server.tool(
    name="alice_list_agents",
    description="Lists AI agents configured on the team server (GET /api/agents/).",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_list_agents():
    # Exposes operator agent definitions without changing them
    payload = team_http.team_request("GET", "/api/agents/")
    return team_http.format_team_response(payload)

@server.tool(
    name="alice_post_agent",
    description=(
        "Creates an agent or sends a usage prompt via POST /api/agents/. "
        "Pass agent_body as JSON with type create (and config) or type usage "
        "(model, id, message, optional context)."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
)
def alice_post_agent(agent_body):
    # Forwards a validated agent create or usage payload to the team server
    try:
        body = build_agent_post_body(agent_body)
        payload = team_http.team_request("POST", "/api/agents/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "agent post failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected agent post status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_patch_agent",
    description="Updates an agent via PATCH /api/agents/{tag} (config JSON per AgentConfig).",
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False},
)
def alice_patch_agent(agent_tag, config_body):
    # Applies a new agent configuration to an existing tag
    try:
        tag = team_http.validate_host_tag(agent_tag)
        body = build_agent_patch_body(config_body)
        path = f"/api/agents/{tag}"
        payload = team_http.team_request("PATCH", path, body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "agent patch failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected agent patch status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_delete_agent",
    description="Deletes an agent via DELETE /api/agents/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_delete_agent(agent_tag):
    # Removes one agent definition by its tag
    try:
        tag = team_http.validate_host_tag(agent_tag)
        path = f"/api/agents/{tag}"
        payload = team_http.team_request("DELETE", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "delete agent failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected delete agent status: {status}"},
        )

    return team_http.format_team_response(payload)