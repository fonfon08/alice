from logic.core import server
from logic import team_http

@server.tool(
    name="alice_list_sessions",
    description="Lists implant sessions from GET /api/sessions/.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_list_sessions(mode="default", long_polling=True):
    # Returns hosts known to the team server for operator triage
    allowed = ("default", "graphs", "sessions_lp")
    value = str(mode or "default").strip()

    if value not in allowed:
        raise ValueError(f"mode must be one of: {', '.join(allowed)}")

    poll = bool(long_polling)
    params = {"mode": value, "long_polling": poll}
    payload = team_http.team_request("GET", "/api/sessions/", params=params)
    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "list sessions failed"))
        raise RuntimeError(message)

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_patch_session",
    description="Updates session notes via PATCH /api/sessions/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": True},
)
def alice_patch_session(host_tag, notes=""):
    # Persists operator notes on a single implant session row
    try:
        tag = team_http.validate_host_tag(host_tag)
        text = str(notes or "")

        if len(text) > 65535:
            raise ValueError("notes exceeds 65535 characters")

        body = {"notes": text}
        path = f"/api/sessions/{tag}"
        payload = team_http.team_request("PATCH", path, body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "patch session failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected patch session status: {status}"},
        )

    return team_http.format_team_response(payload)

@server.tool(
    name="alice_delete_session",
    description="Removes a session record via DELETE /api/sessions/{tag}.",
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": True},
)
def alice_delete_session(host_tag):
    # Deletes the session from the team server database; does not silently noop
    try:
        tag = team_http.validate_host_tag(host_tag)
        path = f"/api/sessions/{tag}"
        payload = team_http.team_request("DELETE", path)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "delete session failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected delete response status: {status}"},
        )

    return team_http.format_team_response(payload)