#!/usr/bin/env python3

# Copyright (C) 2026 Gustavo Henrique T.
# SPDX-License-Identifier: GPL-3.0-or-later
# See LICENSE and DISCLAIMER.md in the repository root.

import os
import re
import subprocess
import sys
from pathlib import Path

# VARIABLES ======================================================================================

root = Path(__file__).resolve().parent
alice_cmd = Path(sys.argv[0]).name

server_root = root / "server"
client_root = root / "client" / "gui"
toolchain = root / "toolchain"

alice_help = f"""USAGE:
    {alice_cmd} <mode> <command> ...

MODES
    server                             Server mode
    client                             Client mode

COMMANDS
    help                               Show this help message
    version                            Show version of the server and client

    server start                       Start server
    client start                       Start client

    server config list                 List server config
    server config set <key> <value>    Set server config
    server config reset <key>          Reset server config to default
    server config load <file>          Load server config from file
    server config create-tls           Create a self signed cert and enable TLS

    server key list                    List operators keys
    server key add john                Create operator key
    server key rem john                Remove operator key

    server mcp [on|off]                Enable or disable MCP server
    server mcp reauth                  Recreate operator key of MCP server
    server mcp mode [http|stdio]       Set MCP server mode

    server mcp tls [true|false]        Enable or disable TLS
    server mcp create-tls              Create a self signed cert and enable TLS
    server mcp host <host>             Set MCP HTTP host
    server mcp port <port>             Set MCP HTTP port
    server mcp path <path>             Set MCP HTTP path
    server mcp certfile <file>         Set MCP HTTP certfile
    server mcp keyfile <file>          Set MCP HTTP keyfile
    server mcp access_token <token>    Set MCP HTTP access token

    server venv list                   List installed python packages
    server venv install <package>      Install a python package
    server venv uninstall <package>    Uninstall a python package

    server db usage                    Show database information
    server db export <path>            Export database to a file
    server db import <file>            Import database from a file
"""

# FUNCTIONS ======================================================================================


def is_root():
    if os.name == "nt":
        return False
    return os.geteuid() == 0


def venv_python():
    # Finds the server virtualenv interpreter on Windows or POSIX
    for candidate in (
        server_root / ".venv" / "Scripts" / "python.exe",
        root / ".venv" / "Scripts" / "python.exe",
        server_root / "venv" / "Scripts" / "python.exe",
        server_root / "venv" / "bin" / "python3",
    ):
        if candidate.is_file():
            return candidate
    return None


def server_env():
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(server_root), str(server_root / "core")])
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    if toolchain.is_dir():
        paths = [str(toolchain / "mingw64" / "bin")]
        for nim_dir in sorted(toolchain.glob("nim-*"), reverse=True):
            if (nim_dir / "bin").is_dir():
                paths.append(str(nim_dir / "bin"))
                break
        env["PATH"] = os.pathsep.join(paths + [env.get("PATH", "")])
        gcc = toolchain / "mingw64" / "bin" / "x86_64-w64-mingw32-gcc.exe"
        if gcc.is_file():
            env.setdefault("MINGW64_GCC", str(gcc))
    return env


def client():
    if os.name == "nt":
        for candidate in (
            client_root / "dist" / "win-unpacked" / "ALICE.exe",
            client_root / "dist" / "win-unpacked" / "alice.exe",
        ):
            if candidate.is_file():
                subprocess.Popen([str(candidate)], cwd=str(client_root))
                return

        electron = client_root / "node_modules" / "electron" / "dist" / "electron.exe"
        if electron.is_file():
            subprocess.Popen([str(electron), str(client_root)], cwd=str(client_root))
            return

        print(
            f"[ \x1b[38;2;255;48;48mERROR\x1b[0m ] Client not built. Run: cd client\\gui && npm install && npm run build",
            file=sys.stderr,
        )
        sys.exit(1)

    if sys.platform == "darwin":
        app = client_root / "dist" / "mac" / "alice.app" / "Contents" / "MacOS" / "alice"
        if not app.is_file():
            app = client_root / "dist" / "mac-arm64" / "alice.app" / "Contents" / "MacOS" / "alice"
        if not app.is_file():
            print(f"[ \x1b[38;2;255;48;48mERROR\x1b[0m ] Client app not found: {client_root / 'dist' / 'mac' / 'alice.app'}", file=sys.stderr)
            sys.exit(1)
        os.execv(str(app), [str(app)])

    gui = Path("/usr/local/bin/alice-gui")
    if os.access(gui, os.X_OK):
        os.execv(gui, [str(gui)])

    if not os.access(client_root / "dist" / "alice.AppImage", os.X_OK):
        print(f"[ \x1b[38;2;255;48;48mERROR\x1b[0m ] Client AppImage not found: {client_root / 'dist' / 'alice.AppImage'}", file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    if is_root():
        env["DISPLAY"] = env.get("DISPLAY") or ":0"
        sudo_user = env.get("SUDO_USER", "")
        if sudo_user:
            env["XAUTHORITY"] = f"/home/{sudo_user}/.Xauthority"

    argv = [str(client_root / "dist" / "alice.AppImage")]
    if is_root():
        argv.append("--no-sandbox")
    os.execve(str(client_root / "dist" / "alice.AppImage"), argv, env)


def server(argv):
    if not server_root.is_dir():
        print(f"[ \x1b[38;2;255;48;48mERROR\x1b[0m ] Server dir not found: {server_root}", file=sys.stderr)
        sys.exit(1)

    python = venv_python()
    if python is None:
        print(
            "[ \x1b[38;2;255;48;48mERROR\x1b[0m ] Server virtualenv not found. Run install\\windows.bat server",
            file=sys.stderr,
        )
        sys.exit(1)

    main_py = server_root / "main.py"
    sys.exit(subprocess.call([str(python), str(main_py), *argv], cwd=str(server_root), env=server_env()))


def version():
    sv = ""
    cv = ""
    version_py = server_root / "version.py"
    if version_py.is_file():
        for line in version_py.read_text().splitlines():
            m = re.match(r'^\s*__version__\s*=\s*"([^"]*)"', line)
            if m:
                sv = m.group(1)
                break
    package_json = client_root / "package.json"
    if package_json.is_file():
        for line in package_json.read_text().splitlines():
            m = re.search(r'.*"version"\s*:\s*"([^"]*)"', line)
            if m:
                cv = m.group(1)
                break
    if not sv:
        sv = "unknown"
    if not cv:
        cv = "unknown"
    print(f"client\t{cv}")
    print(f"server\t{sv}")


# MAIN LOGIC =====================================================================================

args = sys.argv[1:]
args_spaced = f" {' '.join(args)} " if args else " "

if len(args) == 0 or " help " in args_spaced:
    print(alice_help)
    sys.exit(0)

if len(args) >= 2 and args[0] == "client" and args[1] == "start":
    if is_root():
        print("[ \x1b[38;2;255;48;48mERROR\x1b[0m ] The client must not be executed with sudo", file=sys.stderr)
        sys.exit(1)
    client()
    sys.exit(0)

if len(args) >= 1 and args[0] == "server":
    if is_root():
        print("[ \x1b[38;2;255;48;48mERROR\x1b[0m ] The server must not be executed with sudo", file=sys.stderr)
        sys.exit(1)
    server(args[1:])

if len(args) >= 1 and args[0] == "version":
    version()
    sys.exit(0)

print(alice_help, file=sys.stderr)
sys.exit(1)
