#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
#
# DASHBOARD launcher wrapper.
#
# Resolves the project directory from its own location, so DASHBOARD can
# be cloned anywhere on the filesystem and still launch correctly. This is
# what the generated .desktop file calls (Exec=run-dashboard.sh).
#
# If python3 is not on PATH, set the PYTHON environment variable to an
# absolute python3 binary before running this script.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MAIN_PY="$SCRIPT_DIR/00_app/00_main.py"

if [ ! -f "$MAIN_PY" ]; then
    echo "DASHBOARD: entry point not found: $MAIN_PY" >&2
    echo "Expected the project layout (00_app must live next to run-dashboard.sh)." >&2
    exit 1
fi

if [ -n "${PYTHON:-}" ]; then
    PY_BIN="$PYTHON"
else
    PY_BIN="$(command -v python3 || true)"
fi

if [ -z "$PY_BIN" ] || [ ! -x "$PY_BIN" ] && ! command -v "$PY_BIN" >/dev/null 2>&1; then
    echo "DASHBOARD: python3 not found. Install Python 3 (>= 3.10) or set PYTHON." >&2
    exit 1
fi

exec "$PY_BIN" "$MAIN_PY" "$@"