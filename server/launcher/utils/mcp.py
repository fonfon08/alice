import secrets
import string
import subprocess
from pathlib import Path
import bcrypt
from infra.database.database import User, sqlite_db_sync as sqlite_db
from launcher.utils.config import config_operations, config_set, validate_config


def parse_operator_key_line(line):
    raw = str(line or "").strip()

    if raw.count(":") < 2:
        return "", "", ""

    name, passwd, key_secret = raw.split(":", 2)
    return name.strip(), passwd.strip(), key_secret.strip()


def provision_mcp_operator(username, force_new):
    sqlite_db.start()
    base = str(username or "").strip()

    if not base:
        print("MCP username is required")
        return 1

    if "/" in base or "\\" in base or base in (".", ".."):
        print("Invalid MCP username")
        return 1

    if len(base) > 150:
        print("MCP username must be less than 150 characters")
        return 1

    parser = config_operations("read")
    current_key = ""

    if parser.has_section("mcp"):
        current_key = parser.get("mcp", "operator_key", fallback="").strip()
        key_user, _, _ = parse_operator_key_line(current_key)

        if key_user and current_key and not force_new:
            return 0

    pool = string.ascii_letters + string.digits
    password = "".join(secrets.choice(pool) for _ in range(23))
    operator_key = "".join(secrets.choice(pool) for _ in range(256))
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    rows = sqlite_db.read(User, user=base)

    if rows:
        sqlite_db.modify(
            User,
            {"user": base},
            {"password_hash": password_hash, "secret": operator_key},
        )
        action = "updated"
    else:
        sqlite_db.write(User(user=base, password_hash=password_hash, secret=operator_key))
        action = "created"

    key_path = Path.cwd() / f"{base}.key"
    key_path.write_text(f"{base}:{password}:{operator_key}\n", encoding="utf-8")

    credential_line = f"{base}:{password}:{operator_key}"

    if config_set("mcp.operator_key", credential_line):
        return 1

    print(credential_line)
    print(f"MCP operator {action}: {base}")
    print(f"Saved: {key_path}")
    return 0


def mcp_enable():
    parser = config_operations("read")
    username = "mcp"

    raw = ""
    if parser.has_section("mcp"):
        raw = parser.get("mcp", "operator_key", fallback="").strip()
        key_user, key_pass, key_secret = parse_operator_key_line(raw)
        if key_user:
            username = key_user

    key_user, key_pass, key_secret = parse_operator_key_line(raw)
    missing_key = not (key_user and key_pass and key_secret)

    if missing_key:
        if provision_mcp_operator(username, True):
            return 1

    code = config_set("mcp.enabled", "true")

    if code:
        return code

    print("MCP server on")
    return 0

def mcp_disable():
    code = config_set("mcp.enabled", "false")

    if code:
        return code

    print("MCP server off")
    return 0

def mcp_http_set(option, value):
    # Sets one [mcp.http] key from the mcp CLI
    key = str(option or "").strip().lower()
    allowed = ("host", "port", "path", "tls", "certfile", "keyfile", "access_token")
    raw = str(value or "").strip()
    if key not in allowed:
        print(
            'Invalid syntax. Use "mcp <host|port|path|tls|certfile|keyfile|access_token> <value>".'
        )
        return 1
    if not raw:
        print(f'Invalid syntax. Use "mcp {key} <value>".')
        return 1
    if key == "tls":
        flag = raw.lower()
        if flag not in ("true", "false", "1", "0", "yes", "no", "on", "off"):
            print('Invalid syntax. Use "mcp tls [true|false]".')
            return 1
        raw = "true" if flag in ("true", "1", "yes", "on") else "false"
    if key == "path" and not raw.startswith("/"):
        raw = "/" + raw
    if config_set(f"mcp.http.{key}", raw):
        return 1
    print(f"MCP HTTP {key} set to {raw}")
    return 0

def mcp_reauth():
    parser = config_operations("read")
    username = "mcp"

    if parser.has_section("mcp"):
        raw = parser.get("mcp", "operator_key", fallback="").strip()
        key_user, _, _ = parse_operator_key_line(raw)
        if key_user:
            username = key_user

    if provision_mcp_operator(username, True):
        return 1

    print("MCP operator key recreated")
    return 0


def mcp_mode(mode):
    # Switches MCP between stdio and Streamable HTTP
    value = str(mode or "").strip().lower()
    if value not in ("http", "stdio"):
        print('Invalid syntax. Use "mcp mode [http|stdio]".')
        return 1
    if config_set("mcp.mode", value):
        return 1
    print(f"MCP server mode set to {value}")
    return 0


def mcp_create_tls():
    # Creates a self signed certificate and enables TLS on MCP HTTP
    server_root = Path(__file__).resolve().parents[2]
    certs_dir = (server_root / "infra" / "certs" / "mcp").resolve()
    certs_dir.mkdir(parents=True, exist_ok=True)
    certfile = certs_dir / "cert.pem"
    keyfile = certs_dir / "key.pem"
    parser = config_operations("read")
    conf_cert = ""
    conf_key = ""
    if parser.has_section("mcp.http"):
        conf_cert = parser.get("mcp.http", "certfile", fallback="").strip()
        conf_key = parser.get("mcp.http", "keyfile", fallback="").strip()
    if conf_cert or conf_key:
        print(
            f"Current MCP TLS paths: certfile={conf_cert or '(unset)'}, "
            f"keyfile={conf_key or '(unset)'}"
        )
        answer = input(
            "Replace existing MCP TLS certificate paths with a new self-signed certificate? [y/N]: "
        ).strip().lower()
        if answer not in ("y", "yes"):
            print("Cancelled.")
            return 0
    if conf_cert and conf_key:
        cp = Path(conf_cert).expanduser().resolve()
        kp = Path(conf_key).expanduser().resolve()
        if cp.parent == certs_dir:
            certfile = cp
        if kp.parent == certs_dir:
            keyfile = kp
    for path in (certfile, keyfile):
        if path.is_file():
            path.unlink()
    try:
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-keyout",
                str(keyfile),
                "-out",
                str(certfile),
                "-days",
                "365",
                "-nodes",
                "-subj",
                "/CN=localhost",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("Error: openssl not found")
        return 1
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc)).strip()
        print(f"Error: openssl failed ({detail})")
        return 1
    cert_path = str(certfile)
    key_path = str(keyfile)
    if not parser.has_section("mcp.http"):
        parser.add_section("mcp.http")
    parser.set("mcp.http", "tls", "true")
    parser.set("mcp.http", "certfile", cert_path)
    parser.set("mcp.http", "keyfile", key_path)
    config_operations("write", parser)
    err = validate_config()
    if err:
        print(err)
        return 1
    print(f"MCP TLS enabled (cert={cert_path}, key={key_path})")
    return 0