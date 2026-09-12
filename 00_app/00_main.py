#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Entry point.
Launches the GTK application and shows the main window.

Qt (PyQt6) is initialized BEFORE GTK so that the TEST overlay's
QApplication can coexist with GTK4's event loop on Wayland.
"""

import sys
from pathlib import Path

# PyQt6 must be imported before GTK so its QApplication is created first.
# Qt's WindowStaysOnTopHint works natively on Wayland; GTK4's
# Gdk.ToplevelState.ABOVE is ignored by GNOME Shell 50.4 on Wayland.
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Prevent Qt from trying to use an X11 backend when running on Wayland.
import os
os.environ.setdefault("QT_QPA_PLATFORM", "wayland")

# Initialise a headless QApplication early (no screens needed here).
# The real screen-backed app is created lazily inside test_overlay.py.
_qt_app = QApplication.instance()
if _qt_app is None:
    QApplication([])

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

# Pump Qt events every 50 ms so the overlay stays responsive alongside GTK.
def _pump_qt_events() -> bool:
    """Process pending Qt events from the GLib main loop."""
    app = QApplication.instance()
    if app is not None:
        app.processEvents()
    return True  # Keep firing.

GLib.timeout_add(50, _pump_qt_events)

from window import create_window


def on_activate(app):
    """Callback invoked when the application is activated."""
    win = create_window(app)
    win.present()


def on_shutdown(app):
    """Clean up the Qt application when GTK shuts down."""
    qt_app = QApplication.instance()
    if qt_app is not None:
        qt_app.quit()


def main():
    app = Gtk.Application(application_id="org.ficus.Dashboard")
    app.connect("activate", on_activate)
    app.connect("shutdown", on_shutdown)
    return app.run(None)


if __name__ == "__main__":
    raise SystemExit(main())
