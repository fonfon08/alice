#!/usr/bin/env bash

# Copyright (C) 2026 Gustavo Henrique T.
# SPDX-License-Identifier: GPL-3.0-or-later
# See LICENSE in the repository root.

set -euo pipefail

# ======================================================================================
# VARIABLES
# ======================================================================================

help_message="Usage: bash docker.sh <mode>

MODES:
  server    Install server
  client    Install client
  all       Install server and client

EXAMPLES:
  bash docker.sh server
  bash docker.sh client
  bash docker.sh all
"

script_dir="$(cd "$(dirname "$0")" && pwd)"
main_dir="$(cd "${script_dir}/../.." && pwd)"
server_dockerfile="${script_dir}/server/Dockerfile"
client_dockerfile="${script_dir}/client/Dockerfile"

# ======================================================================================
# UTILS
# ======================================================================================

check_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is not installed." >&2
    exit 1
  fi
  if docker info >/dev/null 2>&1; then
    return
  fi
  if [[ "$EUID" -ne 0 ]]; then
    echo "Please run as root: sudo bash $0 ${1:-}" >&2
    exit 1
  fi
  echo "Cannot talk to the Docker daemon. Is it running?" >&2
  echo "Start it with: sudo systemctl start docker" >&2
  docker info >&2 || true
  exit 1
}

check_dockerfile() {
  if [[ ! -f "$1" ]]; then
    echo "Not found: $1" >&2
    exit 1
  fi
}

validations_check() {
  check_docker "${1:-}"
}

# ======================================================================================
# CLIENT INSTALLATION
# ======================================================================================

install_client() {
  check_dockerfile "${client_dockerfile}"
  docker build -f "${client_dockerfile}" -t alice-client "${main_dir}"
}

# ======================================================================================
# SERVER INSTALLATION
# ======================================================================================

install_server() {
  check_dockerfile "${server_dockerfile}"
  docker build -f "${server_dockerfile}" -t alice-server "${main_dir}"
}

# ======================================================================================
# MAIN ENTRYPOINT
# ======================================================================================

if [[ "${1:-}" = "server" || "${1:-}" = "client" || "${1:-}" = "all" ]]; then
  validations_check "${1:-}"
fi

if [ "${1:-}" = "server" ]; then
  install_server
elif [ "${1:-}" = "client" ]; then
  install_client
elif [ "${1:-}" = "all" ]; then
  install_server
  install_client
else
  echo "$help_message" >&2
  exit 1
fi
