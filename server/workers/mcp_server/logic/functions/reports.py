from logic.core import server
from logic import team_http

report_types = ("activity", "hosts", "ioc")
file_types = ("pdf", "html", "json")

def parse_report_host_tags(raw):
    # Accepts comma-separated text or a list of host tag strings
    tags = []
    if isinstance(raw, (list, tuple)):
        pieces = raw
    else:
        text = str(raw or "").strip()
        pieces = text.split(",") if text else []

    for piece in pieces:
        item = str(piece or "").strip()
        if item and item not in tags:
            team_http.validate_host_tag(item)
            tags.append(item)

    return tags

def build_create_report_body(
    name,
    report_type,
    file_type="pdf",
    description="",
    host_tags="",
    hide_credentials=False,
):
    # Validates report creation fields before POST /api/reports/
    title = str(name or "").strip()

    if not title:
        raise ValueError("name is required")

    kind = str(report_type or "").strip().lower()

    if kind not in report_types:
        raise ValueError(f"report_type must be one of: {', '.join(report_types)}")

    export = str(file_type or "pdf").strip().lower()

    if export not in file_types:
        raise ValueError(f"file_type must be one of: {', '.join(file_types)}")

    text = str(description or "").strip()
    tags = parse_report_host_tags(host_tags)
    flag = bool(hide_credentials)
    return {
        "name": title,
        "description": text,
        "reportType": kind,
        "fileType": export,
        "hostTags": tags,
        "hideCredentials": flag,
    }

@server.tool(
    name="alice_list_reports",
    description="Lists generated reports via GET /api/reports/.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_list_reports():
    # Returns report metadata stored on the team server
    payload = team_http.team_request("GET", "/api/reports/")
    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "reports list failed"))
        raise RuntimeError(message)

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_create_report",
    description=(
        "Creates a report via POST /api/reports/. "
        "report_type is activity, hosts, or ioc; file_type is pdf, html, or json; "
        "host_tags is an optional comma-separated list of session tags."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
)
def alice_create_report(
    name,
    report_type,
    file_type="pdf",
    description="",
    host_tags="",
    hide_credentials=False,
):
    # Builds and stores a new engagement report artifact
    try:
        body = build_create_report_body(
            name,
            report_type,
            file_type,
            description,
            host_tags,
            hide_credentials,
        )
        payload = team_http.team_request("POST", "/api/reports/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "create report failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected create report status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_download_report",
    description="Downloads report file payload via GET /api/reports/{tag}/download.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_download_report(report_tag):
    # Fetches JSON with base64 report bytes; not a raw binary team_get_binary route
    try:
        tag = team_http.validate_report_tag(report_tag)
        path = f"/api/reports/{tag}/download"
        payload = team_http.team_request("GET", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "report download failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_view_report",
    description="Returns HTML report preview via GET /api/reports/{tag}/view.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_view_report(report_tag):
    # Loads the HTML preview when the report was saved with html or pdf output
    try:
        tag = team_http.validate_report_tag(report_tag)
        path = f"/api/reports/{tag}/view"
        payload = team_http.team_request("GET", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "report view failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_delete_report",
    description="Removes a stored report via DELETE /api/reports/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_delete_report(report_tag):
    # Deletes report files and metadata for the given tag
    try:
        tag = team_http.validate_report_tag(report_tag)
        path = f"/api/reports/{tag}"
        payload = team_http.team_request("DELETE", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "report delete failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected report delete status: {status}"},
        )

    return team_http.format_team_response(payload)