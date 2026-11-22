from urllib.parse import quote
from logic.core import server
from logic import team_http

def parse_host_tags_csv(text):
    # Splits comma-separated host filters into a deduplicated list
    if isinstance(text, (list, tuple)):
        seen = []
        for piece in text:
            tag = str(piece or "").strip()
            if tag and tag not in seen:
                seen.append(tag)
        return seen

    raw = str(text or "").strip()

    if not raw:
        return []

    seen = []
    for piece in raw.split(","):
        tag = piece.strip()

        if tag and tag not in seen:
            seen.append(tag)

    return seen

@server.tool(
    name="alice_list_iocs",
    description="Lists IOC records from GET /api/iocs/ with optional search and host filters.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_list_iocs(
    search="",
    host_tags_csv="",
    page=1,
    page_size=50,
):
    # Returns paginated IOCs collected from implants and file transfers

    if page < 1:
        raise ValueError("page must be >= 1")

    if page_size < 1 or page_size > 500:
        raise ValueError("page_size must be between 1 and 500")

    tags = parse_host_tags_csv(host_tags_csv)
    params = {"page": page, "pageSize": page_size}
    cleaned = str(search or "").strip()

    if cleaned:
        params["search"] = cleaned

    if tags:
        params["hostTags"] = tags

    payload = team_http.team_request("GET", "/api/iocs/", params=params)
    return team_http.format_team_response(payload)

@server.tool(
    name="alice_delete_ioc",
    description="Removes one IOC row via DELETE /api/iocs/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_delete_ioc(tag):
    # Deletes a single IOC identifier from the team server database
    try:
        value = str(tag or "").strip()

        if not value:
            raise ValueError("tag is required")

        if len(value) > 256:
            raise ValueError("tag is too long")

        encoded = quote(value, safe="")
        path = f"/api/iocs/{encoded}"
        payload = team_http.team_request("DELETE", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "delete ioc failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected delete ioc status: {status}"},
        )

    return team_http.format_team_response(payload)