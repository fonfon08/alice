import json
from logic.core import server
from logic import team_http

def build_script_patch_body(raw):
    # Parses PATCH /api/scripts/{tag} JSON matching PatchScriptRequest rules
    if isinstance(raw, dict):
        body = raw
    else:
        text = str(raw or "").strip()

        if not text:
            raise ValueError("patch_body must be a non-empty JSON object string")

        try:
            body = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"patch_body must be valid JSON: {exc}") from exc

        if not isinstance(body, dict):
            raise ValueError("patch_body must decode to a JSON object")

    status = body.get("status")

    if status is not None:
        if isinstance(status, bool):
            raise ValueError("status must be 0 or 1")
        if isinstance(status, str):
            status = status.strip()
            if status not in ("0", "1"):
                raise ValueError("status must be 0 or 1")
            body["status"] = int(status)
        elif status not in (0, 1):
            raise ValueError("status must be 0 or 1")
        return body

    content = body.get("content")

    if content is None:
        raise ValueError("patch_body requires content unless status is set")

    if isinstance(content, str) and not content.strip():
        raise ValueError("content is required unless status is set")

    return body

@server.tool(
    name="alice_list_scripts",
    description="Lists AliceScripts on the team server (GET /api/scripts/).",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_list_scripts():
    # Returns script metadata and content for operator review
    payload = team_http.team_request("GET", "/api/scripts/")
    return team_http.format_team_response(payload)

@server.tool(
    name="alice_create_script",
    description="Creates a AliceScript via POST /api/scripts/ (name, content, optional description).",
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False},
)
def alice_create_script(name, content, description=""):
    # Stores a new script row on the team server
    try:
        clean_name = str(name or "").strip()
        clean_content = str(content or "")
        clean_desc = str(description or "").strip()

        if not clean_name:
            raise ValueError("name is required")

        if not clean_content.strip():
            raise ValueError("content is required")

        body = {"name": clean_name, "content": clean_content, "description": clean_desc}
        payload = team_http.team_request("POST", "/api/scripts/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "create script failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected create script status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_patch_script",
    description=(
        "Updates a AliceScript via PATCH /api/scripts/{tag}. "
        "Pass patch_body JSON (content required unless setting status 0|1)."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False},
)
def alice_patch_script(script_tag, patch_body):
    # Applies partial script updates including optional run status toggles
    try:
        tag = team_http.validate_host_tag(script_tag)
        body = build_script_patch_body(patch_body)
        path = f"/api/scripts/{tag}"
        payload = team_http.team_request("PATCH", path, body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "patch script failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected patch script status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_delete_script",
    description="Deletes a AliceScript via DELETE /api/scripts/{tag} (optional content confirmation).",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_delete_script(script_tag, content=""):
    # Removes one script by tag; content mirrors the REST delete body field
    try:
        tag = team_http.validate_host_tag(script_tag)
        text = "" if content is None else str(content)

        if len(text) > 1_000_000:
            raise ValueError("delete content confirmation exceeds 1000000 characters")

        body = {"content": text}
        path = f"/api/scripts/{tag}"
        payload = team_http.team_request("DELETE", path, body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "delete script failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected delete script status: {status}"},
        )

    return team_http.format_team_response(payload)