from launcher.utils.mcp import (
    mcp_create_tls,
    mcp_disable,
    mcp_enable,
    mcp_http_set,
    mcp_mode,
    mcp_reauth,
)

def main_mcp(option):
    # Receives the mcp command and calls on/off, reauth, mode, http keys, or create-tls
    parts = option.split()

    if len(parts) < 2 or parts[0] != "mcp":
        print("Invalid option")
        return

    action = parts[1]

    if action in ("on", "off"):
        if len(parts) != 2:
            print('Invalid syntax. Use "mcp [on|off]".')
            return
        if action == "on":
            exit_code = mcp_enable()
        else:
            exit_code = mcp_disable()
        if exit_code:
            raise SystemExit(exit_code)
        return

    if action == "reauth":
        if len(parts) != 2:
            print('Invalid syntax. Use "mcp reauth".')
            return
        exit_code = mcp_reauth()
        if exit_code:
            raise SystemExit(exit_code)
        return

    if action == "mode":
        if len(parts) != 3:
            print('Invalid syntax. Use "mcp mode [http|stdio]".')
            return
        exit_code = mcp_mode(parts[2])
        if exit_code:
            raise SystemExit(exit_code)
        return

    if action == "create-tls":
        if len(parts) != 2:
            print('Invalid syntax. Use "mcp create-tls".')
            return
        exit_code = mcp_create_tls()
        if exit_code:
            raise SystemExit(exit_code)
        return

    if action in ("host", "port", "path", "tls", "certfile", "keyfile", "access_token"):
        if len(parts) < 3:
            print(f'Invalid syntax. Use "mcp {action} <value>".')
            return
        exit_code = mcp_http_set(action, " ".join(parts[2:]))
        if exit_code:
            raise SystemExit(exit_code)
        return

    print("Invalid option")
