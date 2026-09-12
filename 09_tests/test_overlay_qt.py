# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""Tests for the PyQt6 TEST overlay module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "00_app"))


def test_overlay_module_exists():
    """Import test_overlay successfully."""
    import importlib
    mod = importlib.import_module("test_overlay")
    assert hasattr(mod, "show_overlay")
    assert hasattr(mod, "hide_overlay")
    assert hasattr(mod, "is_overlay_visible")
    assert callable(mod.show_overlay)
    assert callable(mod.hide_overlay)
    assert callable(mod.is_overlay_visible)


def test_overlay_class_exists():
    """TestOverlayWindow class is importable."""
    from test_overlay import TestOverlayWindow
    assert TestOverlayWindow is not None


def test_overlay_window_flags():
    """Overlay window has the correct always-on-top flags."""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from test_overlay import TestOverlayWindow

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    overlay = TestOverlayWindow()
    flags = overlay.windowFlags()
    assert flags & Qt.WindowType.WindowStaysOnTopHint
    assert flags & Qt.WindowType.FramelessWindowHint
    assert flags & Qt.WindowType.Tool
    assert flags & Qt.WindowType.Window
