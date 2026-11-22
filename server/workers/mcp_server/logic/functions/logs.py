from logic.core import server
from logic import team_http

@server.tool(
    name="alice_list_logs",
    description="Lists operator and server logs via GET /api/logs/.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_list_logs(
    search="",
    log_type="all",
    category="all",
    page=1,
    page_size=50,
):
    # Returns paginated log lines with optional type and category filters

    if page < 1:
        raise ValueError("page must be >= 1")

    if page_size < 1 or page_size > 500:
        raise ValueError("page_size must be between 1 and 500")

    params = {"page": page, "pageSize": page_size}
    text = str(search or "").strip()

    if text:
        params["search"] = text

    ltype = str(log_type or "all").strip() or "all"
    cat = str(category or "all").strip() or "all"

    if ltype != "all":
        params["logType"] = ltype

    if cat != "all":
        params["category"] = cat

    payload = team_http.team_request("GET", "/api/logs/", params=params)
    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "logs list failed"))
        raise RuntimeError(message)

    if status and status != "success":
        raise RuntimeError(f"unexpected logs list status: {status}")

    return team_http.format_team_response(payload)