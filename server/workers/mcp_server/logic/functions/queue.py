from logic.core import server
from logic import team_http

@server.tool(
    name="alice_queue_list",
    description="Lists implant queue lines via GET /api/queue/ with search and pagination.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_queue_list(
    search="",
    host_tag="all",
    page=1,
    page_size=50,
):
    # Returns queued commands and their completion state for triage

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

    payload = team_http.team_request("GET", "/api/queue/", params=params)
    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "queue list failed"))
        raise RuntimeError(message)

    if status and status != "success":
        raise RuntimeError(f"unexpected queue list status: {status}")

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_queue_delete",
    description="Deletes one queue line via DELETE /api/queue/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_queue_delete(entry_tag):
    # Removes a single queue row from the team server database
    try:
        raw = str(entry_tag or "").strip()

        if not raw:
            raise ValueError("entry_tag is required")

        tag = team_http.validate_entry_tag(raw)
        path = f"/api/queue/{team_http.quote_path_segment(tag)}"
        payload = team_http.team_request("DELETE", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "delete queue line failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected delete queue status: {status}"},
        )

    return team_http.format_team_response(payload)