#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Entry point.
Launches the GTK application and shows the main window.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from _01_window import create_window


def on_activate(app):
    """Callback invoked when the application is activated."""
    win = create_window(app)
    win.present()


def main():
    app = Gtk.Application(application_id="org.ficus.Dashboard")
    app.connect("activate", on_activate)
    return app.run(None)


if __name__ == "__main__":
    raise SystemExit(main())
