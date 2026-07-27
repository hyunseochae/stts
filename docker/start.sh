#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/compose/docker-compose.yml"

echo "=================================================="
echo " Starting Voice Assistant MSA Containers         "
echo "=================================================="
echo " -> Compose File: $COMPOSE_FILE"

docker compose -f "$COMPOSE_FILE" up -d "$@"

echo "=================================================="
echo " Status Check:                                    "
docker compose -f "$COMPOSE_FILE" ps
echo "=================================================="
