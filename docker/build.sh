#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/compose/docker-compose.yml"

echo "=================================================="
echo " Building Docker Images for Voice Assistant MSA   "
echo "=================================================="
echo " -> Compose File: $COMPOSE_FILE"

docker compose -f "$COMPOSE_FILE" build "$@"

echo "=================================================="
echo " Build Completed Successfully!                   "
echo "=================================================="
