# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 ficus-pro
"""
DASHBOARD – Window factory.
Creates the application window with a toggle button for the TEST overlay.
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from test_overlay import TestOverlayWindow

# Module-level reference so the click handler can access the overlay
# without walking the widget tree.
_overlay: TestOverlayWindow | None = None


def create_window(app: Gtk.Application) -> Gtk.ApplicationWindow:
    """
    Return a Gtk.ApplicationWindow with a "Toggle TEST Overlay" button.
    Clicking the button creates (or hides) a translucent overlay window
    displaying only the text "TEST".
    """
    win = Gtk.ApplicationWindow(application=app)
    win.set_title("DASHBOARD")
    win.set_default_size(400, 300)
    win.set_icon_name("org.ficus.Dashboard")

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.set_halign(Gtk.Align.CENTER)
    box.set_valign(Gtk.Align.CENTER)
    box.set_spacing(12)
    win.set_child(box)

    global _overlay

    overlay_btn = Gtk.Button(label="Toggle TEST Overlay")
    overlay_btn.set_tooltip_text(
        "Show or hide a transparent overlay window displaying 'TEST'.\n"
        "In this build, the overlay appears at the top-left by default."
    )
    overlay_btn.connect("clicked", _on_toggle_clicked)
    box.append(overlay_btn)

    return win


def _on_toggle_clicked(btn: Gtk.Button) -> None:
    """
    Show or hide the TEST overlay window.
    """
    global _overlay

    if _overlay is None:
        # Create the overlay (will appear at top-left by default in this GTK4 build)
        overlay = TestOverlayWindow()
        overlay.show()
        _overlay = overlay
    else:
        if _overlay.get_visible():
            _overlay.hide()
        else:
            _overlay.show()

    _refresh_button_label(btn)


def _refresh_button_label(btn: Gtk.Button) -> None:
    """Update the button label to reflect overlay visibility."""
    global _overlay
    if _overlay is not None and _overlay.get_visible():
        btn.set_label("Hide TEST Overlay")
    else:
        btn.set_label("Toggle TEST Overlay")