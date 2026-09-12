#!/usr/bin/env bash
# Build a single-file executable for DASHBOARD.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPEC_FILE="$PROJECT_ROOT/01_build/00_dashboard.spec"

echo "==> Installing system dependencies (requires sudo)..."
sudo dnf install -y python3-gobject gtk4 python3-gobject-devel

echo "==> Installing PyInstaller..."
pip install --user pyinstaller PyQt6

echo "==> Freezing application using spec file..."
cd "$PROJECT_ROOT"
pyinstaller --clean --noconfirm "$SPEC_FILE"

echo "==> Executable created at: $PROJECT_ROOT/dist/dashboard"
