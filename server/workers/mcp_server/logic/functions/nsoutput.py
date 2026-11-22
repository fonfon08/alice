from logic.core import server
from logic import team_http

@server.tool(
    name="alice_fetch_nsoutput",
    description=(
        "Waits for new AliceScript console output via GET /api/nsoutput/ "
        "(long-poll; may take until a script prints)."
    ),
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False},
)
def alice_fetch_nsoutput():
    # Blocks until the team server reports fresh alicescript output rows
    try:
        try:
            payload = team_http.team_request("GET", "/api/nsoutput/")
        except RuntimeError as exc:
            message = str(exc).lower()

            if "timeout" in message or "timed out" in message:
                raise RuntimeError(
                    "nsoutput long-poll timed out; retry when a AliceScript is expected to print"
                ) from exc

            raise

        if isinstance(payload, dict):
            status = str(payload.get("status", "")).strip().lower()

            if status == "failure":
                message = str(payload.get("message", "nsoutput fetch failed"))
                payload = {"status": "failure", "message": message}
        else:
            payload = {"status": "success", "content": payload}
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    return team_http.format_team_response(payload)