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
import time
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
    return is_overlay_visible()


def is_overlay_visible(max_wait: float = 3.0) -> bool:
    """Return True if the overlay is currently visible.

    A freshly launched overlay daemon needs a moment to import PyQt6 and
    bind its Unix socket, so transient connection failures are retried
    (up to ``max_wait`` seconds) instead of being misread as "hidden".
    """
    deadline = time.monotonic() + max_wait
    while True:
        resp = _run_overlay(["--visible"])
        if resp in ("true", "false"):
            return resp == "true"
        if time.monotonic() >= deadline:
            break
        time.sleep(0.05)
    return False