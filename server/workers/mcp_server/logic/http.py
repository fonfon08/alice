import logging
import os
import secrets
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from logic.core import server
from utils import config

class HttpAccessTokenGate(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        expected = str(config.http_access_token or "").strip()
        if not expected:
            return await call_next(request)
        header = str(request.headers.get("authorization") or "").strip()
        presented = header
        if header.lower().startswith("bearer "):
            presented = header[7:].strip()
        if presented and len(presented) == len(expected) and secrets.compare_digest(presented, expected):
            return await call_next(request)
        return Response("unauthorized", status_code=401)

def run_http():
    # Serves the same MCPServer tools over Streamable HTTP, with optional TLS
    config.ensure_access_token()
    host = str(config.http_host or "127.0.0.1").strip() or "127.0.0.1"
    port = int(config.http_port or 9100)
    path = str(config.http_path or "/mcp").strip() or "/mcp"
    if not path.startswith("/"):
        path = "/" + path
    tls_on = bool(config.http_tls)
    cert_path = str(config.http_certfile or "").strip()
    key_path = str(config.http_keyfile or "").strip()
    tls_skip = {"", "none", "false", "null", "unset"}
    uvicorn_kwargs = {
        "host": host,
        "port": port,
        "log_level": "critical",
        "access_log": False,
        "log_config": None,
    }
    if (
        tls_on
        and cert_path.lower() not in tls_skip
        and key_path.lower() not in tls_skip
        and os.path.isfile(cert_path)
        and os.path.isfile(key_path)
        and os.access(cert_path, os.R_OK)
        and os.access(key_path, os.R_OK)
    ):
        uvicorn_kwargs["ssl_certfile"] = cert_path
        uvicorn_kwargs["ssl_keyfile"] = key_path
    for name in (
        "",
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "uvicorn.asgi",
        "fastapi",
        "starlette",
        "mcp_server",
        "mcp_server.http",
        "mcp_server.core",
    ):
        log = logging.getLogger(name) if name else logging.getLogger()
        log.handlers.clear()
        log.setLevel(logging.CRITICAL)
        log.propagate = False
    logging.disable(logging.CRITICAL)
    starlette_app = server.streamable_http_app(streamable_http_path=path, host=host)
    starlette_app.add_middleware(HttpAccessTokenGate)
    cfg = uvicorn.Config(starlette_app, **uvicorn_kwargs)
    http_server = uvicorn.Server(cfg)
    http_server.run()
