import json
from logic.core import server
from logic import team_http

def build_listener_body(raw):
    # Parses and validates listener POST JSON before it hits the team server
    if isinstance(raw, dict):
        body = raw
    else:
        text = str(raw or "").strip()

        if not text:
            raise ValueError("listener_body must be a non-empty JSON object string")

        try:
            body = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"listener_body must be valid JSON: {exc}") from exc

        if not isinstance(body, dict):
            raise ValueError("listener_body must decode to a JSON object")

    req_type = str(body.get("type") or "").strip()

    if req_type not in ("create", "restart"):
        raise ValueError('listener_body.type must be "create" or "restart"')

    if req_type == "restart":
        tag = str(body.get("tag") or "").strip()
        if not tag:
            raise ValueError("restart listener_body requires tag")
        team_http.validate_host_tag(tag)
        return body

    listener_type = str(body.get("listenerType") or "").strip()

    if listener_type not in ("channel", "file_server"):
        raise ValueError('create listener_body.listenerType must be "channel" or "file_server"')

    for field in ("name", "host"):

        if not str(body.get(field) or "").strip():
            raise ValueError(f"create listener_body requires {field}")

    port = body.get("portToOpen")

    if not isinstance(port, int) or port < 1 or port > 65535:
        raise ValueError("create listener_body.portToOpen must be 1-65535")

    return body

@server.tool(
    name="alice_list_listeners",
    description="Lists C2 listeners configured on the team server (GET /api/listeners/).",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_list_listeners():
    # Shows listener tags and types for infrastructure awareness
    payload = team_http.team_request("GET", "/api/listeners/")
    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "list listeners failed"))
        raise RuntimeError(message)

    if status and status != "success":
        raise RuntimeError(f"unexpected listeners list status: {status}")

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_create_listener",
    description=(
        "Creates or restarts a listener via POST /api/listeners/. "
        "Pass listener_body as JSON matching the REST API "
        '(type restart with tag, or type create with listenerType channel|file_server).'
    ),
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_create_listener(listener_body):
    # Forwards a validated listener payload to the team server router
    try:
        body = build_listener_body(listener_body)
        payload = team_http.team_request("POST", "/api/listeners/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "listener create failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected listener create status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_delete_listener",
    description="Deletes a listener via DELETE /api/listeners/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_delete_listener(listener_tag):
    # Removes one listener definition by its tag
    try:
        tag = team_http.validate_host_tag(listener_tag)
        path = f"/api/listeners/{tag}"
        payload = team_http.team_request("DELETE", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "delete listener failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected delete listener status: {status}"},
        )

    return team_http.format_team_response(payload)