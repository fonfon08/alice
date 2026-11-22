#!/usr/bin/env bash

root="$(cd "$(dirname "$0")/.." && pwd)"
conf="${root}/server.conf"

if [ ! -f "${conf}" ]; then
  echo "server.conf not found at ${conf}" >&2
  exit 1
fi

trim() {
  local v="$1"
  v="${v#"${v%%[![:space:]]*}"}"
  v="${v%"${v##*[![:space:]]}"}"
  printf '%s' "$v"
}

http="$(grep -A 15 '^\[mcp.http\]' "${conf}")"
host="$(trim "$(echo "${http}" | grep -E '^[[:space:]]*host[[:space:]]*=' | head -1 | cut -d= -f2-)")"
port="$(trim "$(echo "${http}" | grep -E '^[[:space:]]*port[[:space:]]*=' | head -1 | cut -d= -f2-)")"
path="$(trim "$(echo "${http}" | grep -E '^[[:space:]]*path[[:space:]]*=' | head -1 | cut -d= -f2-)")"
tls="$(trim "$(echo "${http}" | grep -E '^[[:space:]]*tls[[:space:]]*=' | head -1 | cut -d= -f2-)")"
access_token="$(trim "$(echo "${http}" | grep -E '^[[:space:]]*access_token[[:space:]]*=' | head -1 | cut -d= -f2-)")"
[ -z "${host}" ] && host="127.0.0.1"
[ -z "${port}" ] && port="9100"
[ -z "${path}" ] && path="/mcp"
case "${path}" in /*) ;; *) path="/${path}" ;; esac
case "$(printf '%s' "${tls}" | tr '[:upper:]' '[:lower:]')" in
  true | 1 | yes | on) scheme="https" ;;
  *) scheme="http" ;;
esac

echo "Command: ${root}/venv/bin/python"
echo "Args:    ${root}/workers/mcp_server/main.py"
echo
echo "host=${host}"
echo "port=${port}"
echo "path=${path}"
echo "tls=${tls:-false}"
echo "access_token=${access_token}"
echo "url=${scheme}://${host}:${port}${path}"
