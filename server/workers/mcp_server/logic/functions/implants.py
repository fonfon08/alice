import json
from logic.core import server
from logic import team_http

def parse_implant_request(raw):
    # Validates implant POST JSON before forwarding to the builder router
    if isinstance(raw, dict):
        body = raw
    else:
        text = str(raw or "").strip()

        if not text:
            raise ValueError("implant_body must be a non-empty JSON object string")

        try:
            body = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"implant_body must be valid JSON: {exc}") from exc

        if not isinstance(body, dict):
            raise ValueError("implant_body must decode to a JSON object")

    req_type = str(body.get("type") or "").strip()

    if req_type != "build":
        raise ValueError('implant_body.type must be "build"')

    base = str(body.get("implant_base") or "").strip()

    if base not in ("stageless", "loader"):
        raise ValueError('implant_body.implant_base must be "stageless" or "loader"')

    config = body.get("config")

    if not isinstance(config, dict):
        raise ValueError("implant_body.config must be a JSON object")

    return body

@server.tool(
    name="alice_build_implant",
    description=(
        "Builds a stageless or loader implant via POST /api/implants/. "
        "Pass implant_body as a JSON string with type build, implant_base, and config "
        "(same shape as the REST API and GUI builder)."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False},
)
def alice_build_implant(implant_body):
    # Forwards a full implant build request; output may include base64 artifact bytes
    try:
        body = parse_implant_request(implant_body)
        payload = team_http.team_request("POST", "/api/implants/", body=body)
    except Exception as exc:
        return team_http.format_team_response(
            {"status": "failure", "message": str(exc)},
        )

    status = str(payload.get("status", "")).strip().lower()

    if status == "failure":
        message = str(payload.get("message", "implant build failed"))
        return team_http.format_team_response({"status": "failure", "message": message})

    if status and status != "success":
        return team_http.format_team_response(
            {"status": "failure", "message": f"unexpected implant build status: {status}"},
        )

    return team_http.format_team_response(payload)