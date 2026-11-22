import secrets
import re
from urllib.parse import urlparse
from utils import conf_dump

base_url = ""
tls_verify = True
operator_key_line = ""
enabled = False
mode = "stdio"
http_host = "127.0.0.1"
http_port = 9100
http_path = "/mcp"
http_tls = False
http_certfile = "none"
http_keyfile = "none"
http_access_token = ""
host_tag_pattern = re.compile(r"^[A-Za-z0-9]{3,32}$")
command_max_chars = 8192
binary_max_bytes = 52428800

def apply_conf_block(block):
    # Copies one mcp dict from server.conf into module-level settings
    global enabled, base_url, tls_verify, mode, operator_key_line
    global http_host, http_port, http_path
    global http_tls, http_certfile, http_keyfile, http_access_token

    if not isinstance(block, dict):
        return

    enabled = bool(block.get("enabled"))

    if block.get("base_url"):
        base_url = str(block.get("base_url", "")).strip().rstrip("/")

    operator_key_line = str(block.get("operator_key", "")).strip()

    if "tls_verify" in block:
        tls_verify = bool(block.get("tls_verify"))

    raw_mode = str(block.get("mode", "")).strip().lower()
    if raw_mode in ("stdio", "http"):
        mode = raw_mode

    http_block = block.get("http")
    if not isinstance(http_block, dict):
        http_block = {}
    raw_host = str(http_block.get("host", "")).strip()
    if raw_host:
        http_host = raw_host
    raw_path = str(http_block.get("path", "")).strip()
    if raw_path:
        http_path = raw_path if raw_path.startswith("/") else "/" + raw_path
    raw_port = http_block.get("port", http_port)
    try:
        parsed_port = int(raw_port)
    except (TypeError, ValueError):
        parsed_port = 9100
    if parsed_port < 1 or parsed_port > 65535:
        parsed_port = 9100
    http_port = parsed_port
    if "tls" in http_block:
        http_tls = bool(http_block.get("tls"))
    raw_cert = str(http_block.get("certfile", "")).strip()
    if raw_cert:
        http_certfile = raw_cert
    raw_key = str(http_block.get("keyfile", "")).strip()
    if raw_key:
        http_keyfile = raw_key
    raw_access_token = str(http_block.get("access_token", "")).strip()
    if raw_access_token:
        http_access_token = raw_access_token

def validate_base_url():
    # Ensures we have a usable team server URL before any HTTP tool runs
    global base_url

    if not base_url:
        raise RuntimeError("team server URL is missing ([server] host/port)")

    parsed = urlparse(base_url)

    if parsed.scheme not in ("http", "https"):
        raise RuntimeError("team server URL must start with http:// or https://")

    if not parsed.netloc:
        raise RuntimeError("team server URL host is missing")

    base_url = base_url.rstrip("/")

def load_settings():
    # Loads MCP connection settings from server.conf
    apply_conf_block(conf_dump.dump_mcp_config())
    validate_base_url()

def ensure_access_token():
    # Creates mcp.http.access_token when HTTP starts with an empty value
    global http_access_token
    token = str(http_access_token or "").strip()
    if token:
        http_access_token = token
        return token
    token = secrets.token_urlsafe(32)
    http_access_token = token
    conf_dump.persist_http_access_token(token)
    return token
