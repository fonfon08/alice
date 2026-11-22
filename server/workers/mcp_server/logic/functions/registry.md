# MCP tools ↔ team server routes

Checklist against `server/core/routes`. `[x]` = at least one MCP tool hits the route; `[ ]` = not covered.

## Auth

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| POST /auth/login | env only | `alice_auth_login_info` (documents env auth, no live login) |
| POST /auth/check | x | `alice_auth_check` |

## /api/sessions

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/sessions/ | x | `alice_list_sessions` |
| PATCH /api/sessions/{tag} | x | `alice_patch_session` |
| DELETE /api/sessions/{tag} | x | `alice_delete_session` |

## /api/listeners

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/listeners/ | x | `alice_list_listeners` |
| POST /api/listeners/ | x | `alice_create_listener` |
| DELETE /api/listeners/{tag} | x | `alice_delete_listener` |

## /api/aes

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| POST /api/aes/create | x | `alice_create_aes_key` |

## /api/agents

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/agents/ | x | `alice_list_agents` |
| POST /api/agents/ | x | `alice_post_agent` |
| PATCH /api/agents/{tag} | x | `alice_patch_agent` |
| DELETE /api/agents/{tag} | x | `alice_delete_agent` |

## /api/credentials

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/credentials/ | x | `alice_list_credentials` |
| POST /api/credentials/ | x | `alice_create_credential` |
| PATCH /api/credentials/{tag} | x | `alice_patch_credential` |
| DELETE /api/credentials/{tag} | x | `alice_delete_credential` |

## /api/scripts

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/scripts/ | x | `alice_list_scripts` |
| POST /api/scripts/ | x | `alice_create_script` |
| PATCH /api/scripts/{tag} | x | `alice_patch_script` |
| DELETE /api/scripts/{tag} | x | `alice_delete_script` |

## /api/nsoutput

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/nsoutput/ | x | `alice_fetch_nsoutput` |

## /api/terminal

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| POST /api/terminal/ | x | `alice_terminal_command`, `alice_terminal_help`, `alice_terminal_command_with_file`, `alice_terminal_upload_raw`, `alice_terminal_download` |

## /api/explorer

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| POST /api/explorer/ | x | `alice_explorer_list`, `alice_explorer_download_file` |

## /api/process

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| POST /api/process/ | x | `alice_list_processes` |

## /api/implants

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| POST /api/implants/ | x | `alice_build_implant` |

## /api/file_server

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/file_server/{tag} | x | `alice_file_server_list` |
| GET /api/file_server/{tag}/files/{file_name}/download | x | `alice_file_server_download` |
| POST /api/file_server/{tag}/files/{file_name} | x | `alice_file_server_upload` |
| PATCH /api/file_server/{tag}/files/{file_name} | x | `alice_file_server_rename` |
| DELETE /api/file_server/{tag}/files/{file_name} | x | `alice_file_server_delete` |

## /api/screenshot

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/screenshot/{tag} | x | `alice_screenshot_get` |

## /api/keylogger

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/keylogger/ | x | `alice_keylogger_list` |
| DELETE /api/keylogger/{tag} | x | `alice_keylogger_delete` |

## /api/queue

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/queue/ | x | `alice_queue_list` |
| DELETE /api/queue/{tag} | x | `alice_queue_delete` |

## /api/iocs

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/iocs/ | x | `alice_list_iocs` |
| DELETE /api/iocs/{tag} | x | `alice_delete_ioc` |

## /api/logs

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/logs/ | x | `alice_list_logs` |

## /api/notifications

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/notifications/ | x | `alice_list_notifications` |
| GET /api/notifications/custom | x | `alice_list_custom_notifications` |

## /api/network

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/network/ | x | `alice_list_network` |
| POST /api/network/ | x | `alice_create_socks_network`, `alice_create_port_forward_network`, `alice_restart_network` |
| DELETE /api/network/{tag} | x | `alice_delete_network` |

## /api/reports

| Route | Covered | MCP tool(s) |
|-------|---------|-------------|
| GET /api/reports/ | x | `alice_list_reports` |
| POST /api/reports/ | x | `alice_create_report` |
| GET /api/reports/{tag}/download | x | `alice_download_report` |
| GET /api/reports/{tag}/view | x | `alice_view_report` |
| DELETE /api/reports/{tag} | x | `alice_delete_report` |