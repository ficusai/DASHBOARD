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
    """Launch qt_overlay.py and return stdout if it exits quickly.

    Commands that query state (e.g. --visible) exit immediately and
    their output is returned.  Commands that may start the daemon
    (e.g. --show, --toggle) are launched fire-and-forget; None is
    returned so the caller checks state via --visible instead.
    """
    try:
        proc = subprocess.Popen(
            [sys.executable, str(_OVERLAY_SCRIPT)] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Only wait for short-running commands (queries).
        # Daemon-starting commands run indefinitely and must not be waited on.
        if args in (["--visible"],):
            try:
                stdout, _stderr = proc.communicate(timeout=5)
                return (stdout or b"").decode().strip() or None
            except subprocess.TimeoutExpired:
                proc.kill()
                return None
        # For other commands just launch and forget.
        return None
    except (FileNotFoundError, OSError):
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
    _run_overlay(["--toggle"])
    # Give the daemon a moment to start, then query state.
    import time
    time.sleep(0.3)
    return is_overlay_visible()


def is_overlay_visible() -> bool:
    """Return True if the overlay is currently visible."""
    resp = _run_overlay(["--visible"])
    return resp == "true"
