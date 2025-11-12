#!/usr/bin/env bash
# Convenience wrapper to launch the universal INSTALL script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_SCRIPT="$SCRIPT_DIR/INSTALL"

if [[ $EUID -eq 0 ]]; then
    echo "[HACHI] Please run this installer as a regular user, not as root."
    exit 1
fi

if [[ ! -f "$INSTALL_SCRIPT" ]]; then
    echo "[HACHI] Unable to find the core INSTALL script at $INSTALL_SCRIPT" >&2
    exit 1
fi

chmod +x "$INSTALL_SCRIPT"

exec "$INSTALL_SCRIPT"
