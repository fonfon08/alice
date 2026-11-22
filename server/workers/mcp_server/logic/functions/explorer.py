from logic.core import server
from logic import team_http

@server.tool(
    name="alice_explorer_list",
    description="Lists folders on an implant path via POST /api/explorer/.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_explorer_list(host_tag, path="/", auto_refresh=False):
    # Browses remote directories without downloading file contents
    tag = team_http.validate_host_tag(host_tag)
    folder_path = str(path or "/").strip() or "/"
    body = {
        "host": tag,
        "path": folder_path,
        "getContent": False,
        "autoRefresh": bool(auto_refresh),
    }
    payload = team_http.team_request("POST", "/api/explorer/", body=body)
    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message") or payload.get("error") or "explorer list failed")
        raise RuntimeError(message)

    if status and status != "success":
        raise RuntimeError(f"unexpected explorer list status: {status}")

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_explorer_download_file",
    description="Downloads a remote file via POST /api/explorer/ with getContent true.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_explorer_download_file(host_tag, path, file_name):
    # Returns base64 file bytes in the explorer response when the implant succeeds
    tag = team_http.validate_host_tag(host_tag)
    file_path = str(path or "").strip()

    if not file_path or file_path == "/":
        raise ValueError("path must name the remote file to download")

    name = str(file_name or "").strip()

    if not name:
        raise ValueError("file_name is required")

    body = {
        "host": tag,
        "path": file_path,
        "getContent": True,
        "autoRefresh": False,
        "fileName": name,
    }
    payload = team_http.team_request("POST", "/api/explorer/", body=body)
    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message") or payload.get("error") or "explorer download failed")
        raise RuntimeError(message)

    if status and status != "success":
        raise RuntimeError(f"unexpected explorer download status: {status}")

    return team_http.format_team_response(payload)