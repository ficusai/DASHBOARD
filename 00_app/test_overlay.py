# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Transparent TEST overlay window (PyQt6).

Extracted from PROGRESS /floating_overlay_card.py pattern.
Uses PyQt6 Qt.WindowStaysOnTopHint which works natively on Wayland,
unlike GTK4's Gdk.ToplevelState.ABOVE (ignored by GNOME Shell on Wayland).

The overlay is a top-level QWidget created by show_overlay() and toggled
by the main window's button via show_overlay() / hide_overlay().
Qt events are pumped by the main GTK event loop via GLib.timeout_add().
"""

import os
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QFont


# Overlay reference managed by show_overlay() / hide_overlay().
_overlay: Optional["QApplication"] = None


def _get_qt_app() -> QApplication:
    """Return the global QApplication instance, creating it if needed."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _ensure_overlay_exists() -> Optional[QWidget]:
    """Return the existing overlay widget or None if it hasn't been created yet."""
    import test_overlay as _mod
    return getattr(_mod, "_widget", None)


class TestOverlayWindow(QWidget):
    """
    A translucent, frameless overlay showing the text "TEST".

    Uses Qt.WindowStaysOnTopHint so it stays above all other windows,
    including on Wayland where GTK4's Gdk.ToplevelState.ABOVE is ignored
    by GNOME Shell 50.4.

    Supports click-and-drag repositioning.
    """

    def __init__(self) -> None:
        super().__init__()

        self._custom_position = False
        self._is_dragging = False
        self._drag_offset = None

        # Always-on-top, frameless, tool-window (no taskbar entry)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(140, 60)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        # Translucent dark background + blue TEST label
        self.setStyleSheet("""
            TestOverlayWindow {
                background-color: rgba(15, 23, 42, 180);
            }
            QLabel {
                color: #60a5fa;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI', Ubuntu, sans-serif;
            }
        """)

        label = QLabel("TEST", self)
        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(label)

    # ------------------------------------------------------------------ #
    #  Drag support                                                        #
    # ------------------------------------------------------------------ #

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._custom_position = True
            self._is_dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._is_dragging and self._drag_offset is not None:
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._drag_offset = None
            event.accept()

    # ------------------------------------------------------------------ #
    #  Positioning                                                         #
    # ------------------------------------------------------------------ #

    def position_default(self) -> None:
        """Place the overlay at the top-left of the primary screen."""
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = self.width(), self.height()
        margin = 24
        self.move(margin, margin + h)


def show_overlay() -> None:
    """Create and show the TEST overlay if it isn't already visible."""
    global _overlay
    qt_app = _get_qt_app()

    if _overlay is None:
        _overlay = TestOverlayWindow()
        _overlay.position_default()
        import test_overlay as _mod
        _mod._widget = _overlay

    _overlay.show()
    _overlay.raise_()
    _overlay.activateWindow()


def hide_overlay() -> None:
    """Hide the TEST overlay without destroying it."""
    global _overlay
    w = _get_widget()
    if w is not None:
        w.hide()


def is_overlay_visible() -> bool:
    """Return True if the overlay is currently visible."""
    w = _get_widget()
    return w is not None and w.isVisible()


def _get_widget() -> Optional[QWidget]:
    """Retrieve the current overlay widget instance."""
    import test_overlay as _mod
    return getattr(_mod, "_widget", None)
