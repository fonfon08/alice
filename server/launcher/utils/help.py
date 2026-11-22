usage = """USAGE:
    server <command> ...

COMMANDS
    start                       Start server

    config list                 List server config
    config set <key> <value>    Set server config
    config reset <key>          Reset server config to default
    config load <file>          Load server config from file
    config create-tls           Create a self signed cert and enable TLS

    key list                    List operators keys
    key add <name>              Create operator key
    key rem <name>              Remove operator key

    mcp [on|off]                Enable or disable MCP server
    mcp reauth                  Recreate operator key of MCP server
    mcp mode [http|stdio]       Set MCP server mode

    mcp tls [true|false]        Enable or disable TLS
    mcp create-tls              Create a self signed cert and enable TLS
    mcp host <host>             Set MCP HTTP host
    mcp port <port>             Set MCP HTTP port
    mcp path <path>             Set MCP HTTP path
    mcp certfile <file>         Set MCP HTTP certfile
    mcp keyfile <file>          Set MCP HTTP keyfile
    mcp access_token <token>    Set MCP HTTP access token

    venv list                   List installed python packages
    venv install <package>      Install a python package
    venv uninstall <package>    Uninstall a python package

    db usage                    Show database information
    db export <path>            Export database to a file
    db import <file>            Import database from a file
"""
