import configparser
from pathlib import Path

def parse_bool(value, default):
    # Interprets boolean strings the same way as the launcher config loader

    if value is None:
        return default

    text = str(value).strip().lower()

    if text in ("1", "true", "yes", "on"):
        return True

    if text in ("0", "false", "no", "off"):
        return False

    return default

def server_conf_path():
    # Points at server.conf next to the team server root
    return Path(__file__).resolve().parents[3] / "server.conf"

def read_server_conf():
    # Opens server.conf into a ConfigParser or returns an empty parser
    parser = configparser.ConfigParser(interpolation=None)
    path = server_conf_path()

    if path.is_file():
        parser.read(path, encoding="utf-8")

    return parser

def server_public_url(parser):
    # Builds a team server base URL from [server] and [server.tls]

    if not parser.has_section("server"):
        return ""

    host = parser.get("server", "host", fallback="127.0.0.1").strip() or "127.0.0.1"
    port = parser.get("server", "port", fallback="9000").strip() or "9000"
    tls = False
    cert_raw = ""
    key_raw = ""

    if parser.has_section("server.tls"):
        raw = parser.get("server.tls", "tls", fallback="false").strip().lower()
        tls = raw in ("1", "true", "yes", "on")
        cert_raw = parser.get("server.tls", "certfile", fallback="").strip()
        key_raw = parser.get("server.tls", "keyfile", fallback="").strip()
    tls_skip = {"", "none", "false", "null", "unset"}
    if (
        not tls
        or cert_raw.lower() in tls_skip
        or key_raw.lower() in tls_skip
        or not Path(cert_raw).is_file()
        or not Path(key_raw).is_file()
    ):
        tls = False

    scheme = "https" if tls else "http"

    if host in ("0.0.0.0", "::", "[::]"):
        host = "127.0.0.1"

    return f"{scheme}://{host}:{port}"

def mcp_text(parser, key, default=""):
    # Reads one string from the mcp section

    if not parser.has_section("mcp"):
        return default

    raw = parser.get("mcp", key, fallback=default).strip()
    return raw if raw else default

def dump_mcp_config():
    # Extracts the mcp block from server.conf like launcher load_config does for other workers
    try:
        from launcher.utils.config import config

        block = config.get("mcp")

        if isinstance(block, dict) and block:
            return block

    except Exception:
        pass

    parser = read_server_conf()
    enabled = parse_bool(mcp_text(parser, "enabled", "false"), False)
    base_url = server_public_url(parser)
    operator_key = mcp_text(parser, "operator_key", "")
    tls_verify = True
    verify_host = "127.0.0.1"
    if parser.has_section("server"):
        verify_host = parser.get("server", "host", fallback="127.0.0.1").strip() or "127.0.0.1"
    if verify_host in ("0.0.0.0", "::", "[::]"):
        verify_host = "127.0.0.1"
    if verify_host in ("127.0.0.1", "localhost", "::1"):
        tls_verify = False
    elif parser.has_section("server.tls"):
        cert_raw = parser.get("server.tls", "certfile", fallback="").strip()
        if not cert_raw or cert_raw.lower() == "none":
            tls_verify = False
    mode = mcp_text(parser, "mode", "stdio").lower()
    if mode not in ("stdio", "http"):
        mode = "stdio"
    http_host = "127.0.0.1"
    http_port = 9100
    http_path = "/mcp"
    http_tls = False
    http_certfile = "none"
    http_keyfile = "none"
    http_access_token = ""

    if parser.has_section("mcp.http"):
        host_raw = parser.get("mcp.http", "host", fallback="").strip()
        if host_raw:
            http_host = host_raw
        port_raw = parser.get("mcp.http", "port", fallback="").strip()
        if port_raw:
            try:
                parsed_port = int(port_raw)
            except ValueError:
                parsed_port = 9100
            if parsed_port < 1 or parsed_port > 65535:
                parsed_port = 9100
            http_port = parsed_port
        path_raw = parser.get("mcp.http", "path", fallback="").strip()
        if path_raw:
            http_path = path_raw if path_raw.startswith("/") else "/" + path_raw
        tls_raw = parser.get("mcp.http", "tls", fallback="false").strip()
        http_tls = parse_bool(tls_raw, False)
        cert_raw = parser.get("mcp.http", "certfile", fallback="").strip()
        if cert_raw:
            http_certfile = cert_raw
        key_raw = parser.get("mcp.http", "keyfile", fallback="").strip()
        if key_raw:
            http_keyfile = key_raw
        access_token_raw = parser.get("mcp.http", "access_token", fallback="").strip()
        if access_token_raw:
            http_access_token = access_token_raw

    return {
        "enabled": enabled,
        "base_url": base_url.rstrip("/") if base_url else "",
        "operator_key": operator_key,
        "tls_verify": tls_verify,
        "mode": mode,
        "http": {
            "host": http_host,
            "port": http_port,
            "path": http_path,
            "tls": http_tls,
            "certfile": http_certfile,
            "keyfile": http_keyfile,
            "access_token": http_access_token,
        },
    }

def persist_http_access_token(token):
    # Writes mcp.http.access_token into server.conf and drops the old password key
    value = str(token or "").strip()
    if not value:
        raise RuntimeError("mcp.http.access_token is empty")
    path = server_conf_path()
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    if path.is_file():
        parser.read(path, encoding="utf-8")
    if not parser.has_section("mcp.http"):
        parser.add_section("mcp.http")
    parser.set("mcp.http", "access_token", value)
    if parser.has_option("mcp.http", "password"):
        parser.remove_option("mcp.http", "password")
    with open(path, "w", encoding="utf-8") as handle:
        parser.write(handle)
