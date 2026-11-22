import os
import socket
import subprocess
import sys
import time
from pathlib import Path

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None
    import msvcrt

server_root = Path(__file__).resolve().parents[3]
worker_dir = server_root / "workers" / "mcp_server"
lock_path = server_root / "infra" / "tmp" / "mcp-http.lock"
err_path = server_root / "infra" / "tmp" / "mcp-http.err"


def wait_listen(host, port, timeout, proc=None):
    # Waits until the MCP HTTP port accepts TCP and the worker is still alive
    bind = "127.0.0.1" if str(host) in ("0.0.0.0", "::", "[::]") else str(host)
    deadline = time.time() + float(timeout)
    while time.time() < deadline:
        if proc is not None and proc.poll() is not None:
            return False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.4)
        try:
            sock.connect((bind, int(port)))
        except OSError:
            time.sleep(0.1)
            continue
        finally:
            try:
                sock.close()
            except OSError:
                pass
        time.sleep(0.2)
        if proc is not None and proc.poll() is not None:
            return False
        return True
    return False


def crash_detail(proc):
    # Reads the worker stderr dump so a dead child is not reported as ready
    code = proc.poll()
    text = ""
    if err_path.is_file():
        try:
            text = err_path.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            text = ""
    if text:
        return f"exit {code}: {text[-2000:]}"
    if code is not None:
        return f"exit {code}"
    return "worker did not become ready in time"


def boot(mcp=None):
    # Reads mcp conf, starts HTTP when enabled, returns fields for server.py prints
    block = mcp if isinstance(mcp, dict) else {}
    enabled = bool(block.get("enabled"))
    mode = str(block.get("mode") or "stdio").strip().lower()
    if mode not in ("stdio", "http"):
        mode = "stdio"
    http = block.get("http") if isinstance(block.get("http"), dict) else {}
    host = str(http.get("host") or "127.0.0.1")
    port = http.get("port") or 9100
    path = str(http.get("path") or "/mcp")
    if not path.startswith("/"):
        path = "/" + path
    scheme = "https" if http.get("tls") else "http"
    error = None
    if enabled and mode == "http":
        try:
            start_worker(host, port)
        except Exception as exc:
            error = str(exc)
    return {
        "enabled": enabled,
        "mode": mode,
        "host": host,
        "port": port,
        "path": path,
        "scheme": scheme,
        "error": error,
    }


def start_worker(host, port):
    # Starts one MCP HTTP subprocess on this thread and waits until it listens
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        else:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    except OSError:
        os.close(fd)
        if wait_listen(host, port, 30.0):
            return None
        raise RuntimeError("MCP HTTP port did not open")
    python = sys.executable
    for candidate in (server_root / ".venv" / "Scripts" / "python.exe",
                      server_root / "venv" / "Scripts" / "python.exe",
                      server_root / "venv" / "bin" / "python3"):
        if candidate.is_file():
            python = str(candidate)
            break
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(server_root), str(server_root / "core")])
    err_file = open(err_path, "wb")
    proc = subprocess.Popen(
        [str(python), str(worker_dir / "main.py")],
        cwd=str(worker_dir),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=err_file,
    )
    if not wait_listen(host, port, 30.0, proc):
        os.close(fd)
        err_file.close()
        raise RuntimeError(crash_detail(proc))
    return proc
