from logic.core import server
from logic import team_http

@server.tool(
    name="alice_list_credentials",
    description="Lists stored credentials from the team server vault (GET /api/credentials/).",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_list_credentials():
    # Returns credential rows; sensitive values stay redacted in formatted output
    payload = team_http.team_request("GET", "/api/credentials/")
    return team_http.format_team_response(payload)

@server.tool(
    name="alice_create_credential",
    description="Stores a credential via POST /api/credentials/ (name, server, host, content).",
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
)
def alice_create_credential(
    name,
    server,
    host,
    content,
    description="",
):
    # Adds one vault entry with the fields expected by the team server API
    try:
        clean_name = str(name or "").strip()
        clean_server = str(server or "").strip()
        clean_host = str(host or "").strip()
        clean_content = str(content or "").strip()
        clean_desc = str(description or "").strip()

        if not clean_name or not clean_server or not clean_host or not clean_content:
            raise ValueError("name, server, host, and content are required")

        body = {
            "name": clean_name,
            "server": clean_server,
            "host": clean_host,
            "content": clean_content,
        }

        if clean_desc:
            body["desc"] = clean_desc

        payload = team_http.team_request("POST", "/api/credentials/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "create credential failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected create credential status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_patch_credential",
    description="Updates a credential via PATCH /api/credentials/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
)
def alice_patch_credential(
    credential_tag,
    name,
    server,
    host,
    content,
    description="",
):
    # Replaces stored credential fields for an existing tag
    try:
        tag = team_http.validate_host_tag(credential_tag)
        clean_name = str(name or "").strip()
        clean_server = str(server or "").strip()
        clean_host = str(host or "").strip()
        clean_content = str(content or "").strip()
        clean_desc = str(description or "").strip()

        if not clean_name or not clean_server or not clean_host or not clean_content:
            raise ValueError("name, server, host, and content are required")

        body = {
            "name": clean_name,
            "server": clean_server,
            "host": clean_host,
            "content": clean_content,
        }

        if clean_desc:
            body["desc"] = clean_desc

        path = f"/api/credentials/{tag}"
        payload = team_http.team_request("PATCH", path, body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "patch credential failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected patch credential status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_delete_credential",
    description="Deletes a credential via DELETE /api/credentials/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": True},
)
def alice_delete_credential(credential_tag):
    # Removes one credential row from the vault by tag
    try:
        tag = team_http.validate_host_tag(credential_tag)
        path = f"/api/credentials/{tag}"
        payload = team_http.team_request("DELETE", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "delete credential failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected delete credential status: {status}"},
        )

    return team_http.format_team_response(payload)