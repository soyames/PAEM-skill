#!/usr/bin/env bash
# PAEM Interactive Installer

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/scripts/install.py" "$@"
