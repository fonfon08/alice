from pathlib import Path
from logic.core import server
from logic import team_http

def read_local_file_bytes(local_path):
    # Reads bytes from the operator workstation for file_server upload tools
    if isinstance(local_path, (bytes, bytearray)):
        raw = bytes(local_path).decode(errors="surrogateescape").strip()
    else:
        raw = str(local_path or "").strip()

    if not raw:
        raise ValueError("local_path is required")

    path = Path(raw).expanduser()

    if not path.is_file():
        raise ValueError(f"local_path is not a readable file: {path}")

    size = path.stat().st_size

    if size > team_http.binary_max_bytes:
        raise ValueError(f"local file exceeds {team_http.binary_max_bytes} bytes")

    return path.read_bytes()

@server.tool(
    name="alice_file_server_list",
    description="Lists files on a file-server listener via GET /api/file_server/{tag}.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_file_server_list(listener_tag):
    # Returns file metadata stored for the given file-server listener tag
    raw = str(listener_tag or "").strip()

    if not raw:
        raise ValueError("listener_tag is required")

    tag = team_http.validate_host_tag(raw)
    path = f"/api/file_server/{team_http.quote_path_segment(tag)}"
    payload = team_http.team_request("GET", path)

    if not isinstance(payload, dict):
        raise RuntimeError("unexpected file_server list response")

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_file_server_download",
    description=(
        "Downloads a file from a file-server listener via "
        "GET /api/file_server/{tag}/files/{file_name}/download. "
        "Returns JSON with content_base64 (50 MiB cap)."
    ),
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_file_server_download(listener_tag, file_name):
    # Fetches one file as base64 so MCP text tools can return the payload
    tag = team_http.validate_host_tag(listener_tag)
    name = team_http.validate_file_name(file_name)
    segment = f"/api/file_server/{team_http.quote_path_segment(tag)}"
    segment = f"{segment}/files/{team_http.quote_path_segment(name)}/download"
    payload = team_http.team_get_binary(segment)
    return team_http.format_team_response(payload)

@server.tool(
    name="alice_file_server_upload",
    description=(
        "Uploads a local file to a file-server listener via "
        "POST /api/file_server/{tag}/files/{file_name} with a raw byte body."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False},
)
def alice_file_server_upload(listener_tag, file_name, local_path):
    # Streams bytes from local_path to the team server file-server content root
    try:
        tag = team_http.validate_host_tag(listener_tag)
        name = team_http.validate_file_name(file_name)
        data = read_local_file_bytes(local_path)
        segment = f"/api/file_server/{team_http.quote_path_segment(tag)}"
        segment = f"{segment}/files/{team_http.quote_path_segment(name)}"
        payload = team_http.team_post_binary(segment, data)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "file_server upload failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected file_server upload status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_file_server_rename",
    description=(
        "Renames a file on a file-server listener via "
        "PATCH /api/file_server/{tag}/files/{file_name}."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False},
)
def alice_file_server_rename(listener_tag, file_name, new_file_name):
    # Sends new_file_name JSON matching FileServerRenameRequest
    try:
        tag = team_http.validate_host_tag(listener_tag)
        current = team_http.validate_file_name(file_name)
        fresh = team_http.validate_file_name(new_file_name)
        segment = f"/api/file_server/{team_http.quote_path_segment(tag)}"
        segment = f"{segment}/files/{team_http.quote_path_segment(current)}"
        body = {"new_file_name": fresh}
        payload = team_http.team_request("PATCH", segment, body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "file_server rename failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected file_server rename status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_file_server_delete",
    description="Deletes a file from a file-server listener via DELETE /api/file_server/{tag}/files/{file_name}.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_file_server_delete(listener_tag, file_name):
    # Removes one stored file under the listener content directory
    try:
        raw = str(listener_tag or "").strip()

        if not raw:
            raise ValueError("listener_tag is required")

        tag = team_http.validate_host_tag(raw)
        name = team_http.validate_file_name(file_name)
        segment = f"/api/file_server/{team_http.quote_path_segment(tag)}"
        segment = f"{segment}/files/{team_http.quote_path_segment(name)}"
        payload = team_http.team_request("DELETE", segment)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    if not isinstance(payload, dict):
        return team_http.format_team_response(
            {"status": "failure", "message": "unexpected file_server delete response"},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "file_server delete failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected file_server delete status: {status}"},
        )

    return team_http.format_team_response(payload)