#!/usr/bin/env bash
# PAEM installer - forwards its arguments to scripts/install.py (try --list).

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(command -v python3 || command -v python)" || { echo "PAEM's installer needs Python 3.11+" >&2; exit 1; }
exec "$PYTHON" "$SCRIPT_DIR/scripts/install.py" "$@"
