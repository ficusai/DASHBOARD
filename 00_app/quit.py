# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Quit handler (placeholder).
In GTK 4, closing the last window automatically terminates the application.
This module is reserved for future custom shutdown behaviour.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def on_close_request(window: Gtk.ApplicationWindow) -> bool:
    """
    Optional handler connected to the 'close-request' signal.
    Return False to allow the default destroy behaviour.
    """
    # Future: save state, ask for confirmation, etc.
    return False
