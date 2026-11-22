from logic.core import server
from logic import team_http

def normalize_notification_payload(payload, default_error):
    # Long-poll routes use status or legacy message/host|custom shapes
    if not isinstance(payload, dict):
        return {"status": "success", "data": payload}

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", default_error))
        return {"status": "failure", "message": message}

    if status and status not in ("success", "successful"):
        return {
            "status": "failure",
            "message": f"unexpected notifications status: {status}",
        }

    if not status:
        note = str(payload.get("message", "")).strip().lower()

        if note == "failure":
            return {
                "status": "failure",
                "message": str(payload.get("message", default_error)),
            }

        if note and note not in ("successful", "success"):
            return {
                "status": "failure",
                "message": f"unexpected notifications response message: {note}",
            }

        out = dict(payload)
        out.setdefault("status", "success")
        return out

    return payload

@server.tool(
    name="alice_list_notifications",
    description="Long-polls GET /api/notifications/ for new implant host events.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_list_notifications():
    # Waits until new hosts appear or the team server ends the long poll
    path = "/api/notifications/"
    try:
        payload = team_http.team_request("GET", path)
        normalized = normalize_notification_payload(payload, "notifications fetch failed")
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    return team_http.format_team_response(normalized)

@server.tool(
    name="alice_list_custom_notifications",
    description="Long-polls GET /api/notifications/custom for custom alert rows.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_list_custom_notifications():
    # Returns custom notification payloads created by scripts or operators
    path = "/api/notifications/custom"
    try:
        payload = team_http.team_request("GET", path)
        normalized = normalize_notification_payload(payload, "custom notifications fetch failed")
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    return team_http.format_team_response(normalized)