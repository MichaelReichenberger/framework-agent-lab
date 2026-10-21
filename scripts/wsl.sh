#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
options=(-f compose.wsl.yaml)
if [[ -f .env.wsl ]]; then
    options=(--env-file .env.wsl "${options[@]}")
fi
exec docker compose "${options[@]}" "$@"
