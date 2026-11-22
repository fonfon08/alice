from urllib.parse import quote
from logic.core import server
from logic import team_http

def validate_listener_port(port):
    # Ensures SOCKS and port-forward listener ports stay in the valid range
    try:
        value = int(port)
    except (TypeError, ValueError) as err:
        raise ValueError("port must be an integer") from err

    if value < 1:
        raise ValueError("port must be >= 1")

    if value > 65535:
        raise ValueError("port must be <= 65535")

    return value

def validate_network_tag(tag):
    # Normalizes a network session tag before delete requests
    raw = tag
    value = str(raw or "").strip()

    if not value:
        raise ValueError("tag is required")

    if len(value) > 128:
        raise ValueError("tag is too long")

    if any(ch.isspace() for ch in value):
        raise ValueError("tag must not contain whitespace")

    return value

@server.tool(
    name="alice_list_network",
    description="Lists SOCKS and port-forward sessions from GET /api/network/.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_list_network():
    # Shows active listener-backed tunnels managed by the team server
    payload = team_http.team_request("GET", "/api/network/")
    return team_http.format_team_response(payload)

@server.tool(
    name="alice_create_socks_network",
    description="Opens a SOCKS listener via POST /api/network/ (type create, networkType socks).",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": True},
)
def alice_create_socks_network(
    host_tag,
    port_to_open,
    auth_user="",
    auth_pass="",
):
    # Creates a SOCKS pivot on the chosen implant host tag
    try:
        tag = team_http.validate_host_tag(host_tag)
        port = validate_listener_port(port_to_open)
        body = {
            "type": "create",
            "networkType": "socks",
            "portToOpen": port,
            "hostTag": tag,
            "authUser": str(auth_user or "").strip(),
            "authPass": str(auth_pass or "").strip(),
        }
        payload = team_http.team_request("POST", "/api/network/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "create socks network failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected create socks network status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_create_port_forward_network",
    description="Opens a TCP port forward via POST /api/network/ (networkType port_forwarding).",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": True},
)
def alice_create_port_forward_network(
    host_tag,
    port_to_open,
    forward_host,
    forward_port,
    protocol="tcp",
):
    # Forwards a local team-server port to a remote host through an implant
    try:
        tag = team_http.validate_host_tag(host_tag)
        local_port = validate_listener_port(port_to_open)
        remote_port = validate_listener_port(forward_port)
        target = str(forward_host or "").strip()

        if not target:
            raise ValueError("forward_host is required")

        proto = str(protocol or "tcp").strip().lower()

        if proto != "tcp":
            raise ValueError("only tcp port forwarding is supported")

        body = {
            "type": "create",
            "networkType": "port_forwarding",
            "portToOpen": local_port,
            "hostTag": tag,
            "forwardHost": target,
            "forwardPort": remote_port,
            "protocol": "tcp",
        }
        payload = team_http.team_request("POST", "/api/network/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "create port forward failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected create port forward status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_restart_network",
    description="Restarts an existing network session via POST /api/network/ (type restart).",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_restart_network(connection_id):
    # Restarts a SOCKS or port-forward listener by session id
    try:
        session_id = str(connection_id or "").strip()

        if not session_id:
            raise ValueError("connection_id is required")

        if len(session_id) > 128:
            raise ValueError("connection_id is too long")

        body = {"type": "restart", "id": session_id}
        payload = team_http.team_request("POST", "/api/network/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "restart network failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected restart network status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_delete_network",
    description="Stops a network session via DELETE /api/network/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_delete_network(tag):
    # Tears down one SOCKS or port-forward listener by tag or session id
    try:
        value = validate_network_tag(tag)
        encoded = quote(value, safe="")
        path = f"/api/network/{encoded}"
        payload = team_http.team_request("DELETE", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "delete network failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected delete network status: {status}"},
        )

    return team_http.format_team_response(payload)