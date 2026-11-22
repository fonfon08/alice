from logic.core import server
from logic import team_http

@server.tool(
    name="alice_list_processes",
    description="Lists the process tree for a host via POST /api/process/.",
    annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": True},
)
def alice_list_processes(host_tag):
    # Queues ps on the implant and waits for the stored process tree JSON
    tag = team_http.validate_host_tag(host_tag)
    body = {"host": tag}
    payload = team_http.team_request("POST", "/api/process/", body=body)
    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("error") or payload.get("message") or "process list failed")
        raise RuntimeError(message)

    if status and status != "success":
        raise RuntimeError(f"unexpected process list status: {status}")

    return team_http.format_team_response(payload)