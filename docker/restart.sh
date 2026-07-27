#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================================="
echo " Restarting Voice Assistant MSA Containers       "
echo "=================================================="

"$SCRIPT_DIR/stop.sh"
"$SCRIPT_DIR/start.sh" "$@"

echo "=================================================="
echo " Containers Restarted Successfully!               "
echo "=================================================="
