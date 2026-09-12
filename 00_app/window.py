# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Window factory.
Creates an empty application window with only the system title-bar
(which contains the close button).
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def create_window(app: Gtk.Application) -> Gtk.ApplicationWindow:
    """
    Return a minimal Gtk.ApplicationWindow attached to *app*.
    No child widgets are added, so the window appears empty.
    """
    win = Gtk.ApplicationWindow(application=app)
    win.set_title("DASHBOARD")
    win.set_default_size(400, 300)
    win.set_icon_name("org.ficus.Dashboard")

    # The window is deliberately left empty.
    # The close button (X) is provided by the system title-bar.
    return win
