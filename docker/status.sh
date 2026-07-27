#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/compose/docker-compose.yml"

echo "=================================================="
echo " Voice Assistant MSA Status                      "
echo "=================================================="

docker compose -f "$COMPOSE_FILE" ps "$@"
