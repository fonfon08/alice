def operator_note(kind, *, detail="", mcp_enabled=True):
    # Single entry for agent/operator hints (MCP instructions and tool errors)
    enable_cmd = "./alice.py server mcp on"
    reauth_cmd = "./alice.py server mcp reauth"

    if kind == "enable_cmd":
        return enable_cmd

    if kind == "reauth_cmd":
        return reauth_cmd

    if kind == "disabled":
        return (
            f"MCP is disabled in server.conf (mcp.enabled=false). "
            f"Operator: {enable_cmd} from the ALICE repo root, then reload MCP in the IDE."
        )

    if kind == "missing_credentials":
        return (
            "MCP operator_key missing (mcp.operator_key in server.conf). "
            f"Operator: {enable_cmd} or {reauth_cmd} from repo root, then reload MCP."
        )

    if kind == "unauthorized":
        base = str(detail or "").strip() or "not authorized"
        return (
            f"{base} Operator: {reauth_cmd} from the ALICE repo root "
            "(syncs operator key with the team server DB), then reload MCP."
        )

    if kind == "instructions":
        lines = [
            "ALICE MCP worker talks to the team server REST API using mcp.* from server.conf.",
            f"If tools fail with HTTP 401 or login errors, the operator must run {reauth_cmd} "
            "from the repo root (recreates operator key in server.conf), then reload MCP.",
        ]

        if not mcp_enabled:
            lines.append(
                f"mcp.enabled is false in server.conf; operator should run {enable_cmd} "
                "before using tools."
            )

        return " ".join(lines)

    raise ValueError(f"unknown operator_note kind: {kind}")