from logic.core import server
from logic import team_http

@server.tool(
    name="alice_create_aes_key",
    description="Generates a new AES key via POST /api/aes/create.",
    annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False},
)
def alice_create_aes_key():
    # Asks the team server for a fresh implant encryption key
    try:
        payload = team_http.team_request("POST", "/api/aes/create")
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "aes key creation failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected aes create status: {status}"},
        )

    if not payload:
        return team_http.format_team_response(
            {"status": "failure", "message": "empty response from /api/aes/create"},
        )

    return team_http.format_team_response(payload)