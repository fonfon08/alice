# Side-effect imports register MCP tools. Route coverage: logic/functions/registry.md

import importlib

def register_all_tools():
    # Imports every logic.functions module so @server.tool decorators run once
    module_names = (
        "logic.functions.aes",
        "logic.functions.agents",
        "logic.functions.auth",
        "logic.functions.credentials",
        "logic.functions.explorer",
        "logic.functions.file_server",
        "logic.functions.implants",
        "logic.functions.iocs",
        "logic.functions.keylogger",
        "logic.functions.listeners",
        "logic.functions.logs",
        "logic.functions.network",
        "logic.functions.notifications",
        "logic.functions.nsoutput",
        "logic.functions.process",
        "logic.functions.queue",
        "logic.functions.reports",
        "logic.functions.screenshot",
        "logic.functions.scripts",
        "logic.functions.sessions",
        "logic.functions.terminal",
    )
    for name in module_names:
        importlib.import_module(name)