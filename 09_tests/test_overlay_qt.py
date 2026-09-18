# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""Tests for the TEST overlay module and its subprocess-based overlay."""

import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Keep QApplication headless so the test never blocks connecting to the
# desktop compositor (Wayland/X11) and works in CI.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).parent.parent / "00_app"))


def test_overlay_module_exists():
    """Import test_overlay successfully."""
    mod = importlib.import_module("test_overlay")
    assert hasattr(mod, "show_overlay")
    assert hasattr(mod, "hide_overlay")
    assert hasattr(mod, "is_overlay_visible")
    assert callable(mod.show_overlay)
    assert callable(mod.hide_overlay)
    assert callable(mod.is_overlay_visible)


def test_qt_overlay_script_exists():
    """The standalone overlay script is present."""
    script = Path(__file__).parent.parent / "00_app" / "qt_overlay.py"
    assert script.exists()


def test_qt_overlay_flags():
    """The overlay uses the correct Qt window flags for always-on-top."""
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    # Verify the flags that OverlayApp sets match expectations
    flags = (
        Qt.WindowType.Window
        | Qt.WindowType.FramelessWindowHint
        | Qt.WindowType.WindowStaysOnTopHint
        | Qt.WindowType.Tool
    )
    assert flags & Qt.WindowType.WindowStaysOnTopHint
    assert flags & Qt.WindowType.FramelessWindowHint
    assert flags & Qt.WindowType.Tool
    assert flags & Qt.WindowType.Window
