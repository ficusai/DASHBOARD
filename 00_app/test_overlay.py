# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – TEST overlay management (subprocess-based).

The overlay runs as a separate PyQt6 process (qt_overlay.py) to avoid
GTK/Qt GType conflicts on Wayland.  This module launches or signals
that process via subprocess.
"""

import subprocess
import sys
from pathlib import Path


# Overlay script path — kept relative to this module's location.
_OVERLAY_SCRIPT = Path(__file__).with_name("qt_overlay.py")


def _run_overlay(args: list[str]) -> str | None:
    """Launch qt_overlay.py with the given flags and return stdout."""
    try:
        result = subprocess.run(
            [sys.executable, str(_OVERLAY_SCRIPT)] + args,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def show_overlay() -> None:
    """Show the TEST overlay (launches the overlay process if needed)."""
    _run_overlay(["--show"])


def hide_overlay() -> None:
    """Hide the TEST overlay."""
    _run_overlay(["--hide"])


def toggle_overlay() -> bool:
    """
    Toggle the overlay visibility.

    Returns:
        True if the overlay is now visible, False otherwise.
    """
    resp = _run_overlay(["--toggle"])
    return resp == "shown"


def is_overlay_visible() -> bool:
    """Return True if the overlay is currently visible."""
    resp = _run_overlay(["--visible"])
    return resp == "true"
