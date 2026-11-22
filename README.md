<p align="center">
  <img src="eris.png" width="150" alt="ALICE">
</p>

<h1 align="center">ALICE</h1>

<p align="center">Post-exploitation framework for red team operations.</p>

---

ALICE is a Windows-first fork of [NukeRat](https://github.com/nukeratframework/nukerat). The server, console and implants are rebranded and adapted to run natively on Windows.

## Install

Download `ALICE-Full-Setup-1.8.0.exe` from [Releases](../../releases). It installs the server and console, creates the operator key, pulls the implant toolchain and starts the team server.

Requirements: Windows 10/11 x64, Python 3.10+ in `PATH`.

From source:

```bat
install\windows.bat server
install\windows.bat toolchain
python alice.py server key add operator
python alice.py server start
python alice.py client start
```

The key is saved to `server\operator.key`. The console connects to `http://127.0.0.1:9000`.

## Ports

| Port | Service |
|------|---------|
| 9000 | Team server API and client authentication |
| 8443 | Default HTTP listener |
| 8000 | MCP HTTP server (optional) |

Listeners can bind any port. Open the callback port you pick in the firewall.

## Features

- Listeners: HTTP, TCP, SMB, file server, SOCKS5, port forward
- Implants: Windows and Linux (Nim), macOS (Go); x64 and ARM64
- Evasion: indirect syscalls, stack spoofing, sleep mask, AMSI/ETW patch, PE metadata
- Injection: VirtualAlloc, section mapping, module stomping
- Armory: 550+ BOF and .NET utilities
- LOTL: 240+ native Windows binaries
- Post: terminal, file explorer, process tree, credentials, keylogger, screenshots, network pivots
- Automation: AliceScripts, MCP server, AI agent integration
- External C2: Telegram, Discord
- Reports: command history, IOCs, compromised hosts

## Layout

```
alice.py        launcher (server / client / version)
server/         FastAPI team server, SQLite, listeners
client/gui/     Electron + React console
implants/       Nim and Go implant sources
install/        Windows installer and build scripts
```

## Build

```bat
install\make_release.ps1          REM production zip
install\make_full_installer.ps1   REM all-in-one setup
```

Client only:

```bat
cd client\gui
npm install
npm run build
npm run dist
```

## Credits

Based on [NukeRat](https://github.com/nukeratframework/nukerat), GPLv3.
SGN (MIT, Ege Balcı), nimcrypto (MIT, Eugene Kabanov), LOLBAS (GPLv3).

See [LICENSE](LICENSE) and [DISCLAIMER.md](DISCLAIMER.md).
